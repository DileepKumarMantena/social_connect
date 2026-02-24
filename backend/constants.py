import hashlib

# Mock user database
users_db = {
    "superadmin": {
        "username": "superadmin",
        "email": "superadmin@company.com",
        "password_hash": hashlib.sha256("SuperAdmin123!".encode()).hexdigest(),
        "name": "Super Admin",
        "role": "super_admin",
        "companyid": 0,
        "activitystatus": True,
        "access_expires_at": None,
        "created_by": None
    },
    "admin1": {
        "username": "admin1",
        "email": "admin1@company.com",
        "password_hash": hashlib.sha256("Admin123!".encode()).hexdigest(),
        "name": "Admin One",
        "role": "admin",
        "companyid": 1,
        "activitystatus": True,
        "access_expires_at": None,
        "created_by": 1
    },
    "user1": {
        "username": "user1",
        "email": "user1@company.com",
        "password_hash": hashlib.sha256("User123!".encode()).hexdigest(),
        "name": "User One",
        "role": "user",
        "companyid": 1,
        "activitystatus": True,
        "access_expires_at": None,
        "created_by": 2
    }
}

# OTP storage (in production, use Redis or database)
otp_storage = {}

# Development Mode Configuration
DEV_MODE = True  # Set to False to use database instead of mock data

# Database Configuration
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'Dileep@1234',
    'database': 'social_connect',
    'autocommit': True
}

# API Configuration
API_TITLE = "Social Connect API"
API_VERSION = "1.0.0"
API_HOST = "0.0.0.0"
API_PORT = 8000

# CORS Configuration
ALLOWED_ORIGINS = ["http://localhost:3000", "http://192.168.1.6:3000"]

# OTP Configuration
OTP_EXPIRY_MINUTES = 10
OTP_LENGTH = 4

# Email Configuration (update these for real email sending)
SMTP_EMAIL = "your-email@gmail.com"  # Replace with your Gmail
SMTP_PASSWORD = "your-app-password"   # Replace with your Gmail app password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# User Configuration
DEFAULT_USERNAME = "testuser"
DEFAULT_EMAIL = "test@example.com"
DEFAULT_PASSWORD = "Password123!"

# JWT Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Mock dashboard data
channels_db = [
    {"id": 1, "name": "facebook", "connected": True, "active": True, "followers": 1500},
    {"id": 2, "name": "instagram", "connected": True, "active": False, "followers": 800},
    {"id": 3, "name": "linkedin", "connected": False, "active": False, "followers": 0},
    {"id": 4, "name": "twitter", "connected": False, "active": False, "followers": 0}
]

campaigns_db = [
    {"id": 1, "name": "Summer Sale", "status": "active", "leads": 45, "conversion_rate": 12.5},
    {"id": 2, "name": "Product Launch", "status": "completed", "leads": 120, "conversion_rate": 8.3},
    {"id": 3, "name": "Holiday Special", "status": "draft", "leads": 0, "conversion_rate": 0}
]

leads_db = [
    {"id": 1, "name": "John Doe", "email": "john@example.com", "status": "new", "campaign_id": 1},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "status": "contacted", "campaign_id": 1},
    {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "status": "converted", "campaign_id": 2},
    {"id": 4, "name": "Alice Brown", "email": "alice@example.com", "status": "new", "campaign_id": 1}
]
