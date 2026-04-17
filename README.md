# CIVIC AI - Civic Issue Reporting Platform

A comprehensive platform connecting citizens, government authorities, and service providers for efficient civic issue resolution.

## 🌟 Features

- **Multi-Role System**: Citizens, Vendors, Government Bodies, Administrators
- **Complaint Management**: Public and personal issue tracking
- **Intelligent Routing**: Auto-assign to appropriate authorities
- **AI Integration**: Image classification, text analysis, priority prediction
- **Real-time Tracking**: Status updates and notifications
- **Vendor Marketplace**: Service provider discovery and estimates
- **Rating System**: Review and feedback mechanism
- **Analytics Dashboard**: Performance metrics and insights

## 🏗️ Architecture

- **Backend**: Flask (Python) + SQLAlchemy + MySQL
- **Frontend**: React + Material-UI
- **AI/ML**: TensorFlow + NLP transformers
- **Authentication**: JWT with role-based access control

## 📁 Project Structure

```
civic_ai/
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── middleware/      # Auth middleware
│   │   ├── ai/              # AI/ML integration
│   │   └── utils/           # Utility functions
│   ├── config/              # Configuration
│   ├── migrations/          # Database migrations
│   └── tests/               # Test suite
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   └── utils/           # Frontend utilities
│   └── public/              # Static assets
└── docs/
    ├── ARCHITECTURE.md      # System architecture
    ├── API_DOCUMENTATION.md # API reference
    ├── SETUP.md             # Installation guide
    └── USER_GUIDE.md        # User manual
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- MySQL 8.0+

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configure your environment
flask init-db
flask run
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

See [SETUP.md](docs/SETUP.md) for detailed instructions.

## 📖 Documentation

- [Architecture Documentation](docs/ARCHITECTURE.md)
- [API Documentation](docs/API_DOCUMENTATION.md)
- [Setup Guide](docs/SETUP.md)
- [User Guide](docs/USER_GUIDE.md)

## 🔑 Key Features

### For Citizens
- Easy complaint submission with image upload
- Real-time status tracking
- Automatic routing to authorities
- Service provider marketplace
- Rating and review system

### For Vendors
- Browse available jobs
- Cost estimate submission
- Job management
- Performance tracking
- Customer ratings

### For Government
- Complaint assignment
- Team management
- SLA tracking
- Performance analytics
- Department statistics

### For Admins
- Platform monitoring
- User management
- Vendor verification
- System analytics
- Audit trails

## 🤖 AI Features

1. **Image Classification**: Auto-detect issue type from photos
2. **Text Analysis**: Intelligent complaint categorization
3. **Priority Prediction**: ML-based urgency assessment
4. **Sentiment Analysis**: User satisfaction tracking

## 🔐 Security

- JWT authentication
- Role-based access control
- Password hashing (bcrypt)
- Input validation
- SQL injection prevention
- XSS protection

## 📊 Database

MySQL schema includes:
- Users (multi-role)
- Complaints (public/personal)
- Vendors & Government Bodies
- Estimates & Ratings
- Notifications & Audit Logs

## 🧪 Testing

```bash
# Backend
cd backend
pytest tests/ -v

# Frontend
cd frontend
npm test
```

## 🏭 Deployment

### Production Stack
- Backend: Gunicorn + Nginx
- Frontend: Nginx static serving
- Database: MySQL 8.0
- Cache: Redis (optional)
- Queue: Celery (optional)

See [SETUP.md](docs/SETUP.md) for production deployment guide.

## 📝 API Endpoints

### Authentication
- POST `/api/auth/register` - User registration
- POST `/api/auth/login` - Login
- GET `/api/auth/profile` - Get profile

### Complaints
- POST `/api/complaints/` - Create complaint
- GET `/api/complaints/` - List complaints
- PUT `/api/complaints/{id}/status` - Update status

### Vendor
- GET `/api/vendor/dashboard` - Vendor dashboard
- POST `/api/vendor/complaints/{id}/accept` - Accept job
- POST `/api/vendor/complaints/{id}/estimate` - Submit estimate

### Government
- GET `/api/government/dashboard` - Government dashboard
- POST `/api/government/complaints/{id}/assign` - Assign complaint
- POST `/api/government/complaints/{id}/resolve` - Resolve

### Admin
- GET `/api/admin/dashboard` - Platform stats
- GET `/api/admin/users` - User management
- POST `/api/admin/vendors/{id}/verify-license` - Verify vendor

### AI
- POST `/api/ai/classify-text` - Text classification
- POST `/api/ai/predict-priority` - Priority prediction

See [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for complete API reference.

## 🎨 UI/UX

- Modern, responsive design
- Material-UI components
- Mobile-friendly
- Accessibility features
- Intuitive navigation

## 🔄 Workflow

### Public Complaint Flow
1. Citizen submits complaint
2. AI analyzes and categorizes
3. Auto-assign to government body
4. Department reviews and assigns
5. Work starts and completes
6. Citizen rates service

### Personal Complaint Flow
1. Citizen submits complaint
2. System finds nearby vendors
3. Vendor accepts and provides estimate
4. Citizen approves estimate
5. Work completes
6. Citizen rates and reviews

## 🌐 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 📄 License

This project is for educational and demonstration purposes.

## 👥 Support

For questions or issues:
- Check documentation
- Review API docs
- Contact: support@civicai.com

## 🙏 Acknowledgments

Built with modern web technologies for efficient civic engagement.

---

**CIVIC AI** - Connecting communities for better civic services.
