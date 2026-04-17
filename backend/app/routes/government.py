"""
Government Body Routes - Government-specific operations
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Complaint, GovernmentBody, StatusHistory
from app.middleware.auth import get_current_user
from app.utils.helpers import create_notification
from datetime import datetime

government_bp = Blueprint('government', __name__)


@government_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def government_dashboard():
    """Get government dashboard data"""
    user = get_current_user()
    if not user or not user.government_profile:
        return jsonify({'error': 'Government profile not found'}), 404

    gov = user.government_profile

    # Get complaint statistics
    assigned = Complaint.query.filter_by(
        government_body_id=gov.id,
        status='assigned'
    ).count()

    in_progress = Complaint.query.filter_by(
        government_body_id=gov.id,
        status='in_progress'
    ).count()

    resolved = Complaint.query.filter_by(
        government_body_id=gov.id,
        status='resolved'
    ).count()

    overdue = Complaint.query.filter(
        Complaint.government_body_id == gov.id,
        Complaint.status != 'resolved',
        Complaint.sla_deadline < datetime.utcnow()
    ).count()

    return jsonify({
        'department': gov.to_dict(),
        'stats': {
            'assigned': assigned,
            'in_progress': in_progress,
            'resolved': resolved,
            'overdue': overdue
        }
    }), 200


@government_bp.route('/complaints', methods=['GET'])
@jwt_required()
def get_assigned_complaints():
    """Get complaints assigned to this government body"""
    user = get_current_user()
    if not user or not user.government_profile:
        return jsonify({'error': 'Government profile not found'}), 404

    gov = user.government_profile

    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    priority = request.args.get('priority')
    category = request.args.get('category')

    query = Complaint.query.filter_by(government_body_id=gov.id)

    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    if category:
        query = query.filter_by(category=category)

    # Order by priority (critical first) then by date
    priority_order = {
        'critical': 1,
        'high': 2,
        'medium': 3,
        'low': 4
    }

    complaints = query.order_by(
        Complaint.priority,
        Complaint.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'complaints': [c.to_dict(include_details=True) for c in complaints.items],
        'total': complaints.total,
        'page': page,
        'per_page': per_page,
        'pages': complaints.pages
    }), 200


@government_bp.route('/complaints/<int:complaint_id>', methods=['GET'])
@jwt_required()
def get_complaint_details(complaint_id):
    """Get complaint details"""
    user = get_current_user()
    if not user or not user.government_profile:
        return jsonify({'error': 'Government profile not found'}), 404

    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    if complaint.government_body_id != user.government_profile.id:
        return jsonify({'error': 'Unauthorized access'}), 403

    return jsonify({
        'complaint': complaint.to_dict(include_details=True)
    }), 200


@government_bp.route('/complaints/<int:complaint_id>/assign', methods=['POST'])
@jwt_required()
def assign_to_department(complaint_id):
    """Assign complaint to specific team/worker within department"""
    user = get_current_user()
    if not user or not user.government_profile:
        return jsonify({'error': 'Government profile not found'}), 404

    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    if complaint.complaint_type != 'public':
        return jsonify({'error': 'Can only assign public complaints'}), 400

    data = request.get_json()
    assigned_to_id = data.get('assigned_to_id')
    comment = data.get('comment', '')

    if not assigned_to_id:
        return jsonify({'error': 'assigned_to_id is required'}), 400

    old_status = complaint.status
    complaint.status = 'assigned'
    complaint.assigned_to_type = 'government'
    complaint.assigned_to_id = assigned_to_id

    # Create status history
    status_history = StatusHistory(
        complaint_id=complaint.id,
        old_status=old_status,
        new_status='assigned',
        changed_by=user.id,
        comment=comment or 'Assigned to department'
    )
    db.session.add(status_history)

    # Notify citizen
    create_notification(
        complaint.user_id,
        'Complaint Assigned',
        f'Your complaint "{complaint.title}" has been assigned to {user.government_profile.department_name}.',
        'success',
        complaint.id
    )

    try:
        db.session.commit()
        return jsonify({
            'message': 'Complaint assigned successfully',
            'complaint': complaint.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@government_bp.route('/complaints/<int:complaint_id>/start', methods=['POST'])
@jwt_required()
def start_work(complaint_id):
    """Mark complaint as in progress"""
    user = get_current_user()
    if not user or not user.government_profile:
        return jsonify({'error': 'Government profile not found'}), 404

    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    if complaint.status != 'assigned':
        return jsonify({'error': 'Complaint is not assigned'}), 400

    old_status = complaint.status
    complaint.status = 'in_progress'

    # Create status history
    status_history = StatusHistory(
        complaint_id=complaint.id,
        old_status=old_status,
        new_status='in_progress',
        changed_by=user.id,
        comment='Work started'
    )
    db.session.add(status_history)

    # Notify citizen
    create_notification(
        complaint.user_id,
        'Work Started',
        f'Work has started on your complaint "{complaint.title}".',
        'info',
        complaint.id
    )

    try:
        db.session.commit()
        return jsonify({
            'message': 'Work marked as in progress',
            'complaint': complaint.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@government_bp.route('/complaints/<int:complaint_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_complaint(complaint_id):
    """Mark complaint as resolved"""
    user = get_current_user()
    if not user or not user.government_profile:
        return jsonify({'error': 'Government profile not found'}), 404

    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    data = request.get_json()
    resolution_notes = data.get('resolution_notes', '')

    old_status = complaint.status
    complaint.status = 'resolved'
    complaint.resolved_at = datetime.utcnow()

    # Create status history
    status_history = StatusHistory(
        complaint_id=complaint.id,
        old_status=old_status,
        new_status='resolved',
        changed_by=user.id,
        comment=resolution_notes or 'Complaint resolved'
    )
    db.session.add(status_history)

    # Notify citizen
    create_notification(
        complaint.user_id,
        'Complaint Resolved',
        f'Your complaint "{complaint.title}" has been resolved. Please rate the service.',
        'success',
        complaint.id
    )

    try:
        db.session.commit()

        # Auto-close after 7 days if no feedback
        from flask import current_app
        # In a real system, you'd schedule this

        return jsonify({
            'message': 'Complaint resolved successfully',
            'complaint': complaint.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@government_bp.route('/complaints/<int:complaint_id>/reject', methods=['POST'])
@jwt_required()
def reject_complaint(complaint_id):
    """Reject a complaint (with reason)"""
    user = get_current_user()
    if not user or not user.government_profile:
        return jsonify({'error': 'Government profile not found'}), 404

    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    data = request.get_json()
    reason = data.get('reason', '')

    if not reason:
        return jsonify({'error': 'Rejection reason is required'}), 400

    old_status = complaint.status
    complaint.status = 'rejected'

    # Create status history
    status_history = StatusHistory(
        complaint_id=complaint.id,
        old_status=old_status,
        new_status='rejected',
        changed_by=user.id,
        comment=f'Rejected: {reason}'
    )
    db.session.add(status_history)

    # Notify citizen
    create_notification(
        complaint.user_id,
        'Complaint Rejected',
        f'Your complaint "{complaint.title}" has been rejected. Reason: {reason}',
        'error',
        complaint.id
    )

    try:
        db.session.commit()
        return jsonify({
            'message': 'Complaint rejected',
            'complaint': complaint.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@government_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """Get department statistics"""
    user = get_current_user()
    if not user or not user.government_profile:
        return jsonify({'error': 'Government profile not found'}), 404

    gov = user.government_profile

    from sqlalchemy import func

    # Total complaints by category
    category_stats = db.session.query(
        Complaint.category,
        func.count(Complaint.id)
    ).filter_by(
        government_body_id=gov.id
    ).group_by(Complaint.category).all()

    # Total complaints by status
    status_stats = db.session.query(
        Complaint.status,
        func.count(Complaint.id)
    ).filter_by(
        government_body_id=gov.id
    ).group_by(Complaint.status).all()

    # Total complaints by priority
    priority_stats = db.session.query(
        Complaint.priority,
        func.count(Complaint.id)
    ).filter_by(
        government_body_id=gov.id
    ).group_by(Complaint.priority).all()

    # Resolution time stats
    avg_resolution_days = db.session.query(
        func.avg(
            func.datediff(Complaint.resolved_at, Complaint.created_at)
        )
    ).filter_by(
        government_body_id=gov.id,
        status='resolved'
    ).scalar()

    return jsonify({
        'department': gov.to_dict(),
        'category_stats': [{'category': c[0], 'count': c[1]} for c in category_stats],
        'status_stats': [{'status': s[0], 'count': s[1]} for s in status_stats],
        'priority_stats': [{'priority': p[0], 'count': p[1]} for p in priority_stats],
        'avg_resolution_days': round(avg_resolution_days, 2) if avg_resolution_days else 0
    }), 200


@government_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_government_profile():
    """Get government profile"""
    user = get_current_user()
    if not user or not user.government_profile:
        return jsonify({'error': 'Government profile not found'}), 404

    return jsonify({
        'government': user.government_profile.to_dict()
    }), 200
