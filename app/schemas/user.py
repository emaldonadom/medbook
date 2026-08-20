from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role_id: int = 3


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role_id: int

    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class UserMeResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: RoleResponse

    class Config:
        from_attributes = True