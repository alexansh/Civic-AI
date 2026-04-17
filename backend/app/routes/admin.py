"""
Admin Routes - Admin-specific operations
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import User, Vendor, GovernmentBody, Complaint, AuditLog, Rating
from app.middleware.auth import admin_required, get_current_user
from app.utils.helpers import create_notification
from datetime import datetime

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    """Get admin dashboard data"""
    # User statistics
    total_users = User.query.count()
    citizens = User.query.filter_by(role='citizen').count()
    vendors = User.query.filter_by(role='vendor').count()
    government_users = User.query.filter_by(role='government').count()

    # Complaint statistics
    total_complaints = Complaint.query.count()
    public_complaints = Complaint.query.filter_by(complaint_type='public').count()
    personal_complaints = Complaint.query.filter_by(complaint_type='personal').count()

    # Status breakdown
    submitted = Complaint.query.filter_by(status='submitted').count()
    in_progress = Complaint.query.filter_by(status='in_progress').count()
    resolved = Complaint.query.filter_by(status='resolved').count()
    overdue = Complaint.query.filter(
        Complaint.status != 'resolved',
        Complaint.sla_deadline < datetime.utcnow()
    ).count()

    # Vendor statistics
    verified_vendors = Vendor.query.filter_by(license_verified=True).count()
    pending_verification = Vendor.query.filter_by(license_verified=False).count()

    # Government department statistics
    active_departments = GovernmentBody.query.filter_by(is_active_dept=True).count()

    return jsonify({
        'users': {
            'total': total_users,
            'citizens': citizens,
            'vendors': vendors,
            'government': government_users
        },
        'complaints': {
            'total': total_complaints,
            'public': public_complaints,
            'personal': personal_complaints,
            'submitted': submitted,
            'in_progress': in_progress,
            'resolved': resolved,
            'overdue': overdue
        },
        'vendors': {
            'verified': verified_vendors,
            'pending_verification': pending_verification
        },
        'departments': {
            'active': active_departments
        }
    }), 200


@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role = request.args.get('role')
    is_verified = request.args.get('is_verified')

    query = User.query

    if role:
        query = query.filter_by(role=role)
    if is_verified is not None:
        query = query.filter_by(is_verified=is_verified == 'true')

    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'users': [u.to_dict() for u in users.items],
        'total': users.total,
        'page': page,
        'per_page': per_page,
        'pages': users.pages
    }), 200


@admin_bp.route('/users/<int:user_id>/verify', methods=['POST'])
@admin_required
def verify_user(user_id):
    """Verify a user (especially vendors)"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.is_verified = True

    # If vendor, verify their license
    if user.role == 'vendor' and user.vendor_profile:
        data = request.get_json()
        if data and data.get('license_verified'):
            user.vendor_profile.license_verified = True

    create_notification(
        user.id,
        'Account Verified',
        'Your account has been verified by the administrator.',
        'success'
    )

    try:
        db.session.commit()
        return jsonify({'message': 'User verified successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/<int:user_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_user(user_id):
    """Deactivate a user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    reason = data.get('reason', '') if data else ''

    user.is_active = False

    create_notification(
        user.id,
        'Account Deactivated',
        f'Your account has been deactivated. Reason: {reason}',
        'error'
    )

    try:
        db.session.commit()
        return jsonify({'message': 'User deactivated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/vendors', methods=['GET'])
@admin_required
def get_vendors():
    """Get all vendors with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category')
    verified = request.args.get('verified')

    query = Vendor.query

    if category:
        query = query.filter_by(category=category)
    if verified is not None:
        query = query.filter_by(license_verified=verified == 'true')

    vendors = query.order_by(Vendor.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'vendors': [v.to_dict() for v in vendors.items],
        'total': vendors.total,
        'page': page,
        'per_page': per_page,
        'pages': vendors.pages
    }), 200


@admin_bp.route('/vendors/<int:vendor_id>/verify-license', methods=['POST'])
@admin_required
def verify_vendor_license(vendor_id):
    """Verify vendor license"""
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return jsonify({'error': 'Vendor not found'}), 404

    data = request.get_json()
    verified = data.get('verified', True)

    vendor.license_verified = verified

    # Notify vendor
    if vendor.user:
        status = 'verified' if verified else 'rejected'
        create_notification(
            vendor.user_id,
            f'License {status.title()}',
            f'Your vendor license has been {status}.',
            'success' if verified else 'error'
        )

    try:
        db.session.commit()
        return jsonify({'message': f'License {"verified" if verified else "rejected"} successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/government-bodies', methods=['GET'])
@admin_required
def get_government_bodies():
    """Get all government bodies"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    gov_bodies = GovernmentBody.query.order_by(
        GovernmentBody.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'government_bodies': [g.to_dict() for g in gov_bodies.items],
        'total': gov_bodies.total,
        'page': page,
        'per_page': per_page,
        'pages': gov_bodies.pages
    }), 200


@admin_bp.route('/government-bodies', methods=['POST'])
@admin_required
def create_government_body():
    """Create a new government body"""
    data = request.get_json()

    # Validate required fields
    required = ['email', 'password', 'name', 'phone', 'department_name']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    try:
        # Create user
        user = User(
            email=data['email'],
            name=data['name'],
            phone=data['phone'],
            role='government',
            is_verified=True
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()

        # Create government body
        gov_body = GovernmentBody(
            user_id=user.id,
            department_name=data['department_name'],
            department_type=data.get('department_type', 'municipal'),
            jurisdiction_area=data.get('jurisdiction_area'),
            jurisdiction_categories=data.get('jurisdiction_categories'),
            office_address=data.get('office_address'),
            contact_number=data.get('contact_number'),
            email_official=data.get('email_official'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            is_active_dept=True
        )
        db.session.add(gov_body)
        db.session.commit()

        create_notification(
            user.id,
            'Account Created',
            'Your government account has been created by the administrator.',
            'success'
        )

        return jsonify({
            'message': 'Government body created successfully',
            'government': gov_body.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/complaints', methods=['GET'])
@admin_required
def get_all_complaints():
    """Get all complaints with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    complaint_type = request.args.get('complaint_type')
    priority = request.args.get('priority')
    category = request.args.get('category')

    query = Complaint.query

    if status:
        query = query.filter_by(status=status)
    if complaint_type:
        query = query.filter_by(complaint_type=complaint_type)
    if priority:
        query = query.filter_by(priority=priority)
    if category:
        query = query.filter_by(category=category)

    complaints = query.order_by(Complaint.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'complaints': [c.to_dict(include_details=True) for c in complaints.items],
        'total': complaints.total,
        'page': page,
        'per_page': per_page,
        'pages': complaints.pages
    }), 200


@admin_bp.route('/complaints/<int:complaint_id>/assign', methods=['PUT'])
@admin_required
def admin_assign_complaint(complaint_id):
    """Admin manually assign complaint"""
    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    data = request.get_json()
    assigned_to_type = data.get('assigned_to_type')  # vendor or government
    assigned_to_id = data.get('assigned_to_id')

    if not assigned_to_type or not assigned_to_id:
        return jsonify({'error': 'assigned_to_type and assigned_to_id are required'}), 400

    old_status = complaint.status
    complaint.status = 'assigned'
    complaint.assigned_to_type = assigned_to_type
    complaint.assigned_to_id = assigned_to_id

    if assigned_to_type == 'government':
        complaint.government_body_id = assigned_to_id
    elif assigned_to_type == 'vendor':
        complaint.vendor_id = assigned_to_id

    # Create status history
    status_history = StatusHistory(
        complaint_id=complaint.id,
        old_status=old_status,
        new_status='assigned',
        comment=f'Manually assigned by admin to {assigned_to_type} {assigned_to_id}'
    )
    db.session.add(status_history)

    try:
        db.session.commit()
        return jsonify({'message': 'Complaint assigned successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/audit-logs', methods=['GET'])
@admin_required
def get_audit_logs():
    """Get audit logs"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    user_id = request.args.get('user_id')
    entity_type = request.args.get('entity_type')

    query = AuditLog.query

    if user_id:
        query = query.filter_by(user_id=user_id)
    if entity_type:
        query = query.filter_by(entity_type=entity_type)

    logs = query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'audit_logs': [log.to_dict() for log in logs.items],
        'total': logs.total,
        'page': page,
        'per_page': per_page,
        'pages': logs.pages
    }), 200


@admin_bp.route('/statistics', methods=['GET'])
@admin_required
def get_platform_statistics():
    """Get comprehensive platform statistics"""
    from sqlalchemy import func

    # Complaints by type over time (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    complaints_by_day = db.session.query(
        func.date(Complaint.created_at),
        func.count(Complaint.id)
    ).filter(
        Complaint.created_at >= thirty_days_ago
    ).group_by(
        func.date(Complaint.created_at)
    ).all()

    # Top categories
    top_categories = db.session.query(
        Complaint.category,
        func.count(Complaint.id)
    ).group_by(
        Complaint.category
    ).order_by(
        func.count(Complaint.id).desc()
    ).limit(10).all()

    # Average resolution time by priority
    avg_resolution = db.session.query(
        Complaint.priority,
        func.avg(
            func.datediff(Complaint.resolved_at, Complaint.created_at)
        )
    ).filter_by(
        status='resolved'
    ).group_by(
        Complaint.priority
    ).all()

    return jsonify({
        'complaints_by_day': [
            {'date': str(d[0]), 'count': d[1]}
            for d in complaints_by_day
        ],
        'top_categories': [
            {'category': c[0], 'count': c[1]}
            for c in top_categories
        ],
        'avg_resolution_by_priority': [
            {'priority': r[0], 'avg_days': round(r[1], 2) if r[1] else 0}
            for r in avg_resolution
        ]
    }), 200
