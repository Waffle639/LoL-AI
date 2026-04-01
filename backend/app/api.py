"""
API d'inferència per a predicció de partides de LoL

Endpoints:
    GET  /health                - Health check
    POST /predict               - Predicció (requereix API Key + crèdits)
    POST /billing/checkout      - Comprar crèdits via Stripe
    GET  /billing/credits       - Consultar crèdits restants
    POST /webhooks/stripe       - Webhook de Stripe (ús intern)
"""

from fastapi import FastAPI, Request, Depends, Response, HTTPException, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
import joblib
import logging
import stripe
import os

from dotenv import load_dotenv
load_dotenv()

from app.core.config import settings, setup_logging
from app.core.database import get_db, create_tables, APIKey, User, CreditTransaction, revoke_all_user_tokens
from app.ml.train import LoLNeuralNetWrapper
from app.auth import (
    verify_password,
    create_access_token,
    create_refresh_token,
    rotate_refresh_token,
    decode_refresh_token,
    hash_token,
    revoke_refresh_token,
    get_current_user,
    get_current_user_jwt,
    hash_key,
)
from app.routers import predict, billing
from app.routers import predict_pregame
from app import webhooks
from app.schemas import *

setup_logging()
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

_neural_net         = None
_pregame_artifacts  = None
_model_version      = None

def load_model():
    global _neural_net, _pregame_artifacts, _model_version

    _neural_net = LoLNeuralNetWrapper(str(settings.resolve_path(settings.NN_MODEL_PATH)))
    logger.info("Neural Network carregada")

    pregame_path = str(settings.resolve_path(settings.PREGAME_MODEL_PATH))
    try:
        _pregame_artifacts = joblib.load(pregame_path)
        logger.info("RandomForest Pre-Game carregat")
    except FileNotFoundError:
        _pregame_artifacts = None
        logger.warning(f"Model pre-game no trobat a {pregame_path}. Executa train.py per entrenar-lo.")

    _model_version = settings.APP_VERSION


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()           # Crea tablas SQLite si no existen
    logger.info("Base de datos SQLite inicializada")
    load_model()
    yield
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "API para predicciones de League of Legends con autenticacion dual (JWT + API Key).\n\n"
        "Flujo recomendado:\n"
        "1) POST /auth/register o /auth/login\n"
        "2) Authorize en Swagger con Bearer token\n"
        "3) Llamar /predict o /predict/pregame"
    ),
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True},
)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
def ratelimit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Too many login attempts"})

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://tu-dominio.com",
        "https://app.tu-dominio.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ROUTERS ====================
app.include_router(predict.router)
app.include_router(predict_pregame.router)
app.include_router(webhooks.router)
app.include_router(billing.router)


# ==================== ENDPOINTS BASE ====================

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Estado del servicio",
    description="Comprueba si la API esta activa y si los modelos estan cargados.",
)
def health_check():
    return {
        "status": "healthy",
        "neural_net_loaded": _neural_net is not None,
        "pregame_model_loaded": _pregame_artifacts is not None,
        "model_version": _model_version
    }


@app.get("/")
def root():
    return {
        "message": "LoL 2024 AI API",
        "version": settings.APP_VERSION,
        "endpoints": {
            "health":   "/health",
            "predict":  "/predict  (requiere X-API-Key)",
            "checkout": "/billing/checkout",
            "docs":     "/docs"
        }
    }


class AuthLoginRequest(BaseModel):
    email: EmailStr
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "email": "demo@lolai.com",
                "password": "DemoPass123"
            }]
        }
    }


class AuthRegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


def _cookie_secure() -> bool:
    return os.getenv("COOKIE_SECURE", "false").lower() in {"1", "true", "yes"}


def _set_refresh_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=_cookie_secure(),
        samesite="strict",
        max_age=60 * 60 * 24 * 7,
        path="/auth/refresh",
    )


def _clear_refresh_cookie(response: Response):
    response.delete_cookie(key="refresh_token", path="/auth/refresh")


@app.post(
    "/auth/register",
    summary="Registro principal",
    description="Crea cuenta, API key inicial y sesion JWT.",
    tags=["auth"],
)
def auth_register(payload: AuthRegisterRequest, response: Response, db: Session = Depends(get_db)):
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

    from app.auth import hash_password, hash_key
    import secrets

    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        plan="starter",
        is_active=True,
    )
    db.add(user)
    db.flush()

    raw_key = "lol_" + secrets.token_urlsafe(32)
    hashed = hash_key(raw_key)
    key_obj = APIKey(
        key=hashed,
        name=username,
        credits=0,
        is_active=True,
        user_id=user.id,
        key_prefix=raw_key[:16],
    )
    db.add(key_obj)
    db.add(CreditTransaction(api_key=hashed, amount=0, description=raw_key))
    db.commit()

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id, db)
    _set_refresh_cookie(response, refresh_token)

    return {
        "message": "Cuenta creada",
        "username": user.username,
        "email": user.email,
        "api_key": raw_key,
        "credits_remaining": key_obj.credits,
        "access_token": access_token,
        "token_type": "bearer",
    }


@app.post(
    "/auth/login",
    summary="Login JWT",
    description="Devuelve access token y guarda refresh token en cookie segura.",
    tags=["auth"],
)
@limiter.limit("5/minute")
def auth_login(request: Request, payload: AuthLoginRequest, response: Response, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Cuenta desactivada")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id, db)
    _set_refresh_cookie(response, refresh_token)

    key_obj = db.query(APIKey).filter(
        APIKey.user_id == user.id,
        APIKey.is_active.is_(True),
    ).order_by(APIKey.created_at.desc()).first()
    credits = key_obj.credits if key_obj else 0

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "username": user.username,
        "email": user.email,
        "credits_remaining": credits,
    }


@app.post(
    "/auth/refresh",
    summary="Renovar access token",
    description="Renueva el access token usando la cookie refresh_token.",
    tags=["auth"],
)
def auth_refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    payload = decode_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Refresh token inválido")

    new_refresh = rotate_refresh_token(refresh_token, db)
    if not new_refresh:
        raise HTTPException(status_code=401, detail="Refresh token inválido o revocado")

    user_id = int(payload["sub"])
    access_token = create_access_token(user_id)
    _set_refresh_cookie(response, new_refresh)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post(
    "/auth/logout",
    summary="Cerrar sesion",
    description="Revoca el refresh token actual o todos los tokens del usuario.",
    tags=["auth"],
)
def auth_logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    logout_all: bool = False,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if logout_all:
        revoke_all_user_tokens(db, user.id)
    elif refresh_token:
        revoke_refresh_token(db, hash_token(refresh_token))

    _clear_refresh_cookie(response)
    return {"detail": "Logout exitoso"}


@app.get(
    "/auth/me",
    summary="Perfil autenticado",
    description="Devuelve perfil y creditos con JWT o API key.",
    tags=["auth"],
)
def auth_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    key_obj = db.query(APIKey).filter(
        APIKey.user_id == user.id,
        APIKey.is_active.is_(True),
    ).order_by(APIKey.created_at.desc()).first()

    return {
        "username": user.username,
        "email": user.email,
        "plan": user.plan,
        "api_key_prefix": key_obj.key_prefix if key_obj else None,
        "credits_remaining": key_obj.credits if key_obj else 0,
    }


@app.get(
    "/auth/apikey",
    summary="Rotar API key",
    description="Genera una nueva API key para integraciones directas (requiere JWT).",
    tags=["auth"],
)
def auth_apikey(user: User = Depends(get_current_user_jwt), db: Session = Depends(get_db)):
    old_key = db.query(APIKey).filter(
        APIKey.user_id == user.id,
        APIKey.is_active.is_(True),
    ).order_by(APIKey.created_at.desc()).first()

    credits = old_key.credits if old_key else 0
    if old_key:
        old_key.is_active = False

    import secrets
    raw_key = "lol_" + secrets.token_urlsafe(32)
    hashed = hash_key(raw_key)

    new_key = APIKey(
        key=hashed,
        name=user.username,
        credits=credits,
        is_active=True,
        user_id=user.id,
        key_prefix=raw_key[:16],
    )
    db.add(new_key)
    db.add(CreditTransaction(api_key=hashed, amount=0, description=raw_key))
    db.commit()

    return {"api_key": raw_key}


@app.get("/success")
def payment_success():
    dashboard_url = os.getenv("FRONTEND_DASHBOARD_URL", "http://localhost:5174")
    return RedirectResponse(url=f"{dashboard_url}/billing?success=true", status_code=303)
    
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"error": "ValidationError", "detail": str(exc)}
    )