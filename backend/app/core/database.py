"""
Base de datos SQLite con SQLAlchemy.
Guarda usuarios, API keys, créditos y transacciones de Stripe.

Relaciones:
    User 1──N APIKey (user.api_keys / api_key.user)
    APIKey 1──N CreditTransaction (api_key.transactions / tx.api_key_obj)
"""

from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, ForeignKey, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timezone
from typing import Optional
import os
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]


def resolve_database_url() -> str:
    """Resolve sqlite relative paths against backend root (stable across CWDs)."""
    db_url = os.getenv("DATABASE_URL", "sqlite:///./lol_api.db")

    if db_url.startswith("sqlite:///") and not db_url.startswith("sqlite:////"):
        rel_path = db_url.replace("sqlite:///", "", 1)
        if rel_path.startswith("./"):
            rel_path = rel_path[2:]
        return f"sqlite:///{(BACKEND_ROOT / rel_path).resolve()}"

    return db_url


DATABASE_URL = resolve_database_url()

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Habilitar FOREIGN KEYS en cada conexión SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def utc_now() -> datetime:
    """Return current UTC datetime using timezone-aware API."""
    return datetime.now(timezone.utc)


# ==================== MODELOS ====================

class User(Base):
    """Cuenta de usuario con credenciales de acceso."""
    __tablename__ = "users"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    username            = Column(String, unique=True, index=True, nullable=False)
    email               = Column(String, unique=True, index=True, nullable=False)
    hashed_password     = Column(String, nullable=False)
    stripe_customer_id  = Column(String, nullable=True)
    plan                = Column(String, default="starter")   # "starter" | "monthly"
    is_active           = Column(Boolean, default=True)
    created_at          = Column(DateTime, default=utc_now)

    # Relación: un usuario tiene N api_keys
    api_keys            = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens      = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


class PendingRegistration(Base):
    """Registro temporal almacenado antes de confirmar el pago con Stripe."""
    __tablename__ = "pending_registrations"

    id              = Column(String, primary_key=True)        # token UUID
    username        = Column(String, nullable=False)
    email           = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    plan            = Column(String, default="starter")
    created_at      = Column(DateTime, default=utc_now)


class APIKey(Base):
    __tablename__ = "api_keys"

    key         = Column(String, primary_key=True, index=True)
    name        = Column(String, nullable=False)
    credits     = Column(Integer, default=0)
    is_active   = Column(Boolean, default=True)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    key_prefix  = Column(String, nullable=True)               # Primeros 16 chars (para mostrar en dashboard)
    created_at  = Column(DateTime, default=utc_now)
    updated_at  = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relaciones
    user         = relationship("User", back_populates="api_keys")
    transactions = relationship("CreditTransaction", back_populates="api_key_obj", cascade="all, delete-orphan")


class CreditTransaction(Base):
    __tablename__ = "credit_transactions"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    api_key             = Column(String, ForeignKey("api_keys.key", ondelete="CASCADE"), index=True)
    amount              = Column(Integer)
    description         = Column(String)
    stripe_session_id   = Column(String, nullable=True)
    created_at          = Column(DateTime, default=utc_now)

    # Relación inversa
    api_key_obj         = relationship("APIKey", back_populates="transactions")


class RefreshToken(Base):
    """Refresh token persistido en DB para permitir revocación."""
    __tablename__ = "refresh_tokens"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash  = Column(String, nullable=False, unique=True, index=True)
    expires_at  = Column(DateTime, nullable=False)
    revoked     = Column(Boolean, nullable=False, default=False)
    created_at  = Column(DateTime, default=utc_now)

    user        = relationship("User", back_populates="refresh_tokens")


# ==================== REFRESH TOKENS HELPERS ====================

def save_refresh_token(db, user_id: int, token_hash: str, expires_at: datetime) -> RefreshToken:
    token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        revoked=False,
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def get_refresh_token(db, token_hash: str) -> Optional[RefreshToken]:
    return db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()


def revoke_refresh_token(db, token_hash: str) -> None:
    token = get_refresh_token(db, token_hash)
    if token and not token.revoked:
        token.revoked = True
        db.commit()


def revoke_all_user_tokens(db, user_id: int) -> None:
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked.is_(False),
    ).update({"revoked": True}, synchronize_session=False)
    db.commit()


# ==================== INIT ====================

def create_tables():
    """Crea las tablas si no existen."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency de FastAPI para obtener sesión de DB."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
