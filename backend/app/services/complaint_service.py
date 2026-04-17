"""
Complaint Service - Business logic for complaint routing and vendor matching
"""

from app.models import Vendor, GovernmentBody, Complaint
from app.utils.helpers import calculate_distance
from app import db


def route_complaint(complaint):
    """Route complaint to appropriate vendor or government body"""
    if complaint.complaint_type == 'public':
        route_to_government(complaint)
    else:
        route_to_vendor(complaint)


def route_to_government(complaint):
    """Route public complaint to government body"""
    # Find government bodies that handle this category
    category = complaint.category

    # Query government bodies
    gov_bodies = GovernmentBody.query.filter(
        GovernmentBody.is_active_dept == True
    ).all()

    # Find best match based on category and location
    best_match = None
    best_score = 0

    for gov in gov_bodies:
        score = 0

        # Check if this department handles this category
        if gov.jurisdiction_categories:
            import json
            categories = json.loads(gov.jurisdiction_categories)
            if category in categories:
                score += 50

        # Check location proximity if available
        if (gov.latitude and gov.longitude and
            complaint.location_latitude and complaint.location_longitude):
            distance = calculate_distance(
                complaint.location_latitude,
                complaint.location_longitude,
                gov.latitude,
                gov.longitude
            )
            # Closer departments get higher score
            if distance < 5:  # Within 5 km
                score += 30
            elif distance < 10:
                score += 20
            elif distance < 20:
                score += 10

        if score > best_score:
            best_score = score
            best_match = gov

    # Assign to government body
    if best_match:
        complaint.assigned_to_type = 'government'
        complaint.assigned_to_id = best_match.id
        complaint.government_body_id = best_match.id
        complaint.status = 'assigned'
    else:
        # No specific department found, mark for admin review
        complaint.status = 'under_review'


def route_to_vendor(complaint):
    """Route personal complaint to nearby vendors"""
    category = complaint.category

    # Find nearby vendors
    vendors = find_nearby_vendors(
        complaint.location_latitude,
        complaint.location_longitude,
        category
    )

    # For personal complaints, we don't auto-assign
    # We just mark it as ready for vendor selection
    complaint.status = 'submitted'

    # Store potential vendors in complaint metadata
    # In a real system, you'd send notifications to these vendors
    return vendors


def find_nearby_vendors(latitude, longitude, category, radius_km=20):
    """Find nearby vendors for a given category"""
    if not latitude or not longitude:
        return []

    vendors = Vendor.query.filter(
        Vendor.is_available == True,
        Vendor.license_verified == True
    ).all()

    # Filter by category and distance
    matching_vendors = []

    for vendor in vendors:
        # Check category match
        if vendor.category != category:
            # Check subcategories
            import json
            if vendor.subcategories:
                subcategories = json.loads(vendor.subcategories)
                if category not in subcategories:
                    continue

        # Check distance
        if vendor.latitude and vendor.longitude:
            distance = calculate_distance(
                latitude, longitude,
                vendor.latitude, vendor.longitude
            )

            if distance <= vendor.service_radius_km and distance <= radius_km:
                matching_vendors.append(vendor)
                vendor.distance = round(distance, 2)  # Add distance info

    # Sort by distance and rating
    matching_vendors.sort(
        key=lambda v: (getattr(v, 'distance', 999), -v.rating)
    )

    return matching_vendors[:10]  # Return top 10


def auto_assign_vendor(complaint_id, vendor_id):
    """Auto-assign a vendor to a personal complaint"""
    complaint = Complaint.query.get(complaint_id)
    vendor = Vendor.query.get(vendor_id)

    if not complaint or not vendor:
        return False

    if complaint.complaint_type != 'personal':
        return False

    complaint.assigned_to_type = 'vendor'
    complaint.assigned_to_id = vendor.id
    complaint.vendor_id = vendor.id
    complaint.status = 'assigned'

    db.session.commit()
    return True


def calculate_estimate(complaint, vendor):
    """Calculate estimated cost for a personal complaint"""
    # Base cost from vendor
    base_cost = vendor.base_service_charge or 50.0

    # Category multipliers
    category_multipliers = {
        'electrical': 1.5,
        'plumbing': 1.3,
        'carpentry': 1.2,
        'painting': 1.0,
        'cleaning': 0.8,
        'gardening': 0.9,
        'other': 1.0
    }

    multiplier = category_multipliers.get(complaint.category, 1.0)
    estimated_cost = base_cost * multiplier

    # Add severity adjustment
    if complaint.severity_level:
        severity_multiplier = 1 + (complaint.severity_level - 3) * 0.2
        estimated_cost *= severity_multiplier

    return round(estimated_cost, 2)
