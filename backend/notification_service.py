"""
Notification service for library system
Handles automatic notifications for various events
"""
from sqlalchemy.orm import Session
from database import Notification, Hold, User, Book, HoldStatusEnum, NotificationTypeEnum
from datetime import datetime, timedelta
from typing import List

def notify_book_available(db: Session, book_id: int, available_copies: int = 1):
    """
    Notify users with holds when a book becomes available
    Processes holds in queue order
    """
    # Get active holds for this book, ordered by queue position
    active_holds = db.query(Hold).filter(
        Hold.book_id == book_id,
        Hold.status == HoldStatusEnum.ACTIVE
    ).order_by(Hold.queue_position).limit(available_copies).all()
    
    notifications_sent = []
    
    for hold in active_holds:
        # Create notification
        notification = Notification(
            user_id=hold.user_id,
            title="Book Available for Pickup",
            message=f"Good news! '{hold.book.title}' by {hold.book.author} is now available for pickup. "
                   f"Please visit the library within 7 days to collect your reserved book.",
            notification_type=NotificationTypeEnum.BOOK_AVAILABLE
        )
        
        db.add(notification)
        notifications_sent.append({
            "user_id": hold.user_id,
            "user_name": hold.user.full_name,
            "book_title": hold.book.title,
            "hold_id": hold.id
        })
    
    db.commit()
    return notifications_sent

def notify_overdue_loans(db: Session):
    """
    Send notifications for overdue loans
    This would typically be run as a scheduled job
    """
    from database import Loan, LoanStatusEnum
    
    # Get overdue loans that don't have recent overdue notifications
    overdue_loans = db.query(Loan).filter(
        Loan.status == LoanStatusEnum.ACTIVE,
        Loan.due_date < datetime.utcnow()
    ).all()
    
    notifications_sent = []
    
    for loan in overdue_loans:
        # Check if we've already sent an overdue notification recently (within 3 days)
        recent_overdue_notification = db.query(Notification).filter(
            Notification.user_id == loan.user_id,
            Notification.notification_type == NotificationTypeEnum.OVERDUE_REMINDER,
            Notification.created_at >= datetime.utcnow() - timedelta(days=3)
        ).first()
        
        if not recent_overdue_notification:
            days_overdue = (datetime.utcnow() - loan.due_date).days
            fine_amount = days_overdue * 0.50  # $0.50 per day
            
            notification = Notification(
                user_id=loan.user_id,
                title="Overdue Book Reminder",
                message=f"Your book '{loan.book_copy.book.title}' was due on {loan.due_date.strftime('%Y-%m-%d')} "
                       f"and is now {days_overdue} days overdue. Current fine: ${fine_amount:.2f}. "
                       f"Please return the book as soon as possible to avoid additional charges.",
                notification_type=NotificationTypeEnum.OVERDUE_REMINDER
            )
            
            db.add(notification)
            notifications_sent.append({
                "user_id": loan.user_id,
                "user_name": loan.user.full_name,
                "book_title": loan.book_copy.book.title,
                "days_overdue": days_overdue,
                "fine_amount": fine_amount
            })
    
    db.commit()
    return notifications_sent

def notify_hold_expiring(db: Session):
    """
    Notify users about expiring holds
    This would typically be run as a scheduled job
    """
    from datetime import timedelta
    
    # Get holds that will expire in 1 day
    tomorrow = datetime.utcnow() + timedelta(days=1)
    expiring_holds = db.query(Hold).filter(
        Hold.status == HoldStatusEnum.FULFILLED,
        Hold.expiry_date.between(datetime.utcnow(), tomorrow)
    ).all()
    
    notifications_sent = []
    
    for hold in expiring_holds:
        notification = Notification(
            user_id=hold.user_id,
            title="Hold Expiring Soon",
            message=f"Your reserved book '{hold.book.title}' will expire on "
                   f"{hold.expiry_date.strftime('%Y-%m-%d at %I:%M %p')}. "
                   f"Please visit the library to pick it up before it expires.",
            notification_type=NotificationTypeEnum.HOLD_EXPIRING
        )
        
        db.add(notification)
        notifications_sent.append({
            "user_id": hold.user_id,
            "user_name": hold.user.full_name,
            "book_title": hold.book.title,
            "expiry_date": hold.expiry_date
        })
    
    db.commit()
    return notifications_sent

def notify_fine_notice(db: Session, user_id: int, fine_amount: float, reason: str):
    """
    Send notification when a fine is issued
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        notification = Notification(
            user_id=user_id,
            title="Fine Notice",
            message=f"A fine of ${fine_amount:.2f} has been added to your account for: {reason}. "
                   f"Please pay your fines to continue borrowing books.",
            notification_type=NotificationTypeEnum.FINE_NOTICE
        )
        
        db.add(notification)
        db.commit()
        
        return {
            "user_id": user_id,
            "user_name": user.full_name,
            "fine_amount": fine_amount,
            "reason": reason
        }
    
    return None

def cleanup_old_notifications(db: Session, days_to_keep: int = 90):
    """
    Clean up old notifications to prevent database bloat
    Keep only notifications from the last X days
    """
    from datetime import timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
    
    old_notifications = db.query(Notification).filter(
        Notification.created_at < cutoff_date
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return old_notifications
