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
from app.auth import get_current_api_key_with_credits, consume_credit
from app.schemas import PreGameMatchInput, PreGameMatchResponse, PreGameTeamResult

router = APIRouter(tags=["predict"])


def _resolve_label(value, encoder):
    """
    Resolve a player/champion/team value to (canonical_name, encoded_int).
    Accepts:
      - int code          → reverse-lookup the canonical name
      - str of digits     → treated as int code
      - str name (exact)  → used directly
      - str name (wrong case) → case-insensitive match
    Raises ValueError if nothing matches.
    """
    classes = encoder.classes_
    if isinstance(value, int):
        return classes[value], value
    try:
        code = int(value)
        return classes[code], code
    except (ValueError, TypeError, IndexError):
        pass
    if value in classes:
        return value, int(encoder.transform([value])[0])
    lower = str(value).lower()
    for c in classes:
        if str(c).lower() == lower:
            return c, int(encoder.transform([c])[0])
    raise ValueError(f"'{value}' not found")


def _lookup_player_data(player_name, champion, position: str, side: str,
                        team_name, artifacts: dict) -> dict | None:
    """
    Cerca les stats históriques d'un jugador/campió/equip als lookup tables
    i codifica les variables categòriques.
    Accepta noms (str) o codis numèrics (int) per a player_name, champion i team_name.
    Retorna un dict amb les 10 features pre-game o None si no es pot codificar.
    """
    encoders      = artifacts['encoders']
    team_stats    = artifacts['team_stats']
    player_stats  = artifacts['player_stats']
    champ_stats   = artifacts['champion_stats']
    pc_stats      = artifacts['player_champ_stats']

    # --- Resolve names/codes → canonical name + encoded int ---
    try:
        team_name_,   team_enc   = _resolve_label(team_name,   encoders['team'])
        player_name_, player_enc = _resolve_label(player_name, encoders['player'])
        champion_,    champ_enc  = _resolve_label(champion,    encoders['champion'])
        side_enc    = int(encoders['side'].transform([side])[0])
        pos_enc     = int(encoders['position'].transform([position])[0])
    except (ValueError, IndexError):
        return None

    # --- Lookup historical stats (defaults si no existeix) ---
    ts = team_stats.loc[team_stats['teamname'] == team_name_, 'team_winrate']
    team_wr = float(ts.values[0]) if len(ts) > 0 else 0.5

    ps = player_stats.loc[player_stats['playername'] == player_name_]
    player_wr  = float(ps['player_winrate'].values[0]) if len(ps) > 0 else 0.5
    player_kda = float(ps['player_kda'].values[0])     if len(ps) > 0 else 3.0

    cs = champ_stats.loc[champ_stats['champion'] == champion_, 'champion_winrate']
    champ_wr = float(cs.values[0]) if len(cs) > 0 else 0.5

    pcs = pc_stats.loc[
        (pc_stats['playername'] == player_name_) & (pc_stats['champion'] == champion_),
        'player_champ_winrate'
    ]
    pc_wr = float(pcs.values[0]) if len(pcs) > 0 else 0.5

    return {
        'canonical': {
            'team':    team_name_,
            'player':  player_name_,
            'champion': champion_,
        },
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


@router.post(
    "/predict/pregame",
    response_model=PreGameMatchResponse,
    summary="Prediccion pregame",
    description="Calcula probabilidad de victoria antes de jugar, usando drafts y roster.",
)
def predict_pregame(
    data: PreGameMatchInput,
    key_obj: APIKey = Depends(get_current_api_key_with_credits),
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
        player_results  = []
        feature_rows    = []
        canonical_team  = str(team_input.team_name)  # fallback; overridden on first success

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

            canonical_team = data_p['canonical']['team']
            feature_rows.append(data_p['features'])
            player_results.append({
                'player':   data_p['canonical']['player'],
                'champion': data_p['canonical']['champion'],
                'position': p.position,
                **data_p['stats'],
                'victory_prob': 0.0,   # filled after batch predict
            })

        if not feature_rows:
            raise HTTPException(
                status_code=422,
                detail=f"No es poden codificar els jugadors/campions de '{team_input.team_name}'. "
                       "Comprova que els noms coincideixen amb el dataset d'entrenament."
            )

        X = pd.DataFrame(feature_rows)[feature_names]
        probs = rf_model.predict_proba(X)[:, 1].tolist()

        for i, row in enumerate(player_results):
            row['victory_prob'] = probs[i]

        avg_prob = float(np.mean(probs))
        return player_results, avg_prob, canonical_team

    team1_players, team1_raw, t1_name = predict_team(data.team1)
    team2_players, team2_raw, t2_name = predict_team(data.team2)

    # Normalize to 100%
    total = team1_raw + team2_raw
    t1_pct = (team1_raw / total) * 100
    t2_pct = (team2_raw / total) * 100

    predicted_winner = t1_name if t1_pct >= t2_pct else t2_name
    confidence       = max(t1_pct, t2_pct)

    consume_credit(key_obj, db, description="Predicció LoL /predict/pregame")

    return PreGameMatchResponse(
        team1=PreGameTeamResult(
            team_name=t1_name,
            side=data.team1.side,
            victory_prob=round(t1_pct, 2),
        ),
        team2=PreGameTeamResult(
            team_name=t2_name,
            side=data.team2.side,
            victory_prob=round(t2_pct, 2),
        ),
        predicted_winner=predicted_winner,
        confidence=round(confidence, 2),
        model_version=model_version or "1.0.0",
    )
