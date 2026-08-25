from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id"),
        index=True,
        nullable=False
    )

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False
    )

    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    reason: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    patient: Mapped["Patient"] = relationship(
        back_populates="appointments"
    )

    doctor: Mapped["User"] = relationship(
        foreign_keys=[doctor_id]
    )

    @property
    def patient_name(self) -> str:
        return self.patient.user.name

    @property
    def doctor_name(self) -> str:
        return self.doctor.name