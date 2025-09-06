from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from models import NotificationResponse, UserRole
from auth import get_current_user, require_role
from database import (
    get_db, User, Notification,
    NotificationTypeEnum, UserRoleEnum
)

router = APIRouter()

@router.get("/notifications/", response_model=List[NotificationResponse])
def get_user_notifications(
    unread_only: bool = Query(False, description="Show only unread notifications"),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's notifications"""
    
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
    return notifications

@router.put("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a notification as read"""
    
    notification = db.query(Notification).filter(
        and_(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Notification marked as read"}

@router.put("/notifications/mark-all-read")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all notifications as read for the current user"""
    
    unread_notifications = db.query(Notification).filter(
        and_(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        )
    ).all()
    
    count = len(unread_notifications)
    
    for notification in unread_notifications:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": f"Marked {count} notifications as read",
        "count": count
    }

@router.get("/notifications/summary")
def get_notification_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notification summary for the current user"""
    
    total_notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).count()
    
    unread_notifications = db.query(Notification).filter(
        and_(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        )
    ).count()
    
    # Get recent notifications (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_notifications = db.query(Notification).filter(
        and_(
            Notification.user_id == current_user.id,
            Notification.created_at >= week_ago
        )
    ).count()
    
    return {
        "total_notifications": total_notifications,
        "unread_notifications": unread_notifications,
        "recent_notifications": recent_notifications,
        "has_unread": unread_notifications > 0
    }

# Staff-only endpoints
@router.post("/notifications/broadcast")
def broadcast_notification(
    title: str,
    message: str,
    notification_type: str = "general",
    target_role: Optional[str] = Query(None, description="Target specific role (admin, librarian, member)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.LIBRARIAN]))
):
    """Broadcast notification to users - Staff only"""
    
    # Validate notification type
    try:
        notif_type = NotificationTypeEnum(notification_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid notification type. Valid options: {[t.value for t in NotificationTypeEnum]}"
        )
    
    # Get target users
    query = db.query(User).filter(User.is_active == True)
    
    if target_role:
        try:
            role_enum = UserRoleEnum(target_role)
            query = query.filter(User.role == role_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Valid options: {[r.value for r in UserRoleEnum]}"
            )
    
    target_users = query.all()
    
    # Create notifications for each user
    notifications_created = 0
    for user in target_users:
        notification = Notification(
            user_id=user.id,
            title=title,
            message=message,
            notification_type=notif_type
        )
        db.add(notification)
        notifications_created += 1
    
    db.commit()
    
    return {
        "message": "Notification broadcast successfully",
        "notifications_created": notifications_created,
        "target_role": target_role or "all_users"
    }
