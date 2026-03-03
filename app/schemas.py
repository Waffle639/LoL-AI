"""
Pydantic Schemas - LoL Esports 2024 AI

Models per validació de requests/responses per la predicció de partides de LoL.
Dataset: 2024_LoL_esports_match_data_from_OraclesElixir1.csv
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional, List


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------

class LoLMatchInput(BaseModel):
    """
    Request schema per al model SGDClassifier (post-game / in-game stats).
    Conté les 14 features de stats de partida usades a IA_LoL.ipynb.
    """

    kills: int = Field(..., ge=0, le=30, description="Kills del jugador en la partida (0-30)")
    deaths: int = Field(..., ge=0, le=30, description="Morts del jugador en la partida (0-30)")
    assists: int = Field(..., ge=0, le=40, description="Assistències del jugador en la partida (0-40)")
    teamkills: int = Field(..., ge=0, le=80, description="Total de kills de l'equip (0-80)")
    teamdeaths: int = Field(..., ge=0, le=80, description="Total de morts de l'equip (0-80)")
    dragons: int = Field(..., ge=0, le=5, description="Dragons aconseguits per l'equip (0-5)")
    opp_dragons: int = Field(..., ge=0, le=5, description="Dragons aconseguits pel rival (0-5)")
    elders: int = Field(..., ge=0, le=3, description="Elder dragons aconseguits per l'equip (0-3)")
    opp_elders: int = Field(..., ge=0, le=3, description="Elder dragons aconseguits pel rival (0-3)")
    barons: int = Field(..., ge=0, le=5, description="Barons aconseguits per l'equip (0-5)")
    opp_barons: int = Field(..., ge=0, le=5, description="Barons aconseguits pel rival (0-5)")
    towers: int = Field(..., ge=0, le=11, description="Torres destruïdes per l'equip (0-11)")
    opp_towers: int = Field(..., ge=0, le=11, description="Torres destruïdes pel rival (0-11)")
    totalgold: float = Field(..., ge=0.0, description="Or total acumulat pel jugador")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "kills": 5, "deaths": 2, "assists": 8,
                "teamkills": 25, "teamdeaths": 10,
                "dragons": 3, "opp_dragons": 1,
                "elders": 1, "opp_elders": 0,
                "barons": 2, "opp_barons": 0,
                "towers": 9, "opp_towers": 3,
                "totalgold": 15000
            }]
        }
    }


class LoLNeuralNetInput(BaseModel):
    """
    Request schema per a la Xarxa Neuronal PyTorch (IA_LoL_NeuralNetwork.ipynb).
    Inclou les variables categòriques codificades, les stats històriques calculades
    i les 14 stats de partida.
    """

    # --- Variables categòriques (Label Encoded, enters) ---
    team_encoded: int = Field(..., ge=0, description="Equip codificat amb LabelEncoder")
    player_encoded: int = Field(..., ge=0, description="Jugador codificat amb LabelEncoder")
    champion_encoded: int = Field(..., ge=0, description="Campió codificat amb LabelEncoder")
    side_encoded: int = Field(..., ge=0, le=1, description="Costat: 0=Blue, 1=Red")
    position_encoded: int = Field(..., ge=0, le=4, description="Posició codificada: top/jng/mid/bot/sup (0-4)")

    # --- Stats històriques (calculades abans de la partida) ---
    team_winrate: float = Field(..., ge=0.0, le=1.0, description="Winrate de l'equip (0.0-1.0)")
    player_winrate: float = Field(..., ge=0.0, le=1.0, description="Winrate del jugador (0.0-1.0)")
    player_kda: float = Field(..., ge=0.0, description="KDA del jugador: (kills+assists)/(deaths+1)")
    champion_winrate: float = Field(..., ge=0.0, le=1.0, description="Winrate del campió (0.0-1.0)")
    player_champ_winrate: float = Field(..., ge=0.0, le=1.0, description="Winrate del jugador amb aquest campió (0.0-1.0)")

    # --- Stats de partida (les mateixes 14 de LoLMatchInput) ---
    kills: int = Field(..., ge=0, le=30, description="Kills del jugador (0-30)")
    deaths: int = Field(..., ge=0, le=30, description="Morts del jugador (0-30)")
    assists: int = Field(..., ge=0, le=40, description="Assistències del jugador (0-40)")
    teamkills: int = Field(..., ge=0, le=80, description="Total kills de l'equip (0-80)")
    teamdeaths: int = Field(..., ge=0, le=80, description="Total morts de l'equip (0-80)")
    dragons: int = Field(..., ge=0, le=5, description="Dragons de l'equip (0-5)")
    opp_dragons: int = Field(..., ge=0, le=5, description="Dragons del rival (0-5)")
    elders: int = Field(..., ge=0, le=3, description="Elders de l'equip (0-3)")
    opp_elders: int = Field(..., ge=0, le=3, description="Elders del rival (0-3)")
    barons: int = Field(..., ge=0, le=5, description="Barons de l'equip (0-5)")
    opp_barons: int = Field(..., ge=0, le=5, description="Barons del rival (0-5)")
    towers: int = Field(..., ge=0, le=11, description="Torres destruïdes per l'equip (0-11)")
    opp_towers: int = Field(..., ge=0, le=11, description="Torres destruïdes pel rival (0-11)")
    totalgold: float = Field(..., ge=0.0, description="Or total acumulat pel jugador")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "team_encoded": 42, "player_encoded": 130, "champion_encoded": 7,
                "side_encoded": 0, "position_encoded": 2,
                "team_winrate": 0.65, "player_winrate": 0.58, "player_kda": 3.2,
                "champion_winrate": 0.52, "player_champ_winrate": 0.71,
                "kills": 5, "deaths": 2, "assists": 8,
                "teamkills": 25, "teamdeaths": 10,
                "dragons": 3, "opp_dragons": 1,
                "elders": 1, "opp_elders": 0,
                "barons": 2, "opp_barons": 0,
                "towers": 9, "opp_towers": 3,
                "totalgold": 15000
            }]
        }
    }


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class PredictionResponse(BaseModel):
    """Response schema per a qualsevol endpoint de predicció de partida."""

    prediction: int = Field(..., description="Predicció binària: 0=derrota, 1=victòria")
    probability: float = Field(..., ge=0.0, le=1.0, description="Probabilitat de victòria (0.0-1.0)")
    model_version: str = Field(..., description="Versió del model utilitzat")
    result_label: str = Field(..., description="Etiqueta llegible: 'Victory' o 'Defeat'")


class HealthResponse(BaseModel):
    """Response schema per l'endpoint de health check."""

    status: str = Field(..., description="Estat del servei: 'healthy' o 'unhealthy'")
    model_loaded: bool = Field(..., description="Si el model SGD està carregat")
    neural_net_loaded: bool = Field(..., description="Si la xarxa neuronal PyTorch està carregada")
    pregame_model_loaded: bool = Field(False, description="Si el RandomForest pre-game està carregat")
    model_version: Optional[str] = Field(None, description="Versió del model carregat")


class ErrorResponse(BaseModel):
    """Response schema per errors."""

    error: str = Field(..., description="Tipus d'error")
    detail: str = Field(..., description="Detalls de l'error")


# ---------------------------------------------------------------------------
# Pre-Game prediction schemas
# ---------------------------------------------------------------------------

class PreGamePlayerInput(BaseModel):
    """Un jugador amb el seu campió i posició per a predicció pre-game."""

    player: str = Field(..., description="Nom del jugador (ex: 'Caps')")
    champion: str = Field(..., description="Nom del campió (ex: 'Azir')")
    position: Literal['top', 'jng', 'mid', 'bot', 'sup'] = Field(
        ..., description="Posició: top / jng / mid / bot / sup"
    )


class PreGameTeamInput(BaseModel):
    """Un equip de 5 jugadors per a predicció pre-game."""

    team_name: str = Field(..., description="Nom de l'equip (ex: 'G2 Esports')")
    side: Literal['Blue', 'Red'] = Field(..., description="Costat: Blue o Red")
    players: List[PreGamePlayerInput] = Field(
        ..., min_length=5, max_length=5,
        description="Exactament 5 jugadors"
    )


class PreGameMatchInput(BaseModel):
    """Request per a la predicció pre-game d'un enfrontament entre dos equips."""

    team1: PreGameTeamInput
    team2: PreGameTeamInput

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "team1": {
                    "team_name": "G2 Esports",
                    "side": "Blue",
                    "players": [
                        {"player": "BrokenBlade", "champion": "K'Sante",  "position": "top"},
                        {"player": "Yike",        "champion": "Vi",        "position": "jng"},
                        {"player": "Caps",        "champion": "Azir",      "position": "mid"},
                        {"player": "Hans Sama",   "champion": "Varus",     "position": "bot"},
                        {"player": "Mikyx",       "champion": "Zyra",      "position": "sup"}
                    ]
                },
                "team2": {
                    "team_name": "MAD Lions KOI",
                    "side": "Red",
                    "players": [
                        {"player": "Myrwn",      "champion": "Gwen",         "position": "top"},
                        {"player": "Elyoya",     "champion": "Viego",        "position": "jng"},
                        {"player": "Fresskowy",  "champion": "Neeko",        "position": "mid"},
                        {"player": "Supa",       "champion": "Ashe",         "position": "bot"},
                        {"player": "Alvaro",     "champion": "Renata Glasc", "position": "sup"}
                    ]
                }
            }]
        }
    }


class PreGamePlayerResult(BaseModel):
    """Resultat de la predicció pre-game per a un jugador individual."""

    player: str
    champion: str
    position: str
    victory_prob: float = Field(..., description="Probabilitat de victòria individual (0-1)")
    team_winrate: float
    player_winrate: float
    player_kda: float
    champion_winrate: float
    player_champ_winrate: float


class PreGameTeamResult(BaseModel):
    """Resultat de la predicció pre-game per a un equip complet."""

    team_name: str
    side: str
    victory_prob: float = Field(..., description="Probabilitat de victòria de l'equip normalitzada (0-100)")


class PreGameMatchResponse(BaseModel):
    """Response de la predicció pre-game d'un enfrontament complet."""

    team1: PreGameTeamResult
    team2: PreGameTeamResult
    predicted_winner: str = Field(..., description="Nom de l'equip que es prediu guanyador")
    confidence: float = Field(..., description="Probabilitat del guanyador (0-100)")
    model_version: str
