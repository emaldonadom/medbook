from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user
from app.models.user import User


def require_roles(*required_role_ids: int):
    def role_checker(
        current_user: User = Depends(get_current_user)
    ):
        if current_user.role_id not in required_role_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción"
            )

        return current_user

    return role_checker