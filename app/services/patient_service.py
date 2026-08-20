from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.user import User


class PatientService:

    @staticmethod
    def create_patient(
        db: Session,
        user: User,
        date_of_birth,
        phone: str,
        address: str
    ):
        existing_patient = (
            db.query(Patient)
            .filter(Patient.user_id == user.id)
            .first()
        )

        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este usuario ya tiene un perfil de paciente"
            )

        patient = Patient(
            user_id=user.id,
            date_of_birth=date_of_birth,
            phone=phone,
            address=address
        )

        db.add(patient)
        db.commit()
        db.refresh(patient)

        return patient