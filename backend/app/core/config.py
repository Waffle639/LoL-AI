"""
Configuration Management (Sessió 4)

Configuració centralitzada amb variables d'entorn i pydantic-settings.
"""

from pydantic_settings import BaseSettings
from pathlib import Path
import logging

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Configuració de l'aplicació carregada des de .env."""

    # Paths
    CSV_PATH: str 
    MODEL_DIR: str 
    METADATA_DIR: str 
    DEPLOYMENT_CRITERIA: str 

    # Model - MUST be set in .env (no hardcoded default)
    NN_MODEL_PATH: str
    NN_METADATA_PATH: str

    PREGAME_MODEL_PATH: str
    PREGAME_METADATA_PATH: str

    # API
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Logging 
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/api.log"

    # App metadata
    APP_NAME: str = "Heart Disease Prediction API"
    APP_VERSION: str = "1.0.0"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }

    def resolve_path(self, path: str) -> Path:
        """Resol un path relatiu al directori arrel del projecte."""
        return PROJECT_ROOT / path


# 🔮 SESSIONS FUTURES:
# S'afegiran més camps: METADATA_PATH, PREDICTIONS_LOG_PATH, etc.


_settings = None


def get_settings() -> Settings:
    """Get settings singleton (enables test overrides)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Module-level instance per imports fàcils: from app.config import settings
settings = get_settings()


def setup_logging(log_file: str = None, log_level: str = None) -> None:
    """Configura logging a fitxer i consola. Cridar una vegada a l'inici."""
    if log_file is None:
        log_file = str(settings.resolve_path(settings.LOG_FILE))
    if log_level is None:
        log_level = settings.LOG_LEVEL

    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode="w"),
            logging.StreamHandler(),
        ],
    )