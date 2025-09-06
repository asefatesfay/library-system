from enum import Enum
from pydantic import BaseModel, EmailStr, Field
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

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

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

# Loan Models
class LoanBase(BaseModel):
    book_copy_id: int

class LoanCreate(LoanBase):
    pass

class LoanRenew(BaseModel):
    notes: Optional[str] = None

class LoanReturn(BaseModel):
    return_notes: Optional[str] = None
    condition_notes: Optional[str] = None

class LoanResponse(BaseModel):
    id: int
    user_id: int
    book_copy_id: int
    loan_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    renewal_count: int = 0
    status: str
    notes: Optional[str] = None
    
    # Nested relationships
    book_copy: BookCopyResponse
    user: Optional[UserResponse] = None  # Only included for staff views
    
    class Config:
        from_attributes = True

# Fine Models
class FineBase(BaseModel):
    amount: float = Field(..., gt=0, description="Fine amount")
    reason: str = Field(..., min_length=1, max_length=200)
    
class FineCreate(FineBase):
    user_id: int
    loan_id: Optional[int] = None

class FineResponse(FineBase):
    id: int
    user_id: int
    loan_id: Optional[int] = None
    fine_date: datetime
    is_paid: bool = False
    paid_date: Optional[datetime] = None
    
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

# Hold Models
class HoldBase(BaseModel):
    book_id: int
    notes: Optional[str] = None

class HoldCreate(HoldBase):
    pass

class HoldCancel(BaseModel):
    reason: Optional[str] = None

class HoldResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    hold_date: datetime
    queue_position: int
    status: str
    fulfilled_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    notes: Optional[str] = None
    
    # Nested relationships
    book: BookResponse
    user: Optional[UserResponse] = None  # Only included for staff views
    
    class Config:
        from_attributes = True

# Membership Statistics
class MembershipStats(BaseModel):
    member_since: datetime
    total_loans: int
    active_loans: int
    overdue_loans: int
    active_holds: int
    outstanding_fines: float
    total_fines_paid: float
    recent_loans: List[LoanResponse]
    current_holds: List[HoldResponse]
    is_active: bool

# Notification Models
class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    notification_type: str
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
