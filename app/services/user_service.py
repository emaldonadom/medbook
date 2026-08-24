from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password


def create_user(db: Session, user_data: UserCreate):
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario registrado con ese email"
        )

    user = User(
        name=user_data.name,
        email=user_data.email,
        password=hash_password(user_data.password),
        role_id=user_data.role_id
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_users(db: Session, skip: int = 0, limit: int = 100, role_id: int = None):
    query = db.query(User)

    if role_id is not None:
        query = query.filter(User.role_id == role_id)

    return (
        query
        .order_by(User.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user_or_404(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    return user


def update_user(db: Session, user_id: int, user_data: UserUpdate):
    user = get_user_or_404(db, user_id)

    if user_data.email is not None and user_data.email != user.email:
        existing_user = (
            db.query(User)
            .filter(User.email == user_data.email)
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un usuario registrado con ese email"
            )

        user.email = user_data.email

    if user_data.name is not None:
        user.name = user_data.name

    if user_data.password is not None:
        user.password = hash_password(user_data.password)

    if user_data.role_id is not None:
        user.role_id = user_data.role_id

    db.commit()
    db.refresh(user)

    return user


def delete_user(db: Session, user_id: int):
    user = get_user_or_404(db, user_id)

    db.delete(user)
    db.commit()