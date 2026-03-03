"""
Endpoint de predicció pre-game — requereix API Key amb crèdits.
POST /predict/pregame → Prediu el resultat d'una partida de LoL
a partir dels rosters dels dos equips (abans que comenci la partida).
"""

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db, APIKey
from app.auth import verify_api_key, consume_credit
from app.schemas import PreGameMatchInput, PreGameMatchResponse, PreGameTeamResult

router = APIRouter(tags=["predict"])


def _lookup_player_data(player_name: str, champion: str, position: str, side: str,
                        team_name: str, artifacts: dict) -> dict | None:
    """
    Cerca les stats históriques d'un jugador/campió/equip als lookup tables
    i codifica les variables categòriques.
    Retorna un dict amb les 10 features pre-game o None si no es pot codificar.
    """
    encoders      = artifacts['encoders']
    team_stats    = artifacts['team_stats']
    player_stats  = artifacts['player_stats']
    champ_stats   = artifacts['champion_stats']
    pc_stats      = artifacts['player_champ_stats']

    # --- Lookup historical stats (defaults si no existeix) ---
    ts = team_stats.loc[team_stats['teamname'] == team_name, 'team_winrate']
    team_wr = float(ts.values[0]) if len(ts) > 0 else 0.5

    ps = player_stats.loc[player_stats['playername'] == player_name]
    player_wr  = float(ps['player_winrate'].values[0]) if len(ps) > 0 else 0.5
    player_kda = float(ps['player_kda'].values[0])     if len(ps) > 0 else 3.0

    cs = champ_stats.loc[champ_stats['champion'] == champion, 'champion_winrate']
    champ_wr = float(cs.values[0]) if len(cs) > 0 else 0.5

    pcs = pc_stats.loc[
        (pc_stats['playername'] == player_name) & (pc_stats['champion'] == champion),
        'player_champ_winrate'
    ]
    pc_wr = float(pcs.values[0]) if len(pcs) > 0 else 0.5

    # --- Encode categoricals (skip row if unknown label) ---
    try:
        team_enc    = int(encoders['team'].transform([team_name])[0])
        player_enc  = int(encoders['player'].transform([player_name])[0])
        champ_enc   = int(encoders['champion'].transform([champion])[0])
        side_enc    = int(encoders['side'].transform([side])[0])
        pos_enc     = int(encoders['position'].transform([position])[0])
    except ValueError:
        return None

    return {
        'features': {
            'team_encoded':        team_enc,
            'player_encoded':      player_enc,
            'champion_encoded':    champ_enc,
            'side_encoded':        side_enc,
            'position_encoded':    pos_enc,
            'team_winrate':        team_wr,
            'player_winrate':      player_wr,
            'player_kda':          player_kda,
            'champion_winrate':    champ_wr,
            'player_champ_winrate': pc_wr,
        },
        'stats': {
            'team_winrate':        team_wr,
            'player_winrate':      player_wr,
            'player_kda':          player_kda,
            'champion_winrate':    champ_wr,
            'player_champ_winrate': pc_wr,
        }
    }


@router.post("/predict/pregame", response_model=PreGameMatchResponse)
def predict_pregame(
    data: PreGameMatchInput,
    key_obj: APIKey = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    import app.api as api_module
    artifacts      = api_module._pregame_artifacts
    model_version  = api_module._model_version

    if artifacts is None:
        raise HTTPException(status_code=503, detail="Model pre-game no disponible")

    rf_model       = artifacts['model']
    feature_names  = artifacts['feature_names']

    def predict_team(team_input):
        player_results = []
        feature_rows   = []

        for p in team_input.players:
            data_p = _lookup_player_data(
                player_name=p.player,
                champion=p.champion,
                position=p.position,
                side=team_input.side,
                team_name=team_input.team_name,
                artifacts=artifacts,
            )
            if data_p is None:
                # Unknown label → skip silently (will get default prob)
                continue

            feature_rows.append(data_p['features'])
            player_results.append({
                'player':   p.player,
                'champion': p.champion,
                'position': p.position,
                **data_p['stats'],
                'victory_prob': 0.0,   # filled after batch predict
            })

        if not feature_rows:
            raise HTTPException(
                status_code=422,
                detail=f"No es poden codificar els jugadors/campions de {team_input.team_name}. "
                       "Comprova que els noms coincideixen amb el dataset d'entrenament."
            )

        X = pd.DataFrame(feature_rows)[feature_names]
        probs = rf_model.predict_proba(X)[:, 1].tolist()

        for i, row in enumerate(player_results):
            row['victory_prob'] = probs[i]

        avg_prob = float(np.mean(probs))
        return player_results, avg_prob

    team1_players, team1_raw = predict_team(data.team1)
    team2_players, team2_raw = predict_team(data.team2)

    # Normalize to 100%
    total = team1_raw + team2_raw
    t1_pct = (team1_raw / total) * 100
    t2_pct = (team2_raw / total) * 100

    predicted_winner = data.team1.team_name if t1_pct >= t2_pct else data.team2.team_name
    confidence       = max(t1_pct, t2_pct)

    consume_credit(key_obj, db, description="Predicció LoL /predict/pregame")

    return PreGameMatchResponse(
        team1=PreGameTeamResult(
            team_name=data.team1.team_name,
            side=data.team1.side,
            victory_prob=round(t1_pct, 2),
        ),
        team2=PreGameTeamResult(
            team_name=data.team2.team_name,
            side=data.team2.side,
            victory_prob=round(t2_pct, 2),
        ),
        predicted_winner=predicted_winner,
        confidence=round(confidence, 2),
        model_version=model_version or "1.0.0",
    )
