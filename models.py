from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Enums matching database
class UserRole(str, Enum):
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    MEMBER = "member"

class LoanStatus(str, Enum):
    ACTIVE = "active"
    RETURNED = "returned"
    OVERDUE = "overdue"

class HoldStatus(str, Enum):
    ACTIVE = "active"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"

class BookCopyStatus(str, Enum):
    AVAILABLE = "available"
    CHECKED_OUT = "checked_out"
    ON_HOLD = "on_hold"
    DAMAGED = "damaged"
    LOST = "lost"

# User Models
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.MEMBER
    phone: Optional[str] = None
    address: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    membership_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# Book Models
class BookBase(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    genre: Optional[str] = None
    description: Optional[str] = None

class BookCreate(BookBase):
    total_copies: int = 1

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    genre: Optional[str] = None
    description: Optional[str] = None

class BookResponse(BookBase):
    id: int
    total_copies: int
    available_copies: int
    created_at: datetime

    class Config:
        from_attributes = True

# Book Copy Models
class BookCopyResponse(BaseModel):
    id: int
    book_id: int
    barcode: Optional[str] = None
    status: BookCopyStatus
    condition_notes: Optional[str] = None
    acquired_date: datetime

    class Config:
        from_attributes = True

# Loan Models
class LoanCreate(BaseModel):
    book_copy_id: int

class LoanResponse(BaseModel):
    id: int
    user_id: int
    book_copy_id: int
    loan_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    renewal_count: int
    status: LoanStatus
    notes: Optional[str] = None
    
    # Nested objects
    book_copy: BookCopyResponse
    
    class Config:
        from_attributes = True

class LoanRenew(BaseModel):
    notes: Optional[str] = None

class LoanReturn(BaseModel):
    return_notes: Optional[str] = None
    condition_notes: Optional[str] = None

# Hold Models
class HoldCreate(BaseModel):
    book_id: int

class HoldResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    hold_date: datetime
    expiry_date: Optional[datetime] = None
    status: HoldStatus
    position_in_queue: Optional[int] = None
    
    # Nested objects
    book: BookResponse
    
    class Config:
        from_attributes = True

# Fine Models
class FineResponse(BaseModel):
    id: int
    user_id: int
    loan_id: Optional[int] = None
    amount: float
    reason: str
    fine_date: datetime
    paid_date: Optional[datetime] = None
    is_paid: bool
    
    class Config:
        from_attributes = True

class FinePayment(BaseModel):
    payment_method: str
    notes: Optional[str] = None

# Authentication Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
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
