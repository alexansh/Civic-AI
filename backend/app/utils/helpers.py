"""
Helper Utilities
"""

import math
from datetime import datetime, timedelta
from app.models import Notification
from app import db


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS coordinates using Haversine formula"""
    if None in [lat1, lon1, lat2, lon2]:
        return float('inf')

    R = 6371  # Earth's radius in kilometers

    lat1 = math.radians(float(lat1))
    lat2 = math.radians(float(lat2))
    dlat = math.radians(float(lat2) - float(lat1))
    dlon = math.radians(float(lon2) - float(lon1))

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    return R * c


def create_notification(user_id, title, message, notification_type='info', related_complaint_id=None):
    """Create a notification for a user"""
    try:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            related_complaint_id=related_complaint_id
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    except Exception as e:
        db.session.rollback()
        print(f"Error creating notification: {e}")
        return None


def generate_sla_deadline(priority, complaint_type='public'):
    """Generate SLA deadline based on priority"""
    now = datetime.utcnow()

    # SLA deadlines in days
    sla_map = {
        'critical': 1,
        'high': 3,
        'medium': 7,
        'low': 14
    }

    days = sla_map.get(priority, 7)
    return now + timedelta(days=days)


def formatFileSize(size_bytes):
    """Format file size"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def calculate_priority_score(severity, affected_count, complaint_type):
    """Calculate priority score (0-100) based on factors"""
    # Base score from severity (1-5)
    severity_scores = {1: 10, 2: 30, 3: 50, 4: 70, 5: 90}
    base_score = severity_scores.get(severity, 50)

    # Add points for affected people
    if affected_count:
        if affected_count > 100:
            base_score += 10
        elif affected_count > 50:
            base_score += 5

    # Public complaints get slightly higher priority
    if complaint_type == 'public':
        base_score += 5

    # Cap at 100
    return min(base_score, 100)


def determine_priority_from_score(score):
    """Determine priority label from score"""
    if score >= 80:
        return 'critical'
    elif score >= 60:
        return 'high'
    elif score >= 40:
        return 'medium'
    else:
        return 'low'


def calculate_vendor_rating(vendor):
    """Calculate vendor's average rating"""
    from app.models import Rating

    ratings = Rating.query.filter_by(
        target_type='vendor',
        target_id=vendor.id
    ).all()

    if not ratings:
        return 0.0

    total = sum(r.rating for r in ratings)
    return round(total / len(ratings), 2)


def paginate_query(query, page, per_page=20):
    """Paginate a SQLAlchemy query"""
    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
