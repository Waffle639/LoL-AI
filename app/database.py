"""
Base de datos SQLite con SQLAlchemy.
Guarda API keys, créditos y transacciones de Stripe.
"""

from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lol_api.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # necesario para SQLite con FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ==================== MODELOS ====================

class APIKey(Base):
    __tablename__ = "api_keys"

    key         = Column(String, primary_key=True, index=True)
    name        = Column(String, nullable=False)          # etiqueta para identificarla (ej: "cliente_1")
    credits     = Column(Integer, default=0)
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CreditTransaction(Base):
    __tablename__ = "credit_transactions"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    api_key             = Column(String, index=True)
    amount              = Column(Integer)                 # positivo = recarga, negativo = consumo
    description         = Column(String)
    stripe_session_id   = Column(String, nullable=True)
    created_at          = Column(DateTime, default=datetime.utcnow)


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
