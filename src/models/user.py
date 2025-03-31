from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    github_token: Optional[str] = None

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    github_token: Optional[str] = None
    github_username: Optional[str] = None

    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str 