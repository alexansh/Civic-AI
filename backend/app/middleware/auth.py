"""
Authentication Middleware - JWT and Role-based Access Control
"""

from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.models import User


def jwt_required(fn):
    """Verify JWT token is present and valid"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        return fn(*args, **kwargs)
    return wrapper


from flask_jwt_extended import jwt_required as jwt_required_original

def admin_required(fn):
    """Require admin role"""
    @wraps(fn)
    @jwt_required_original()
    def wrapper(*args, **kwargs):
        current_user = get_current_user()
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper


def citizen_required(fn):
    """Require citizen role"""
    @wraps(fn)
    @jwt_required
    def wrapper(*args, **kwargs):
        current_user = get_current_user()
        if not current_user or current_user.role != 'citizen':
            return jsonify({'error': 'Citizen access required'}), 403
        return fn(*args, **kwargs)
    return wrapper


def vendor_required(fn):
    """Require vendor role"""
    @wraps(fn)
    @jwt_required
    def wrapper(*args, **kwargs):
        current_user = get_current_user()
        if not current_user or current_user.role != 'vendor':
            return jsonify({'error': 'Vendor access required'}), 403
        return fn(*args, **kwargs)
    return wrapper


def government_required(fn):
    """Require government role"""
    @wraps(fn)
    @jwt_required
    def wrapper(*args, **kwargs):
        current_user = get_current_user()
        if not current_user or current_user.role != 'government':
            return jsonify({'error': 'Government access required'}), 403
        return fn(*args, **kwargs)
    return wrapper


def get_current_user():
    """Get current user from JWT token"""
    try:
        user_id = get_jwt_identity()
        # Convert to int if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)
        user = User.query.get(user_id)
        return user
    except Exception:
        return None


def optional_jwt_required(fn):
    """Optional JWT - doesn't fail if token is missing"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
        except Exception:
            pass
        return fn(*args, **kwargs)
    return wrapper
