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

    @staticmethod
    def get_patients(db: Session, skip: int = 0, limit: int = 100):
        return (
            db.query(Patient)
            .order_by(Patient.id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_patient_or_404(db: Session, patient_id: int) -> Patient:
        patient = (
            db.query(Patient)
            .filter(Patient.id == patient_id)
            .first()
        )

        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente no encontrado"
            )

        return patient

    @staticmethod
    def update_patient(
        db: Session,
        patient_id: int,
        date_of_birth=None,
        phone: str = None,
        address: str = None
    ):
        patient = PatientService.get_patient_or_404(db, patient_id)

        if date_of_birth is not None:
            patient.date_of_birth = date_of_birth

        if phone is not None:
            patient.phone = phone

        if address is not None:
            patient.address = address

        db.commit()
        db.refresh(patient)

        return patient

    @staticmethod
    def delete_patient(db: Session, patient_id: int):
        patient = PatientService.get_patient_or_404(db, patient_id)

        db.delete(patient)
        db.commit()