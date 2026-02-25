"""
Endpoint de predicción — requiere API Key con créditos.

POST /predict → Predice el resultado de una partida de LoL
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, APIKey
from app.auth import verify_api_key, consume_credit

router = APIRouter(tags=["predict"])


@router.post("/predict")
def predict(
    # Aquí pon tu PredictRequest schema cuando lo tengas
    request: dict,
    key_obj: APIKey = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Predice el resultado de una partida profesional de LoL.
    
    Requiere header: X-API-Key: lol_xxxx
    Consume 1 crédito por llamada.
    """
    # ----- Tu lógica de predicción aquí -----
    # from app.main import _model, _neural_net
    # result = _model.predict(...)
    # -----------------------------------------

    # IMPORTANTE: consume el crédito DESPUÉS de la predicción exitosa
    consume_credit(key_obj, db, description="Predicción LoL")

    return {
        "prediction": "blue_team_wins",   # reemplaza con tu resultado real
        "confidence": 0.78,
        "credits_remaining": key_obj.credits,
    }
