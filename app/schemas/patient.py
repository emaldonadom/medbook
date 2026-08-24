from datetime import date
from typing import Optional

from pydantic import BaseModel


class PatientCreate(BaseModel):
    date_of_birth: date
    phone: str
    address: str


class PatientUpdate(BaseModel):
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class PatientResponse(BaseModel):
    id: int
    user_id: int
    date_of_birth: date
    phone: str
    address: str

    model_config = {
        "from_attributes": True
    }