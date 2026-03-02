"""
Endpoint de predicció — requereix API Key amb crèdits.
POST /predict → Prediu el resultat d'una partida de LoL
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db, APIKey
from app.auth import verify_api_key, consume_credit
from app.schemas import LoLNeuralNetInput, PredictionResponse
import pandas as pd

router = APIRouter(tags=["predict"])

ALL_FEATURES = [
    'team_encoded', 'player_encoded', 'champion_encoded', 'side_encoded', 'position_encoded',
    'team_winrate', 'player_winrate', 'player_kda', 'champion_winrate', 'player_champ_winrate',
    'kills', 'deaths', 'assists', 'teamkills', 'teamdeaths',
    'dragons', 'opp_dragons', 'elders', 'opp_elders',
    'barons', 'opp_barons', 'towers', 'opp_towers', 'totalgold'
]

@router.post("/predict", response_model=PredictionResponse)
def predict(
    data: LoLNeuralNetInput,
    key_obj: APIKey = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    import app.api as api_module
    _neural_net    = api_module._neural_net
    _model_version = api_module._model_version

    if _neural_net is None:
        raise HTTPException(status_code=503, detail="Model no disponible")

    input_dict = data.model_dump()
    X = pd.DataFrame([[input_dict[f] for f in ALL_FEATURES]], columns=ALL_FEATURES)

    try:
        prob = float(_neural_net.predict_proba(X)[0])
        pred = int(prob > 0.5)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al predecir: {str(e)}")

    consume_credit(key_obj, db, description="Predicció LoL /predict")

    return PredictionResponse(
        result_label="Victory" if pred == 1 else "Defeat",
        prediction=pred,
        probability=round(prob, 4),
        model_version=_model_version or "1.0.0",
        credits_remaining=key_obj.credits
    )