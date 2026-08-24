PATIENT_PAYLOAD = {
    "date_of_birth": "1990-05-20",
    "phone": "+56912345678",
    "address": "Calle Falsa 123",
}

FUTURE_DATE = "2027-01-15T10:00:00"
PAST_DATE = "2020-01-15T10:00:00"


def _create_patient_profile(client, patient_headers):
    client.post("/patients/", json=PATIENT_PAYLOAD, headers=patient_headers)


def _get_doctor_id(client, headers):
    doctors = client.get("/users/doctors", headers=headers).json()
    return doctors[0]["id"]


def test_create_appointment_success(client, patient_headers, doctor_headers):
    _create_patient_profile(client, patient_headers)
    doctor_id = _get_doctor_id(client, patient_headers)

    response = client.post(
        "/appointments/",
        json={
            "doctor_id": doctor_id,
            "scheduled_at": FUTURE_DATE,
            "reason": "Chequeo general",
        },
        headers=patient_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "pending"
    assert body["doctor_id"] == doctor_id


def test_only_patient_role_can_create_appointment(client, doctor_headers):
    response = client.post(
        "/appointments/",
        json={
            "doctor_id": 1,
            "scheduled_at": FUTURE_DATE,
            "reason": "Chequeo general",
        },
        headers=doctor_headers,
    )
    assert response.status_code == 403


def test_create_appointment_without_patient_profile_fails(client, patient_headers, doctor_headers):
    doctor_id = _get_doctor_id(client, patient_headers)

    response = client.post(
        "/appointments/",
        json={
            "doctor_id": doctor_id,
            "scheduled_at": FUTURE_DATE,
            "reason": "Chequeo general",
        },
        headers=patient_headers,
    )

    assert response.status_code == 400
    assert "perfil de paciente" in response.json()["detail"].lower()


def test_create_appointment_with_invalid_doctor_id_returns_404(client, patient_headers):
    _create_patient_profile(client, patient_headers)

    response = client.post(
        "/appointments/",
        json={
            "doctor_id": 99999,
            "scheduled_at": FUTURE_DATE,
            "reason": "Chequeo general",
        },
        headers=patient_headers,
    )

    assert response.status_code == 404


def test_create_appointment_with_past_date_is_rejected(client, patient_headers, doctor_headers):
    _create_patient_profile(client, patient_headers)
    doctor_id = _get_doctor_id(client, patient_headers)

    response = client.post(
        "/appointments/",
        json={
            "doctor_id": doctor_id,
            "scheduled_at": PAST_DATE,
            "reason": "Chequeo general",
        },
        headers=patient_headers,
    )

    assert response.status_code == 422  # error de validación de Pydantic


def test_double_booking_same_doctor_same_time_returns_409(
    client, patient_headers, another_patient_headers, doctor_headers
):
    _create_patient_profile(client, patient_headers)
    _create_patient_profile(client, another_patient_headers)
    doctor_id = _get_doctor_id(client, patient_headers)

    payload = {
        "doctor_id": doctor_id,
        "scheduled_at": FUTURE_DATE,
        "reason": "Chequeo general",
    }

    first = client.post("/appointments/", json=payload, headers=patient_headers)
    assert first.status_code == 200

    second = client.post("/appointments/", json=payload, headers=another_patient_headers)
    assert second.status_code == 409


def test_patient_only_sees_own_appointments(
    client, patient_headers, another_patient_headers, doctor_headers
):
    _create_patient_profile(client, patient_headers)
    _create_patient_profile(client, another_patient_headers)
    doctor_id = _get_doctor_id(client, patient_headers)

    client.post(
        "/appointments/",
        json={"doctor_id": doctor_id, "scheduled_at": FUTURE_DATE, "reason": "Motivo A"},
        headers=patient_headers,
    )
    client.post(
        "/appointments/",
        json={"doctor_id": doctor_id, "scheduled_at": "2027-01-16T10:00:00", "reason": "Motivo B"},
        headers=another_patient_headers,
    )

    response = client.get("/appointments/", headers=patient_headers)
    assert response.status_code == 200
    appointments = response.json()
    assert len(appointments) == 1
    assert appointments[0]["reason"] == "Motivo A"


def test_doctor_sees_only_their_own_appointments(client, patient_headers, doctor_headers):
    _create_patient_profile(client, patient_headers)
    doctor_id = _get_doctor_id(client, patient_headers)

    client.post(
        "/appointments/",
        json={"doctor_id": doctor_id, "scheduled_at": FUTURE_DATE, "reason": "Motivo A"},
        headers=patient_headers,
    )

    response = client.get("/appointments/", headers=doctor_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_patient_can_cancel_own_appointment(client, patient_headers, doctor_headers):
    _create_patient_profile(client, patient_headers)
    doctor_id = _get_doctor_id(client, patient_headers)

    create_resp = client.post(
        "/appointments/",
        json={"doctor_id": doctor_id, "scheduled_at": FUTURE_DATE, "reason": "Motivo A"},
        headers=patient_headers,
    )
    appointment_id = create_resp.json()["id"]

    response = client.patch(
        f"/appointments/{appointment_id}/status",
        json={"status": "cancelled"},
        headers=patient_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_patient_cannot_confirm_appointment(client, patient_headers, doctor_headers):
    _create_patient_profile(client, patient_headers)
    doctor_id = _get_doctor_id(client, patient_headers)

    create_resp = client.post(
        "/appointments/",
        json={"doctor_id": doctor_id, "scheduled_at": FUTURE_DATE, "reason": "Motivo A"},
        headers=patient_headers,
    )
    appointment_id = create_resp.json()["id"]

    response = client.patch(
        f"/appointments/{appointment_id}/status",
        json={"status": "confirmed"},
        headers=patient_headers,
    )

    assert response.status_code == 403


def test_doctor_can_confirm_then_complete_appointment(client, patient_headers, doctor_headers):
    _create_patient_profile(client, patient_headers)
    doctor_id = _get_doctor_id(client, patient_headers)

    create_resp = client.post(
        "/appointments/",
        json={"doctor_id": doctor_id, "scheduled_at": FUTURE_DATE, "reason": "Motivo A"},
        headers=patient_headers,
    )
    appointment_id = create_resp.json()["id"]

    confirm_resp = client.patch(
        f"/appointments/{appointment_id}/status",
        json={"status": "confirmed"},
        headers=doctor_headers,
    )
    assert confirm_resp.status_code == 200
    assert confirm_resp.json()["status"] == "confirmed"

    complete_resp = client.patch(
        f"/appointments/{appointment_id}/status",
        json={"status": "completed"},
        headers=doctor_headers,
    )
    assert complete_resp.status_code == 200
    assert complete_resp.json()["status"] == "completed"


def test_cannot_confirm_a_cancelled_appointment(client, patient_headers, doctor_headers):
    _create_patient_profile(client, patient_headers)
    doctor_id = _get_doctor_id(client, patient_headers)

    create_resp = client.post(
        "/appointments/",
        json={"doctor_id": doctor_id, "scheduled_at": FUTURE_DATE, "reason": "Motivo A"},
        headers=patient_headers,
    )
    appointment_id = create_resp.json()["id"]

    client.patch(
        f"/appointments/{appointment_id}/status",
        json={"status": "cancelled"},
        headers=patient_headers,
    )

    response = client.patch(
        f"/appointments/{appointment_id}/status",
        json={"status": "confirmed"},
        headers=doctor_headers,
    )

    assert response.status_code == 400


def test_other_patient_cannot_view_or_cancel_appointment(
    client, patient_headers, another_patient_headers, doctor_headers
):
    _create_patient_profile(client, patient_headers)
    _create_patient_profile(client, another_patient_headers)
    doctor_id = _get_doctor_id(client, patient_headers)

    create_resp = client.post(
        "/appointments/",
        json={"doctor_id": doctor_id, "scheduled_at": FUTURE_DATE, "reason": "Motivo A"},
        headers=patient_headers,
    )
    appointment_id = create_resp.json()["id"]

    get_response = client.get(f"/appointments/{appointment_id}", headers=another_patient_headers)
    assert get_response.status_code == 403

    patch_response = client.patch(
        f"/appointments/{appointment_id}/status",
        json={"status": "cancelled"},
        headers=another_patient_headers,
    )
    assert patch_response.status_code == 403


def test_delete_appointment_requires_admin(client, patient_headers, doctor_headers):
    _create_patient_profile(client, patient_headers)
    doctor_id = _get_doctor_id(client, patient_headers)

    create_resp = client.post(
        "/appointments/",
        json={"doctor_id": doctor_id, "scheduled_at": FUTURE_DATE, "reason": "Motivo A"},
        headers=patient_headers,
    )
    appointment_id = create_resp.json()["id"]

    response = client.delete(f"/appointments/{appointment_id}", headers=doctor_headers)
    assert response.status_code == 403


def test_admin_can_delete_appointment(client, admin_headers, patient_headers, doctor_headers):
    _create_patient_profile(client, patient_headers)
    doctor_id = _get_doctor_id(client, patient_headers)

    create_resp = client.post(
        "/appointments/",
        json={"doctor_id": doctor_id, "scheduled_at": FUTURE_DATE, "reason": "Motivo A"},
        headers=patient_headers,
    )
    appointment_id = create_resp.json()["id"]

    response = client.delete(f"/appointments/{appointment_id}", headers=admin_headers)
    assert response.status_code == 204
