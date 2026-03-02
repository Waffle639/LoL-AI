"""
Base de datos SQLite con SQLAlchemy.
Guarda usuarios, API keys, créditos y transacciones de Stripe.

Relaciones:
    User 1──N APIKey (user.api_keys / api_key.user)
    APIKey 1──N CreditTransaction (api_key.transactions / tx.api_key_obj)
"""

from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, ForeignKey, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lol_api.db")

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
    created_at          = Column(DateTime, default=datetime.utcnow)

    # Relación: un usuario tiene N api_keys
    api_keys            = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")


class PendingRegistration(Base):
    """Registro temporal almacenado antes de confirmar el pago con Stripe."""
    __tablename__ = "pending_registrations"

    id              = Column(String, primary_key=True)        # token UUID
    username        = Column(String, nullable=False)
    email           = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    plan            = Column(String, default="starter")
    created_at      = Column(DateTime, default=datetime.utcnow)


class APIKey(Base):
    __tablename__ = "api_keys"

    key         = Column(String, primary_key=True, index=True)
    name        = Column(String, nullable=False)
    credits     = Column(Integer, default=0)
    is_active   = Column(Boolean, default=True)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    key_prefix  = Column(String, nullable=True)               # Primeros 16 chars (para mostrar en dashboard)
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    created_at          = Column(DateTime, default=datetime.utcnow)

    # Relación inversa
    api_key_obj         = relationship("APIKey", back_populates="transactions")


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
