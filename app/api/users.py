from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import create_user

from app.core.permissions import require_roles
from app.models.user import User


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "/",
    response_model=UserResponse
)
def create_user_endpoint(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    return create_user(db, user_data)

@router.get("/admin-only")
def admin_only(
    current_user: User = Depends(require_roles(1))
):
    return {
        "message": "Bienvenido administrador",
        "user": current_user.name
    }

@router.get("/doctor-only")
def doctor_only(
    current_user: User = Depends(require_roles(2))
):
    return {
        "message": "Bienvenido, doctor",
        "user": current_user.email
    }


@router.get("/patient-only")
def patient_only(
    current_user: User = Depends(require_roles(3))
):
    return {
        "message": "Bienvenido, paciente",
        "user": current_user.email
    }

@router.get("/staff-only")
def staff_only(
    current_user: User = Depends(require_roles(1, 2))
):
    return {
        "message": "Acceso permitido al personal",
        "user": current_user.email
    }