"""
Endpoint de predicció — requereix API Key amb crèdits.
POST /predict → Prediu el resultat d'una partida de LoL
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db, APIKey, User
from app.auth import get_current_user_with_credits, consume_credit
from app.schemas import LoLNeuralNetInput, PredictionResponse
import pandas as pd

router = APIRouter(tags=["predict"])


def _resolve_categorical(value, encoder, field_name: str) -> int:
    """Resolve a string name or numeric code to an encoded integer."""
    if isinstance(value, int):
        return value
    # String that is a plain number → use as-is
    try:
        return int(value)
    except (ValueError, TypeError):
        pass
    classes = encoder.classes_
    # Exact match
    if value in classes:
        return int(encoder.transform([value])[0])
    # Case-insensitive match
    lower = value.lower()
    for c in classes:
        if str(c).lower() == lower:
            return int(encoder.transform([c])[0])
    from fastapi import HTTPException
    raise HTTPException(
        status_code=422,
        detail=f"'{value}' no és un valor vàlid per a '{field_name}'. "
               f"Usa el nom exacte del dataset o el codi numèric."
    )


def _resolve_label(value, encoder, field_name: str) -> str:
    """Resolve a string name or numeric code to a canonical label."""
    classes = encoder.classes_
    if isinstance(value, int):
        if 0 <= value < len(classes):
            return str(classes[value])
        raise HTTPException(status_code=422, detail=f"'{value}' fora de rang per a '{field_name}'.")
    try:
        code = int(value)
        if 0 <= code < len(classes):
            return str(classes[code])
    except (ValueError, TypeError):
        pass
    if value in classes:
        return str(value)
    lower = str(value).lower()
    for c in classes:
        if str(c).lower() == lower:
            return str(c)
    raise HTTPException(
        status_code=422,
        detail=f"'{value}' no és un valor vàlid per a '{field_name}'. "
               f"Usa el nom exacte del dataset o el codi numèric."
    )


ALL_FEATURES = [
    'team_encoded', 'player_encoded', 'champion_encoded', 'side_encoded', 'position_encoded',
    'team_winrate', 'player_winrate', 'player_kda', 'champion_winrate', 'player_champ_winrate',
    'kills', 'deaths', 'assists', 'teamkills', 'teamdeaths',
    'dragons', 'opp_dragons', 'elders', 'opp_elders',
    'barons', 'opp_barons', 'towers', 'opp_towers', 'totalgold'
]

@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Prediccion con estadisticas",
    description="Predice victoria o derrota con stats y variables codificadas.",
)
def predict(
    data: LoLNeuralNetInput,
    auth_ctx: tuple[User, APIKey | None] = Depends(get_current_user_with_credits),
    db: Session = Depends(get_db),
):
    user, key_obj = auth_ctx
    import app.api as api_module
    _neural_net    = api_module._neural_net
    _model_version = api_module._model_version

    if _neural_net is None:
        raise HTTPException(status_code=503, detail="Model no disponible")

    input_dict = data.model_dump()

    # Resolve string names → int codes using the model's LabelEncoders
    enc = _neural_net.encoders
    for field, key in [
        ('team_encoded', 'team'), ('player_encoded', 'player'),
        ('champion_encoded', 'champion'), ('side_encoded', 'side'),
        ('position_encoded', 'position'),
    ]:
        input_dict[field] = _resolve_categorical(input_dict[field], enc[key], field)

    X = pd.DataFrame([[input_dict[f] for f in ALL_FEATURES]], columns=ALL_FEATURES)

    try:
        prob = float(_neural_net.predict_proba(X)[0])
        pred = int(prob > 0.5)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al predecir: {str(e)}")

    consume_credit(user, db, description="Predicció LoL /predict", api_key_obj=key_obj)

    return PredictionResponse(
        result_label="Victory" if pred == 1 else "Defeat",
        prediction=pred,
        probability=round(prob, 4),
        model_version=_model_version or "1.0.0",
        credits_remaining=user.credits,
    )


@router.get(
    "/predict/options",
    summary="Opciones para /predict",
    description="Listas de equipos, jugadores, campeones, sides y posiciones del modelo activo.",
)
def predict_options():
    import app.api as api_module
    _neural_net = api_module._neural_net

    if _neural_net is None:
        raise HTTPException(status_code=503, detail="Model no disponible")

    enc = _neural_net.encoders
    return {
        "teams": [str(item) for item in enc["team"].classes_],
        "players": [str(item) for item in enc["player"].classes_],
        "champions": [str(item) for item in enc["champion"].classes_],
        "sides": [str(item) for item in enc["side"].classes_],
        "positions": [str(item) for item in enc["position"].classes_],
    }


@router.get(
    "/predict/stats",
    summary="Stats historicas para /predict",
    description="Devuelve winrates y KDA historicos del dataset para auto-rellenar el formulario.",
)
def predict_stats(team: str, player: str, champion: str):
    import app.api as api_module
    artifacts = api_module._pregame_artifacts

    if artifacts is None:
        raise HTTPException(status_code=503, detail="Model pre-game no disponible")

    encoders = artifacts['encoders']
    team_name = _resolve_label(team, encoders['team'], 'team')
    player_name = _resolve_label(player, encoders['player'], 'player')
    champion_name = _resolve_label(champion, encoders['champion'], 'champion')

    team_stats = artifacts['team_stats']
    player_stats = artifacts['player_stats']
    champion_stats = artifacts['champion_stats']
    pc_stats = artifacts['player_champ_stats']

    ts = team_stats.loc[team_stats['teamname'] == team_name, 'team_winrate']
    team_wr = float(ts.values[0]) if len(ts) > 0 else 0.5

    ps = player_stats.loc[player_stats['playername'] == player_name]
    player_wr = float(ps['player_winrate'].values[0]) if len(ps) > 0 else 0.5
    player_kda = float(ps['player_kda'].values[0]) if len(ps) > 0 else 3.0

    cs = champion_stats.loc[champion_stats['champion'] == champion_name, 'champion_winrate']
    champ_wr = float(cs.values[0]) if len(cs) > 0 else 0.5

    pcs = pc_stats.loc[
        (pc_stats['playername'] == player_name) & (pc_stats['champion'] == champion_name),
        'player_champ_winrate'
    ]
    pc_wr = float(pcs.values[0]) if len(pcs) > 0 else 0.5

    return {
        "team": team_name,
        "player": player_name,
        "champion": champion_name,
        "team_winrate": team_wr,
        "player_winrate": player_wr,
        "player_kda": player_kda,
        "champion_winrate": champ_wr,
        "player_champ_winrate": pc_wr,
    }