from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from models import FineResponse, FinePayment, UserRole
from auth import get_current_user, require_role
from database import (
    get_db, User, Fine, Loan,
    UserRoleEnum
)

router = APIRouter()

@router.get("/fines/", response_model=List[FineResponse])
def get_user_fines(
    include_paid: bool = Query(False, description="Include paid fines"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's fines"""
    
    query = db.query(Fine).filter(Fine.user_id == current_user.id)
    
    if not include_paid:
        query = query.filter(Fine.is_paid == False)
    
    fines = query.order_by(Fine.fine_date.desc()).all()
    return fines

@router.get("/fines/{fine_id}", response_model=FineResponse)
def get_fine_details(
    fine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific fine"""
    
    fine = db.query(Fine).filter(Fine.id == fine_id).first()
    
    if not fine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fine not found"
        )
    
    # Users can only see their own fines, staff can see all
    if current_user.role == UserRoleEnum.MEMBER and fine.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return fine

@router.post("/fines/{fine_id}/pay")
def pay_fine(
    fine_id: int,
    payment: FinePayment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Pay a fine"""
    
    fine = db.query(Fine).filter(Fine.id == fine_id).first()
    
    if not fine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fine not found"
        )
    
    # Users can only pay their own fines, staff can process any payment
    if current_user.role == UserRoleEnum.MEMBER and fine.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if already paid
    if fine.is_paid:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Fine already paid"
        )
    
    # Process payment
    fine.is_paid = True
    fine.paid_date = datetime.utcnow()
    
    # Add payment notes if provided
    if payment.notes:
        fine.notes = f"{fine.notes or ''}\nPayment: {payment.notes}".strip()
    
    db.commit()
    db.refresh(fine)
    
    return {
        "message": "Fine paid successfully",
        "fine_id": fine.id,
        "amount_paid": fine.amount,
        "payment_date": fine.paid_date,
        "payment_method": payment.payment_method
    }

@router.get("/fines/summary")
def get_fine_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's fine summary"""
    
    # Outstanding fines
    outstanding_fines = db.query(Fine).filter(
        and_(Fine.user_id == current_user.id, Fine.is_paid == False)
    ).all()
    
    outstanding_amount = sum(fine.amount for fine in outstanding_fines)
    
    # Paid fines (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    paid_fines = db.query(Fine).filter(
        and_(
            Fine.user_id == current_user.id,
            Fine.is_paid == True,
            Fine.paid_date >= six_months_ago
        )
    ).all()
    
    paid_amount = sum(fine.amount for fine in paid_fines)
    
    return {
        "outstanding_fines_count": len(outstanding_fines),
        "outstanding_amount": outstanding_amount,
        "paid_fines_last_6_months": len(paid_fines),
        "paid_amount_last_6_months": paid_amount,
        "can_borrow": outstanding_amount == 0,
        "outstanding_fines": outstanding_fines
    }

# Staff-only endpoints
@router.get("/fines/all", response_model=List[FineResponse])
def get_all_fines(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    paid_status: Optional[bool] = Query(None, description="Filter by payment status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Get all fines - Staff only"""
    
    query = db.query(Fine).options(joinedload(Fine.user))
    
    # Apply filters
    if user_id:
        query = query.filter(Fine.user_id == user_id)
    
    if paid_status is not None:
        query = query.filter(Fine.is_paid == paid_status)
    
    fines = query.order_by(Fine.fine_date.desc()).offset(skip).limit(limit).all()
    return fines

@router.post("/fines/{fine_id}/waive")
def waive_fine(
    fine_id: int,
    reason: str = Query(..., description="Reason for waiving the fine"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Waive a fine - Staff only"""
    
    fine = db.query(Fine).filter(Fine.id == fine_id).first()
    
    if not fine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fine not found"
        )
    
    if fine.is_paid:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot waive a fine that has already been paid"
        )
    
    # Waive the fine
    fine.is_paid = True
    fine.paid_date = datetime.utcnow()
    fine.notes = f"{fine.notes or ''}\nWaived by {current_user.full_name}: {reason}".strip()
    
    db.commit()
    db.refresh(fine)
    
    return {
        "message": "Fine waived successfully",
        "fine_id": fine.id,
        "waived_amount": fine.amount,
        "waived_by": current_user.full_name,
        "reason": reason
    }

@router.get("/fines/stats")
def get_fine_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Get fine statistics - Staff only"""
    
    # Total fines
    total_fines = db.query(Fine).count()
    outstanding_fines = db.query(Fine).filter(Fine.is_paid == False).count()
    paid_fines = db.query(Fine).filter(Fine.is_paid == True).count()
    
    # Fine amounts
    total_amount = db.query(func.sum(Fine.amount)).scalar() or 0
    outstanding_amount = db.query(func.sum(Fine.amount)).filter(
        Fine.is_paid == False
    ).scalar() or 0
    collected_amount = db.query(func.sum(Fine.amount)).filter(
        Fine.is_paid == True
    ).scalar() or 0
    
    # Recent collections (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_collections = db.query(func.sum(Fine.amount)).filter(
        and_(Fine.is_paid == True, Fine.paid_date >= thirty_days_ago)
    ).scalar() or 0
    
    # Top borrowers with fines
    top_fine_users = db.query(
        User.full_name,
        User.email,
        func.sum(Fine.amount).label('total_fines'),
        func.count(Fine.id).label('fine_count')
    ).join(Fine).filter(Fine.is_paid == False).group_by(
        User.id, User.full_name, User.email
    ).order_by(func.sum(Fine.amount).desc()).limit(5).all()
    
    return {
        "total_fines": total_fines,
        "outstanding_fines": outstanding_fines,
        "paid_fines": paid_fines,
        "total_amount": round(total_amount, 2),
        "outstanding_amount": round(outstanding_amount, 2),
        "collected_amount": round(collected_amount, 2),
        "collection_rate": round((collected_amount / total_amount * 100), 2) if total_amount > 0 else 0,
        "recent_collections_30_days": round(recent_collections, 2),
        "top_fine_users": [
            {
                "name": user.full_name,
                "email": user.email,
                "total_fines": float(user.total_fines),
                "fine_count": user.fine_count
            }
            for user in top_fine_users
        ]
    }

@router.get("/fines/report")
def generate_fine_report(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Generate fine report for a date range - Staff only"""
    
    query = db.query(Fine)
    
    # Apply date filters
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Fine.fine_date >= start_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use YYYY-MM-DD"
            )
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(Fine.fine_date < end_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use YYYY-MM-DD"
            )
    
    fines = query.options(joinedload(Fine.user)).all()
    
    # Calculate statistics
    total_fines = len(fines)
    total_amount = sum(fine.amount for fine in fines)
    paid_fines = [fine for fine in fines if fine.is_paid]
    outstanding_fines = [fine for fine in fines if not fine.is_paid]
    
    return {
        "report_period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "summary": {
            "total_fines": total_fines,
            "total_amount": round(total_amount, 2),
            "paid_fines": len(paid_fines),
            "outstanding_fines": len(outstanding_fines),
            "collection_rate": round((len(paid_fines) / total_fines * 100), 2) if total_fines > 0 else 0
        },
        "fines": fines
    }
