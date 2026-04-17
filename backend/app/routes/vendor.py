"""
Vendor Routes - Vendor-specific operations
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Complaint, Estimate, Vendor, Rating
from app.middleware.auth import get_current_user, vendor_required
from app.services.complaint_service import calculate_estimate
from app.utils.helpers import create_notification
from datetime import datetime, timedelta

vendor_bp = Blueprint('vendor', __name__)


@vendor_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def vendor_dashboard():
    """Get vendor dashboard data"""
    user = get_current_user()
    if not user or not user.vendor_profile:
        return jsonify({'error': 'Vendor profile not found'}), 404

    vendor = user.vendor_profile

    # Get assigned complaints
    assigned_complaints = Complaint.query.filter_by(
        vendor_id=vendor.id,
        status='assigned'
    ).count()

    in_progress = Complaint.query.filter_by(
        vendor_id=vendor.id,
        status='in_progress'
    ).count()

    completed = Complaint.query.filter_by(
        vendor_id=vendor.id,
        status='resolved'
    ).count()

    # Get pending estimates
    pending_estimates = Estimate.query.filter_by(
        vendor_id=vendor.id,
        status='pending'
    ).count()

    return jsonify({
        'vendor': vendor.to_dict(),
        'stats': {
            'assigned_complaints': assigned_complaints,
            'in_progress': in_progress,
            'completed': completed,
            'pending_estimates': pending_estimates
        }
    }), 200


@vendor_bp.route('/complaints/available', methods=['GET'])
@jwt_required()
def get_available_complaints():
    """Get available complaints for vendor to accept"""
    user = get_current_user()
    if not user or not user.vendor_profile:
        return jsonify({'error': 'Vendor profile not found'}), 404

    vendor = user.vendor_profile

    # Get complaints in vendor's category and area
    query = Complaint.query.filter_by(
        complaint_type='personal',
        status='submitted'
    )

    # Filter by category
    if vendor.category:
        query = query.filter(
            db.or_(
                Complaint.category == vendor.category
            )
        )

    # Get nearby complaints
    if vendor.latitude and vendor.longitude:
        # In a real system, you'd use spatial queries
        # For now, we'll just return all and filter in Python
        complaints = query.all()
        nearby_complaints = []

        for complaint in complaints:
            if complaint.location_latitude and complaint.location_longitude:
                from app.utils.helpers import calculate_distance
                distance = calculate_distance(
                    vendor.latitude, vendor.longitude,
                    complaint.location_latitude, complaint.location_longitude
                )
                if distance <= vendor.service_radius_km:
                    complaint.distance = round(distance, 2)
                    nearby_complaints.append(complaint)

        complaints = sorted(nearby_complaints, key=lambda c: getattr(c, 'distance', 999))
    else:
        complaints = query.order_by(Complaint.created_at.desc()).limit(50).all()

    return jsonify({
        'complaints': [c.to_dict() for c in complaints[:20]]
    }), 200


@vendor_bp.route('/complaints/my-tasks', methods=['GET'])
@jwt_required()
def get_my_tasks():
    """Get vendor's assigned tasks"""
    user = get_current_user()
    if not user or not user.vendor_profile:
        return jsonify({'error': 'Vendor profile not found'}), 404

    vendor = user.vendor_profile

    status = request.args.get('status')

    query = Complaint.query.filter_by(vendor_id=vendor.id)

    if status:
        query = query.filter_by(status=status)

    complaints = query.order_by(Complaint.created_at.desc()).all()

    return jsonify({
        'complaints': [c.to_dict(include_details=True) for c in complaints]
    }), 200


@vendor_bp.route('/complaints/<int:complaint_id>/accept', methods=['POST'])
@jwt_required()
def accept_complaint(complaint_id):
    """Accept a complaint"""
    user = get_current_user()
    if not user or not user.vendor_profile:
        return jsonify({'error': 'Vendor profile not found'}), 404

    vendor = user.vendor_profile

    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    if complaint.vendor_id != vendor.id:
        return jsonify({'error': 'This complaint is not assigned to you'}), 403

    if complaint.status != 'assigned':
        return jsonify({'error': 'Complaint is not in assignable status'}), 400

    complaint.status = 'in_progress'

    # Create status history
    from app.models import StatusHistory
    status_history = StatusHistory(
        complaint_id=complaint.id,
        old_status='assigned',
        new_status='in_progress',
        changed_by=user.id,
        comment='Work started by vendor'
    )
    db.session.add(status_history)

    # Notify citizen
    create_notification(
        complaint.user_id,
        'Work Started',
        f'Vendor {vendor.business_name} has started working on your complaint "{complaint.title}".',
        'success',
        complaint.id
    )

    db.session.commit()

    return jsonify({
        'message': 'Complaint accepted',
        'complaint': complaint.to_dict()
    }), 200


@vendor_bp.route('/complaints/<int:complaint_id>/estimate', methods=['POST'])
@jwt_required()
def submit_estimate(complaint_id):
    """Submit cost estimate for a complaint"""
    user = get_current_user()
    if not user or not user.vendor_profile:
        return jsonify({'error': 'Vendor profile not found'}), 404

    vendor = user.vendor_profile

    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    if complaint.vendor_id != vendor.id:
        return jsonify({'error': 'This complaint is not assigned to you'}), 403

    if complaint.status not in ['assigned', 'in_progress']:
        return jsonify({'error': 'Cannot submit estimate for this complaint'}), 400

    data = request.get_json()

    if not data.get('labor_cost') or not data.get('total_cost'):
        return jsonify({'error': 'Labor cost and total cost are required'}), 400

    try:
        # Check if estimate already exists
        estimate = Estimate.query.filter_by(complaint_id=complaint_id).first()

        if estimate:
            # Update existing estimate
            estimate.labor_cost = data['labor_cost']
            estimate.material_cost = data.get('material_cost', 0)
            estimate.total_cost = data['total_cost']
            estimate.description = data.get('description', '')
            estimate.status = 'pending'
            estimate.user_approved = False
            estimate.valid_until = datetime.utcnow() + timedelta(days=7)
            estimate.updated_at = datetime.utcnow()
        else:
            # Create new estimate
            estimate = Estimate(
                complaint_id=complaint_id,
                vendor_id=vendor.id,
                labor_cost=data['labor_cost'],
                material_cost=data.get('material_cost', 0),
                total_cost=data['total_cost'],
                description=data.get('description', ''),
                status='pending',
                user_approved=False,
                valid_until=datetime.utcnow() + timedelta(days=7)
            )
            db.session.add(estimate)

        # Update complaint status
        complaint.status = 'pending_approval'
        complaint.estimated_cost = data['total_cost']

        # Notify citizen
        create_notification(
            complaint.user_id,
            'Estimate Received',
            f'Vendor {vendor.business_name} has submitted an estimate of ${data["total_cost"]:.2f} for your complaint.',
            'info',
            complaint.id
        )

        db.session.commit()

        return jsonify({
            'message': 'Estimate submitted successfully',
            'estimate': estimate.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@vendor_bp.route('/complaints/<int:complaint_id>/complete', methods=['POST'])
@jwt_required()
def mark_complete(complaint_id):
    """Mark complaint as completed"""
    user = get_current_user()
    if not user or not user.vendor_profile:
        return jsonify({'error': 'Vendor profile not found'}), 404

    vendor = user.vendor_profile

    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    if complaint.vendor_id != vendor.id:
        return jsonify({'error': 'This complaint is not assigned to you'}), 403

    if complaint.status != 'in_progress':
        return jsonify({'error': 'Complaint is not in progress'}), 400

    data = request.get_json()

    complaint.status = 'resolved'
    complaint.resolved_at = datetime.utcnow()

    # Create status history
    from app.models import StatusHistory
    status_history = StatusHistory(
        complaint_id=complaint.id,
        old_status='in_progress',
        new_status='resolved',
        changed_by=user.id,
        comment=data.get('completion_notes', 'Work completed by vendor')
    )
    db.session.add(status_history)

    # Update vendor stats
    vendor.total_jobs_completed += 1

    # Notify citizen
    create_notification(
        complaint.user_id,
        'Work Completed',
        f'Vendor {vendor.business_name} has marked your complaint as completed. Please rate the service.',
        'success',
        complaint.id
    )

    db.session.commit()

    return jsonify({
        'message': 'Complaint marked as completed',
        'complaint': complaint.to_dict()
    }), 200


@vendor_bp.route('/availability', methods=['PUT'])
@jwt_required()
def update_availability():
    """Update vendor availability"""
    user = get_current_user()
    if not user or not user.vendor_profile:
        return jsonify({'error': 'Vendor profile not found'}), 404

    vendor = user.vendor_profile

    data = request.get_json()

    if 'is_available' in data:
        vendor.is_available = data['is_available']
    if 'latitude' in data:
        vendor.latitude = data['latitude']
    if 'longitude' in data:
        vendor.longitude = data['longitude']

    try:
        db.session.commit()
        return jsonify({
            'message': 'Availability updated',
            'vendor': vendor.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@vendor_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_vendor_profile():
    """Get vendor profile"""
    user = get_current_user()
    if not user or not user.vendor_profile:
        return jsonify({'error': 'Vendor profile not found'}), 404

    return jsonify({
        'vendor': user.vendor_profile.to_dict()
    }), 200
