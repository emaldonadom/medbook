from datetime import date

from pydantic import BaseModel


class PatientCreate(BaseModel):
    date_of_birth: date
    phone: str
    address: str


class PatientResponse(BaseModel):
    id: int
    user_id: int
    date_of_birth: date
    phone: str
    address: str

    model_config = {
        "from_attributes": True
    }