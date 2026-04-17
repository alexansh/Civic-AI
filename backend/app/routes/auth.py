"""
Authentication Routes - Login, Register, Profile Management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User, Vendor, GovernmentBody
from app.middleware.auth import get_current_user
from app.utils.validators import validate_email, validate_password
from app.utils.helpers import create_notification
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()

    # Validate required fields
    required_fields = ['email', 'password', 'name', 'phone', 'role']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    # Validate email format
    if not validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400

    # Validate password strength
    if not validate_password(data['password']):
        return jsonify({'error': 'Password must be at least 8 characters with one uppercase, one lowercase, and one number'}), 400

    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409

    # Validate role
    valid_roles = ['citizen', 'vendor', 'government']
    if data['role'] not in valid_roles:
        return jsonify({'error': f'Invalid role. Must be one of: {valid_roles}'}), 400

    try:
        # Create user
        user = User(
            email=data['email'],
            name=data['name'],
            phone=data['phone'],
            role=data['role'],
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            pincode=data.get('pincode')
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.flush()  # Get user ID

        # Create role-specific profile
        if data['role'] == 'vendor':
            vendor = Vendor(
                user_id=user.id,
                business_name=data.get('business_name', ''),
                category=data.get('category', 'other'),
                subcategories=data.get('subcategories'),
                experience_years=data.get('experience_years'),
                license_number=data.get('license_number'),
                base_service_charge=data.get('base_service_charge', 0),
                service_radius_km=data.get('service_radius_km', 10.0),
                latitude=data.get('latitude'),
                longitude=data.get('longitude')
            )
            db.session.add(vendor)

        elif data['role'] == 'government':
            gov_body = GovernmentBody(
                user_id=user.id,
                department_name=data.get('department_name', ''),
                department_type=data.get('department_type', 'municipal'),
                jurisdiction_area=data.get('jurisdiction_area'),
                jurisdiction_categories=data.get('jurisdiction_categories'),
                office_address=data.get('office_address'),
                contact_number=data.get('contact_number'),
                email_official=data.get('email_official'),
                latitude=data.get('latitude'),
                longitude=data.get('longitude')
            )
            db.session.add(gov_body)

        db.session.commit()

        # Create access token
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role},
            expires_delta=timedelta(days=1)
        )

        return jsonify({
            'message': 'Registration successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()

    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403

    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    # Create access token
    access_token = create_access_token(
        identity=user.id,
        additional_claims={'role': user.role},
        expires_delta=timedelta(days=1)
    )

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'user': user.to_dict(include_details=True)}), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()

    # Update basic fields
    if 'name' in data:
        user.name = data['name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'address' in data:
        user.address = data['address']
    if 'city' in data:
        user.city = data['city']
    if 'state' in data:
        user.state = data['state']
    if 'pincode' in data:
        user.pincode = data['pincode']

    # Update role-specific profiles
    if user.role == 'vendor' and user.vendor_profile:
        vendor_data = data.get('vendor_info', {})
        if 'business_name' in vendor_data:
            user.vendor_profile.business_name = vendor_data['business_name']
        if 'category' in vendor_data:
            user.vendor_profile.category = vendor_data['category']
        if 'subcategories' in vendor_data:
            user.vendor_profile.subcategories = vendor_data['subcategories']
        if 'experience_years' in vendor_data:
            user.vendor_profile.experience_years = vendor_data['experience_years']
        if 'base_service_charge' in vendor_data:
            user.vendor_profile.base_service_charge = vendor_data['base_service_charge']
        if 'service_radius_km' in vendor_data:
            user.vendor_profile.service_radius_km = vendor_data['service_radius_km']
        if 'is_available' in vendor_data:
            user.vendor_profile.is_available = vendor_data['is_available']

    elif user.role == 'government' and user.government_profile:
        gov_data = data.get('government_info', {})
        if 'department_name' in gov_data:
            user.government_profile.department_name = gov_data['department_name']
        if 'jurisdiction_area' in gov_data:
            user.government_profile.jurisdiction_area = gov_data['jurisdiction_area']
        if 'contact_number' in gov_data:
            user.government_profile.contact_number = gov_data['contact_number']

    try:
        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict(include_details=True)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()

    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current and new passwords are required'}), 400

    if not user.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 401

    if not validate_password(data['new_password']):
        return jsonify({'error': 'New password must be at least 8 characters with one uppercase, one lowercase, and one number'}), 400

    user.set_password(data['new_password'])
    db.session.commit()

    return jsonify({'message': 'Password changed successfully'}), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client should discard token)"""
    # Note: With JWT, logout is typically handled client-side by discarding the token
    return jsonify({'message': 'Logout successful'}), 200
