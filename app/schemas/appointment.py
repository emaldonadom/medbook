from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, field_validator

AppointmentStatus = Literal["pending", "confirmed", "completed", "cancelled"]


class AppointmentCreate(BaseModel):
    doctor_id: int
    scheduled_at: datetime
    reason: str

    @field_validator("scheduled_at")
    @classmethod
    def scheduled_at_must_be_future(cls, value: datetime) -> datetime:
        # Comparamos en UTC "naive" para no depender de tzinfo del input
        now = datetime.utcnow()
        naive_value = value.replace(tzinfo=None) if value.tzinfo else value

        if naive_value <= now:
            raise ValueError("La fecha de la cita debe ser en el futuro")

        return value


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    scheduled_at: datetime
    reason: str
    status: AppointmentStatus

    model_config = {
        "from_attributes": True
    }
