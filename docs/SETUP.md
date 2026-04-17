# CIVIC AI - Setup and Installation Guide

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **Node.js 16+** ([Download](https://nodejs.org/))
- **MySQL 8.0+** ([Download](https://dev.mysql.com/downloads/))
- **Git** ([Download](https://git-scm.com/))

---

## Backend Setup

### 1. Clone Repository

```bash
cd civic_ai/backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Database

#### Option A: Using MySQL Command Line

```bash
mysql -u root -p
```

```sql
CREATE DATABASE civic_ai;
CREATE USER 'civic_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON civic_ai.* TO 'civic_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Then import the schema:
```bash
mysql -u root -p civic_ai < migrations/schema.sql
```

#### Option B: Using Flask-Migrate

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5. Set Environment Variables

Create a `.env` file in the backend directory:

```env
FLASK_ENV=development
FLASK_APP=run.py
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Database
DATABASE_URL=mysql+pymysql://civic_user:your_password@localhost/civic_ai

# File Upload
UPLOAD_FOLDER=uploads

# Email (Optional - for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-password

# AI Model Path (if using custom models)
AI_MODEL_PATH=models
```

### 6. Initialize Database

```bash
# Create tables
flask init-db

# Create initial admin user
flask create-admin
```

Default admin credentials:
- Email: `admin@civicai.com`
- Password: `admin123`
- **Change immediately after first login!**

### 7. Run Backend Server

```bash
flask run
```

Server will start at `http://localhost:5000`

---

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd civic_ai/frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment

Create `.env` file:

```env
REACT_APP_API_URL=http://localhost:5000/api
```

### 4. Start Development Server

```bash
npm start
```

Frontend will open at `http://localhost:3000`

---

## First-Time Usage

### 1. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000/api
- **API Docs**: See `docs/API_DOCUMENTATION.md`

### 2. Login as Admin

- Email: `admin@civicai.com`
- Password: `admin123`

### 3. Create Test Accounts

Register new accounts for testing:

**Citizen Account:**
1. Go to Register page
2. Select "Citizen" as account type
3. Fill in details
4. Login and create complaints

**Vendor Account:**
1. Register with "Service Provider" type
2. Fill business details
3. Wait for admin verification (or self-verify for testing)
4. Login to see available jobs

**Government Account:**
1. Admin must create government body
2. Go to Admin Dashboard → Create Government Body
3. Login with government credentials
4. View assigned complaints

---

## Running Tests

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

---

## Production Deployment

### Backend (Gunicorn + Nginx)

#### 1. Install Gunicorn

```bash
pip install gunicorn
```

#### 2. Run with Gunicorn

```bash
gunicorn --bind 0.0.0.0:8000 --workers 4 run:app
```

#### 3. Configure Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        root /path/to/frontend/build;
        try_files $uri $uri/ /index.html;
    }
}
```

### Frontend (Production Build)

```bash
cd frontend
npm run build
```

Copy `build/` folder to your web server.

### Database (Production)

1. Use MySQL 8.0+ on dedicated server
2. Configure connection pooling
3. Enable SSL/TLS connections
4. Set up automated backups
5. Monitor performance

#### Backup Command

```bash
mysqldump -u civic_user -p civic_ai > backup_$(date +%Y%m%d).sql
```

---

## AI/ML Setup (Optional)

### Install ML Dependencies

```bash
pip install tensorflow==2.13.0
pip install torch torchvision
pip install opencv-python
```

### Download Pre-trained Models

Place model files in `backend/models/` directory:

```
backend/
└── models/
    ├── image_classifier.h5
    └── text_model/
```

### Enable AI Features

Update `.env`:
```env
AI_ENABLED=true
AI_MODEL_PATH=models
```

---

## Troubleshooting

### Database Connection Errors

```
sqlalchemy.exc.OperationalError: (2003, "Can't connect to MySQL server")
```

**Solution:**
- Ensure MySQL server is running
- Check credentials in `.env`
- Verify database exists

### Port Already in Use

```
OSError: [Errno 98] Address already in use
```

**Solution:**
```bash
# Kill process on port 5000
lsof -i :5000
kill -9 <PID>

# Or use different port
flask run --port 5001
```

### Module Import Errors

```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
- Activate virtual environment
- Reinstall requirements: `pip install -r requirements.txt`

### CORS Errors in Browser

**Solution:**
- Ensure Flask-CORS is installed
- Check CORS configuration in `app/__init__.py`
- Verify frontend URL in backend CORS settings

### JWT Token Expired

```
{"msg": "Token has expired"}
```

**Solution:**
- Tokens expire after 24 hours
- Login again to get new token
- Implement token refresh for production

---

## Development Tips

### Hot Reload

Backend changes require restart. Use `flask run` with `--reload` flag:

```bash
flask run --reload
```

Frontend auto-reloads on file changes.

### Database Migrations

After model changes:

```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

### Debugging

Enable debug mode in `.env`:
```env
FLASK_ENV=development
```

Add debug prints in Python:
```python
import pdb; pdb.set_trace()
```

### API Testing with cURL

```bash
# Test login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@civicai.com","password":"admin123"}'

# Test protected endpoint
curl http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Environment Variables Reference

### Backend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/production) | `development` |
| `SECRET_KEY` | Flask secret key | Random |
| `JWT_SECRET_KEY` | JWT signing key | Random |
| `DATABASE_URL` | MySQL connection string | `mysql://...` |
| `UPLOAD_FOLDER` | File upload directory | `uploads` |
| `MAX_CONTENT_LENGTH` | Max upload size (bytes) | `16777216` (16MB) |
| `MAIL_SERVER` | SMTP server | `smtp.gmail.com` |
| `MAIL_USERNAME` | Email username | - |
| `MAIL_PASSWORD` | Email password | - |

### Frontend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | `http://localhost:5000/api` |

---

## Support

For issues or questions:
- Check documentation in `docs/` folder
- Review API documentation
- Check application logs
- Contact: support@civicai.com

## Next Steps

1. Review `USER_GUIDE.md` for usage instructions
2. Explore admin dashboard
3. Create test complaints
4. Test vendor workflow
5. Customize for your needs
