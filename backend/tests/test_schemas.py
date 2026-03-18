"""Schema validation tests for core API request models."""

import pytest
from pydantic import ValidationError

from app.schemas import LoLNeuralNetInput, PreGameMatchInput


def test_lol_neural_input_valid(valid_predict_input):
    """LoLNeuralNetInput accepts a valid payload."""
    model = LoLNeuralNetInput(**valid_predict_input)
    assert model.kills == valid_predict_input["kills"]


def test_lol_neural_input_invalid_range(valid_predict_input):
    """LoLNeuralNetInput rejects out-of-range numeric values."""
    bad = valid_predict_input.copy()
    bad["kills"] = -1
    with pytest.raises(ValidationError):
        LoLNeuralNetInput(**bad)


def test_pregame_schema_requires_five_players(valid_pregame_input):
    """PreGameMatchInput enforces exactly 5 players per team."""
    bad = valid_pregame_input.copy()
    bad["team1"] = dict(valid_pregame_input["team1"])
    bad["team1"]["players"] = valid_pregame_input["team1"]["players"][:4]
    with pytest.raises(ValidationError):
        PreGameMatchInput(**bad)
