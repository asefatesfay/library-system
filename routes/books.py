from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models import BookCreate, BookResponse, UserRole
from auth import get_current_user, require_role
from database import get_db, Book, User

router = APIRouter()

@router.get("/books", response_model=List[BookResponse])
def get_all_books(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all books - requires authentication"""
    books = db.query(Book).all()
    return books

@router.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get a specific book - requires authentication"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return book

@router.post("/books", response_model=BookResponse)
def create_book(
    book: BookCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Create a book - requires admin or librarian role"""
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.put("/books/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Update a book - requires admin or librarian role"""
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    for field, value in book.dict().items():
        setattr(db_book, field, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book

@router.delete("/books/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Delete a book - requires admin role only"""
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    db.delete(db_book)
    db.commit()
    return {"message": "Book deleted successfully"}
