from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional
from uuid import UUID

class LoginRequest(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = None

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    date_of_birth: Optional[date]
    phone_number: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class SessionToken(BaseModel):
    session_token: str