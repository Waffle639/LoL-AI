"""Authentication endpoint tests."""

from app.auth import hash_password, decode_refresh_token
from app.core.database import APIKey, User


def test_login_hides_api_key_and_returns_refresh_token(client, db_session_factory):
    """Login should not expose API key and should include refresh token."""
    email = "login_user@example.com"
    password = "DemoPass123"

    with db_session_factory() as db:
        user = User(
            username="login_user",
            email=email,
            hashed_password=hash_password(password),
            plan="starter",
            is_active=True,
        )
        db.add(user)
        db.flush()

        db.add(
            APIKey(
                key="hashed_key_for_test",
                name=user.username,
                credits=7,
                is_active=True,
                user_id=user.id,
                key_prefix="lol_test_prefix",
            )
        )
        db.commit()

    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )

    assert response.status_code == 200
    data = response.json()

    assert "api_key" not in data
    assert data["token_type"] == "bearer"
    assert data["username"] == "login_user"
    assert data["email"] == email
    assert data["credits_remaining"] == 7
    assert data.get("access_token")
    assert data.get("refresh_token")

    payload = decode_refresh_token(data["refresh_token"])
    assert payload is not None
    assert payload.get("type") == "refresh"
