from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import (
    create_user,
    delete_user,
    get_user_or_404,
    get_users,
    update_user,
)

from app.core.permissions import require_roles
from app.core.security import get_current_user
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


@router.get(
    "/",
    response_model=list[UserResponse]
)
def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_roles(1)),
    db: Session = Depends(get_db)
):
    return get_users(db, skip=skip, limit=limit)


@router.get(
    "/doctors",
    response_model=list[UserResponse]
)
def list_doctors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_users(db, role_id=2)


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


@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role_id != 1 and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este usuario"
        )

    return get_user_or_404(db, user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse
)
def update_user_endpoint(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    is_admin = current_user.role_id == 1

    if not is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para editar este usuario"
        )

    if not is_admin and user_data.role_id is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un administrador puede cambiar el rol de un usuario"
        )

    return update_user(db, user_id, user_data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_user_endpoint(
    user_id: int,
    current_user: User = Depends(require_roles(1)),
    db: Session = Depends(get_db)
):
    delete_user(db, user_id)