"""Auth route tests."""


def test_login_success(client, attorney):
    res = client.post(
        "/api/auth/login",
        json={"email": "attorney@example.com", "password": "secret123"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password(client, attorney):
    res = client.post(
        "/api/auth/login",
        json={"email": "attorney@example.com", "password": "nope"},
    )
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_unknown_email_same_error(client):
    # No user enumeration: unknown email returns the same 401 code.
    res = client.post(
        "/api/auth/login",
        json={"email": "ghost@example.com", "password": "whatever"},
    )
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_me_requires_token(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_returns_current_user(client, auth_headers):
    res = client.get("/api/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "attorney@example.com"
