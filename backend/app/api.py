"""
API d'inferència per a predicció de partides de LoL

Endpoints:
    GET  /health                - Health check
    POST /predict               - Predicció (requereix API Key + crèdits)
    POST /billing/checkout      - Comprar crèdits via Stripe
    GET  /billing/credits       - Consultar crèdits restants
    POST /webhooks/stripe       - Webhook de Stripe (ús intern)
"""

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import joblib
import logging
import stripe
import os

from dotenv import load_dotenv
load_dotenv()

from app.core.config import settings, setup_logging
from app.core.database import get_db, create_tables
from app.ml.train import LoLNeuralNetWrapper
from app.auth import verify_api_key
from app.routers import predict, billing
from app.routers import account
from app.routers import predict_pregame
from app import webhooks
from app.schemas import *

setup_logging()
logger = logging.getLogger(__name__)

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
    description="API per predir resultats de partides professionals de LoL. Requereix API Key.",
    lifespan=lifespan,
)

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
app.include_router(account.router)


# ==================== ENDPOINTS BASE ====================

@app.get("/health", response_model=HealthResponse)
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


@app.get("/success")
def payment_success():
    dashboard_url = os.getenv("FRONTEND_DASHBOARD_URL", "http://localhost:5174")
    return RedirectResponse(url=f"{dashboard_url}/billing?success=true", status_code=303)
    
@app.get("/billing/credits")
def get_credits(api_key: str = Depends(verify_api_key), db: Session = Depends(get_db)):

    return {
        "name": api_key.name,
        "credits_remaining": api_key.credits,
    }


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"error": "ValidationError", "detail": str(exc)}
    )