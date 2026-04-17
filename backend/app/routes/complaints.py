"""
Complaint Routes - CRUD operations for complaints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Complaint, StatusHistory, User, Vendor, GovernmentBody, Estimate, Rating
from app.middleware.auth import get_current_user
from app.utils.validators import validate_complaint_input, validate_coordinates
from app.utils.helpers import (
    create_notification,
    generate_sla_deadline,
    calculate_priority_score,
    determine_priority_from_score
)
from app.services.complaint_service import route_complaint, find_nearby_vendors
from datetime import datetime

complaints_bp = Blueprint('complaints', __name__)


@complaints_bp.route('/', methods=['POST'])
@jwt_required()
def create_complaint():
    """Submit a new complaint"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()

    # Validate input
    errors = validate_complaint_input(data)
    if errors:
        return jsonify({'errors': errors}), 400

    try:
        # Create complaint
        complaint = Complaint(
            title=data['title'],
            description=data['description'],
            complaint_type=data.get('complaint_type', 'public'),
            category=data['category'],
            subcategory=data.get('subcategory'),
            location_address=data.get('location_address'),
            location_latitude=data.get('location_latitude'),
            location_longitude=data.get('location_longitude'),
            landmark=data.get('landmark'),
            user_id=user.id,
            severity_level=data.get('severity_level', 3),
            affected_people_count=data.get('affected_people_count', 1)
        )

        # Handle images
        if data.get('images'):
            complaint.set_images(data['images'])

        # Calculate priority
        priority_score = calculate_priority_score(
            complaint.severity_level,
            complaint.affected_people_count,
            complaint.complaint_type
        )
        complaint.priority_score = priority_score
        complaint.priority = determine_priority_from_score(priority_score)

        # Generate SLA deadline
        complaint.sla_deadline = generate_sla_deadline(complaint.priority)

        db.session.add(complaint)
        db.session.flush()

        # Create initial status history
        status_history = StatusHistory(
            complaint_id=complaint.id,
            old_status=None,
            new_status='submitted',
            changed_by=user.id,
            comment='Complaint submitted'
        )
        db.session.add(status_history)

        # Route complaint
        route_complaint(complaint)

        # Create notification for user
        create_notification(
            user.id,
            'Complaint Submitted',
            f'Your complaint "{complaint.title}" has been submitted successfully.',
            'success',
            complaint.id
        )

        # Notify assigned entity if any
        if complaint.assigned_to_type == 'government' and complaint.assigned_to_id:
            gov = GovernmentBody.query.get(complaint.assigned_to_id)
            if gov:
                create_notification(
                    gov.user_id,
                    'New Complaint Assigned',
                    f'Complaint "{complaint.title}" has been assigned to your department.',
                    'warning',
                    complaint.id
                )

        db.session.commit()

        return jsonify({
            'message': 'Complaint created successfully',
            'complaint': complaint.to_dict(include_details=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@complaints_bp.route('/', methods=['GET'])
@jwt_required()
def get_complaints():
    """Get complaints with filtering"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    complaint_type = request.args.get('complaint_type')
    category = request.args.get('category')
    priority = request.args.get('priority')

    # Base query
    query = Complaint.query

    # Filter by user role
    if user.role == 'citizen':
        query = query.filter_by(user_id=user.id)
    elif user.role == 'vendor':
        if user.vendor_profile:
            query = query.filter_by(vendor_id=user.vendor_profile.id)
    elif user.role == 'government':
        if user.government_profile:
            query = query.filter_by(government_body_id=user.government_profile.id)
    # Admin can see all complaints

    # Apply filters
    if status:
        query = query.filter_by(status=status)
    if complaint_type:
        query = query.filter_by(complaint_type=complaint_type)
    if category:
        query = query.filter_by(category=category)
    if priority:
        query = query.filter_by(priority=priority)

    # Order by creation date (newest first)
    query = query.order_by(Complaint.created_at.desc())

    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    complaints = pagination.items

    return jsonify({
        'complaints': [c.to_dict() for c in complaints],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200


@complaints_bp.route('/<int:complaint_id>', methods=['GET'])
@jwt_required()
def get_complaint(complaint_id):
    """Get complaint details"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    # Check authorization
    if user.role == 'citizen' and complaint.user_id != user.id:
        return jsonify({'error': 'Unauthorized access'}), 403

    return jsonify({
        'complaint': complaint.to_dict(include_details=True)
    }), 200


@complaints_bp.route('/<int:complaint_id>', methods=['PUT'])
@jwt_required()
def update_complaint(complaint_id):
    """Update complaint"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    # Only citizen who raised it or admin can update
    if user.role == 'citizen' and complaint.user_id != user.id:
        return jsonify({'error': 'Unauthorized access'}), 403

    # Can only update if status is submitted or under_review
    if complaint.status not in ['submitted', 'under_review']:
        return jsonify({'error': 'Complaint cannot be updated at this stage'}), 400

    data = request.get_json()

    try:
        # Update fields
        if 'title' in data:
            complaint.title = data['title']
        if 'description' in data:
            complaint.description = data['description']
        if 'location_address' in data:
            complaint.location_address = data['location_address']
        if 'location_latitude' in data:
            complaint.location_latitude = data['location_latitude']
        if 'location_longitude' in data:
            complaint.location_longitude = data['location_longitude']
        if 'landmark' in data:
            complaint.landmark = data['landmark']
        if 'images' in data:
            complaint.set_images(data['images'])

        db.session.commit()

        return jsonify({
            'message': 'Complaint updated successfully',
            'complaint': complaint.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@complaints_bp.route('/<int:complaint_id>', methods=['DELETE'])
@jwt_required()
def delete_complaint(complaint_id):
    """Delete complaint"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    # Only citizen who raised it or admin can delete
    if user.role == 'citizen' and complaint.user_id != user.id:
        return jsonify({'error': 'Unauthorized access'}), 403

    # Can only delete if status is submitted
    if complaint.status != 'submitted':
        return jsonify({'error': 'Complaint cannot be deleted at this stage'}), 400

    try:
        db.session.delete(complaint)
        db.session.commit()

        return jsonify({'message': 'Complaint deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@complaints_bp.route('/<int:complaint_id>/status', methods=['PUT'])
@jwt_required()
def update_complaint_status(complaint_id):
    """Update complaint status"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    data = request.get_json()
    new_status = data.get('status')
    comment = data.get('comment', '')

    if not new_status:
        return jsonify({'error': 'Status is required'}), 400

    valid_statuses = [
        'submitted', 'under_review', 'assigned',
        'in_progress', 'pending_approval', 'resolved',
        'rejected', 'closed'
    ]

    if new_status not in valid_statuses:
        return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400

    old_status = complaint.status
    complaint.status = new_status

    # Create status history
    status_history = StatusHistory(
        complaint_id=complaint.id,
        old_status=old_status,
        new_status=new_status,
        changed_by=user.id,
        comment=comment
    )
    db.session.add(status_history)

    # If resolved, set resolved_at
    if new_status == 'resolved':
        complaint.resolved_at = datetime.utcnow()

    # Notify complainant
    create_notification(
        complaint.user_id,
        f'Complaint Status Updated',
        f'Your complaint "{complaint.title}" status has been changed from {old_status} to {new_status}. {comment}',
        'info',
        complaint.id
    )

    try:
        db.session.commit()

        return jsonify({
            'message': 'Status updated successfully',
            'complaint': complaint.to_dict(include_details=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@complaints_bp.route('/nearby-vendors/<int:complaint_id>', methods=['GET'])
@jwt_required()
def get_nearby_vendors_for_complaint(complaint_id):
    """Get nearby vendors for a personal complaint"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    if complaint.complaint_type != 'personal':
        return jsonify({'error': 'This is not a personal complaint'}), 400

    if not complaint.location_latitude or not complaint.location_longitude:
        return jsonify({'error': 'Location not provided for complaint'}), 400

    vendors = find_nearby_vendors(
        complaint.location_latitude,
        complaint.location_longitude,
        complaint.category
    )

    return jsonify({
        'vendors': [v.to_dict() for v in vendors],
        'total': len(vendors)
    }), 200
