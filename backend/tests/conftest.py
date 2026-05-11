"""Shared test fixtures for LoL API basic test suite."""

from __future__ import annotations

import secrets
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Ensure `app.*` imports work when running `pytest backend/tests/` from repo root.
ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import api as api_module
from app.auth import hash_key
from app.core.database import APIKey, Base, User, get_db


class DummyLabelEncoder:
    """Small encoder stub with sklearn-like API used by prediction routers."""

    def __init__(self, classes: list[str]):
        self.classes_ = np.array(classes)

    def transform(self, values: list[str]) -> np.ndarray:
        mapping = {c: i for i, c in enumerate(self.classes_)}
        return np.array([mapping[v] for v in values], dtype=int)


class DummyNeuralNet:
    """Minimal wrapper exposing encoders and predict_proba for /predict."""

    def __init__(self):
        self.encoders = {
            "team": DummyLabelEncoder(["G2 Esports", "MAD Lions KOI", "T1"]),
            "player": DummyLabelEncoder(["Caps", "BrokenBlade", "Yike", "Hans Sama", "Mikyx"]),
            "champion": DummyLabelEncoder(["Azir", "Vi", "Varus", "Zyra", "K'Sante"]),
            "side": DummyLabelEncoder(["Blue", "Red"]),
            "position": DummyLabelEncoder(["top", "jng", "mid", "bot", "sup"]),
        }

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        # Keep output deterministic and valid in [0,1].
        return np.array([0.73] * len(X), dtype=float)


class DummyRFModel:
    """Minimal classifier stub exposing predict_proba for /predict/pregame."""

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        # Blue side slightly favored to keep test assertions stable.
        p1 = np.where(X["side_encoded"].to_numpy() == 0, 0.62, 0.38)
        return np.column_stack((1 - p1, p1))


def _fake_pregame_artifacts() -> dict:
    encoders = {
        "team": DummyLabelEncoder(["G2 Esports", "MAD Lions KOI"]),
        "player": DummyLabelEncoder([
            "BrokenBlade", "Yike", "Caps", "Hans Sama", "Mikyx",
            "Myrwn", "Elyoya", "Fresskowy", "Supa", "Alvaro",
        ]),
        "champion": DummyLabelEncoder([
            "K'Sante", "Vi", "Azir", "Varus", "Zyra",
            "Gwen", "Viego", "Neeko", "Ashe", "Renata Glasc",
        ]),
        "side": DummyLabelEncoder(["Blue", "Red"]),
        "position": DummyLabelEncoder(["top", "jng", "mid", "bot", "sup"]),
    }

    team_stats = pd.DataFrame(
        {
            "teamname": ["G2 Esports", "MAD Lions KOI"],
            "team_winrate": [0.61, 0.54],
        }
    )
    player_stats = pd.DataFrame(
        {
            "playername": [
                "BrokenBlade", "Yike", "Caps", "Hans Sama", "Mikyx",
                "Myrwn", "Elyoya", "Fresskowy", "Supa", "Alvaro",
            ],
            "player_winrate": [0.58, 0.57, 0.62, 0.59, 0.6, 0.51, 0.56, 0.5, 0.52, 0.53],
            "player_kda": [3.1, 3.0, 4.2, 3.6, 3.4, 2.8, 3.3, 2.7, 3.0, 2.9],
        }
    )
    champion_stats = pd.DataFrame(
        {
            "champion": [
                "K'Sante", "Vi", "Azir", "Varus", "Zyra",
                "Gwen", "Viego", "Neeko", "Ashe", "Renata Glasc",
            ],
            "champion_winrate": [0.5, 0.51, 0.53, 0.49, 0.52, 0.5, 0.5, 0.48, 0.47, 0.51],
        }
    )
    player_champ_stats = pd.DataFrame(
        {
            "playername": [
                "BrokenBlade", "Yike", "Caps", "Hans Sama", "Mikyx",
                "Myrwn", "Elyoya", "Fresskowy", "Supa", "Alvaro",
            ],
            "champion": [
                "K'Sante", "Vi", "Azir", "Varus", "Zyra",
                "Gwen", "Viego", "Neeko", "Ashe", "Renata Glasc",
            ],
            "player_champ_winrate": [0.57, 0.56, 0.65, 0.6, 0.59, 0.5, 0.54, 0.49, 0.51, 0.52],
        }
    )

    return {
        "model": DummyRFModel(),
        "feature_names": [
            "team_encoded", "player_encoded", "champion_encoded", "side_encoded", "position_encoded",
            "team_winrate", "player_winrate", "player_kda", "champion_winrate", "player_champ_winrate",
        ],
        "encoders": encoders,
        "team_stats": team_stats,
        "player_stats": player_stats,
        "champion_stats": champion_stats,
        "player_champ_stats": player_champ_stats,
    }


@pytest.fixture(scope="session")
def db_session_factory(tmp_path_factory):
    """Create an isolated SQLite DB for tests and return a session factory."""
    db_dir = tmp_path_factory.mktemp("db")
    db_file = db_dir / "test_api.db"
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal


@pytest.fixture(scope="session")
def client(db_session_factory):
    """FastAPI TestClient with fake model loading and DB dependency override."""
    monkeypatch = pytest.MonkeyPatch()

    def override_get_db():
        db = db_session_factory()
        try:
            yield db
        finally:
            db.close()

    def fake_load_model():
        api_module._neural_net = DummyNeuralNet()
        api_module._pregame_artifacts = _fake_pregame_artifacts()
        api_module._model_version = "test-1.0.0"

    monkeypatch.setattr(api_module, "create_tables", lambda: None)
    monkeypatch.setattr(api_module, "load_model", fake_load_model)
    api_module.app.dependency_overrides[get_db] = override_get_db

    with TestClient(api_module.app) as c:
        yield c

    api_module.app.dependency_overrides.clear()
    monkeypatch.undo()


@pytest.fixture
def seeded_api_key(db_session_factory):
    """Insert a user with credits and return raw/hashed key metadata."""
    raw_key = f"lol_test_{secrets.token_hex(8)}"
    hashed = hash_key(raw_key)
    initial_credits = 5

    with db_session_factory() as db:
        user = User(
            username=f"tester_{secrets.token_hex(4)}",
            email=f"tester_{secrets.token_hex(4)}@example.com",
            hashed_password="not-used-in-tests",
            credits=initial_credits,
            is_active=True,
        )
        db.add(user)
        db.flush()

        key = APIKey(
            key=hashed,
            name=user.username,
            is_active=True,
            user_id=user.id,
            key_prefix=raw_key[:16],
        )
        db.add(key)
        db.commit()

    return {
        "raw": raw_key,
        "hashed": hashed,
        "initial_credits": initial_credits,
        "headers": {"X-API-Key": raw_key},
    }


@pytest.fixture
def zero_credits_api_key(db_session_factory):
    """Insert an active key with zero credits for 402 behavior tests."""
    raw_key = f"lol_zero_{secrets.token_hex(8)}"
    hashed = hash_key(raw_key)

    with db_session_factory() as db:
        user = User(
            username=f"zero_{secrets.token_hex(4)}",
            email=f"zero_{secrets.token_hex(4)}@example.com",
            hashed_password="not-used-in-tests",
            credits=0,
            is_active=True,
        )
        db.add(user)
        db.flush()

        key = APIKey(
            key=hashed,
            name=user.username,
            is_active=True,
            user_id=user.id,
            key_prefix=raw_key[:16],
        )
        db.add(key)
        db.commit()

    return {"raw": raw_key, "hashed": hashed, "headers": {"X-API-Key": raw_key}}


@pytest.fixture
def inactive_api_key(db_session_factory):
    """Insert an inactive key for 403 behavior tests."""
    raw_key = f"lol_inactive_{secrets.token_hex(8)}"
    hashed = hash_key(raw_key)

    with db_session_factory() as db:
        user = User(
            username=f"inactive_{secrets.token_hex(4)}",
            email=f"inactive_{secrets.token_hex(4)}@example.com",
            hashed_password="not-used-in-tests",
            credits=3,
            is_active=True,
        )
        db.add(user)
        db.flush()

        key = APIKey(
            key=hashed,
            name=user.username,
            is_active=False,
            user_id=user.id,
            key_prefix=raw_key[:16],
        )
        db.add(key)
        db.commit()

    return {"raw": raw_key, "hashed": hashed, "headers": {"X-API-Key": raw_key}}


@pytest.fixture
def valid_predict_input():
    """Valid payload for POST /predict using real API schema fields."""
    return {
        "team_encoded": "G2 Esports",
        "player_encoded": "Caps",
        "champion_encoded": "Azir",
        "side_encoded": "Blue",
        "position_encoded": "mid",
        "team_winrate": 0.65,
        "player_winrate": 0.62,
        "player_kda": 3.8,
        "champion_winrate": 0.54,
        "player_champ_winrate": 0.70,
        "kills": 5,
        "deaths": 2,
        "assists": 8,
        "teamkills": 24,
        "teamdeaths": 10,
        "dragons": 3,
        "opp_dragons": 1,
        "elders": 1,
        "opp_elders": 0,
        "barons": 2,
        "opp_barons": 0,
        "towers": 9,
        "opp_towers": 3,
        "totalgold": 14800,
    }


@pytest.fixture
def valid_pregame_input():
    """Valid payload for POST /predict/pregame with 5 players per team."""
    return {
        "team1": {
            "team_name": "G2 Esports",
            "side": "Blue",
            "players": [
                {"player": "BrokenBlade", "champion": "K'Sante", "position": "top"},
                {"player": "Yike", "champion": "Vi", "position": "jng"},
                {"player": "Caps", "champion": "Azir", "position": "mid"},
                {"player": "Hans Sama", "champion": "Varus", "position": "bot"},
                {"player": "Mikyx", "champion": "Zyra", "position": "sup"},
            ],
        },
        "team2": {
            "team_name": "MAD Lions KOI",
            "side": "Red",
            "players": [
                {"player": "Myrwn", "champion": "Gwen", "position": "top"},
                {"player": "Elyoya", "champion": "Viego", "position": "jng"},
                {"player": "Fresskowy", "champion": "Neeko", "position": "mid"},
                {"player": "Supa", "champion": "Ashe", "position": "bot"},
                {"player": "Alvaro", "champion": "Renata Glasc", "position": "sup"},
            ],
        },
    }
