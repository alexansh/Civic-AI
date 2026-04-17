"""
User Model - Handles all user roles and authentication
"""

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db


class User(db.Model):
    """User model for all roles in the system"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)  # admin, citizen, vendor, government
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    pincode = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Role-specific relationships
    vendor_profile = db.relationship('Vendor', backref='user', uselist=False, lazy=True)
    government_profile = db.relationship('GovernmentBody', backref='user', uselist=False, lazy=True)
    complaints_raised = db.relationship('Complaint', backref='citizen', lazy=True, foreign_keys='Complaint.user_id')
    ratings_given = db.relationship('Rating', backref='rater', lazy=True, foreign_keys='Rating.rater_id')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)

    def get_role_display_name(self):
        """Get display name for role"""
        role_names = {
            'admin': 'Administrator',
            'citizen': 'Citizen',
            'vendor': 'Service Provider',
            'government': 'Government Body'
        }
        return role_names.get(self.role, self.role)

    def to_dict(self):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'role': self.role,
            'role_display': self.get_role_display_name(),
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'pincode': self.pincode,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if self.vendor_profile:
            data['vendor_info'] = self.vendor_profile.to_dict()

        if self.government_profile:
            data['government_info'] = self.government_profile.to_dict()

        return data

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class Vendor(db.Model):
    """Vendor/Service Provider profile"""

    __tablename__ = 'vendors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    business_name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)  # electrician, plumber, etc.
    subcategories = db.Column(db.Text)  # JSON array of specialized services
    experience_years = db.Column(db.Integer)
    license_number = db.Column(db.String(50))
    license_verified = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    total_jobs_completed = db.Column(db.Integer, default=0)
    base_service_charge = db.Column(db.Float)
    is_available = db.Column(db.Boolean, default=True)
    service_radius_km = db.Column(db.Float, default=10.0)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    reviews = db.relationship('Rating', backref='vendor_review', lazy=True)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'business_name': self.business_name,
            'category': self.category,
            'subcategories': self.subcategories,
            'experience_years': self.experience_years,
            'license_number': self.license_number,
            'license_verified': self.license_verified,
            'rating': self.rating,
            'total_reviews': self.total_reviews,
            'total_jobs_completed': self.total_jobs_completed,
            'base_service_charge': self.base_service_charge,
            'is_available': self.is_available,
            'service_radius_km': self.service_radius_km,
            'location': {
                'latitude': self.latitude,
                'longitude': self.longitude
            } if self.latitude and self.longitude else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Vendor {self.business_name}>'


class GovernmentBody(db.Model):
    """Government Department/Municipal Body profile"""

    __tablename__ = 'government_bodies'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    department_name = db.Column(db.String(150), nullable=False)
    department_type = db.Column(db.String(50), nullable=False)  # municipal, state, central
    jurisdiction_area = db.Column(db.String(200))  # Area/region they cover
    jurisdiction_categories = db.Column(db.Text)  # JSON array of responsible categories
    office_address = db.Column(db.Text)
    contact_number = db.Column(db.String(20))
    email_official = db.Column(db.String(120))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    is_active_dept = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    assigned_complaints = db.relationship('Complaint', backref='department', lazy=True)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'department_name': self.department_name,
            'department_type': self.department_type,
            'jurisdiction_area': self.jurisdiction_area,
            'jurisdiction_categories': self.jurisdiction_categories,
            'office_address': self.office_address,
            'contact_number': self.contact_number,
            'email_official': self.email_official,
            'location': {
                'latitude': self.latitude,
                'longitude': self.longitude
            } if self.latitude and self.longitude else None,
            'is_active_dept': self.is_active_dept,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<GovernmentBody {self.department_name}>'
