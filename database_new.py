import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, Enum, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta
import enum

# Database URL - supports both SQLite (local) and PostgreSQL (production)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./library.db"  # Default to SQLite for local development
)

print(f"🔗 Connecting to database: {DATABASE_URL}")

# Handle SQLite vs PostgreSQL connection args
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    print("📁 Using SQLite database")
else:
    # For PostgreSQL/other databases
    engine = create_engine(DATABASE_URL)
    print("🐘 Using PostgreSQL database")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class UserRoleEnum(str, enum.Enum):
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    MEMBER = "member"

class LoanStatusEnum(str, enum.Enum):
    ACTIVE = "active"
    RETURNED = "returned"
    OVERDUE = "overdue"

class HoldStatusEnum(str, enum.Enum):
    ACTIVE = "active"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"

class BookCopyStatusEnum(str, enum.Enum):
    AVAILABLE = "available"
    CHECKED_OUT = "checked_out"
    ON_HOLD = "on_hold"
    DAMAGED = "damaged"
    LOST = "lost"

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRoleEnum), default=UserRoleEnum.MEMBER)
    is_active = Column(Boolean, default=True)
    phone = Column(String)
    address = Column(Text)
    membership_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    loans = relationship("Loan", back_populates="user")
    holds = relationship("Hold", back_populates="user")
    fines = relationship("Fine", back_populates="user")

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    author = Column(String, nullable=False, index=True)
    isbn = Column(String, unique=True, index=True)
    publisher = Column(String)
    publication_year = Column(Integer)
    genre = Column(String)
    description = Column(Text)
    total_copies = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    copies = relationship("BookCopy", back_populates="book")
    holds = relationship("Hold", back_populates="book")

class BookCopy(Base):
    __tablename__ = "book_copies"
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    barcode = Column(String, unique=True, index=True)
    status = Column(Enum(BookCopyStatusEnum), default=BookCopyStatusEnum.AVAILABLE)
    condition_notes = Column(Text)
    acquired_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    book = relationship("Book", back_populates="copies")
    loans = relationship("Loan", back_populates="book_copy")

class Loan(Base):
    __tablename__ = "loans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_copy_id = Column(Integer, ForeignKey("book_copies.id"), nullable=False)
    loan_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime)
    renewal_count = Column(Integer, default=0)
    status = Column(Enum(LoanStatusEnum), default=LoanStatusEnum.ACTIVE)
    notes = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="loans")
    book_copy = relationship("BookCopy", back_populates="loans")
    fines = relationship("Fine", back_populates="loan")

class Hold(Base):
    __tablename__ = "holds"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    hold_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime)
    status = Column(Enum(HoldStatusEnum), default=HoldStatusEnum.ACTIVE)
    position_in_queue = Column(Integer)
    
    # Relationships
    user = relationship("User", back_populates="holds")
    book = relationship("Book", back_populates="holds")

class Fine(Base):
    __tablename__ = "fines"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=True)
    amount = Column(Float, nullable=False)
    reason = Column(String, nullable=False)  # "overdue", "damage", "lost"
    fine_date = Column(DateTime, default=datetime.utcnow)
    paid_date = Column(DateTime)
    is_paid = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="fines")
    loan = relationship("Loan", back_populates="fines")

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
