"""
API d'inferència per a predicció de partides de LoL

Endpoints:
    GET  /health                - Health check
    POST /predict               - Predicció (requereix API Key + crèdits)
    POST /billing/checkout      - Comprar crèdits via Stripe
    GET  /billing/credits       - Consultar crèdits restants
    POST /webhooks/stripe       - Webhook de Stripe (ús intern)
"""

from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager
import joblib
import logging
import stripe
import os

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import verify_api_key

from app.config import settings, setup_logging
from app.routers import predict
from app.train import LoLNeuralNetWrapper
from app.database import create_tables

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.schemas import *
from app import webhooks

setup_logging()
logger = logging.getLogger(__name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

_model         = None
_neural_net    = None
_model_version = None

def load_model():
    global _model, _neural_net, _model_version

    sgd_artifacts = joblib.load(str(settings.resolve_path(settings.MODEL_PATH)))
    _model        = sgd_artifacts['model']

    _neural_net   = LoLNeuralNetWrapper(str(settings.resolve_path(settings.NN_MODEL_PATH)))

    _model_version = settings.APP_VERSION
    logger.info("SGDClassifier i Neural Network carregats")


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

# ==================== ROUTERS ====================
app.include_router(predict.router)
app.include_router(webhooks.router)


# ==================== ENDPOINTS BASE ====================

@app.get("/health", response_model=HealthResponse)
def health_check():
    return {
        "status": "healthy",
        "model_loaded": _model is not None,
        "neural_net_loaded": _neural_net is not None,
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