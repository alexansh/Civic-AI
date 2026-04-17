"""
Complaint Model - Handles public and personal complaints
"""

from datetime import datetime
from enum import Enum
from app import db
import json


class ComplaintType(Enum):
    PUBLIC = 'public'
    PERSONAL = 'personal'


class ComplaintStatus(Enum):
    SUBMITTED = 'submitted'
    UNDER_REVIEW = 'under_review'
    ASSIGNED = 'assigned'
    IN_PROGRESS = 'in_progress'
    PENDING_APPROVAL = 'pending_approval'  # For personal - waiting user approval
    RESOLVED = 'resolved'
    REJECTED = 'rejected'
    CLOSED = 'closed'


class Priority(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class Complaint(db.Model):
    """Complaint model for both public and personal issues"""

    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    complaint_type = db.Column(db.String(20), nullable=False, index=True)  # public or personal
    category = db.Column(db.String(50), nullable=False, index=True)  # pothole, electrical, plumbing, etc.
    subcategory = db.Column(db.String(100))

    # Location information
    location_address = db.Column(db.String(300))
    location_latitude = db.Column(db.Float)
    location_longitude = db.Column(db.Float)
    landmark = db.Column(db.String(200))

    # Images
    images = db.Column(db.Text)  # JSON array of image URLs

    # Status and priority
    status = db.Column(db.String(30), default=ComplaintStatus.SUBMITTED.value, index=True)
    priority = db.Column(db.String(20), default=Priority.MEDIUM.value, index=True)
    priority_score = db.Column(db.Float)  # AI-calculated priority score (0-100)

    # User and assignment
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    assigned_to_type = db.Column(db.String(20))  # vendor or government
    assigned_to_id = db.Column(db.Integer)  # ID of vendor or government body

    # AI classification
    ai_classified = db.Column(db.Boolean, default=False)
    ai_classification_confidence = db.Column(db.Float)
    ai_detected_category = db.Column(db.String(50))
    ai_predicted_priority = db.Column(db.String(20))

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    sla_deadline = db.Column(db.DateTime)  # Expected resolution time

    # Additional info
    severity_level = db.Column(db.Integer)  # 1-5 scale
    affected_people_count = db.Column(db.Integer)  # For public complaints
    estimated_cost = db.Column(db.Float)  # For personal complaints

    # Relationships
    status_history = db.relationship('StatusHistory', backref='complaint', lazy=True, cascade='all, delete-orphan')
    estimate = db.relationship('Estimate', backref='complaint', uselist=False, lazy=True)
    rating = db.relationship('Rating', backref='complaint_rating', uselist=False, lazy=True)

    # For public complaints - government assignment
    government_body_id = db.Column(db.Integer, db.ForeignKey('government_bodies.id'))

    # For personal complaints - vendor assignment
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))

    def set_images(self, image_list):
        """Set images as JSON string"""
        self.images = json.dumps(image_list)

    def get_images(self):
        """Get images as list"""
        return json.loads(self.images) if self.images else []

    def add_image(self, image_url):
        """Add image to list"""
        images = self.get_images()
        images.append(image_url)
        self.set_images(images)

    def get_category_display(self):
        """Get display name for category"""
        categories = {
            'pothole': 'Pothole',
            'street_light': 'Street Light',
            'garbage': 'Garbage/Sanitation',
            'water': 'Water Supply',
            'electrical': 'Electrical',
            'plumbing': 'Plumbing',
            'carpentry': 'Carpentry',
            'painting': 'Painting',
            'cleaning': 'Cleaning',
            'gardening': 'Gardening',
            'other': 'Other'
        }
        return categories.get(self.category, self.category)

    def to_dict(self, include_details=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'complaint_type': self.complaint_type,
            'category': self.category,
            'category_display': self.get_category_display(),
            'subcategory': self.subcategory,
            'location': {
                'address': self.location_address,
                'latitude': self.location_latitude,
                'longitude': self.location_longitude,
                'landmark': self.landmark
            },
            'images': self.get_images(),
            'status': self.status,
            'priority': self.priority,
            'priority_score': self.priority_score,
            'user_id': self.user_id,
            'assigned_to_type': self.assigned_to_type,
            'assigned_to_id': self.assigned_to_id,
            'ai_classified': self.ai_classified,
            'ai_confidence': self.ai_classification_confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'sla_deadline': self.sla_deadline.isoformat() if self.sla_deadline else None,
            'severity_level': self.severity_level,
            'affected_people_count': self.affected_people_count,
            'estimated_cost': self.estimated_cost
        }

        if include_details:
            data['status_history'] = [sh.to_dict() for sh in self.status_history]
            if self.estimate:
                data['estimate'] = self.estimate.to_dict()
            if self.rating:
                data['rating'] = self.rating.to_dict()

        return data

    def __repr__(self):
        return f'<Complaint {self.title} ({self.complaint_type})>'


class StatusHistory(db.Model):
    """Track complaint status changes"""

    __tablename__ = 'status_history'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    old_status = db.Column(db.String(30))
    new_status = db.Column(db.String(30), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    changed_by_user = db.relationship('User', backref='status_changes')

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'complaint_id': self.complaint_id,
            'old_status': self.old_status,
            'new_status': self.new_status,
            'changed_by': self.changed_by,
            'changed_by_name': self.changed_by_user.name if self.changed_by_user else 'System',
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<StatusHistory {self.complaint_id}: {self.old_status} → {self.new_status}>'


class Estimate(db.Model):
    """Cost estimate for personal complaints"""

    __tablename__ = 'estimates'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False, unique=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)

    # Cost breakdown
    labor_cost = db.Column(db.Float, nullable=False)
    material_cost = db.Column(db.Float, default=0.0)
    total_cost = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)  # Detailed breakdown

    # Status
    status = db.Column(db.String(20), default='pending', index=True)  # pending, accepted, rejected
    user_approved = db.Column(db.Boolean, default=False)

    # Validity
    valid_until = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'complaint_id': self.complaint_id,
            'vendor_id': self.vendor_id,
            'labor_cost': self.labor_cost,
            'material_cost': self.material_cost,
            'total_cost': self.total_cost,
            'description': self.description,
            'status': self.status,
            'user_approved': self.user_approved,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Estimate {self.complaint_id}: ${self.total_cost}>'


class Rating(db.Model):
    """Ratings and reviews"""

    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False, unique=True)
    rater_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Rating target (could be vendor or government body)
    target_type = db.Column(db.String(20))  # vendor or government
    target_id = db.Column(db.Integer, nullable=False)

    # Rating details
    rating = db.Column(db.Float, nullable=False)  # 1-5
    review_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    vendor_review_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))
    government_review_id = db.Column(db.Integer, db.ForeignKey('government_bodies.id'))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'complaint_id': self.complaint_id,
            'rater_id': self.rater_id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'rating': self.rating,
            'review_text': self.review_text,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Rating {self.rating}/5 for {self.target_type} {self.target_id}>'
