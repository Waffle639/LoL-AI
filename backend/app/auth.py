"""
Servicio de autenticación y creación de cuentas.

Funciones públicas:
    hash_key(key)                  → SHA-256 de una API key
    get_api_key(header)            → Extrae X-API-Key del header
    verify_api_key(key, db)        → Valida key y créditos (FastAPI Depends)
    consume_credit(key_obj, db)    → Descuenta 1 crédito tras una predicción
    create_user_and_api_key(...)   → Crea User + APIKey + CreditTransaction
                                     Único punto de creación de cuentas.
"""

import hashlib
import hmac
import secrets
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db, APIKey, CreditTransaction, User, PendingRegistration

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    """Return current UTC datetime using timezone-aware API."""
    return datetime.now(timezone.utc)


# ==================== UTILS ====================

def hash_key(key: str) -> str:
    """SHA-256 de una API key en texto plano."""
    return hashlib.sha256(key.encode()).hexdigest()


def hash_password(password: str) -> str:
    """Genera un hash seguro pbkdf2 con salt aleatorio. Formato: '<salt_hex>:<key_hex>'."""
    salt = secrets.token_bytes(16).hex()
    key  = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 100_000).hex()
    return f"{salt}:{key}"


def verify_password(plain: str, stored: str) -> bool:
    """Comprueba una contraseña contra su hash pbkdf2."""
    if not stored or ":" not in stored:
        return False
    try:
        salt, key = stored.split(":", 1)
        new_key   = hashlib.pbkdf2_hmac(
            "sha256", plain.encode(), bytes.fromhex(salt), 100_000
        ).hex()
        return hmac.compare_digest(key, new_key)
    except Exception:
        return False


# ==================== FASTAPI DEPS ====================

def get_api_key(x_api_key: str = Header(..., description="Tu API Key")):
    """Extrae el header X-API-Key de la request."""
    return x_api_key


def verify_api_key(api_key: str = Depends(get_api_key), db: Session = Depends(get_db)):
    """Valida la API key y comprueba que tiene créditos."""
    hashed  = hash_key(api_key)
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
                "credits_remaining": key_obj.credits,
            },
        )
    return key_obj


def consume_credit(key_obj: APIKey, db: Session, description: str = "Predicción"):
    """Descuenta 1 crédito y registra la transacción. Llamar tras predicción exitosa."""
    key_obj.credits    -= 1
    key_obj.updated_at  = utc_now()
    db.add(CreditTransaction(api_key=key_obj.key, amount=-1, description=description))
    db.commit()


# ==================== CREACIÓN DE CUENTA ====================

def create_user_and_api_key(
    db:                Session,
    pending_id:        Optional[str],
    customer_id:       Optional[str],
    email_fallback:    str,
    plan:              str,
    credits:           int,
    stripe_session_id: str,
) -> Optional[str]:
    """
    Crea el User (desde PendingRegistration si existe, o con los datos de Stripe)
    y su APIKey asociada.

    Devuelve el raw_key en texto plano para mostrarlo una única vez.
    Devuelve None si el usuario ya existía (protección contra retries del webhook).
    """

    # ── 1. Resolver usuario ───────────────────────────────────────────────────
    pending = (
        db.query(PendingRegistration).filter(PendingRegistration.id == pending_id).first()
        if pending_id else None
    )

    if pending:
        # Protección contra retries: si el usuario ya existe, limpiar y salir
        if db.query(User).filter(User.email == pending.email).first():
            logger.warning(f"Usuario {pending.email} ya existe — ignorando retry")
            db.delete(pending)
            db.commit()
            return None

        user = User(
            username           = pending.username,
            email              = pending.email,
            hashed_password    = pending.hashed_password,
            stripe_customer_id = customer_id,
            plan               = plan,
        )
    else:
        # Sin pending: usar email del objeto de sesión de Stripe
        user = db.query(User).filter(User.email == email_fallback).first()
        if user:
            logger.info(f"Usuario {email_fallback} ya existe — asignando nueva key")
        else:
            user = User(
                username           = email_fallback.split("@")[0],
                email              = email_fallback,
                hashed_password    = "",
                stripe_customer_id = customer_id,
                plan               = plan,
            )

    db.add(user)
    db.flush()  # obtiene user.id sin commit

    # ── 2. Generar API Key ────────────────────────────────────────────────────
    raw_key    = "lol_" + secrets.token_urlsafe(32)
    hashed     = hash_key(raw_key)
    key_prefix = raw_key[:16]

    key_obj = APIKey(
        key        = hashed,
        name       = user.username,
        credits    = credits,
        is_active  = True,
        user_id    = user.id,
        key_prefix = key_prefix,
        created_at = utc_now(),
    )
    db.add(key_obj)
    db.flush()  # persiste la APIKey antes de la FK en CreditTransaction

    # ── 3. Registrar transacción inicial ──────────────────────────────────────
    # La raw_key se guarda temporalmente en description; se borra al mostrarse en /success
    db.add(CreditTransaction(
        api_key           = hashed,
        amount            = credits,
        description       = raw_key,
        stripe_session_id = stripe_session_id,
    ))

    # ── 4. Limpiar pending ────────────────────────────────────────────────────
    if pending:
        db.delete(pending)

    db.commit()
    logger.info(f"✅ Cuenta creada: {user.email} | plan: {plan} | {credits} créditos")
    return raw_key
