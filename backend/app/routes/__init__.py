"""
Routes Package
"""

from app.routes.auth import auth_bp
from app.routes.complaints import complaints_bp
from app.routes.vendor import vendor_bp
from app.routes.government import government_bp
from app.routes.admin import admin_bp
from app.routes.ai import ai_bp

__all__ = [
    'auth_bp',
    'complaints_bp',
    'vendor_bp',
    'government_bp',
    'admin_bp',
    'ai_bp'
]
