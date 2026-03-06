import secrets
import hashlib
from datetime import datetime, timedelta
from constants import OTP_EXPIRY_MINUTES, OTP_LENGTH, users_db, created_users, RESTRICTED_OTP_PATTERNS
import os
from dotenv import load_dotenv
from jose import JWTError, jwt
from constants import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, BREVO_API_KEY, BREVO_SENDER_EMAIL, BREVO_SENDER_NAME, EMAIL_TEMPLATES

# Load environment variables from .env file
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


def generate_otp():
    """Generate a random OTP of specified length, avoiding common patterns"""
    import random
    
    # Generate OTP until we get one that's not restricted
    max_attempts = 10  # Prevent infinite loop
    for attempt in range(max_attempts):
        otp = str(secrets.randbelow(10000)).zfill(OTP_LENGTH)
        
        # Check if OTP is in restricted patterns
        if otp not in RESTRICTED_OTP_PATTERNS:
            return otp
    
    # Fallback: generate a completely random 4-digit number
    # This should rarely be needed due to low probability of hitting restricted patterns
    return str(random.randint(1000, 9999))

def store_otp(otp_storage: dict, email: str, otp: str):
    """Store OTP with expiry time"""
    otp_storage[email] = {
        "otp": otp,
        "expires_at": datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    }

def verify_stored_otp(otp_storage: dict, email: str, otp: str) -> bool:
    """Verify if OTP is valid and not expired"""
    if email not in otp_storage:
        return False
    
    stored_data = otp_storage[email]
    if datetime.now() > stored_data["expires_at"]:
        del otp_storage[email]
        return False
    
    return stored_data["otp"] == otp

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == password_hash

def find_user_by_email(users_db: dict, email: str):
    """Find user by email in users database"""
    for username, user in users_db.items():
        if user["email"] == email:
            return username, user
    return None, None

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength and return (is_valid, error_message)"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "@$!%*?&#" for c in password)
    
    if not has_upper:
        return False, "Password must contain at least 1 uppercase letter (A-Z)"
    
    if not has_lower:
        return False, "Password must contain at least 1 lowercase letter (a-z)"
    
    if not has_digit:
        return False, "Password must contain at least 1 number (0-9)"
    
    if not has_special:
        return False, "Password must contain at least 1 special character (@ $ ! % * ? & # _)"
    
    return True, "Password meets all requirements"

def cleanup_otp(otp_storage: dict, email: str):
    """Remove OTP after successful verification"""
    if email in otp_storage:
        del otp_storage[email]

def send_email(template_key: str, recipient_email: str, template_vars: dict = {}) -> bool:
    """Universal email function that uses templates from constants.py"""
    try:
        # Check if template exists
        if template_key not in EMAIL_TEMPLATES:
            print(f"❌ Email template '{template_key}' not found in EMAIL_TEMPLATES")
            return False
        
        template = EMAIL_TEMPLATES[template_key]
        
        # Check if Brevo API key is configured
        if BREVO_API_KEY == "YOUR_BREVO_API_KEY":
            print("=" * 50)
            print(f"� EMAIL TEMPLATE: {template_key}")
            print("=" * 50)
            print(f"📧 TO: {recipient_email}")
            print(f"� SUBJECT: {template['subject']}")
            print("=" * 50)
            print("⚠️  BREVO API KEY NOT CONFIGURED")
            print("⚠️  Update BREVO_API_KEY in constants.py")
            print("⚠️  Showing email content in terminal for now")
            print("=" * 50)
            return True
        
        # Import Brevo SDK
        import sib_api_v3_sdk
        from sib_api_v3_sdk.rest import ApiException
        
        # Configure Brevo API client
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = BREVO_API_KEY
        
        # Create API instance
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        # Format templates with variables
        html_content = template['html_template'].format(**template_vars)
        text_content = template['text_template'].format(**template_vars)
        subject = template['subject'].format(**template_vars)
        
        # Create email
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": recipient_email}],
            sender={"name": BREVO_SENDER_NAME, "email": BREVO_SENDER_EMAIL},
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
        # Send email
        try:
            api_response = api_instance.send_transac_email(send_smtp_email)
            
            if api_response.message_id:
                print(f"🎉 EMAIL SENT via Brevo!")
                print(f"📧 Template: {template_key}")
                print(f"📧 To: {recipient_email}")
                print(f"� Subject: {subject}")
                print(f"📬 Message ID: {api_response.message_id}")
                print("=" * 50)
                app_logger.info(f"Email '{template_key}' sent successfully to {recipient_email} via Brevo")
                return True
            else:
                print(f"❌ Brevo error: No message ID returned")
                return False
                
        except ApiException as e:
            print(f"❌ Brevo API Error: {e}")
            print(f"🔧 FALLBACK: Showing email in terminal")
            print("=" * 50)
            print(f"📧 Template: {template_key}")
            print(f"📧 To: {recipient_email}")
            print(f"� Subject: {subject}")
            print("=" * 50)
            return False
            
    except ImportError:
        print("❌ Brevo SDK not installed. Run: pip3 install sib-api-v3-sdk")
        print(f"🔧 FALLBACK: Showing email in terminal")
        print("=" * 50)
        print(f"📧 Template: {template_key}")
        print(f"� To: {recipient_email}")
        print("=" * 50)
        return False
        
    except Exception as e:
        app_logger.error(f"Failed to send email: {e}")
        print(f"❌ Error: {e}")
        print(f"🔧 FALLBACK: Showing email in terminal")
        print("=" * 50)
        print(f"📧 Template: {template_key}")
        print(f"📧 To: {recipient_email}")
        print("=" * 50)
        return False

def send_otp_email(recipient_email: str, otp: str, purpose: str = "login") -> bool:
    """Send OTP email using template system"""
    # Get user name from users_db or use default
    user_name = "User"
    user_username = "Unknown"
    user_role = "Unknown"
    
    from constants import DEV_MODE
    from services.mongo_db import mongo_db
    
    if DEV_MODE:
        for username, user in users_db.items():
            if user.get("email") == recipient_email:
                user_name = user.get("name", username)
                user_username = username
                user_role = user.get("role", "Unknown")
                break
    else:
        # Get user from MongoDB
        user = mongo_db.get_user_by_email(recipient_email)
        if user:
            user_name = user.get("name", "User")
            user_username = user.get("username", "Unknown")
            user_role = user.get("role", "Unknown")
    
    from datetime import datetime
    login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    template_vars = {
        "name": user_name,
        "username": user_username,
        "email": recipient_email,
        "role": user_role,
        "login_time": login_time,
        "otp": otp
    }
    
    template_key = f"{purpose}_otp"
    return send_email(template_key, recipient_email, template_vars)

def send_user_created_email(recipient_email: str, user_data: dict) -> bool:
    """Send user creation success email"""
    template_vars = {
        "name": user_data.get("name", "User"),
        "username": user_data.get("username", ""),
        "email": user_data.get("email", ""),
        "password": user_data.get("password", ""),
        "role": user_data.get("role", "")
    }
    
    return send_email("user_created", recipient_email, template_vars)

def send_lead_created_email(recipient_email: str, lead_data: dict, campaign_name: str) -> bool:
    """Send lead creation notification email"""
    from datetime import datetime
    
    template_vars = {
        "name": lead_data.get("name", "User"),
        "lead_name": lead_data.get("name", ""),
        "lead_email": lead_data.get("email", ""),
        "lead_phone": lead_data.get("phone", ""),
        "campaign_name": campaign_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return send_email("lead_created", recipient_email, template_vars)

def send_campaign_created_email(recipient_email: str, campaign_data: dict) -> bool:
    """Send campaign creation notification email"""
    from datetime import datetime
    
    template_vars = {
        "name": campaign_data.get("name", "User"),
        "campaign_name": campaign_data.get("name", ""),
        "platform": campaign_data.get("platform", "Social Media"),
        "launch_date": datetime.now().strftime("%Y-%m-%d"),
        "target_audience": campaign_data.get("target_audience", "General Audience")
    }
    
    return send_email("campaign_created", recipient_email, template_vars)

def send_access_expiring_email(user_data: dict, hours_remaining: int = 24) -> bool:
    """Send email reminder when user access is about to expire"""
    if hours_remaining <= 24:  # Only send if expires in next 24 hours
        template_vars = {
            "name": user_data.get("name", "User"),
            "username": user_data.get("username", ""),
            "hours_remaining": hours_remaining,
            "expiry_date": user_data.get("access_expires_at", "Unknown")
        }
        
        return send_email("access_expiring", user_data.get("email", ""), template_vars)
    
    return True

def send_access_expired_email(user_data: dict) -> bool:
    """Send email when user access has expired"""
    template_vars = {
        "name": user_data.get("name", "User"),
        "username": user_data.get("username", ""),
        "expiry_date": user_data.get("access_expires_at", "Unknown")
    }
    
    return send_email("access_expired", user_data.get("email", ""), template_vars)

from fastapi import HTTPException, status
from services.logger import app_logger
from services.error import APIError

# Role-based authentication middleware
class RoleMiddleware:
    """Middleware for role-based access control"""
    
    @staticmethod
    def get_current_user(token: str) -> dict:
        """Get current user from token"""
        return get_user_from_token(token)
    
    @staticmethod
    def require_role(required_role: str):
        """Decorator to require specific role"""
        def role_checker(current_user: dict):
            user_role = current_user.get("role", "user").strip().lower()
            required_role_clean = required_role.strip().lower()
            
            if user_role != required_role_clean:
                app_logger.warning(f"Access denied: {user_role} attempted to access {required_role_clean} endpoint")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. {required_role_clean} role required."
                )
            
            return current_user
        
        return role_checker
    
    @staticmethod
    def require_minimum_role(minimum_role: str):
        """Decorator to require minimum role level"""
        role_hierarchy = {
            "user": 1,
            "admin": 2, 
            "super_admin": 3
        }
        
        def role_checker(current_user: dict):
            user_role = current_user.get("role", "user").strip().lower()
            minimum_role_clean = minimum_role.strip().lower()
            
            user_level = role_hierarchy.get(user_role, 0)
            required_level = role_hierarchy.get(minimum_role_clean, 0)
            
            if user_level < required_level:
                app_logger.warning(f"Access denied: {user_role} (level {user_level}) attempted to access {minimum_role_clean} (level {required_level}) endpoint")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. {minimum_role_clean} or higher role required."
                )
            
            return current_user
        
        return role_checker
    
    @staticmethod
    def check_access_expiration(current_user: dict):
        """Check if user access has expired"""
        access_expires_at = current_user.get("access_expires_at")
        
        if access_expires_at:
            from datetime import datetime
            if datetime.utcnow() > datetime.fromisoformat(access_expires_at.replace('Z', '+00:00')):
                app_logger.warning(f"Access expired for user: {current_user.get('username')}")
                raise APIError.unauthorized("Access expired. Please contact administrator.")
        
        return current_user
    
    @staticmethod
    def check_company_access(current_user: dict, company_id: int):
        """Check if user can access company data"""
        user_role = current_user.get("role", "user")
        user_company = current_user.get("companyid", 0)
        
        # Super admins can access all companies
        if user_role == "super_admin":
            return current_user
        
        # Admins and users can only access their own company
        if user_company != company_id:
            app_logger.warning(f"Company access denied: user {current_user.get('username')} (company {user_company}) attempted to access company {company_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only access your own company data."
            )
        
        return current_user

# Role check decorators
require_super_admin = RoleMiddleware.require_role("super_admin")
require_admin = RoleMiddleware.require_role("admin") 
require_minimum_admin = RoleMiddleware.require_minimum_role("admin")
require_user = RoleMiddleware.require_role("user")

def create_access_token(data, expires_delta: timedelta = None):
    """Create JWT access token"""
    # Handle both string and dict inputs
    if isinstance(data, str):
        to_encode = {"sub": data}
    else:
        to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_user_from_token(token: str) -> dict:
    """Get current user from JWT token"""
    payload = verify_token(token)
    if payload is None:
        return None
    
    username = payload.get("sub")
    if username is None:
        return None
    
    # Check if we should use MongoDB or mock data
    from constants import DEV_MODE
    from services.mongo_db import mongo_db
    
    if DEV_MODE:
        # Use mock data
        user = users_db.get(username)
        if user is None:
            user = created_users.get(username)
    else:
        # Use MongoDB
        user = mongo_db.get_user_by_username(username)
    
    if user is None:
        return None
    
    return user
