"""
Servicio de autenticación y creación de cuentas.

Funciones públicas:
    hash_key(key)                  → SHA-256 de una API key
    get_api_key(header)            → Extrae X-API-Key del header
    verify_api_key(key, db)        → Valida key y créditos (FastAPI Depends)
    consume_credit(user, db)       → Descuenta 1 crédito de la cuenta
    create_user_and_api_key(...)   → Crea User + APIKey (inactiva) + CreditTransaction
                                     para altas via Stripe.
"""

import hashlib
import hmac
import secrets
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import Header, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.database import (
    get_db,
    APIKey,
    CreditTransaction,
    User,
    PendingRegistration,
    save_refresh_token,
    get_refresh_token,
    revoke_refresh_token,
)

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)
api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-env")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MIN", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def utc_now() -> datetime:
    """Return current UTC datetime using timezone-aware API."""
    return datetime.now(timezone.utc)


# ==================== UTILS ====================

def hash_key(key: str) -> str:
    """SHA-256 de una API key en texto plano."""
    return hashlib.sha256(key.encode()).hexdigest()


def generate_api_key_values() -> tuple[str, str, str]:
    """Genera una API key en claro, su hash y su prefijo de 16 chars."""
    raw_key = "lol_" + secrets.token_urlsafe(32)
    hashed = hash_key(raw_key)
    return raw_key, hashed, raw_key[:16]


def issue_api_key_for_user(db: Session, user: "User", mode: str) -> dict:
    """Crea o regenera una API key activa para el usuario.

    mode: "create" (si no hay key activa) o "regenerate" (rota la actual).
    Devuelve raw key, prefijo y creditos asociados.
    """
    active_key = db.query(APIKey).filter(
        APIKey.user_id == user.id,
        APIKey.is_active.is_(True),
    ).order_by(APIKey.created_at.desc()).first()

    if mode == "create":
        if active_key:
            raise HTTPException(status_code=409, detail="El usuario ya tiene una API key activa")
    elif mode == "regenerate":
        if not active_key:
            raise HTTPException(status_code=404, detail="No hay API key activa para regenerar")
        active_key.is_active = False
        active_key.updated_at = utc_now()
    else:
        raise HTTPException(status_code=400, detail="Modo de API key no valido")

    raw_key, hashed, prefix = generate_api_key_values()
    new_key = APIKey(
        key=hashed,
        name=user.username,
        is_active=True,
        user_id=user.id,
        key_prefix=prefix,
        created_at=utc_now(),
    )
    db.add(new_key)
    db.commit()

    return {
        "api_key": raw_key,
        "api_key_prefix": prefix,
        "credits_remaining": user.credits,
    }


def hash_token(token: str) -> str:
    """SHA-256 hash de un JWT refresh token."""
    return hashlib.sha256(token.encode()).hexdigest()


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


# ==================== JWT ====================

def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MIN),
        "type": "access",
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: int, db: Session) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": expires_at,
        "type": "refresh",
        "jti": secrets.token_hex(16),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    save_refresh_token(db, user_id=user_id, token_hash=hash_token(token), expires_at=expires_at)
    return token


def verify_jwt(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            return None
        return int(payload["sub"])
    except (JWTError, ValueError, TypeError):
        return None


def decode_refresh_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None


def rotate_refresh_token(old_token: str, db: Session) -> Optional[str]:
    payload = decode_refresh_token(old_token)
    if not payload:
        return None

    token_hash = hash_token(old_token)
    stored = get_refresh_token(db, token_hash)
    if not stored or stored.revoked or stored.expires_at < datetime.now(timezone.utc):
        return None

    revoke_refresh_token(db, token_hash)
    user_id = int(payload["sub"])
    return create_refresh_token(user_id=user_id, db=db)


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
    if not key_obj.user_id:
        raise HTTPException(status_code=401, detail="API Key inválida")

    user = db.query(User).filter(User.id == key_obj.user_id, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no autorizado")

    if user.credits <= 0:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "Sin créditos",
                "message": "Recarga créditos en /billing/checkout",
                "credits_remaining": user.credits,
            },
        )
    return key_obj


def verify_api_key_no_credit(api_key: str, db: Session) -> Optional[APIKey]:
    """Valida API key sin exigir créditos; útil para endpoints de cuenta."""
    hashed = hash_key(api_key)
    key_obj = db.query(APIKey).filter(APIKey.key == hashed).first()
    if not key_obj or not key_obj.is_active:
        return None
    return key_obj


def get_current_user(
    x_api_key: Optional[str] = Security(api_key_scheme),
    bearer: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> User:
    """Resuelve el usuario autenticado por JWT o por API key."""

    # Prioridad JWT
    bearer_token = bearer.credentials if bearer else None
    header_token = authorization[7:] if authorization and authorization.startswith("Bearer ") else None
    token = bearer_token or header_token

    if token:
        user_id = verify_jwt(token)
        if user_id:
            user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
            if user:
                return user

    # Fallback API key
    if x_api_key:
        key_obj = verify_api_key_no_credit(x_api_key, db)
        if key_obj and key_obj.user_id:
            user = db.query(User).filter(User.id == key_obj.user_id, User.is_active.is_(True)).first()
            if user:
                return user

    raise HTTPException(status_code=401, detail="Not authenticated")


def get_current_user_jwt(
    bearer: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> User:
    """Resuelve usuario autenticado solo por JWT Bearer."""
    bearer_token = bearer.credentials if bearer else None
    header_token = authorization[7:] if authorization and authorization.startswith("Bearer ") else None
    token = bearer_token or header_token

    if not token:
        raise HTTPException(status_code=401, detail="Bearer token requerido")

    user_id = verify_jwt(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no autorizado")
    return user


def get_current_api_key_with_credits(
    x_api_key: Optional[str] = Security(api_key_scheme),
    bearer: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> APIKey:
    """Resuelve una API key activa con créditos usando JWT o API key directa."""

    bearer_token = bearer.credentials if bearer else None
    header_token = authorization[7:] if authorization and authorization.startswith("Bearer ") else None
    token = bearer_token or header_token

    if token:
        user_id = verify_jwt(token)
        if user_id:
            user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
            if not user:
                raise HTTPException(status_code=401, detail="Usuario no autorizado")
            key_obj = db.query(APIKey).filter(
                APIKey.user_id == user_id,
                APIKey.is_active.is_(True),
            ).order_by(APIKey.created_at.desc()).first()
            if key_obj is None:
                raise HTTPException(status_code=404, detail="No hay API key activa para este usuario")
            if user.credits <= 0:
                raise HTTPException(
                    status_code=402,
                    detail={
                        "error": "Sin créditos",
                        "message": "Recarga créditos en /billing/checkout",
                        "credits_remaining": user.credits,
                    },
                )
            return key_obj

    if x_api_key:
        return verify_api_key(api_key=x_api_key, db=db)

    raise HTTPException(status_code=401, detail="Not authenticated")


def get_current_user_with_credits(
    x_api_key: Optional[str] = Security(api_key_scheme),
    bearer: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> tuple[User, Optional[APIKey]]:
    """Resuelve usuario autenticado y valida créditos en la cuenta."""
    bearer_token = bearer.credentials if bearer else None
    header_token = authorization[7:] if authorization and authorization.startswith("Bearer ") else None
    token = bearer_token or header_token

    if token:
        user_id = verify_jwt(token)
        if user_id:
            user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
            if not user:
                raise HTTPException(status_code=401, detail="Usuario no autorizado")
            if user.credits <= 0:
                raise HTTPException(
                    status_code=402,
                    detail={
                        "error": "Sin créditos",
                        "message": "Recarga créditos en /billing/checkout",
                        "credits_remaining": user.credits,
                    },
                )
            key_obj = db.query(APIKey).filter(
                APIKey.user_id == user.id,
                APIKey.is_active.is_(True),
            ).order_by(APIKey.created_at.desc()).first()
            return user, key_obj

    if x_api_key:
        key_obj = verify_api_key(api_key=x_api_key, db=db)
        user = db.query(User).filter(User.id == key_obj.user_id, User.is_active.is_(True)).first()
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        return user, key_obj

    raise HTTPException(status_code=401, detail="Not authenticated")


def consume_credit(
    user: User,
    db: Session,
    description: str = "Predicción",
    api_key_obj: Optional[APIKey] = None,
):
    """Descuenta 1 crédito de la cuenta y registra la transacción."""
    user.credits -= 1
    db.add(CreditTransaction(
        user_id=user.id,
        api_key=api_key_obj.key if api_key_obj else None,
        amount=-1,
        description=description,
    ))
    db.commit()


def apply_credits_to_user(
    db: Session,
    user: User,
    credits: int,
    description: str,
    stripe_session_id: Optional[str] = None,
    commit: bool = True,
) -> Optional[APIKey]:
    """Suma créditos a la cuenta y registra la transacción."""
    if credits <= 0:
        return None

    user.credits = (user.credits or 0) + credits

    key_obj = db.query(APIKey).filter(
        APIKey.user_id == user.id,
        APIKey.is_active.is_(True),
    ).order_by(APIKey.created_at.desc()).first()

    db.add(CreditTransaction(
        user_id=user.id,
        api_key=key_obj.key if key_obj else None,
        amount=credits,
        description=description,
        stripe_session_id=stripe_session_id,
    ))
    if commit:
        db.commit()
    return key_obj


# ==================== CREACIÓN DE CUENTA ====================

def create_user_and_api_key(
    db:                Session,
    pending_id:        Optional[str],
    customer_id:       Optional[str],
    email_fallback:    str,
    credits:           int,
    stripe_session_id: str,
) -> Optional[str]:
    """
    Crea el User (desde PendingRegistration si existe, o con los datos de Stripe)
    y registra los creditos en la cuenta.

    No expone la API key en claro y solo guarda el hash.
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
            )

    if customer_id and not user.stripe_customer_id:
        user.stripe_customer_id = customer_id

    db.add(user)
    db.flush()  # obtiene user.id sin commit

    # ── 2. Generar API Key inactiva si no existe ─────────────────────────────
    existing_key = db.query(APIKey).filter(
        APIKey.user_id == user.id,
    ).order_by(APIKey.created_at.desc()).first()

    if not existing_key:
        _raw_key, hashed, _prefix = generate_api_key_values()
        key_obj = APIKey(
            key        = hashed,
            name       = user.username,
            is_active  = False,
            user_id    = user.id,
            key_prefix = None,
            created_at = utc_now(),
        )
        db.add(key_obj)
        db.flush()

    apply_credits_to_user(
        db=db,
        user=user,
        credits=credits,
        description="Creditos de checkout",
        stripe_session_id=stripe_session_id,
        commit=False,
    )

    # ── 5. Limpiar pending ────────────────────────────────────────────────────
    if pending:
        db.delete(pending)

    db.commit()
    logger.info(f"✅ Creditos sumados: {user.email} | +{credits}")
    return None
