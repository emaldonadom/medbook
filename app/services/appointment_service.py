from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.user import User
from sqlalchemy.orm import Session, joinedload

DOCTOR_ROLE_ID = 2

# Estados desde los cuales se puede transicionar. Simple pero evita,
# por ejemplo, "confirmar" una cita ya cancelada.
ALLOWED_STATUS_TRANSITIONS = {
    "pending": {"confirmed", "cancelled"},
    "confirmed": {"completed", "cancelled"},
    "completed": set(),
    "cancelled": set(),
}


def create_appointment(
    db: Session,
    patient: Patient,
    doctor_id: int,
    scheduled_at: datetime,
    reason: str
) -> Appointment:
    doctor = (
        db.query(User)
        .filter(User.id == doctor_id, User.role_id == DOCTOR_ROLE_ID)
        .first()
    )

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El doctor indicado no existe"
        )

    # Evitar doble reserva: mismo doctor, mismo horario, cita no cancelada
    conflict = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.scheduled_at == scheduled_at,
            Appointment.status != "cancelled"
        )
        .first()
    )

    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El doctor ya tiene una cita agendada en ese horario"
        )

    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor_id,
        scheduled_at=scheduled_at,
        reason=reason,
        status="pending"
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment


def get_appointment_or_404(db: Session, appointment_id: int) -> Appointment:
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )

    return appointment


def get_appointments_for_user(
    db: Session,
    current_user: User,
    skip: int = 0,
    limit: int = 100
):
    query = (
        db.query(Appointment)
        .options(
            joinedload(Appointment.patient)
            .joinedload(Patient.user)
        )
    )

    if current_user.role_id == 1:
        # admin: ve todas
        pass
    elif current_user.role_id == 2:
        # doctor: solo las suyas
        query = query.filter(Appointment.doctor_id == current_user.id)
    else:
        # paciente: solo las de su propio perfil
        patient = (
            db.query(Patient)
            .filter(Patient.user_id == current_user.id)
            .first()
        )

        if not patient:
            return []

        query = query.filter(Appointment.patient_id == patient.id)

    return (
        query
        .order_by(Appointment.scheduled_at)
        .offset(skip)
        .limit(limit)
        .all()
    )


def user_can_access_appointment(current_user: User, appointment: Appointment, db: Session) -> bool:
    if current_user.role_id == 1:
        return True

    if current_user.role_id == 2:
        return appointment.doctor_id == current_user.id

    patient = (
        db.query(Patient)
        .filter(Patient.user_id == current_user.id)
        .first()
    )

    return bool(patient) and appointment.patient_id == patient.id


def update_appointment_status(
    db: Session,
    appointment: Appointment,
    new_status: str
) -> Appointment:
    allowed_next = ALLOWED_STATUS_TRANSITIONS.get(appointment.status, set())

    if new_status not in allowed_next:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"No se puede pasar de '{appointment.status}' "
                f"a '{new_status}'"
            )
        )

    appointment.status = new_status
    db.commit()
    db.refresh(appointment)

    return appointment


def delete_appointment(db: Session, appointment_id: int):
    appointment = get_appointment_or_404(db, appointment_id)

    db.delete(appointment)
    db.commit()
