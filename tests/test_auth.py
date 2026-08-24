def test_register_user_success(client):
    response = client.post(
        "/users/",
        json={
            "name": "Juan Perez",
            "email": "juan@example.com",
            "password": "supersecret",
            "role_id": 3,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "juan@example.com"
    assert "password" not in body  # nunca debe devolver el hash


def test_register_duplicate_email_returns_400(client):
    payload = {
        "name": "Juan Perez",
        "email": "juan@example.com",
        "password": "supersecret",
        "role_id": 3,
    }

    first = client.post("/users/", json=payload)
    assert first.status_code == 200

    second = client.post("/users/", json=payload)
    assert second.status_code == 400
    assert "email" in second.json()["detail"].lower()


def test_login_success(client):
    client.post(
        "/users/",
        json={
            "name": "Juan Perez",
            "email": "juan@example.com",
            "password": "supersecret",
            "role_id": 3,
        },
    )

    response = client.post(
        "/auth/login",
        data={"username": "juan@example.com", "password": "supersecret"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password_returns_401(client):
    client.post(
        "/users/",
        json={
            "name": "Juan Perez",
            "email": "juan@example.com",
            "password": "supersecret",
            "role_id": 3,
        },
    )

    response = client.post(
        "/auth/login",
        data={"username": "juan@example.com", "password": "incorrecta"},
    )

    assert response.status_code == 401


def test_login_unknown_email_returns_401(client):
    response = client.post(
        "/auth/login",
        data={"username": "no-existe@example.com", "password": "cualquiera"},
    )

    assert response.status_code == 401


def test_me_without_token_returns_401(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_returns_nested_role(client, patient_headers):
    response = client.get("/auth/me", headers=patient_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["role"] == {"id": 3, "name": "patient"}
