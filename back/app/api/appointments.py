from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import require_roles
from app.core.security import get_current_user
from app.database.connection import get_db
from app.models.patient import Patient
from app.models.user import User
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentStatusUpdate,
)
from app.services.appointment_service import (
    create_appointment,
    delete_appointment,
    get_appointment_or_404,
    get_appointments_for_user,
    update_appointment_status,
    user_can_access_appointment,
)

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


@router.post(
    "/",
    response_model=AppointmentResponse
)
def create_appointment_endpoint(
    data: AppointmentCreate,
    current_user: User = Depends(require_roles(3)),
    db: Session = Depends(get_db)
):
    patient = (
        db.query(Patient)
        .filter(Patient.user_id == current_user.id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Necesitas crear tu perfil de paciente antes de agendar una cita"
        )

    return create_appointment(
        db=db,
        patient=patient,
        doctor_id=data.doctor_id,
        scheduled_at=data.scheduled_at,
        reason=data.reason
    )


@router.get(
    "/",
    response_model=list[AppointmentResponse]
)
def list_appointments(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_appointments_for_user(db, current_user, skip=skip, limit=limit)


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse
)
def get_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    appointment = get_appointment_or_404(db, appointment_id)

    if not user_can_access_appointment(current_user, appointment, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver esta cita"
        )

    return appointment


@router.patch(
    "/{appointment_id}/status",
    response_model=AppointmentResponse
)
def update_appointment_status_endpoint(
    appointment_id: int,
    data: AppointmentStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    appointment = get_appointment_or_404(db, appointment_id)

    if not user_can_access_appointment(current_user, appointment, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para modificar esta cita"
        )

    # Un paciente solo puede cancelar su propia cita, no confirmarla/completarla
    if current_user.role_id == 3 and data.status != "cancelled":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Como paciente, solo puedes cancelar tu cita"
        )

    return update_appointment_status(db, appointment, data.status)


@router.delete(
    "/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_appointment_endpoint(
    appointment_id: int,
    current_user: User = Depends(require_roles(1)),
    db: Session = Depends(get_db)
):
    delete_appointment(db, appointment_id)
