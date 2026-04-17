"""
Application Entry Point
"""

import os
from app import create_app
from app import db
from app.models import User, Complaint, Vendor, GovernmentBody

# Get configuration
config_name = os.environ.get('FLASK_ENV', 'development')

# Create application
app = create_app(config_name)


@app.shell_context_processor
def make_shell_context():
    """Make database models available in shell"""
    return {
        'db': db,
        'User': User,
        'Complaint': Complaint,
        'Vendor': Vendor,
        'GovernmentBody': GovernmentBody
    }


@app.cli.command()
def init_db():
    """Initialize database"""
    db.create_all()
    print('Database initialized!')


@app.cli.command()
def create_admin():
    """Create initial admin user"""
    from werkzeug.security import generate_password_hash

    # Check if admin exists
    admin = User.query.filter_by(email='admin@civicai.com').first()
    if admin:
        print('Admin user already exists')
        return

    # Create admin
    admin = User(
        email='admin@civicai.com',
        name='System Administrator',
        phone='1234567890',
        role='admin',
        is_verified=True
    )
    admin.set_password('admin123')  # Change this in production!

    db.session.add(admin)
    db.session.commit()

    print('Admin user created:')
    print('  Email: admin@civicai.com')
    print('  Password: admin123')
    print('  Please change the password immediately!')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
