from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# This matches the database enum
class UserRole(str, Enum):
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    MEMBER = "member"

# Pydantic models for API
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.MEMBER

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Book models
class BookBase(BaseModel):
    title: str
    author: str
    price: float

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
