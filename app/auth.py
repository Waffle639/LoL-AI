"""
Servicio de autenticación por API Key.
Valida la key y verifica que tiene créditos disponibles.
"""

import hashlib

from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db, APIKey, CreditTransaction
from datetime import datetime


def get_api_key(x_api_key: str = Header(..., description="Tu API Key")):
    """Extrae el header X-API-Key de la request."""
    return x_api_key

def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()

def verify_api_key(api_key: str = Depends(get_api_key), db: Session = Depends(get_db)):
    hashed = hash_key(api_key)  # hashea lo que llega
    key_obj = db.query(APIKey).filter(APIKey.key == hashed).first()

    if not key_obj:
        raise HTTPException(status_code=401, detail="API Key inválida")

    if not key_obj.is_active:
        raise HTTPException(status_code=403, detail="API Key desactivada")

    if key_obj.credits <= 0:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "Sin créditos",
                "message": "Recarga créditos en /billing/checkout",
                "credits_remaining": key_obj.credits
            }
        )

    return key_obj


def consume_credit(key_obj: APIKey, db: Session, description: str = "Predicción"):
    """
    Descuenta 1 crédito y registra la transacción.
    Llamar DESPUÉS de hacer la predicción correctamente.
    """
    key_obj.credits -= 1
    key_obj.updated_at = datetime.utcnow()

    transaction = CreditTransaction(
        api_key=key_obj.key,
        amount=-1,
        description=description,
    )
    db.add(transaction)
    db.commit()
