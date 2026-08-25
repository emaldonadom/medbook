def test_list_users_requires_admin(client, patient_headers):
    response = client.get("/users/", headers=patient_headers)
    assert response.status_code == 403


def test_list_users_as_admin(client, admin_headers, patient_headers):
    response = client.get("/users/", headers=admin_headers)

    assert response.status_code == 200
    emails = [u["email"] for u in response.json()]
    assert "admin@medbook.example.com" in emails
    assert "patient@medbook.example.com" in emails


def test_list_doctors_visible_to_any_authenticated_user(client, doctor_headers, patient_headers):
    response = client.get("/users/doctors", headers=patient_headers)

    assert response.status_code == 200
    doctors = response.json()
    assert len(doctors) == 1
    assert doctors[0]["email"] == "doctor@medbook.example.com"


def test_get_own_user_as_self(client, patient_headers):
    me = client.get("/auth/me", headers=patient_headers).json()

    response = client.get(f"/users/{me['id']}", headers=patient_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "patient@medbook.example.com"


def test_get_other_user_forbidden_for_non_admin(client, patient_headers, doctor_headers):
    doctor_me = client.get("/auth/me", headers=doctor_headers).json()

    response = client.get(f"/users/{doctor_me['id']}", headers=patient_headers)
    assert response.status_code == 403


def test_admin_can_get_any_user(client, admin_headers, patient_headers):
    patient_me = client.get("/auth/me", headers=patient_headers).json()

    response = client.get(f"/users/{patient_me['id']}", headers=admin_headers)
    assert response.status_code == 200


def test_get_nonexistent_user_returns_404(client, admin_headers):
    response = client.get("/users/99999", headers=admin_headers)
    assert response.status_code == 404


def test_user_can_update_own_name(client, patient_headers):
    me = client.get("/auth/me", headers=patient_headers).json()

    response = client.put(
        f"/users/{me['id']}",
        json={"name": "Nuevo Nombre"},
        headers=patient_headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Nuevo Nombre"


def test_non_admin_cannot_change_own_role(client, patient_headers):
    me = client.get("/auth/me", headers=patient_headers).json()

    response = client.put(
        f"/users/{me['id']}",
        json={"role_id": 1},
        headers=patient_headers,
    )

    assert response.status_code == 403


def test_admin_can_change_role(client, admin_headers, patient_headers):
    patient_me = client.get("/auth/me", headers=patient_headers).json()

    response = client.put(
        f"/users/{patient_me['id']}",
        json={"role_id": 2},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["role_id"] == 2


def test_update_to_existing_email_returns_400(client, admin_headers, patient_headers, doctor_headers):
    patient_me = client.get("/auth/me", headers=patient_headers).json()

    response = client.put(
        f"/users/{patient_me['id']}",
        json={"email": "doctor@medbook.example.com"},
        headers=admin_headers,
    )

    assert response.status_code == 400


def test_delete_user_requires_admin(client, patient_headers, doctor_headers):
    doctor_me = client.get("/auth/me", headers=doctor_headers).json()

    response = client.delete(f"/users/{doctor_me['id']}", headers=patient_headers)
    assert response.status_code == 403


def test_admin_can_delete_user(client, admin_headers, patient_headers):
    patient_me = client.get("/auth/me", headers=patient_headers).json()

    response = client.delete(f"/users/{patient_me['id']}", headers=admin_headers)
    assert response.status_code == 204

    follow_up = client.get(f"/users/{patient_me['id']}", headers=admin_headers)
    assert follow_up.status_code == 404
