PATIENT_PAYLOAD = {
    "date_of_birth": "1990-05-20",
    "phone": "+56912345678",
    "address": "Calle Falsa 123",
}


def test_create_patient_profile_success(client, patient_headers):
    response = client.post("/patients/", json=PATIENT_PAYLOAD, headers=patient_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["phone"] == PATIENT_PAYLOAD["phone"]


def test_only_patient_role_can_create_profile(client, doctor_headers):
    response = client.post("/patients/", json=PATIENT_PAYLOAD, headers=doctor_headers)
    assert response.status_code == 403


def test_duplicate_patient_profile_returns_400(client, patient_headers):
    first = client.post("/patients/", json=PATIENT_PAYLOAD, headers=patient_headers)
    assert first.status_code == 200

    second = client.post("/patients/", json=PATIENT_PAYLOAD, headers=patient_headers)
    assert second.status_code == 400


def test_get_my_patient_profile(client, patient_headers):
    client.post("/patients/", json=PATIENT_PAYLOAD, headers=patient_headers)

    response = client.get("/patients/me", headers=patient_headers)
    assert response.status_code == 200
    assert response.json()["address"] == PATIENT_PAYLOAD["address"]


def test_get_my_patient_profile_without_creating_one_returns_404(client, patient_headers):
    response = client.get("/patients/me", headers=patient_headers)
    assert response.status_code == 404


def test_list_patients_requires_staff(client, patient_headers):
    response = client.get("/patients/", headers=patient_headers)
    assert response.status_code == 403


def test_doctor_can_list_patients(client, doctor_headers, patient_headers):
    client.post("/patients/", json=PATIENT_PAYLOAD, headers=patient_headers)

    response = client.get("/patients/", headers=doctor_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_patient_cannot_view_another_patients_profile(client, patient_headers, another_patient_headers):
    create_resp = client.post("/patients/", json=PATIENT_PAYLOAD, headers=patient_headers)
    patient_id = create_resp.json()["id"]

    response = client.get(f"/patients/{patient_id}", headers=another_patient_headers)
    assert response.status_code == 403


def test_doctor_can_view_any_patient(client, doctor_headers, patient_headers):
    create_resp = client.post("/patients/", json=PATIENT_PAYLOAD, headers=patient_headers)
    patient_id = create_resp.json()["id"]

    response = client.get(f"/patients/{patient_id}", headers=doctor_headers)
    assert response.status_code == 200


def test_patient_can_update_own_profile(client, patient_headers):
    create_resp = client.post("/patients/", json=PATIENT_PAYLOAD, headers=patient_headers)
    patient_id = create_resp.json()["id"]

    response = client.put(
        f"/patients/{patient_id}",
        json={"phone": "+56900000000"},
        headers=patient_headers,
    )

    assert response.status_code == 200
    assert response.json()["phone"] == "+56900000000"


def test_delete_patient_requires_admin(client, doctor_headers, patient_headers):
    create_resp = client.post("/patients/", json=PATIENT_PAYLOAD, headers=patient_headers)
    patient_id = create_resp.json()["id"]

    response = client.delete(f"/patients/{patient_id}", headers=doctor_headers)
    assert response.status_code == 403


def test_admin_can_delete_patient(client, admin_headers, patient_headers):
    create_resp = client.post("/patients/", json=PATIENT_PAYLOAD, headers=patient_headers)
    patient_id = create_resp.json()["id"]

    response = client.delete(f"/patients/{patient_id}", headers=admin_headers)
    assert response.status_code == 204
