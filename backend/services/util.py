import secrets
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from constants import OTP_EXPIRY_MINUTES, OTP_LENGTH, users_db
import os
from jose import JWTError, jwt
from constants import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES,SMTP_EMAIL, SMTP_PASSWORD, SMTP_SERVER, SMTP_PORT


def generate_otp():
    """Generate a random OTP of specified length"""
    return str(secrets.randbelow(10000)).zfill(OTP_LENGTH)

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

def send_otp_email(recipient_email: str, otp: str) -> bool:
    """Send OTP email to recipient"""
    try:
        # Get email configuration from constants
        
        sender_email = SMTP_EMAIL
        sender_password = SMTP_PASSWORD
        smtp_server = SMTP_SERVER
        smtp_port = SMTP_PORT
        
        # Check if email credentials are configured (not using defaults)
        if sender_email == "your-email@gmail.com" or sender_password == "your-app-password":
            print(f"Email credentials not configured. OTP for {recipient_email}: {otp}")
            print("To configure email, update SMTP_EMAIL and SMTP_PASSWORD in constants.py")
            return False
        
        # Create email message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = "Social Connect - Password Reset OTP"
        
        # Email body
        body = f"""
        Hello,
        
        You requested a password reset for your Social Connect account.
        
        Your OTP is: {otp}
        
        This OTP will expire in 10 minutes.
        
        If you didn't request this, please ignore this email.
        
        Thanks,
        Social Connect Team
        """
        
        message.attach(MIMEText(body, "plain"))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
            return True
            
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

from fastapi import HTTPException, status
from services.logger import app_logger

# Role-based authentication middleware
class RoleMiddleware:
    """Middleware for role-based access control"""
    
    @staticmethod
    def get_current_user(token: str) -> dict:
        """Get current user from token"""
        try:
            payload = verify_token(token)
            return payload
        except Exception as e:
            app_logger.error(f"Token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def require_role(required_role: str):
        """Decorator to require specific role"""
        def role_checker(current_user: dict):
            user_role = current_user.get("role", "user")
            
            if user_role != required_role:
                app_logger.warning(f"Access denied: {user_role} attempted to access {required_role} endpoint")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. {required_role} role required."
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
            user_role = current_user.get("role", "user")
            user_level = role_hierarchy.get(user_role, 0)
            required_level = role_hierarchy.get(minimum_role, 0)
            
            if user_level < required_level:
                app_logger.warning(f"Access denied: {user_role} (level {user_level}) attempted to access {minimum_role} (level {required_level}) endpoint")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. {minimum_role} or higher role required."
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
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Access expired. Please contact administrator."
                )
        
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

def get_current_user(token: str) -> dict:
    """Get current user from JWT token"""
    payload = verify_token(token)
    if payload is None:
        return None
    
    username = payload.get("sub")
    if username is None:
        return None
    
    user = users_db.get(username)
    if user is None:
        return None
    
    return user
