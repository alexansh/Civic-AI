# CIVIC AI - System Architecture Documentation

## Overview

CIVIC AI is a comprehensive civic issue reporting platform built with a modern, scalable architecture. This document outlines the complete system architecture.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│                    (React.js + MUI)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ Citizen  │ │  Vendor  │ │Government│ │  Admin   │      │
│  │   Portal │ │  Portal  │ │  Portal  │ │  Portal  │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTPS
┌─────────────────────────────────────────────────────────────┐
│                         Backend                              │
│                   (Flask REST API)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Layer (Routes)                       │  │
│  │  Auth | Complaints | Vendors | Gov | Admin | AI      │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Business Logic (Services)                   │  │
│  │    Complaint Routing | Vendor Matching | Priority     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           AI/ML Layer                                 │  │
│  │  Image Classification | Text Analysis | Prediction    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Database Layer                          │
│                        (MySQL 8.0)                           │
│  Users | Complaints | Vendors | Gov Bodies | Estimates      │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend
- **Framework**: Flask (Python 3.9+)
- **ORM**: SQLAlchemy
- **Authentication**: Flask-JWT-Extended
- **Database**: MySQL 8.0+
- **AI/ML**: TensorFlow, Hugging Face Transformers (optional)
- **Image Processing**: Pillow, OpenCV

### Frontend
- **Framework**: React 18
- **UI Library**: Material-UI (MUI)
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Forms**: React Hook Form
- **Notifications**: React Toastify

## Project Structure

```
civic_ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py           # App factory
│   │   ├── models/               # Database models
│   │   │   ├── user.py           # User, Vendor, GovernmentBody
│   │   │   ├── complaint.py      # Complaint, StatusHistory, Estimate, Rating
│   │   │   └── notification.py   # Notification, AuditLog
│   │   ├── routes/               # API routes
│   │   │   ├── auth.py           # Authentication endpoints
│   │   │   ├── complaints.py     # Complaint CRUD
│   │   │   ├── vendor.py         # Vendor operations
│   │   │   ├── government.py     # Government operations
│   │   │   ├── admin.py          # Admin operations
│   │   │   └── ai.py             # AI endpoints
│   │   ├── services/             # Business logic
│   │   │   └── complaint_service.py
│   │   ├── middleware/           # Auth middleware
│   │   │   └── auth.py
│   │   ├── ai/                   # AI integration
│   │   │   ├── image_classifier.py
│   │   │   ├── text_classifier.py
│   │   │   └── priority_predictor.py
│   │   └── utils/                # Utilities
│   │       ├── validators.py
│   │       └── helpers.py
│   ├── config/
│   │   └── config.py             # Configuration
│   ├── migrations/
│   │   └── schema.sql            # Database schema
│   ├── run.py                    # Entry point
│   └── requirements.txt

├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/           # Reusable components
│   │   ├── pages/                # Page components
│   │   │   ├── citizen/
│   │   │   ├── vendor/
│   │   │   ├── government/
│   │   │   └── admin/
│   │   ├── services/
│   │   │   └── api.js            # API service
│   │   ├── utils/
│   │   │   └── auth.js           # Auth utilities
│   │   └── App.js
│   └── package.json

└── docs/
    ├── ARCHITECTURE.md
    ├── API_DOCUMENTATION.md
    ├── SETUP.md
    └── USER_GUIDE.md
```

## Core Components

### 1. Authentication System
- JWT-based authentication
- Role-based access control (RBAC)
- Support for 4 user roles: Admin, Citizen, Vendor, Government
- Password hashing with Werkzeug
- Token expiration and refresh

### 2. Complaint Management
- Two complaint types: Public and Personal
- Intelligent routing based on type and category
- Status tracking with history
- Priority calculation (manual + AI)
- SLA deadline management
- Image upload support
- Location tracking (GPS coordinates)

### 3. Routing System
- **Public Complaints**: Auto-routed to relevant government body based on:
  - Category match
  - Geographic proximity
  - Department jurisdiction

- **Personal Complaints**: Routed to nearby vendors based on:
  - Service category
  - Distance from location
  - Vendor availability
  - Service radius

### 4. Vendor Workflow
1. Complaint submitted (Personal issue)
2. System finds nearby vendors
3. Vendor receives notification
4. Vendor accepts/rejects task
5. Vendor provides cost estimate
6. Citizen approves estimate
7. Work begins → In Progress
8. Work completed → Resolved
9. Citizen rates service

### 5. Government Workflow
1. Public complaint submitted
2. Auto-assigned to department
3. Department reviews complaint
4. Assigns to team/worker
5. Work starts
6. Work completed
7. Citizen rates service

### 6. AI Integration

#### Image Classification
- Detects issue type from uploaded images
- Categories: pothole, street_light, garbage, water_leak, electrical, etc.
- Confidence scoring
- Multi-image analysis

#### Text Classification
- Auto-categorizes complaint from description
- Predicts priority level
- Sentiment analysis
- Entity extraction (locations, dates, severity indicators)

#### Priority Prediction
- Combines multiple factors:
  - Text analysis (35%)
  - Image analysis (25%)
  - Severity level (20%)
  - Affected people count (10%)
  - Time factor (5%)
  - Location factor (5%)

## Database Design

### Key Tables

1. **users** - All user accounts with role differentiation
2. **vendors** - Vendor profiles and details
3. **government_bodies** - Government department profiles
4. **complaints** - All complaints (public + personal)
5. **status_history** - Audit trail for status changes
6. **estimates** - Cost estimates for personal complaints
7. **ratings** - Reviews and ratings
8. **notifications** - User notifications
9. **audit_logs** - System audit trail

### Relationships
- One-to-Many: User → Complaints
- One-to-One: User → Vendor/GovernmentBody
- Many-to-One: Complaints → GovernmentBody/Vendor
- One-to-Many: Complaint → StatusHistory
- One-to-One: Complaint → Estimate
- One-to-One: Complaint → Rating

## API Design

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - Login
- `GET /api/auth/profile` - Get profile
- `PUT /api/auth/profile` - Update profile
- `POST /api/auth/change-password` - Change password
- `POST /api/auth/logout` - Logout

### Complaint Endpoints
- `POST /api/complaints/` - Create complaint
- `GET /api/complaints/` - List complaints (filtered by role)
- `GET /api/complaints/{id}` - Get complaint details
- `PUT /api/complaints/{id}` - Update complaint
- `DELETE /api/complaints/{id}` - Delete complaint
- `PUT /api/complaints/{id}/status` - Update status

### Vendor Endpoints
- `GET /api/vendor/dashboard` - Dashboard data
- `GET /api/vendor/complaints/available` - Available jobs
- `GET /api/vendor/complaints/my-tasks` - Assigned tasks
- `POST /api/vendor/complaints/{id}/accept` - Accept job
- `POST /api/vendor/complaints/{id}/estimate` - Submit estimate
- `POST /api/vendor/complaints/{id}/complete` - Mark complete

### Government Endpoints
- `GET /api/government/dashboard` - Dashboard data
- `GET /api/government/complaints` - Assigned complaints
- `POST /api/government/complaints/{id}/assign` - Assign to team
- `POST /api/government/complaints/{id}/start` - Start work
- `POST /api/government/complaints/{id}/resolve` - Resolve
- `POST /api/government/complaints/{id}/reject` - Reject

### Admin Endpoints
- `GET /api/admin/dashboard` - Platform statistics
- `GET /api/admin/users` - List all users
- `POST /api/admin/users/{id}/verify` - Verify user
- `GET /api/admin/vendors` - List vendors
- `POST /api/admin/vendors/{id}/verify-license` - Verify license
- `GET /api/admin/complaints` - All complaints

### AI Endpoints
- `POST /api/ai/classify-image` - Classify image
- `POST /api/ai/classify-text` - Classify text
- `POST /api/ai/predict-priority` - Predict priority
- `POST /api/ai/validate-issue` - Validate issue
- `POST /api/ai/category-suggestion` - Suggest category

## Security

### Authentication
- JWT tokens with 24-hour expiration
- Refresh tokens with 30-day expiration
- Password hashing (bcrypt)
- Role-based access control on all endpoints

### Authorization
- Citizens can only access their own complaints
- Vendors can only see jobs assigned to them
- Government can only see complaints assigned to their department
- Admin has full access

### Data Validation
- Input validation on all endpoints
- Email format validation
- Password strength requirements
- File upload size limits (16MB)
- SQL injection prevention (parameterized queries via ORM)

## Scalability Considerations

### Horizontal Scaling
- Stateless API design (JWT tokens)
- Database connection pooling
- Load balancer ready

### Performance
- Lazy loading of relationships
- Pagination on all list endpoints
- Database indexes on frequently queried fields
- Query optimization

### Future Enhancements
- Redis caching for frequently accessed data
- Message queue (Celery/RabbitMQ) for async tasks
- CDN for image storage
- WebSocket for real-time notifications
- Microservices architecture for large scale

## Deployment

### Development
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run

# Frontend
cd frontend
npm install
npm start
```

### Production
- Backend: Gunicorn + Nginx
- Frontend: Nginx static file serving
- Database: MySQL on separate server
- SSL/TLS certificates
- Environment variables for configuration
- Docker containerization available

## Monitoring & Logging

### Logging
- Application logs
- Error tracking
- Audit logs for important actions
- Performance metrics

### Monitoring
- Database query performance
- API response times
- Error rates
- User activity

## Backup & Recovery
- Regular database backups
- Point-in-time recovery
- Disaster recovery plan
- Data retention policies
