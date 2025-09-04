from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from models import LoanCreate, LoanResponse, LoanRenew, LoanReturn, UserRole
from auth import get_current_user, require_role
from database import (
    get_db, User, Book, BookCopy, Loan, Fine,
    LoanStatusEnum, BookCopyStatusEnum, UserRoleEnum
)

router = APIRouter()

# Configuration constants
LOAN_PERIOD_DAYS = 14
MAX_RENEWALS = 2
MAX_ACTIVE_LOANS_PER_USER = 5
OVERDUE_FINE_PER_DAY = 0.50

@router.post("/loans", response_model=LoanResponse)
def borrow_book(
    loan_request: LoanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Borrow a book - creates a new loan"""
    
    # Get the book copy
    book_copy = db.query(BookCopy).options(joinedload(BookCopy.book)).filter(
        BookCopy.id == loan_request.book_copy_id
    ).first()
    
    if not book_copy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book copy not found"
        )
    
    # Check if copy is available
    if book_copy.status != BookCopyStatusEnum.AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Book copy is not available. Current status: {book_copy.status.value}"
        )
    
    # Check user's active loan limit
    active_loans = db.query(Loan).filter(
        and_(Loan.user_id == current_user.id, Loan.status == LoanStatusEnum.ACTIVE)
    ).count()
    
    if active_loans >= MAX_ACTIVE_LOANS_PER_USER:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Maximum loan limit reached ({MAX_ACTIVE_LOANS_PER_USER} books)"
        )
    
    # Check for outstanding fines (members can't borrow with unpaid fines)
    if current_user.role == UserRoleEnum.MEMBER:
        unpaid_fines = db.query(Fine).filter(
            and_(Fine.user_id == current_user.id, Fine.is_paid == False)
        ).count()
        
        if unpaid_fines > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot borrow books with outstanding fines. Please pay fines first."
            )
    
    # Create the loan
    due_date = datetime.utcnow() + timedelta(days=LOAN_PERIOD_DAYS)
    
    loan = Loan(
        user_id=current_user.id,
        book_copy_id=book_copy.id,
        due_date=due_date,
        status=LoanStatusEnum.ACTIVE
    )
    
    # Update book copy status
    book_copy.status = BookCopyStatusEnum.CHECKED_OUT
    
    # Update book availability count
    book_copy.book.available_copies -= 1
    
    db.add(loan)
    db.commit()
    db.refresh(loan)
    
    return loan

@router.get("/loans", response_model=List[LoanResponse])
def get_user_loans(
    status_filter: Optional[str] = Query(None, description="Filter by loan status"),
    include_returned: bool = Query(False, description="Include returned loans"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's loans"""
    
    query = db.query(Loan).options(
        joinedload(Loan.book_copy).joinedload(BookCopy.book)
    ).filter(Loan.user_id == current_user.id)
    
    # Apply status filter
    if status_filter:
        try:
            status_enum = LoanStatusEnum(status_filter)
            query = query.filter(Loan.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Valid options: {[s.value for s in LoanStatusEnum]}"
            )
    elif not include_returned:
        # By default, exclude returned loans
        query = query.filter(Loan.status != LoanStatusEnum.RETURNED)
    
    loans = query.order_by(Loan.loan_date.desc()).all()
    return loans

@router.get("/loans/{loan_id}", response_model=LoanResponse)
def get_loan_details(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific loan"""
    
    loan = db.query(Loan).options(
        joinedload(Loan.book_copy).joinedload(BookCopy.book)
    ).filter(Loan.id == loan_id).first()
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )
    
    # Users can only see their own loans, staff can see all
    if current_user.role == UserRoleEnum.MEMBER and loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return loan

@router.put("/loans/{loan_id}/renew", response_model=LoanResponse)
def renew_loan(
    loan_id: int,
    renewal_request: LoanRenew,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Renew a loan - extends due date"""
    
    loan = db.query(Loan).options(
        joinedload(Loan.book_copy).joinedload(BookCopy.book)
    ).filter(Loan.id == loan_id).first()
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )
    
    # Users can only renew their own loans
    if current_user.role == UserRoleEnum.MEMBER and loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if loan is active
    if loan.status != LoanStatusEnum.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only active loans can be renewed"
        )
    
    # Check renewal limit
    if loan.renewal_count >= MAX_RENEWALS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Maximum renewals reached ({MAX_RENEWALS})"
        )
    
    # Check if book has holds (can't renew if someone is waiting)
    from database import Hold, HoldStatusEnum
    active_holds = db.query(Hold).filter(
        and_(
            Hold.book_id == loan.book_copy.book.id,
            Hold.status == HoldStatusEnum.ACTIVE
        )
    ).count()
    
    if active_holds > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot renew: other users have this book on hold"
        )
    
    # Extend due date
    loan.due_date = loan.due_date + timedelta(days=LOAN_PERIOD_DAYS)
    loan.renewal_count += 1
    
    if renewal_request.notes:
        loan.notes = f"{loan.notes or ''}\nRenewal {loan.renewal_count}: {renewal_request.notes}".strip()
    
    db.commit()
    db.refresh(loan)
    
    return loan

@router.put("/loans/{loan_id}/return", response_model=dict)
def return_book(
    loan_id: int,
    return_request: LoanReturn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return a borrowed book"""
    
    loan = db.query(Loan).options(
        joinedload(Loan.book_copy).joinedload(BookCopy.book)
    ).filter(Loan.id == loan_id).first()
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )
    
    # Members can only return their own books, staff can process any return
    if current_user.role == UserRoleEnum.MEMBER and loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if already returned
    if loan.status == LoanStatusEnum.RETURNED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Book already returned"
        )
    
    # Calculate if overdue and create fine if necessary
    return_date = datetime.utcnow()
    is_overdue = return_date > loan.due_date
    fine_amount = 0.0
    
    if is_overdue:
        days_overdue = (return_date - loan.due_date).days
        fine_amount = days_overdue * OVERDUE_FINE_PER_DAY
        
        # Create overdue fine
        fine = Fine(
            user_id=loan.user_id,
            loan_id=loan.id,
            amount=fine_amount,
            reason="overdue",
            fine_date=return_date
        )
        db.add(fine)
    
    # Update loan
    loan.return_date = return_date
    loan.status = LoanStatusEnum.RETURNED
    
    if return_request.return_notes:
        loan.notes = f"{loan.notes or ''}\nReturn: {return_request.return_notes}".strip()
    
    # Update book copy
    loan.book_copy.status = BookCopyStatusEnum.AVAILABLE
    
    if return_request.condition_notes:
        loan.book_copy.condition_notes = return_request.condition_notes
    
    # Update book availability
    loan.book_copy.book.available_copies += 1
    
    db.commit()
    
    return {
        "message": "Book returned successfully",
        "return_date": return_date,
        "was_overdue": is_overdue,
        "days_overdue": (return_date - loan.due_date).days if is_overdue else 0,
        "fine_amount": fine_amount,
        "book_title": loan.book_copy.book.title
    }

# Staff-only endpoints
@router.get("/loans/all", response_model=List[LoanResponse])
def get_all_loans(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    overdue_only: bool = Query(False, description="Show only overdue loans"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Get all loans - Staff only"""
    
    query = db.query(Loan).options(
        joinedload(Loan.user),
        joinedload(Loan.book_copy).joinedload(BookCopy.book)
    )
    
    # Apply filters
    if status_filter:
        try:
            status_enum = LoanStatusEnum(status_filter)
            query = query.filter(Loan.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Valid options: {[s.value for s in LoanStatusEnum]}"
            )
    
    if user_id:
        query = query.filter(Loan.user_id == user_id)
    
    if overdue_only:
        query = query.filter(
            and_(
                Loan.status == LoanStatusEnum.ACTIVE,
                Loan.due_date < datetime.utcnow()
            )
        )
    
    loans = query.order_by(Loan.loan_date.desc()).offset(skip).limit(limit).all()
    return loans

@router.get("/loans/stats")
def get_loan_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Get loan statistics - Staff only"""
    
    total_loans = db.query(Loan).count()
    active_loans = db.query(Loan).filter(Loan.status == LoanStatusEnum.ACTIVE).count()
    
    # Overdue loans
    overdue_loans = db.query(Loan).filter(
        and_(
            Loan.status == LoanStatusEnum.ACTIVE,
            Loan.due_date < datetime.utcnow()
        )
    ).count()
    
    # Average loan duration for returned books
    avg_duration_result = db.query(
        func.avg(func.extract('day', Loan.return_date - Loan.loan_date))
    ).filter(Loan.status == LoanStatusEnum.RETURNED).scalar()
    
    avg_loan_duration = round(avg_duration_result, 1) if avg_duration_result else 0
    
    # Most popular books (by loan count)
    popular_books = db.query(
        Book.title,
        Book.author,
        func.count(Loan.id).label('loan_count')
    ).join(BookCopy).join(Loan).group_by(Book.id, Book.title, Book.author).order_by(
        func.count(Loan.id).desc()
    ).limit(5).all()
    
    return {
        "total_loans": total_loans,
        "active_loans": active_loans,
        "overdue_loans": overdue_loans,
        "overdue_percentage": round((overdue_loans / active_loans * 100), 2) if active_loans > 0 else 0,
        "average_loan_duration_days": avg_loan_duration,
        "most_popular_books": [
            {"title": book.title, "author": book.author, "loan_count": book.loan_count}
            for book in popular_books
        ]
    }

@router.put("/loans/{loan_id}/admin-return")
def admin_return_book(
    loan_id: int,
    return_request: LoanReturn,
    waive_fines: bool = Query(False, description="Waive any overdue fines"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Admin/Librarian return a book - can waive fines"""
    
    # Use the regular return function but with admin privileges
    result = return_book(loan_id, return_request, db, current_user)
    
    # If there was a fine and admin wants to waive it
    if waive_fines and result["fine_amount"] > 0:
        # Find and mark the fine as paid
        fine = db.query(Fine).filter(
            and_(Fine.loan_id == loan_id, Fine.is_paid == False)
        ).first()
        
        if fine:
            fine.is_paid = True
            fine.paid_date = datetime.utcnow()
            db.commit()
            
            result["fine_waived"] = True
            result["fine_amount"] = 0.0
    
    return result
