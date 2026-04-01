"""Basic API endpoint tests adapted to the LoL API."""

from app.core.database import APIKey


def test_health_endpoint(client):
    """GET /health returns healthy status and model flags."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["neural_net_loaded"] is True
    assert "pregame_model_loaded" in data
    assert data["model_version"]


def test_predict_requires_api_key(client, valid_predict_input):
    """POST /predict without credentials should be unauthorized."""
    response = client.post("/predict", json=valid_predict_input)
    assert response.status_code == 401


def test_predict_valid_input_consumes_credit(client, db_session_factory, seeded_api_key, valid_predict_input):
    """POST /predict with valid payload returns prediction and consumes one credit."""
    response = client.post("/predict", json=valid_predict_input, headers=seeded_api_key["headers"])
    assert response.status_code == 200

    data = response.json()
    assert data["prediction"] in [0, 1]
    assert 0.0 <= data["probability"] <= 1.0
    assert data["result_label"] in ["Victory", "Defeat"]
    assert data["model_version"]

    with db_session_factory() as db:
        key_obj = db.query(APIKey).filter(APIKey.key == seeded_api_key["hashed"]).first()
        assert key_obj is not None
        assert key_obj.credits == seeded_api_key["initial_credits"] - 1


def test_predict_invalid_range_returns_422(client, seeded_api_key, valid_predict_input):
    """POST /predict with invalid schema value returns 422."""
    bad_data = valid_predict_input.copy()
    bad_data["kills"] = 999
    response = client.post("/predict", json=bad_data, headers=seeded_api_key["headers"])
    assert response.status_code == 422


def test_predict_pregame_valid_input(client, db_session_factory, seeded_api_key, valid_pregame_input):
    """POST /predict/pregame returns winner, confidence and consumes one credit."""
    response = client.post("/predict/pregame", json=valid_pregame_input, headers=seeded_api_key["headers"])
    assert response.status_code == 200

    data = response.json()
    assert "team1" in data and "team2" in data
    assert data["predicted_winner"] in [data["team1"]["team_name"], data["team2"]["team_name"]]
    assert 0.0 <= data["confidence"] <= 100.0
    assert data["model_version"]

    with db_session_factory() as db:
        key_obj = db.query(APIKey).filter(APIKey.key == seeded_api_key["hashed"]).first()
        assert key_obj is not None
        assert key_obj.credits == seeded_api_key["initial_credits"] - 1


def test_predict_pregame_unknown_label_returns_422(client, seeded_api_key, valid_pregame_input):
    """POST /predict/pregame returns 422 when roster labels cannot be encoded."""
    bad_data = valid_pregame_input.copy()
    bad_data["team1"] = dict(valid_pregame_input["team1"])
    bad_data["team1"]["players"] = [dict(p) for p in valid_pregame_input["team1"]["players"]]
    for idx in range(len(bad_data["team1"]["players"])):
        bad_data["team1"]["players"][idx]["champion"] = f"UnknownChamp{idx}"

    response = client.post("/predict/pregame", json=bad_data, headers=seeded_api_key["headers"])
    assert response.status_code == 422
