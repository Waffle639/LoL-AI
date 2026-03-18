"""Extended API behavior tests for auth, edge cases, and prediction consistency."""


def test_root_endpoint_has_basic_metadata(client):
    """GET / exposes version and endpoint map."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"]
    assert data["version"]
    assert "predict" in data["endpoints"]


def test_predict_with_invalid_api_key_returns_401(client, valid_predict_input):
    """Invalid API key should be rejected."""
    response = client.post(
        "/predict",
        json=valid_predict_input,
        headers={"X-API-Key": "lol_invalid_key"},
    )
    assert response.status_code == 401


def test_predict_with_inactive_key_returns_403(client, inactive_api_key, valid_predict_input):
    """Inactive API keys should not be allowed to predict."""
    response = client.post("/predict", json=valid_predict_input, headers=inactive_api_key["headers"])
    assert response.status_code == 403


def test_predict_with_zero_credits_returns_402(client, zero_credits_api_key, valid_predict_input):
    """Keys with no credits should return 402 with recharge hint."""
    response = client.post("/predict", json=valid_predict_input, headers=zero_credits_api_key["headers"])
    assert response.status_code == 402
    detail = response.json()["detail"]
    assert detail["error"] == "Sin créditos"
    assert "credits_remaining" in detail


def test_predict_accepts_case_insensitive_category_names(client, seeded_api_key, valid_predict_input):
    """Categorical fields should accept case-insensitive names."""
    payload = valid_predict_input.copy()
    payload["team_encoded"] = "g2 esports"
    payload["player_encoded"] = "caps"
    payload["champion_encoded"] = "azir"
    payload["side_encoded"] = "blue"
    payload["position_encoded"] = "mid"

    response = client.post("/predict", json=payload, headers=seeded_api_key["headers"])
    assert response.status_code == 200
    assert 0.0 <= response.json()["probability"] <= 1.0


def test_predict_accepts_numeric_encoded_categories(client, seeded_api_key, valid_predict_input):
    """Categorical fields should accept numeric values as strings."""
    payload = valid_predict_input.copy()
    payload["team_encoded"] = "0"
    payload["player_encoded"] = "0"
    payload["champion_encoded"] = "0"
    payload["side_encoded"] = "0"
    payload["position_encoded"] = "2"

    response = client.post("/predict", json=payload, headers=seeded_api_key["headers"])
    assert response.status_code == 200


def test_pregame_probabilities_sum_to_100(client, seeded_api_key, valid_pregame_input):
    """Pre-game output should normalize both team probabilities to ~100%."""
    response = client.post("/predict/pregame", json=valid_pregame_input, headers=seeded_api_key["headers"])
    assert response.status_code == 200

    data = response.json()
    total = data["team1"]["victory_prob"] + data["team2"]["victory_prob"]
    assert abs(total - 100.0) < 0.01


def test_pregame_invalid_side_returns_422(client, seeded_api_key, valid_pregame_input):
    """Schema validation should reject unsupported side values."""
    payload = valid_pregame_input.copy()
    payload["team1"] = dict(valid_pregame_input["team1"])
    payload["team1"]["side"] = "Green"

    response = client.post("/predict/pregame", json=payload, headers=seeded_api_key["headers"])
    assert response.status_code == 422
