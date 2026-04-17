"""
Validation Utilities
"""

import re
from datetime import datetime


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True


def validate_phone(phone):
    """Validate phone number"""
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None


def validate_coordinates(lat, lng):
    """Validate GPS coordinates"""
    if lat is None or lng is None:
        return False
    try:
        lat = float(lat)
        lng = float(lng)
        return -90 <= lat <= 90 and -180 <= lng <= 180
    except (ValueError, TypeError):
        return False


def validate_date_format(date_string, format='%Y-%m-%d'):
    """Validate date format"""
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False


def validate_complaint_input(data):
    """Validate complaint submission data"""
    errors = []

    if not data.get('title') or len(data['title'].strip()) < 5:
        errors.append('Title must be at least 5 characters')

    if not data.get('description') or len(data['description'].strip()) < 10:
        errors.append('Description must be at least 10 characters')

    if not data.get('category'):
        errors.append('Category is required')

    valid_categories = [
        'pothole', 'street_light', 'garbage', 'water',
        'electrical', 'plumbing', 'carpentry', 'painting',
        'cleaning', 'gardening', 'other'
    ]
    if data.get('category') and data['category'] not in valid_categories:
        errors.append(f'Invalid category. Must be one of: {valid_categories}')

    valid_types = ['public', 'personal']
    if data.get('complaint_type') and data['complaint_type'] not in valid_types:
        errors.append(f'Invalid complaint type. Must be one of: {valid_types}')

    return errors
