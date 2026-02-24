"""
API d'inferència per a predicció de malaltia cardíaca (Sessió 2)

Endpoints:
    GET  /health  - Health check
"""

from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager
import joblib
import pandas as pd
import logging

from app.config import settings, setup_logging
from app.train import LoLNeuralNetWrapper

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.schemas import *

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


# Models globals
_model      = None   # SGDClassifier  (sklearn)
_neural_net = None   # LoLNeuralNetWrapper (PyTorch)
_model_version = None


def load_model():
    """Carrega els dos models a l'inici de l'aplicació."""
    global _model, _neural_net, _model_version

    sgd_artifacts = joblib.load(str(settings.resolve_path(settings.MODEL_PATH)))
    _model        = sgd_artifacts['model']   # SGDClassifier listo → _model.predict(X)

    _neural_net   = LoLNeuralNetWrapper(str(settings.resolve_path(settings.NN_MODEL_PATH)))
    # listo → _neural_net.predict(X) / _neural_net.predict_proba(X)

    _model_version = settings.APP_VERSION
    logger.info("SGDClassifier i Neural Network carregats")


# Lifespan context manager (modern FastAPI pattern)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestió del cicle de vida de l'aplicació (startup/shutdown)."""
    # Startup: carregar model
    load_model()
    yield
    # Shutdown: netejar recursos (si cal)
    logger.info("Shutting down...")


# IMPORTANT: Passar lifespan a FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API per predir resultats de partides de LoL",
    lifespan=lifespan,
)


# ==================== ENDPOINTS ====================

@app.get("/health", response_model=HealthResponse)
def health_check():
    """
    Health check endpoint.

    Retorna l'estat del servei i informació sobre el model carregat.
    """
    return {
        "status": "healthy",
        "model_loaded": _model is not None,
        "neural_net_loaded": _neural_net is not None,
        "model_version": _model_version
    }


@app.get("/")
def root():
    """Endpoint arrel amb informació bàsica."""
    return {
        "message": "Heart Disease Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "docs": "/docs"
        }
    }


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    """
    Custom handler per errors de validació de Pydantic.

    Retorna missatges d'error més clars quan les dades d'entrada són invàlides.
    """
    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationError",
            "detail": str(exc)
        }
    )