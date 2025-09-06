from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from models import HoldCreate, HoldResponse, HoldCancel, UserRole
from auth import get_current_user, require_role
from database import (
    get_db, User, Book, BookCopy, Hold, Loan,
    HoldStatusEnum, LoanStatusEnum, UserRoleEnum
)

router = APIRouter()

# Configuration constants
HOLD_EXPIRY_DAYS = 7  # How long a hold is kept when book becomes available

@router.post("/holds", response_model=HoldResponse)
def place_hold(
    hold_request: HoldCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Place a hold on a book"""
    
    # Get the book
    book = db.query(Book).filter(Book.id == hold_request.book_id).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Check if book is currently available (no need for hold)
    if book.available_copies > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Book is currently available. No need to place a hold."
        )
    
    # Check if user already has an active hold on this book
    existing_hold = db.query(Hold).filter(
        and_(
            Hold.user_id == current_user.id,
            Hold.book_id == book.id,
            Hold.status == HoldStatusEnum.ACTIVE
        )
    ).first()
    
    if existing_hold:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have an active hold on this book"
        )
    
    # Check if user currently has this book checked out
    active_loan = db.query(Loan).join(BookCopy).filter(
        and_(
            Loan.user_id == current_user.id,
            BookCopy.book_id == book.id,
            Loan.status == LoanStatusEnum.ACTIVE
        )
    ).first()
    
    if active_loan:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You currently have this book checked out"
        )
    
    # Calculate queue position
    queue_position = db.query(Hold).filter(
        and_(Hold.book_id == book.id, Hold.status == HoldStatusEnum.ACTIVE)
    ).count() + 1
    
    # Create the hold
    hold = Hold(
        user_id=current_user.id,
        book_id=book.id,
        queue_position=queue_position,
        status=HoldStatusEnum.ACTIVE,
        notes=hold_request.notes
    )
    
    db.add(hold)
    db.commit()
    db.refresh(hold)
    
    return hold

@router.get("/holds", response_model=List[HoldResponse])
def get_user_holds(
    status_filter: Optional[str] = Query(None, description="Filter by hold status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's holds"""
    
    query = db.query(Hold).options(
        joinedload(Hold.book)
    ).filter(Hold.user_id == current_user.id)
    
    # Apply status filter
    if status_filter:
        try:
            status_enum = HoldStatusEnum(status_filter)
            query = query.filter(Hold.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Valid options: {[s.value for s in HoldStatusEnum]}"
            )
    
    holds = query.order_by(Hold.hold_date.desc()).all()
    return holds

@router.get("/holds/{hold_id}", response_model=HoldResponse)
def get_hold_details(
    hold_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific hold"""
    
    hold = db.query(Hold).options(
        joinedload(Hold.book)
    ).filter(Hold.id == hold_id).first()
    
    if not hold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hold not found"
        )
    
    # Users can only see their own holds, staff can see all
    if current_user.role == UserRoleEnum.MEMBER and hold.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return hold

@router.put("/holds/{hold_id}/cancel", response_model=dict)
def cancel_hold(
    hold_id: int,
    cancel_request: HoldCancel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a hold"""
    
    hold = db.query(Hold).options(
        joinedload(Hold.book)
    ).filter(Hold.id == hold_id).first()
    
    if not hold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hold not found"
        )
    
    # Users can only cancel their own holds, staff can cancel any
    if current_user.role == UserRoleEnum.MEMBER and hold.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if hold is active
    if hold.status != HoldStatusEnum.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only active holds can be cancelled"
        )
    
    # Cancel the hold
    hold.status = HoldStatusEnum.CANCELLED
    
    if cancel_request.reason:
        hold.notes = f"{hold.notes or ''}\nCancelled: {cancel_request.reason}".strip()
    
    # Update queue positions for remaining holds
    remaining_holds = db.query(Hold).filter(
        and_(
            Hold.book_id == hold.book_id,
            Hold.status == HoldStatusEnum.ACTIVE,
            Hold.queue_position > hold.queue_position
        )
    ).all()
    
    for remaining_hold in remaining_holds:
        remaining_hold.queue_position -= 1
    
    db.commit()
    
    return {
        "message": "Hold cancelled successfully",
        "book_title": hold.book.title,
        "cancelled_at": datetime.utcnow()
    }

# Staff-only endpoints
@router.get("/holds/all", response_model=List[HoldResponse])
def get_all_holds(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    book_id: Optional[int] = Query(None, description="Filter by book ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Get all holds - Staff only"""
    
    query = db.query(Hold).options(
        joinedload(Hold.user),
        joinedload(Hold.book)
    )
    
    # Apply filters
    if status_filter:
        try:
            status_enum = HoldStatusEnum(status_filter)
            query = query.filter(Hold.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Valid options: {[s.value for s in HoldStatusEnum]}"
            )
    
    if book_id:
        query = query.filter(Hold.book_id == book_id)
    
    if user_id:
        query = query.filter(Hold.user_id == user_id)
    
    holds = query.order_by(Hold.hold_date.desc()).offset(skip).limit(limit).all()
    return holds

@router.put("/holds/{hold_id}/fulfill")
def fulfill_hold(
    hold_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Mark a hold as fulfilled when book becomes available - Staff only"""
    
    hold = db.query(Hold).options(
        joinedload(Hold.book),
        joinedload(Hold.user)
    ).filter(Hold.id == hold_id).first()
    
    if not hold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hold not found"
        )
    
    if hold.status != HoldStatusEnum.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only active holds can be fulfilled"
        )
    
    # Check if book is available
    if hold.book.available_copies <= 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Book is not currently available"
        )
    
    # Check if this is the next hold in queue
    next_hold = db.query(Hold).filter(
        and_(
            Hold.book_id == hold.book_id,
            Hold.status == HoldStatusEnum.ACTIVE
        )
    ).order_by(Hold.queue_position).first()
    
    if next_hold.id != hold.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This hold is not next in queue"
        )
    
    # Mark hold as fulfilled
    hold.status = HoldStatusEnum.FULFILLED
    hold.fulfilled_date = datetime.utcnow()
    hold.expiry_date = datetime.utcnow() + timedelta(days=HOLD_EXPIRY_DAYS)
    
    # Update queue positions for remaining holds
    remaining_holds = db.query(Hold).filter(
        and_(
            Hold.book_id == hold.book_id,
            Hold.status == HoldStatusEnum.ACTIVE,
            Hold.queue_position > hold.queue_position
        )
    ).all()
    
    for remaining_hold in remaining_holds:
        remaining_hold.queue_position -= 1
    
    db.commit()
    
    return {
        "message": "Hold fulfilled successfully",
        "user_email": hold.user.email,
        "book_title": hold.book.title,
        "expiry_date": hold.expiry_date,
        "pickup_instructions": "Please pick up your reserved book within 7 days"
    }

@router.get("/holds/stats")
def get_hold_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Get hold statistics - Staff only"""
    
    total_holds = db.query(Hold).count()
    active_holds = db.query(Hold).filter(Hold.status == HoldStatusEnum.ACTIVE).count()
    fulfilled_holds = db.query(Hold).filter(Hold.status == HoldStatusEnum.FULFILLED).count()
    
    # Expired holds (fulfilled but not picked up)
    expired_holds = db.query(Hold).filter(
        and_(
            Hold.status == HoldStatusEnum.FULFILLED,
            Hold.expiry_date < datetime.utcnow()
        )
    ).count()
    
    # Most requested books
    popular_books = db.query(
        Book.title,
        Book.author,
        func.count(Hold.id).label('hold_count')
    ).join(Hold).group_by(Book.id, Book.title, Book.author).order_by(
        func.count(Hold.id).desc()
    ).limit(5).all()
    
    # Average wait time (for fulfilled holds)
    avg_wait_result = db.query(
        func.avg(func.extract('day', Hold.fulfilled_date - Hold.hold_date))
    ).filter(Hold.status == HoldStatusEnum.FULFILLED).scalar()
    
    avg_wait_days = round(avg_wait_result, 1) if avg_wait_result else 0
    
    return {
        "total_holds": total_holds,
        "active_holds": active_holds,
        "fulfilled_holds": fulfilled_holds,
        "expired_holds": expired_holds,
        "average_wait_days": avg_wait_days,
        "most_requested_books": [
            {"title": book.title, "author": book.author, "hold_count": book.hold_count}
            for book in popular_books
        ]
    }

@router.get("/books/{book_id}/holds", response_model=List[HoldResponse])
def get_book_holds(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Get all holds for a specific book - Staff only"""
    
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    holds = db.query(Hold).options(
        joinedload(Hold.user)
    ).filter(Hold.book_id == book_id).order_by(Hold.queue_position).all()
    
    return holds
