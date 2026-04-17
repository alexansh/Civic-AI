# CIVIC AI - API Documentation

Complete API reference for the CIVIC AI platform.

## Base URL
```
http://localhost:5000/api
```

## Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

---

## Authentication Endpoints

### Register User
**POST** `/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe",
  "phone": "1234567890",
  "role": "citizen",
  "address": "123 Main St",
  "city": "Springfield",
  "state": "IL",
  "pincode": "62701"
}
```

**Vendor Specific Fields:**
```json
{
  "role": "vendor",
  "business_name": "Joe's Plumbing",
  "category": "plumbing",
  "experience_years": 10,
  "license_number": "PLB12345",
  "base_service_charge": 50.0
}
```

**Government Specific Fields:**
```json
{
  "role": "government",
  "department_name": "Public Works Department",
  "department_type": "municipal",
  "jurisdiction_area": "Downtown District",
  "jurisdiction_categories": ["pothole", "street_light", "garbage"],
  "office_address": "City Hall, 100 Main St"
}
```

**Response:**
```json
{
  "message": "Registration successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhb...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "role": "citizen"
  }
}
```

### Login
**POST** `/auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhb...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "role": "citizen",
    "is_verified": true
  }
}
```

### Get Profile
**GET** `/auth/profile`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "role": "citizen",
    "vendor_info": {
      "business_name": "Joe's Plumbing",
      "rating": 4.5,
      "total_jobs_completed": 127
    }
  }
}
```

---

## Complaint Endpoints

### Create Complaint
**POST** `/complaints/`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "Large pothole on Main Street",
  "description": "There is a large pothole in the middle of Main Street near the intersection with Oak Avenue. It's causing damage to vehicles.",
  "complaint_type": "public",
  "category": "pothole",
  "subcategory": "road damage",
  "location_address": "123 Main Street, Springfield",
  "location_latitude": 39.7817,
  "location_longitude": -89.6501,
  "landmark": "Near Starbucks",
  "severity_level": 4,
  "affected_people_count": 50,
  "images": ["image1.jpg", "image2.jpg"]
}
```

**Response:** `201 Created`
```json
{
  "message": "Complaint created successfully",
  "complaint": {
    "id": 1,
    "title": "Large pothole on Main Street",
    "status": "assigned",
    "priority": "high",
    "priority_score": 75.5,
    "assigned_to_type": "government",
    "assigned_to_id": 3,
    "created_at": "2026-04-06T10:30:00"
  }
}
```

### List Complaints
**GET** `/complaints/`

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 20)
- `status` (string): Filter by status
- `complaint_type` (string): Filter by type (public/personal)
- `category` (string): Filter by category
- `priority` (string): Filter by priority

**Response:**
```json
{
  "complaints": [...],
  "total": 150,
  "page": 1,
  "per_page": 20,
  "pages": 8
}
```

### Get Complaint Details
**GET** `/complaints/{id}`

**Response:**
```json
{
  "complaint": {
    "id": 1,
    "title": "Large pothole on Main Street",
    "description": "There is a large pothole...",
    "complaint_type": "public",
    "category": "pothole",
    "status": "in_progress",
    "priority": "high",
    "location": {
      "address": "123 Main Street, Springfield",
      "latitude": 39.7817,
      "longitude": -89.6501
    },
    "images": ["image1.jpg"],
    "status_history": [
      {
        "old_status": "submitted",
        "new_status": "assigned",
        "created_at": "2026-04-06T10:35:00"
      }
    ]
  }
}
```

### Update Complaint Status
**PUT** `/complaints/{id}/status`

**Request Body:**
```json
{
  "status": "in_progress",
  "comment": "Team dispatched to location"
}
```

**Valid Statuses:**
- `submitted`
- `under_review`
- `assigned`
- `in_progress`
- `pending_approval`
- `resolved`
- `rejected`
- `closed`

---

## Vendor Endpoints

### Get Dashboard
**GET** `/vendor/dashboard`

**Response:**
```json
{
  "vendor": {
    "id": 5,
    "business_name": "Joe's Plumbing",
    "rating": 4.5,
    "is_available": true
  },
  "stats": {
    "assigned_complaints": 3,
    "in_progress": 2,
    "completed": 45,
    "pending_estimates": 1
  }
}
```

### Get Available Complaints
**GET** `/vendor/complaints/available`

Returns complaints matching vendor's category and within service radius.

**Response:**
```json
{
  "complaints": [
    {
      "id": 10,
      "title": "Leaking pipe in basement",
      "category": "plumbing",
      "distance": 2.5,
      "created_at": "2026-04-06T09:00:00"
    }
  ]
}
```

### Accept Complaint
**POST** `/vendor/complaints/{id}/accept`

**Response:**
```json
{
  "message": "Complaint accepted"
}
```

### Submit Estimate
**POST** `/vendor/complaints/{id}/estimate`

**Request Body:**
```json
{
  "labor_cost": 150.0,
  "material_cost": 50.0,
  "total_cost": 200.0,
  "description": "Replace leaking pipe section. Includes parts and labor."
}
```

**Response:**
```json
{
  "message": "Estimate submitted successfully",
  "estimate": {
    "id": 1,
    "total_cost": 200.0,
    "status": "pending"
  }
}
```

---

## Government Endpoints

### Get Dashboard
**GET** `/government/dashboard`

**Response:**
```json
{
  "department": {
    "id": 3,
    "department_name": "Public Works",
    "department_type": "municipal"
  },
  "stats": {
    "assigned": 15,
    "in_progress": 8,
    "resolved": 127,
    "overdue": 2
  }
}
```

### GetAssigned Complaints
**GET** `/government/complaints`

**Query Parameters:**
- `page`, `per_page`, `status`, `priority`, `category`

**Response:**
```json
{
  "complaints": [...],
  "total": 150,
  "page": 1
}
```

### Assign to Team
**POST** `/government/complaints/{id}/assign`

**Request Body:**
```json
{
  "assigned_to_id": 5,
  "comment": "Assigning to Road Maintenance Team A"
}
```

### Start Work
**POST** `/government/complaints/{id}/start`

### Resolve Complaint
**POST** `/government/complaints/{id}/resolve`

**Request Body:**
```json
{
  "resolution_notes": "Pothole filled and road surface repaired. Area cleaned."
}
```

### Reject Complaint
**POST** `/government/complaints/{id}/reject`

**Request Body:**
```json
{
  "reason": "This issue falls under state highway jurisdiction, not municipal"
}
```

---

## Admin Endpoints

### Get Dashboard Statistics
**GET** `/admin/dashboard`

**Response:**
```json
{
  "users": {
    "total": 1500,
    "citizens": 1200,
    "vendors": 250,
    "government": 50
  },
  "complaints": {
    "total": 5000,
    "public": 3000,
    "personal": 2000,
    "submitted": 150,
    "in_progress": 200,
    "resolved": 4500,
    "overdue": 15
  },
  "vendors": {
    "verified": 230,
    "pending_verification": 20
  },
  "departments": {
    "active": 45
  }
}
```

### List Users
**GET** `/admin/users`

**Query Parameters:**
- `role` (citizen/vendor/government)
- `is_verified` (true/false)

### Verify User
**POST** `/admin/users/{id}/verify`

### Verify Vendor License
**POST** `/admin/vendors/{id}/verify-license`

**Request Body:**
```json
{
  "verified": true
}
```

### Get Platform Statistics
**GET** `/admin/statistics`

Returns detailed analytics including:
- Complaints by day (last 30 days)
- Top complaint categories
- Average resolution time by priority

---

## AI Endpoints

### Classify Text
**POST** `/ai/classify-text`

**Request Body:**
```json
{
  "description": "Large pothole causing damage to cars on Main Street"
}
```

**Response:**
```json
{
  "category": {
    "category": "pothole",
    "confidence": 0.92,
    "top_3": ["pothole", "street_light", "building_damage"]
  },
  "priority": {
    "priority": "high",
    "confidence": 0.75
  },
  "sentiment": {
    "sentiment": "negative",
    "confidence": 0.68
  }
}
```

### Predict Priority
**POST** `/ai/predict-priority`

**Request Body:**
```json
{
  "description": "Massive sinkhole blocking entire street, very dangerous",
  "category": "pothole",
  "severity_level": 5,
  "affected_people_count": 100,
  "complaint_type": "public"
}
```

**Response:**
```json
{
  "priority": "critical",
  "score": 92.5,
  "breakdown": {
    "individual_scores": {
      "text": 0.85,
      "severity": 1.0,
      "affected": 0.95
    }
  }
}
```

### Validate Issue
**POST** `/ai/validate-issue`

Checks if the provided description/image represents a valid civic issue.

### Suggest Category
**POST** `/ai/category-suggestion`

Returns category suggestions based on description.

---

## Error Responses

All endpoints return consistent error format:

```json
{
  "error": "Error message describing what went wrong"
}
```

Common HTTP Status Codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

---

## Rate Limiting

API requests are limited to:
- 100 requests per minute for public endpoints
- 1000 requests per minute for authenticated users

Exceeding rate limits returns `429 Too Many Requests`.
