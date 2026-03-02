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
    },
    "marketing1": {
        "username": "marketing1",
        "email": "marketing1@company.com",
        "password_hash": hashlib.sha256("Marketing123!".encode()).hexdigest(),
        "name": "Marketing Manager",
        "role": "marketing_manager",
        "companyid": 1,
        "activitystatus": True,
        "access_expires_at": None,
        "created_by": 1
    },
    "content1": {
        "username": "content1",
        "email": "content1@company.com",
        "password_hash": hashlib.sha256("Content123!".encode()).hexdigest(),
        "name": "Content Editor",
        "role": "content_editor",
        "companyid": 1,
        "activitystatus": True,
        "access_expires_at": None,
        "created_by": 1
    },
    "sales1": {
        "username": "sales1",
        "email": "sales1@company.com",
        "password_hash": hashlib.sha256("Sales123!".encode()).hexdigest(),
        "name": "Sales Manager",
        "role": "sales_manager",
        "companyid": 1,
        "activitystatus": True,
        "access_expires_at": None,
        "created_by": 1
    }
}

# OTP storage (in production, use Redis or database)
otp_storage = {}

# JSON Database Configuration
USE_JSON_DB = False  # Disable JSON database for now
DEV_MODE = True  # Use mock data from constants

# API Configuration
API_TITLE = "Social Connect API"
API_VERSION = "1.0.0"
API_HOST = "0.0.0.0"
API_PORT = 8003

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

# In-memory tracking for mock mode (resets on server restart)
created_users = {}
created_roles = {}
deleted_roles = set()

# JWT Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Mock dashboard data
channels_db = [
    {"id": 1, "name": "facebook", "connected": True, "active": True, "followers": 1500, "created_by": "admin1"},
    {"id": 2, "name": "instagram", "connected": True, "active": False, "followers": 800, "created_by": "admin1"},
    {"id": 3, "name": "linkedin", "connected": False, "active": False, "followers": 0, "created_by": "superadmin"},
    {"id": 4, "name": "twitter", "connected": False, "active": False, "followers": 0, "created_by": "admin1"},
    {"id": 5, "name": "youtube", "connected": True, "active": True, "followers": 2500, "created_by": "superadmin"}
]

campaigns_db = [
    {"id": 1, "name": "Summer Sale", "status": "active", "leads": 45, "conversion_rate": 12.5, "created_by": "admin1"},
    {"id": 2, "name": "Product Launch", "status": "completed", "leads": 120, "conversion_rate": 8.3, "created_by": "admin1"},
    {"id": 3, "name": "Holiday Special", "status": "draft", "leads": 0, "conversion_rate": 0, "created_by": "superadmin"},
    {"id": 4, "name": "New Year Campaign", "status": "active", "leads": 25, "conversion_rate": 15.2, "created_by": "superadmin"},
    {"id": 5, "name": "Admin Campaign", "status": "active", "leads": 30, "conversion_rate": 10.5, "created_by": "admin1"}
]

leads_db = [
    {"id": 1, "name": "John Doe", "email": "john@example.com", "status": "new", "campaign_id": 1, "created_by": "admin1"},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "status": "contacted", "campaign_id": 1, "created_by": "admin1"},
    {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "status": "converted", "campaign_id": 2, "created_by": "admin1"},
    {"id": 4, "name": "Alice Brown", "email": "alice@example.com", "status": "new", "campaign_id": 1, "created_by": "superadmin"},
    {"id": 5, "name": "David Lee", "email": "david@example.com", "status": "new", "campaign_id": 4, "created_by": "superadmin"},
    {"id": 6, "name": "Emma Wilson", "email": "emma@example.com", "status": "contacted", "campaign_id": 4, "created_by": "superadmin"}
]

# Analytics database
analytics_db = [
    {"id": 1, "metric": "campaign_performance", "value": 85.2, "period": "monthly", "campaign_id": 1, "date": "2026-02-01", "created_by": "admin1"},
    {"id": 2, "metric": "lead_conversion", "value": 12.5, "period": "weekly", "campaign_id": 1, "date": "2026-02-15", "created_by": "admin1"},
    {"id": 3, "metric": "engagement_rate", "value": 68.4, "period": "monthly", "channel_id": 1, "date": "2026-02-01", "created_by": "admin1"},
    {"id": 4, "metric": "roi", "value": 245.6, "period": "quarterly", "campaign_id": 2, "date": "2026-01-01", "created_by": "admin1"},
    {"id": 5, "metric": "click_through_rate", "value": 8.9, "period": "weekly", "campaign_id": 1, "date": "2026-02-15", "created_by": "superadmin"},
    {"id": 6, "metric": "cost_per_lead", "value": 45.3, "period": "monthly", "campaign_id": 3, "date": "2026-02-01", "created_by": "superadmin"}
]

# Scheduler database
scheduler_db = [
    {"id": 1, "campaign_id": 1, "task_name": "Summer Sale Launch", "scheduled_date": "2026-03-01", "scheduled_time": "10:00", "status": "pending", "priority": "high", "created_by": "admin1"},
    {"id": 2, "campaign_id": 2, "task_name": "Product Launch Email", "scheduled_date": "2026-02-28", "scheduled_time": "14:30", "status": "scheduled", "priority": "medium", "created_by": "admin1"},
    {"id": 3, "campaign_id": 1, "task_name": "Social Media Posts", "scheduled_date": "2026-02-27", "scheduled_time": "09:00", "status": "completed", "priority": "low", "created_by": "admin1"},
    {"id": 4, "campaign_id": 3, "task_name": "Holiday Special Prep", "scheduled_date": "2026-03-15", "scheduled_time": "11:00", "status": "pending", "priority": "high", "created_by": "superadmin"},
    {"id": 5, "campaign_id": 1, "task_name": "Follow-up Campaign", "scheduled_date": "2026-03-05", "scheduled_time": "16:00", "status": "pending", "priority": "medium", "created_by": "superadmin"}
]

# Settings database (user-specific settings)
user_settings_db = {
    "admin1": {
        "notifications": {
            "email_alerts": True,
            "sms_alerts": False,
            "push_notifications": True,
            "weekly_reports": True
        },
        "preferences": {
            "theme": "light",
            "language": "en",
            "timezone": "UTC",
            "date_format": "MM/DD/YYYY"
        },
        "security": {
            "session_timeout": 30,
            "two_factor_auth": False,
            "login_notifications": True
        }
    },
    "superadmin": {
        "notifications": {
            "email_alerts": True,
            "sms_alerts": True,
            "push_notifications": True,
            "weekly_reports": True
        },
        "preferences": {
            "theme": "dark",
            "language": "en",
            "timezone": "UTC",
            "date_format": "DD/MM/YYYY"
        },
        "security": {
            "session_timeout": 60,
            "two_factor_auth": True,
            "login_notifications": True
        }
    },
    "marketing1": {
        "notifications": {
            "email_alerts": True,
            "sms_alerts": False,
            "push_notifications": True,
            "weekly_reports": True
        },
        "preferences": {
            "theme": "light",
            "language": "en",
            "timezone": "UTC",
            "date_format": "MM/DD/YYYY"
        },
        "security": {
            "session_timeout": 30,
            "two_factor_auth": False,
            "login_notifications": True
        }
    },
    "content1": {
        "notifications": {
            "email_alerts": True,
            "sms_alerts": False,
            "push_notifications": False,
            "weekly_reports": False
        },
        "preferences": {
            "theme": "light",
            "language": "en",
            "timezone": "UTC",
            "date_format": "MM/DD/YYYY"
        },
        "security": {
            "session_timeout": 30,
            "two_factor_auth": False,
            "login_notifications": True
        }
    },
    "sales1": {
        "notifications": {
            "email_alerts": True,
            "sms_alerts": True,
            "push_notifications": True,
            "weekly_reports": True
        },
        "preferences": {
            "theme": "light",
            "language": "en",
            "timezone": "UTC",
            "date_format": "MM/DD/YYYY"
        },
        "security": {
            "session_timeout": 30,
            "two_factor_auth": False,
            "login_notifications": True
        }
    }
}
