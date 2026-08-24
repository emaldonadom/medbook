from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.patient import Patient
from app.models.user import User
from app.schemas.patient import PatientCreate, PatientResponse, PatientUpdate
from app.services.patient_service import PatientService
from app.core.permissions import require_roles
from app.core.security import get_current_user


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.post(
    "/",
    response_model=PatientResponse
)
def create_patient(
    data: PatientCreate,
    current_user: User = Depends(require_roles(3)),
    db: Session = Depends(get_db)
):
    return PatientService.create_patient(
        db=db,
        user=current_user,
        date_of_birth=data.date_of_birth,
        phone=data.phone,
        address=data.address
    )


@router.get(
    "/",
    response_model=list[PatientResponse]
)
def list_patients(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_roles(1, 2)),
    db: Session = Depends(get_db)
):
    return PatientService.get_patients(db, skip=skip, limit=limit)


@router.get(
    "/me",
    response_model=PatientResponse
)
def get_my_patient_profile(
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todavía no creaste tu perfil de paciente"
        )

    return patient


def _get_owned_or_staff_patient(patient_id: int, current_user: User, db: Session):
    patient = PatientService.get_patient_or_404(db, patient_id)

    is_staff = current_user.role_id in (1, 2)
    is_owner = patient.user_id == current_user.id

    if not is_staff and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a este paciente"
        )

    return patient


@router.get(
    "/{patient_id}",
    response_model=PatientResponse
)
def get_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return _get_owned_or_staff_patient(patient_id, current_user, db)


@router.put(
    "/{patient_id}",
    response_model=PatientResponse
)
def update_patient(
    patient_id: int,
    data: PatientUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    _get_owned_or_staff_patient(patient_id, current_user, db)

    return PatientService.update_patient(
        db,
        patient_id,
        date_of_birth=data.date_of_birth,
        phone=data.phone,
        address=data.address
    )


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_patient(
    patient_id: int,
    current_user: User = Depends(require_roles(1)),
    db: Session = Depends(get_db)
):
    PatientService.delete_patient(db, patient_id)