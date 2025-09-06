from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from models import (
    UserCreate, UserResponse, UserUpdate, MembershipStats, 
    UserRole, LoanResponse, HoldResponse, FineResponse
)
from auth import get_current_user, require_role, hash_password
from database import (
    get_db, User, Book, BookCopy, Loan, Hold, Fine,
    UserRoleEnum, LoanStatusEnum, HoldStatusEnum
)

router = APIRouter()

@router.post("/members", response_model=UserResponse)
def create_member(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Create a new library member - Staff only"""
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Create new member
    hashed_password = hash_password(user_data.password)
    
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=UserRoleEnum.MEMBER,  # New registrations are always members
        phone=user_data.phone,
        address=user_data.address,
        is_active=True,
        membership_date=datetime.utcnow()
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.get("/members", response_model=List[UserResponse])
def get_all_members(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by name or email"),
    role_filter: Optional[str] = Query(None, description="Filter by role"),
    active_only: bool = Query(True, description="Show only active members"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Get all library members - Staff only"""
    
    query = db.query(User)
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.full_name.ilike(search_term),
                User.email.ilike(search_term)
            )
        )
    
    if role_filter:
        try:
            role_enum = UserRoleEnum(role_filter)
            query = query.filter(User.role == role_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Valid options: {[r.value for r in UserRoleEnum]}"
            )
    
    if active_only:
        query = query.filter(User.is_active == True)
    
    members = query.order_by(User.membership_date.desc()).offset(skip).limit(limit).all()
    return members

@router.get("/members/{member_id}", response_model=UserResponse)
def get_member_details(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get member details"""
    
    member = db.query(User).filter(User.id == member_id).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    # Users can only see their own details, staff can see all
    if (current_user.role == UserRoleEnum.MEMBER and 
        current_user.id != member_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return member

@router.put("/members/{member_id}", response_model=UserResponse)
def update_member(
    member_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update member information"""
    
    member = db.query(User).filter(User.id == member_id).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    # Users can only update their own details, staff can update any
    if (current_user.role == UserRoleEnum.MEMBER and 
        current_user.id != member_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update fields if provided
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "password" and value:
            # Hash the new password
            setattr(member, "hashed_password", hash_password(value))
        else:
            setattr(member, field, value)
    
    db.commit()
    db.refresh(member)
    
    return member

@router.get("/members/{member_id}/activity", response_model=MembershipStats)
def get_member_activity(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get member's library activity statistics"""
    
    member = db.query(User).filter(User.id == member_id).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    # Users can only see their own activity, staff can see all
    if (current_user.role == UserRoleEnum.MEMBER and 
        current_user.id != member_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Calculate statistics
    total_loans = db.query(Loan).filter(Loan.user_id == member_id).count()
    active_loans = db.query(Loan).filter(
        and_(Loan.user_id == member_id, Loan.status == LoanStatusEnum.ACTIVE)
    ).count()
    
    # Overdue loans
    overdue_loans = db.query(Loan).filter(
        and_(
            Loan.user_id == member_id,
            Loan.status == LoanStatusEnum.ACTIVE,
            Loan.due_date < datetime.utcnow()
        )
    ).count()
    
    # Active holds
    active_holds = db.query(Hold).filter(
        and_(Hold.user_id == member_id, Hold.status == HoldStatusEnum.ACTIVE)
    ).count()
    
    # Outstanding fines
    outstanding_fines = db.query(func.sum(Fine.amount)).filter(
        and_(Fine.user_id == member_id, Fine.is_paid == False)
    ).scalar() or 0.0
    
    # Total fines paid
    total_fines_paid = db.query(func.sum(Fine.amount)).filter(
        and_(Fine.user_id == member_id, Fine.is_paid == True)
    ).scalar() or 0.0
    
    # Recent activity (last 5 loans)
    recent_loans = db.query(Loan).options(
        joinedload(Loan.book_copy).joinedload(BookCopy.book)
    ).filter(Loan.user_id == member_id).order_by(
        Loan.loan_date.desc()
    ).limit(5).all()
    
    # Current holds
    current_holds = db.query(Hold).options(
        joinedload(Hold.book)
    ).filter(
        and_(Hold.user_id == member_id, Hold.status == HoldStatusEnum.ACTIVE)
    ).order_by(Hold.queue_position).all()
    
    return MembershipStats(
        member_since=member.membership_date,
        total_loans=total_loans,
        active_loans=active_loans,
        overdue_loans=overdue_loans,
        active_holds=active_holds,
        outstanding_fines=outstanding_fines,
        total_fines_paid=total_fines_paid,
        recent_loans=recent_loans,
        current_holds=current_holds,
        is_active=member.is_active
    )

@router.put("/members/{member_id}/deactivate")
def deactivate_member(
    member_id: int,
    reason: str = Query(..., description="Reason for deactivation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Deactivate a member account - Staff only"""
    
    member = db.query(User).filter(User.id == member_id).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    if not member.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Member is already deactivated"
        )
    
    # Check for active loans
    active_loans = db.query(Loan).filter(
        and_(Loan.user_id == member_id, Loan.status == LoanStatusEnum.ACTIVE)
    ).count()
    
    if active_loans > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot deactivate member with {active_loans} active loans"
        )
    
    # Check for outstanding fines
    outstanding_fines = db.query(func.sum(Fine.amount)).filter(
        and_(Fine.user_id == member_id, Fine.is_paid == False)
    ).scalar() or 0.0
    
    if outstanding_fines > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot deactivate member with ${outstanding_fines:.2f} in outstanding fines"
        )
    
    # Deactivate the member
    member.is_active = False
    
    # Cancel any active holds
    active_holds = db.query(Hold).filter(
        and_(Hold.user_id == member_id, Hold.status == HoldStatusEnum.ACTIVE)
    ).all()
    
    for hold in active_holds:
        hold.status = HoldStatusEnum.CANCELLED
        hold.notes = f"{hold.notes or ''}\nCancelled due to account deactivation: {reason}".strip()
    
    db.commit()
    
    return {
        "message": "Member deactivated successfully",
        "member_email": member.email,
        "reason": reason,
        "cancelled_holds": len(active_holds),
        "deactivated_at": datetime.utcnow()
    }

@router.put("/members/{member_id}/reactivate")
def reactivate_member(
    member_id: int,
    notes: str = Query(None, description="Notes for reactivation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Reactivate a member account - Staff only"""
    
    member = db.query(User).filter(User.id == member_id).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    if member.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Member is already active"
        )
    
    # Reactivate the member
    member.is_active = True
    
    db.commit()
    
    return {
        "message": "Member reactivated successfully",
        "member_email": member.email,
        "notes": notes,
        "reactivated_at": datetime.utcnow()
    }

@router.get("/members/stats")
def get_membership_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Get overall membership statistics - Staff only"""
    
    total_members = db.query(User).filter(User.role == UserRoleEnum.MEMBER).count()
    active_members = db.query(User).filter(
        and_(User.role == UserRoleEnum.MEMBER, User.is_active == True)
    ).count()
    
    # New members this month
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_members_this_month = db.query(User).filter(
        and_(
            User.role == UserRoleEnum.MEMBER,
            User.membership_date >= start_of_month
        )
    ).count()
    
    # Members with active loans
    members_with_loans = db.query(func.count(func.distinct(Loan.user_id))).filter(
        Loan.status == LoanStatusEnum.ACTIVE
    ).scalar()
    
    # Members with overdue items
    members_with_overdue = db.query(func.count(func.distinct(Loan.user_id))).filter(
        and_(
            Loan.status == LoanStatusEnum.ACTIVE,
            Loan.due_date < datetime.utcnow()
        )
    ).scalar()
    
    # Top borrowers (most loans in last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    top_borrowers = db.query(
        User.full_name,
        User.email,
        func.count(Loan.id).label('loan_count')
    ).join(Loan).filter(
        Loan.loan_date >= thirty_days_ago
    ).group_by(User.id, User.full_name, User.email).order_by(
        func.count(Loan.id).desc()
    ).limit(5).all()
    
    return {
        "total_members": total_members,
        "active_members": active_members,
        "inactive_members": total_members - active_members,
        "new_members_this_month": new_members_this_month,
        "members_with_active_loans": members_with_loans,
        "members_with_overdue_items": members_with_overdue,
        "top_borrowers_last_30_days": [
            {
                "name": borrower.full_name,
                "email": borrower.email,
                "loan_count": borrower.loan_count
            }
            for borrower in top_borrowers
        ]
    }
