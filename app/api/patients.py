from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.schemas.patient import PatientCreate, PatientResponse
from app.services.patient_service import PatientService
from app.core.permissions import require_roles


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