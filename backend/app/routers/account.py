"""Endpoints JSON de cuenta para landing y dashboard."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from app.core.database import get_db, User, APIKey
from app.auth import verify_password, hash_password, hash_key, get_api_key, get_current_user_jwt, issue_api_key_for_user

router = APIRouter(prefix="/account", tags=["account"])


class RegisterRequest(BaseModel):
    username: str = Field(..., description="Nombre de usuario")
    email: EmailStr = Field(..., description="Email de acceso")
    password: str = Field(..., description="Contrasena (minimo 8 caracteres)")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "username": "summoner1",
                "email": "summoner1@lolai.com",
                "password": "Pass12345"
            }]
        }
    }


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email registrado")
    password: str = Field(..., description="Contrasena")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "email": "summoner1@lolai.com",
                "password": "Pass12345"
            }]
        }
    }


@router.post(
    "/register",
    summary="Crear cuenta",
    description="Legacy: usa /auth/register. Crea usuario (sin API key inicial).",
    deprecated=True,
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    username = payload.username.strip()
    email = payload.email.strip().lower()
    password = payload.password.strip()

    if len(username) < 3:
        raise HTTPException(status_code=400, detail="El nombre de usuario debe tener al menos 3 caracteres")
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres")

    existing = db.query(User).filter((User.email == email) | (User.username == username)).first()
    if existing:
        raise HTTPException(status_code=409, detail="El email o el nombre de usuario ya están registrados")

    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        is_active=True,
    )
    db.add(user)
    db.flush()

    db.commit()

    return {
        "message": "Cuenta creada",
        "username": user.username,
        "email": user.email,
        "api_key_prefix": None,
        "credits_remaining": user.credits,
    }

@router.post(
    "/login",
    summary="Login con API key",
    description="Legacy: usa /auth/login. Valida usuario y devuelve su API key y creditos.",
    deprecated=True,
)
def login_submit(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    password = payload.password

    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Cuenta desactivada")

    key_obj = db.query(APIKey).filter(
        APIKey.user_id == user.id,
        APIKey.is_active.is_(True),
    ).order_by(APIKey.created_at.desc()).first()
    credits = user.credits

    return {
        "message": "Login correcto",
        "username": user.username,
        "email": user.email,
        "api_key_prefix": key_obj.key_prefix if key_obj else None,
        "credits_remaining": credits,
    }


@router.get(
    "/me",
    summary="Perfil actual",
    description="Legacy: usa /auth/me. Devuelve datos de la cuenta usando X-API-Key.",
    deprecated=True,
)
def me(api_key: str = Depends(get_api_key), db: Session = Depends(get_db)):
    hashed = hash_key(api_key)
    key_obj = db.query(APIKey).filter(APIKey.key == hashed, APIKey.is_active == True).first()
    if not key_obj:
        raise HTTPException(status_code=401, detail="API Key inválida")

    user = db.query(User).filter(User.id == key_obj.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {
        "username": user.username,
        "email": user.email,
        "api_key_prefix": key_obj.key_prefix,
        "credits_remaining": user.credits,
    }


# ==================== LOGOUT ====================

@router.post(
    "/logout",
    summary="Logout cliente",
    description="Respuesta informativa. El cliente debe borrar su API key local.",
    deprecated=True,
)
def logout():
    return {"message": "Logout correcto. El cliente debe eliminar la API key local."}


@router.get(
    "/apikey",
    summary="Rotar API key",
    description="Legacy: usa /auth/apikey/regenerate. Genera una nueva API key y desactiva la anterior.",
    deprecated=True,
)
def get_or_rotate_api_key(user: User = Depends(get_current_user_jwt), db: Session = Depends(get_db)):
    return issue_api_key_for_user(db=db, user=user, mode="regenerate")
