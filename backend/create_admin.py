"""Create initial admin user"""
from app import db, create_app
from app.models import User

app = create_app()
with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(email='admin@civicai.com').first()
    if admin:
        print('Admin already exists!')
    else:
        # Create admin
        admin = User(
            email='admin@civicai.com',
            name='System Administrator',
            phone='1234567890',
            role='admin',
            is_verified=True
        )
        admin.set_password('admin123')

        db.session.add(admin)
        db.session.commit()

        print('Admin user created!')
        print('Email: admin@civicai.com')
        print('Password: admin123')
