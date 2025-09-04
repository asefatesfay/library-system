from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from models import BookCreate, BookResponse, BookUpdate, BookCopyResponse, UserRole
from auth import get_current_user, require_role
from database import get_db, Book, BookCopy, User, BookCopyStatusEnum

router = APIRouter()

@router.get("/books", response_model=List[BookResponse])
def browse_catalog(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by title, author, or ISBN"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    author: Optional[str] = Query(None, description="Filter by author"),
    available_only: bool = Query(False, description="Show only books with available copies"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Browse library catalog - supports search and filters"""
    query = db.query(Book)
    
    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Book.title.ilike(search_term)) |
            (Book.author.ilike(search_term)) |
            (Book.isbn.ilike(search_term))
        )
    
    # Apply genre filter
    if genre:
        query = query.filter(Book.genre.ilike(f"%{genre}%"))
    
    # Apply author filter
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    
    # Apply availability filter
    if available_only:
        query = query.filter(Book.available_copies > 0)
    
    # Apply pagination
    books = query.offset(skip).limit(limit).all()
    return books

@router.get("/books/{book_id}", response_model=BookResponse)
def get_book_details(
    book_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific book"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return book

@router.get("/books/{book_id}/copies", response_model=List[BookCopyResponse])
def get_book_copies(
    book_id: int,
    status_filter: Optional[str] = Query(None, description="Filter by copy status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all copies of a specific book with their status"""
    # Verify book exists
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    query = db.query(BookCopy).filter(BookCopy.book_id == book_id)
    
    # Apply status filter if provided
    if status_filter:
        try:
            status_enum = BookCopyStatusEnum(status_filter)
            query = query.filter(BookCopy.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Valid options: {[s.value for s in BookCopyStatusEnum]}"
            )
    
    copies = query.all()
    return copies

@router.get("/books/{book_id}/availability")
def check_book_availability(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check availability status of a book"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Get copy status counts
    copy_counts = db.query(BookCopy.status, func.count(BookCopy.id)).filter(
        BookCopy.book_id == book_id
    ).group_by(BookCopy.status).all()
    
    status_summary = {status.value: 0 for status in BookCopyStatusEnum}
    for status, count in copy_counts:
        status_summary[status.value] = count
    
    return {
        "book_id": book_id,
        "title": book.title,
        "total_copies": book.total_copies,
        "available_copies": book.available_copies,
        "copy_status": status_summary,
        "can_borrow": book.available_copies > 0,
        "can_hold": book.available_copies == 0 and book.total_copies > 0
    }

@router.post("/books", response_model=BookResponse)
def add_book_to_catalog(
    book: BookCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Add a new book to the library catalog - creates book and initial copies"""
    # Check if book with same ISBN already exists
    if book.isbn:
        existing_book = db.query(Book).filter(Book.isbn == book.isbn).first()
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Book with ISBN {book.isbn} already exists"
            )
    
    # Create book record
    book_data = book.dict()
    total_copies = book_data.pop("total_copies", 1)
    
    db_book = Book(
        **book_data,
        total_copies=total_copies,
        available_copies=total_copies
    )
    db.add(db_book)
    db.flush()  # Get the book ID
    
    # Create book copies
    for copy_num in range(1, total_copies + 1):
        barcode = f"{db_book.isbn.replace('-', '')}{copy_num:03d}" if db_book.isbn else f"BOOK{db_book.id:04d}{copy_num:03d}"
        
        book_copy = BookCopy(
            book_id=db_book.id,
            barcode=barcode,
            status=BookCopyStatusEnum.AVAILABLE,
            condition_notes="New acquisition"
        )
        db.add(book_copy)
    
    db.commit()
    db.refresh(db_book)
    return db_book

@router.put("/books/{book_id}", response_model=BookResponse)
def update_book_information(
    book_id: int,
    book_update: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Update book information - does not affect copies"""
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Update only provided fields
    update_data = book_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_book, field, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book

@router.post("/books/{book_id}/copies")
def add_book_copies(
    book_id: int,
    copies_to_add: int = Query(..., ge=1, description="Number of copies to add"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Add additional copies of an existing book"""
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Create new copies
    current_copy_count = db_book.total_copies
    for copy_num in range(current_copy_count + 1, current_copy_count + copies_to_add + 1):
        barcode = f"{db_book.isbn.replace('-', '')}{copy_num:03d}" if db_book.isbn else f"BOOK{db_book.id:04d}{copy_num:03d}"
        
        book_copy = BookCopy(
            book_id=db_book.id,
            barcode=barcode,
            status=BookCopyStatusEnum.AVAILABLE,
            condition_notes="Additional copy"
        )
        db.add(book_copy)
    
    # Update book totals
    db_book.total_copies += copies_to_add
    db_book.available_copies += copies_to_add
    
    db.commit()
    
    return {
        "message": f"Added {copies_to_add} copies to '{db_book.title}'",
        "new_total_copies": db_book.total_copies,
        "available_copies": db_book.available_copies
    }

@router.delete("/books/{book_id}")
def remove_book_from_catalog(
    book_id: int,
    force: bool = Query(False, description="Force delete even if copies are checked out"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Remove a book from catalog - Admin only, checks for active loans"""
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Check for checked out copies unless forcing
    if not force:
        checked_out_copies = db.query(BookCopy).filter(
            BookCopy.book_id == book_id,
            BookCopy.status == BookCopyStatusEnum.CHECKED_OUT
        ).count()
        
        if checked_out_copies > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot delete book: {checked_out_copies} copies are currently checked out. Use force=true to override."
            )
    
    # Delete all copies first (cascading should handle this, but being explicit)
    db.query(BookCopy).filter(BookCopy.book_id == book_id).delete()
    
    # Delete the book
    db.delete(db_book)
    db.commit()
    
    return {"message": f"Book '{db_book.title}' and all its copies have been removed from the catalog"}

# Library Management Endpoints
@router.get("/books/stats/catalog")
def get_catalog_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Get library catalog statistics - Staff only"""
    total_books = db.query(Book).count()
    total_copies = db.query(BookCopy).count()
    available_copies = db.query(BookCopy).filter(BookCopy.status == BookCopyStatusEnum.AVAILABLE).count()
    checked_out_copies = db.query(BookCopy).filter(BookCopy.status == BookCopyStatusEnum.CHECKED_OUT).count()
    
    # Genre distribution
    genre_stats = db.query(Book.genre, func.count(Book.id)).group_by(Book.genre).all()
    
    return {
        "total_book_titles": total_books,
        "total_physical_copies": total_copies,
        "available_copies": available_copies,
        "checked_out_copies": checked_out_copies,
        "circulation_rate": round((checked_out_copies / total_copies * 100), 2) if total_copies > 0 else 0,
        "genre_distribution": [{"genre": genre or "Unknown", "count": count} for genre, count in genre_stats]
    }

@router.get("/books/genres")
def list_available_genres(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of all genres in the catalog"""
    genres = db.query(Book.genre).distinct().filter(Book.genre.isnot(None)).all()
    return {"genres": [genre[0] for genre in genres if genre[0]]}

@router.get("/books/search/suggestions")
def get_search_suggestions(
    query: str = Query(..., min_length=2, description="Search query for suggestions"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get search suggestions for titles and authors"""
    search_term = f"%{query}%"
    
    # Get title suggestions
    title_suggestions = db.query(Book.title).filter(
        Book.title.ilike(search_term)
    ).distinct().limit(5).all()
    
    # Get author suggestions
    author_suggestions = db.query(Book.author).filter(
        Book.author.ilike(search_term)
    ).distinct().limit(5).all()
    
    return {
        "titles": [title[0] for title in title_suggestions],
        "authors": [author[0] for author in author_suggestions]
    }
