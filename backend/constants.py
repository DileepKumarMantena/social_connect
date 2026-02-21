import hashlib

# Mock user database
users_db = {
    "testuser": {
        "username": "testuser",
        "email": "test@example.com",
        "password_hash": hashlib.sha256("Password123!".encode()).hexdigest()
    }
}

# OTP storage (in production, use Redis or database)
otp_storage = {}

# API Configuration
API_TITLE = "Social Connect API"
API_VERSION = "1.0.0"
API_HOST = "0.0.0.0"
API_PORT = 8000

# CORS Configuration
ALLOWED_ORIGINS = ["http://localhost:3000"]

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
