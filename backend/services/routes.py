from fastapi import status
from pydantic import BaseModel
from typing import Optional, Union
from datetime import datetime
import hashlib
from constants import users_db, otp_storage, channels_db, campaigns_db, leads_db, analytics_db, scheduler_db, user_settings_db, DEV_MODE
from services.util import (
    verify_password, hash_password, generate_otp, store_otp, 
    verify_stored_otp, find_user_by_email, cleanup_otp, send_otp_email,
    create_access_token, get_current_user, validate_password_strength,
    RoleMiddleware, require_super_admin, require_admin, require_minimum_admin
)
from services.response import LoginResponse, OTPResponse, PasswordResetResponse, UserProfileResponse, ChannelResponse, CampaignResponse, LeadResponse, DashboardStatsResponse, AnalyticsResponse, SchedulerResponse, SettingsResponse
from services.error import APIError
from services.logger import app_logger
from stored_procedures.dashboard_service import dashboard_service
from datetime import datetime, timedelta

# User service functions (moved from separate file to keep structure simple)
def create_user_service(username, email, password, name, role, companyid, created_by, access_hours=None):
    """Create a new user with optional time-based access"""
    try:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Calculate access expiration if specified
        access_expires_at = None
        if access_hours and role != 'super_admin':  # Super admins don't expire
            access_expires_at = datetime.utcnow() + timedelta(hours=access_hours)
        
        if DEV_MODE:
            # Mock implementation
            if username in users_db:
                raise Exception("Username already exists")
            
            new_user = {
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "name": name,
                "role": role,
                "companyid": companyid,
                "activitystatus": True,
                "access_expires_at": access_expires_at.isoformat() if access_expires_at else None,
                "created_by": created_by
            }
            
            users_db[username] = new_user
            app_logger.info(f"User {username} created with role {role}")
            return 1
        else:
            # Database implementation
            from stored_procedures.user_service import user_service
            return user_service.create_user(username, email, password, name, role, companyid, created_by, access_hours)
            
    except Exception as e:
        app_logger.error(f"Failed to create user {username}: {e}")
        raise e

def clear_all_users_except_super_admin():
    """Clear all users except super admin"""
    try:
        if DEV_MODE:
            # Mock implementation
            users_to_keep = {}
            for username, user in users_db.items():
                if user["role"] == "super_admin":
                    users_to_keep[username] = user
            
            users_db.clear()
            users_db.update(users_to_keep)
            
            return len(users_to_keep)
        else:
            # Database implementation
            from stored_procedures.user_service import user_service
            return user_service.clear_all_users_except_super_admin()
            
    except Exception as e:
        app_logger.error(f"Failed to clear users: {e}")
        raise e

def get_user_profile_service(token: str) -> dict:
    """Get current user profile"""
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid token")
    
    if DEV_MODE:
        # Mock implementation
        user = users_db.get(current_user["username"])
        if not user:
            raise APIError.not_found("User not found")
        
        # Remove sensitive data
        profile_data = {
            "username": user["username"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "companyid": user["companyid"],
            "activitystatus": user["activitystatus"],
            "access_expires_at": user["access_expires_at"],
            "created_by": user["created_by"]
        }
        app_logger.info(f"Profile requested for user: {current_user['username']}")
        return profile_data
    else:
        # Database implementation
        try:
            from stored_procedures.user_service import user_service
            profile_data = user_service.get_user_profile(current_user["username"])
            app_logger.info(f"Profile requested for user: {current_user['username']}")
            return profile_data
            
        except Exception as e:
            app_logger.error(f"Failed to get user profile: {e}")
            raise APIError.internal("Failed to get user profile")

def health_check() -> dict:
    """System health check"""
    try:
        if DEV_MODE:
            # Mock implementation
            status = {
                "status": "healthy",
                "message": "Service operational",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "environment": "development",
                "database": "mock",
                "services": {
                    "authentication": "operational",
                    "user_management": "operational",
                    "dashboard": "operational",
                    "admin_panel": "operational"
                }
            }
            app_logger.info("Health check requested - mock mode")
            return status
        else:
            # Database implementation
            from stored_procedures.user_service import user_service
            db_status = user_service.check_database_health()
            status = {
                "status": "healthy" if db_status else "degraded",
                "message": "Service operational" if db_status else "Service degraded",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "environment": "production",
                "database": "mysql" if db_status else "error",
                "services": {
                    "authentication": "operational",
                    "user_management": "operational" if db_status else "down",
                    "dashboard": "operational",
                    "admin_panel": "operational" if db_status else "down"
                }
            }
            app_logger.info(f"Health check requested - database status: {db_status}")
            return status
            
    except Exception as e:
        app_logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": "Service unavailable",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "environment": "development" if DEV_MODE else "production",
            "error": str(e)
        }

def verify_user_credentials_service(username, password):
    """Verify user credentials and check access expiration"""
    try:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if DEV_MODE:
            # Mock implementation
            user = users_db.get(username)
            if not user or user["password_hash"] != password_hash:
                return None
            
            # Check if access has expired
            if user.get('access_expires_at'):
                if datetime.utcnow() > datetime.fromisoformat(user['access_expires_at'].replace('Z', '+00:00')):
                    app_logger.warning(f"Access expired for user: {username}")
                    return None
            
            return user
        else:
            # Database implementation
            from stored_procedures.user_service import user_service
            return user_service.verify_user_credentials(username, password)
            
    except Exception as e:
        app_logger.error(f"Failed to verify credentials for {username}: {e}")
        raise e

class APIRequest(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    otp: Optional[str] = None

def login_user(request: APIRequest) -> LoginResponse:
    """Authenticate user and return login response with JWT token"""
    username = request.username
    password = request.password
    
    # Validate required fields
    if not username or not password:
        raise APIError.bad_request("Username and password are required")
    
    if DEV_MODE:
        app_logger.info("Using mock data for login (DEV_MODE=True)")
        # Mock authentication
        user = users_db.get(username)
        if not user or not verify_password(password, user["password_hash"]):
            raise APIError.unauthorized("Invalid username or password")
    else:
        app_logger.info("Using database for login (DEV_MODE=False)")
        # Database authentication
        user = verify_user_credentials_service(username, password)
        if not user:
            raise APIError.unauthorized("Invalid username or password")
    
    # Generate JWT token with complete user data
    if DEV_MODE:
        # Add 'sub' field for JWT standard compliance
        user_data = user.copy()
        user_data["sub"] = user["username"]
    else:
        # Get user data from database service
        user_data = {
            "sub": user["username"],  # Use 'sub' as per JWT standard
            "username": user["username"],
            "email": user["email"],
            "name": user.get("name", ""),
            "role": user.get("role", "user"),
            "companyid": user.get("companyid", 0),
            "activitystatus": user.get("activitystatus", True),
            "access_expires_at": user.get("access_expires_at"),
            "created_by": user.get("created_by")
        }
    
    access_token = create_access_token(user_data)
    
    return LoginResponse(
        message="Login successful",
        access_token=access_token,
        token_type="bearer",
        user={
            "username": user["username"],
            "email": user["email"],
            "name": user.get("name", ""),
            "role": user.get("role", "user"),
            "companyid": user.get("companyid", 0),
            "activitystatus": user.get("activitystatus", True)
        }
    )

def send_forgot_password_otp(request: APIRequest) -> OTPResponse:
    """Send OTP to user's email for password reset"""
    email = request.email
    
    # Validate required fields
    if not email:
        raise APIError.bad_request("Email is required")
    
    if DEV_MODE:
        app_logger.info("Using mock data for OTP generation (DEV_MODE=True)")
        # Mock user check
        username, user = find_user_by_email(users_db, email)
        if not user:
            raise APIError.not_found("Email not found")
    else:
        app_logger.info("Using database for OTP generation (DEV_MODE=False)")
        # Database user check
        user = user_service.get_user_by_email(email)
        if not user:
            raise APIError.not_found("Email not found")
    
    # Generate and store OTP
    otp = generate_otp()
    store_otp(otp_storage, email, otp)
    
    # Send email with OTP
    email_sent = send_otp_email(email, otp)
    
    if email_sent:
        app_logger.info(f"OTP {otp} sent successfully to {email}")
    else:
        app_logger.error(f"Failed to send OTP to {email}. OTP: {otp}")
    
    return OTPResponse(message="OTP sent to your email")

def verify_otp(request: APIRequest) -> OTPResponse:
    """Verify OTP for password reset"""
    email = request.email
    otp = request.otp
    
    # Validate required fields
    if not email or not otp:
        raise APIError.bad_request("Email and OTP are required")
    
    if DEV_MODE:
        app_logger.info("Using mock data for OTP verification (DEV_MODE=True)")
        # Mock OTP verification
        if not verify_stored_otp(otp_storage, email, otp):
            raise APIError.unauthorized("Invalid or expired OTP")
    else:
        app_logger.info("Using database for OTP verification (DEV_MODE=False)")
        # TODO: Implement database OTP verification here
        if not verify_stored_otp(otp_storage, email, otp):  # Temporary - replace with database call
            raise APIError.unauthorized("Invalid or expired OTP")
    
    return OTPResponse(message="OTP verified successfully")

def reset_password(request: APIRequest) -> PasswordResetResponse:
    """Reset password with new credentials"""
    email = request.email
    new_password = request.password
    
    # Validate required fields
    if not email or not new_password:
        raise APIError.bad_request("Email and new password are required")
    
    # Validate password strength
    if not validate_password_strength(new_password):
        raise APIError.bad_request("Password must be at least 8 characters long and contain uppercase, lowercase, and numbers")
    
    if DEV_MODE:
        app_logger.info("Using mock data for password reset (DEV_MODE=True)")
        # Mock password reset
        username, user = find_user_by_email(users_db, email)
        if not user:
            raise APIError.not_found("Email not found")
        
        # Update password in mock database
        user["password_hash"] = hash_password(new_password)
    else:
        app_logger.info("Using database for password reset (DEV_MODE=False)")
        # Database password reset
        user = user_service.get_user_by_email(email)
        if not user:
            raise APIError.not_found("Email not found")
        
        # Update password in database
        user_service.update_password(email, new_password)
    
    # Cleanup OTP after successful password reset
    cleanup_otp(otp_storage, email)
    
    return PasswordResetResponse(message="Password reset successfully")

def get_user_profile(token: str) -> UserProfileResponse:
    """Get current user profile (protected endpoint)"""
    if DEV_MODE:
        app_logger.info("Using mock data for user profile (DEV_MODE=True)")
        # Mock user profile
        user = get_current_user(token)
        if not user:
            raise APIError.unauthorized("Invalid or expired token")
    else:
        app_logger.info("Using database for user profile (DEV_MODE=False)")
        # TODO: Implement database user profile here
        user = get_current_user(token)  # Temporary - replace with database call
        if not user:
            raise APIError.unauthorized("Invalid or expired token")
    
    return UserProfileResponse(
        message="Profile retrieved successfully",
        user={
            "username": user["username"],
            "email": user["email"]
        }
    )

def get_channels(token: str) -> ChannelResponse:
    """Get channels based on user role and permissions"""
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid or expired token")
    
    if DEV_MODE:
        app_logger.info("Using mock data for channels (DEV_MODE=True)")
        
        # Filter channels based on user role
        if current_user["role"] == "super_admin":
            # Super admin sees all channels
            filtered_channels = channels_db
        elif current_user["role"] == "admin":
            # Admin sees only channels they created
            filtered_channels = [channel for channel in channels_db 
                                if channel.get("created_by") == current_user["username"]]
        else:
            # Other roles see channels based on permissions
            filtered_channels = channels_db  # For now, show all - can be enhanced with permissions
        
        return ChannelResponse(
            message="Channels retrieved successfully (mock data)",
            channels=filtered_channels
        )
    else:
        app_logger.info("Using database for channels (DEV_MODE=False)")
        channels = dashboard_service.get_channels()
        return ChannelResponse(
            message="Channels retrieved successfully (database)",
            channels=channels
        )

def get_campaigns(token: str) -> CampaignResponse:
    """Get campaigns based on user role and permissions"""
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid or expired token")
    
    if DEV_MODE:
        app_logger.info("Using mock data for campaigns (DEV_MODE=True)")
        
        # Filter campaigns based on user role
        if current_user["role"] == "super_admin":
            # Super admin sees all campaigns
            filtered_campaigns = campaigns_db
        elif current_user["role"] == "admin":
            # Admin sees only campaigns they created
            filtered_campaigns = [campaign for campaign in campaigns_db 
                                if campaign.get("created_by") == current_user["username"]]
        else:
            # Other roles see campaigns based on permissions
            filtered_campaigns = campaigns_db  # For now, show all - can be enhanced with permissions
        
        return CampaignResponse(
            message="Campaigns retrieved successfully (mock data)",
            campaigns=filtered_campaigns
        )
    else:
        app_logger.info("Using database for campaigns (DEV_MODE=False)")
        campaigns = dashboard_service.get_campaigns()
        return CampaignResponse(
            message="Campaigns retrieved successfully (database)",
            campaigns=campaigns
        )

def get_leads(token: str) -> LeadResponse:
    """Get leads based on user role and permissions"""
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid or expired token")
    
    if DEV_MODE:
        app_logger.info("Using mock data for leads (DEV_MODE=True)")
        
        # Filter leads based on user role
        if current_user["role"] == "super_admin":
            # Super admin sees all leads
            filtered_leads = leads_db
        elif current_user["role"] == "admin":
            # Admin sees only leads they created
            filtered_leads = [lead for lead in leads_db 
                            if lead.get("created_by") == current_user["username"]]
        else:
            # Other roles see leads based on permissions
            filtered_leads = leads_db  # For now, show all - can be enhanced with permissions
        
        return LeadResponse(
            message="Leads retrieved successfully (mock data)",
            leads=filtered_leads
        )
    else:
        app_logger.info("Using database for leads (DEV_MODE=False)")
        leads = dashboard_service.get_leads()
        return LeadResponse(
            message="Leads retrieved successfully (database)",
            leads=leads
        )

def get_dashboard_stats() -> DashboardStatsResponse:
    """Get dashboard statistics"""
    if DEV_MODE:
        app_logger.info("Using mock data for dashboard stats (DEV_MODE=True)")
        connected_channels = len([ch for ch in channels_db if ch.get("connected", False)])
        active_campaigns = len([ca for ca in campaigns_db if ca.get("status") == "active"])
        total_leads = len(leads_db)
        
        return DashboardStatsResponse(
            message="Dashboard stats retrieved successfully (mock data)",
            stats={
                "channels": connected_channels,
                "campaigns": active_campaigns,
                "leads": total_leads
            }
        )
    else:
        app_logger.info("Using database for dashboard stats (DEV_MODE=False)")
        stats = dashboard_service.get_dashboard_stats()
        return DashboardStatsResponse(
            message="Dashboard stats retrieved successfully (database)",
            stats=stats
        )

def get_analytics(token: str) -> AnalyticsResponse:
    """Get analytics based on user role and permissions"""
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid or expired token")
    
    if DEV_MODE:
        app_logger.info("Using mock data for analytics (DEV_MODE=True)")
        
        # Filter analytics based on user role
        if current_user["role"] == "super_admin":
            # Super admin sees all analytics
            filtered_analytics = analytics_db
        elif current_user["role"] == "admin":
            # Admin sees only analytics they created
            filtered_analytics = [analytic for analytic in analytics_db 
                                if analytic.get("created_by") == current_user["username"]]
        else:
            # Other roles see analytics based on permissions
            filtered_analytics = analytics_db  # For now, show all - can be enhanced with permissions
        
        return AnalyticsResponse(
            message="Analytics retrieved successfully (mock data)",
            analytics=filtered_analytics
        )
    else:
        app_logger.info("Using database for analytics (DEV_MODE=False)")
        # TODO: Implement database analytics retrieval
        return AnalyticsResponse(
            message="Analytics retrieved successfully (database)",
            analytics=[]
        )

def get_scheduler(token: str) -> SchedulerResponse:
    """Get scheduler data based on user role and permissions"""
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid or expired token")
    
    if DEV_MODE:
        app_logger.info("Using mock data for scheduler (DEV_MODE=True)")
        
        # Filter schedules based on user role
        if current_user["role"] == "super_admin":
            # Super admin sees all schedules
            filtered_schedules = scheduler_db
        elif current_user["role"] == "admin":
            # Admin sees only schedules they created
            filtered_schedules = [schedule for schedule in scheduler_db 
                                if schedule.get("created_by") == current_user["username"]]
        else:
            # Other roles see schedules based on permissions
            filtered_schedules = scheduler_db  # For now, show all - can be enhanced with permissions
        
        return SchedulerResponse(
            message="Scheduler data retrieved successfully (mock data)",
            schedules=filtered_schedules
        )
    else:
        app_logger.info("Using database for scheduler (DEV_MODE=False)")
        # TODO: Implement database scheduler retrieval
        return SchedulerResponse(
            message="Scheduler data retrieved successfully (database)",
            schedules=[]
        )

def get_settings(token: str) -> SettingsResponse:
    """Get user settings"""
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid or expired token")
    
    if DEV_MODE:
        app_logger.info("Using mock data for settings (DEV_MODE=True)")
        
        # Get user-specific settings
        username = current_user["username"]
        user_settings = user_settings_db.get(username, {
            "notifications": {"email_alerts": True, "sms_alerts": False, "push_notifications": True, "weekly_reports": True},
            "preferences": {"theme": "light", "language": "en", "timezone": "UTC", "date_format": "MM/DD/YYYY"},
            "security": {"session_timeout": 30, "two_factor_auth": False, "login_notifications": True}
        })
        
        return SettingsResponse(
            message="Settings retrieved successfully (mock data)",
            settings=user_settings
        )
    else:
        app_logger.info("Using database for settings (DEV_MODE=False)")
        # TODO: Implement database settings retrieval
        return SettingsResponse(
            message="Settings retrieved successfully (database)",
            settings={}
        )

# Role-based management endpoints

class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str
    name: str
    role: str  # 'admin' or 'user'
    companyid: int
    access_hours: Optional[int] = None  # Time-based access in hours

class ExtendAccessRequest(BaseModel):
    user_id: int
    hours: int

def create_user(request: CreateUserRequest, token: str) -> dict:
    """Create a new user (super_admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_super_admin(current_user)
    
    if DEV_MODE:
        # Mock implementation
        if request.username in users_db:
            raise APIError.bad_request("Username already exists")
        
        # Create mock user
        new_user = {
            "username": request.username,
            "email": request.email,
            "password_hash": hashlib.sha256(request.password.encode()).hexdigest(),
            "name": request.name,
            "role": request.role,
            "companyid": request.companyid,
            "activitystatus": True,
            "access_expires_at": None,
            "created_by": current_user["username"]
        }
        
        users_db[request.username] = new_user
        app_logger.info(f"User {request.username} created with role {request.role}")
        
        return {
            "message": "User created successfully",
            "user": {
                "username": new_user["username"],
                "email": new_user["email"],
                "name": new_user["name"],
                "role": new_user["role"],
                "companyid": new_user["companyid"]
            }
        }
    else:
        # Database implementation
        try:
            current_user_id = current_user.get("id", 1)  # Get current user ID
            rows_affected = create_user_service(
                request.username, request.email, request.password,
                request.name, request.role, request.companyid,
                current_user_id, request.access_hours
            )
            
            if rows_affected > 0:
                return {
                    "message": "User created successfully",
                    "user": {
                        "username": request.username,
                        "email": request.email,
                        "name": request.name,
                        "role": request.role,
                        "companyid": request.companyid
                    }
                }
            else:
                raise APIError.internal("Failed to create user")
                
        except Exception as e:
            app_logger.error(f"Failed to create user: {e}")
            raise APIError.internal("Failed to create user")

def get_users(token: str, role_filter: Optional[str] = None) -> dict:
    """Get users created by current user (super_admin and admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_minimum_admin(current_user)
    
    if DEV_MODE:
        # Mock implementation
        if current_user["role"] == "super_admin":
            # Super admin can see all users
            users_list = list(users_db.values())
        else:
            # Admin can only see users they created
            users_list = [u for u in users_db.values() 
                         if u.get("created_by") == current_user["username"]]
        
        if role_filter:
            users_list = [u for u in users_list if u.get("role") == role_filter]
        
        # Remove sensitive data
        safe_users = []
        for user in users_list:
            safe_user = {
                "username": user["username"],
                "email": user["email"],
                "name": user["name"],
                "role": user["role"],
                "companyid": user["companyid"],
                "activitystatus": user["activitystatus"],
                "access_expires_at": user.get("access_expires_at"),
                "created_by": user.get("created_by")
            }
            safe_users.append(safe_user)
        
        return {
            "message": "Users retrieved successfully",
            "users": safe_users
        }
    else:
        # Database implementation
        try:
            current_user_id = current_user.get("id", 1)
            users_list = user_service.get_users_by_creator(current_user_id, role_filter)
            
            return {
                "message": "Users retrieved successfully",
                "users": users_list
            }
            
        except Exception as e:
            app_logger.error(f"Failed to get users: {e}")
            raise APIError.internal("Failed to get users")

def extend_user_access(request: ExtendAccessRequest, token: str) -> dict:
    """Extend user access (super_admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_super_admin(current_user)
    
    if DEV_MODE:
        # Mock implementation
        user_found = False
        for user in users_db.values():
            if user.get("id") == request.user_id or user["username"] == str(request.user_id):
                user_found = True
                # In mock, we'll just set a future expiration
                from datetime import datetime, timedelta
                user["access_expires_at"] = (datetime.utcnow() + timedelta(hours=request.hours)).isoformat()
                app_logger.info(f"Access extended for user {user['username']} by {request.hours} hours")
                break
        
        if not user_found:
            raise APIError.not_found("User not found")
        
        return {"message": "User access extended successfully"}
    else:
        # Database implementation
        try:
            rows_affected = user_service.extend_user_access(request.user_id, request.hours)
            if rows_affected > 0:
                return {"message": "User access extended successfully"}
            else:
                raise APIError.not_found("User not found")
                
        except Exception as e:
            app_logger.error(f"Failed to extend user access: {e}")
            raise APIError.internal("Failed to extend user access")

def deactivate_user(user_id, token: str) -> dict:
    """Deactivate a user (super_admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_super_admin(current_user)
    
    if DEV_MODE:
        # Mock implementation
        user_found = False
        for user in users_db.values():
            # Handle both numeric ID and username
            if (user.get("id") == user_id or 
                user["username"] == str(user_id) or 
                user["username"] == user_id):
                user_found = True
                user["activitystatus"] = False
                app_logger.info(f"User {user['username']} deactivated")
                break
        
        if not user_found:
            raise APIError.not_found("User not found")
        
        return {"message": "User deactivated successfully"}
    else:
        # Database implementation
        try:
            rows_affected = user_service.deactivate_user(user_id)
            if rows_affected > 0:
                return {"message": "User deactivated successfully"}
            else:
                raise APIError.not_found("User not found")
                
        except Exception as e:
            app_logger.error(f"Failed to deactivate user: {e}")
            raise APIError.internal("Failed to deactivate user")

def clear_all_data(token: str) -> dict:
    """Clear all user data (super_admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_super_admin(current_user)
    
    if DEV_MODE:
        # Mock implementation - clear all users except super admin
        users_to_keep = {}
        for username, user in users_db.items():
            if user["role"] == "super_admin":
                users_to_keep[username] = user
        
        users_db.clear()
        users_db.update(users_to_keep)
        
        app_logger.info("All user data cleared (except super admin)")
        return {"message": "All data cleared successfully"}
    else:
        # Database implementation
        try:
            from stored_procedures.user_service import user_service
            # Delete all non-super admin users
            rows_affected = user_service.clear_all_users_except_super_admin()
            app_logger.info(f"Cleared {rows_affected} users from database")
            return {"message": "All data cleared successfully"}
            
        except Exception as e:
            app_logger.error(f"Failed to clear data: {e}")
            raise APIError.internal("Failed to clear data")

# ------------------- Role Management Models -------------------

class RoleRequest(BaseModel):
    """Request model for creating/updating roles"""
    role_name: str
    permissions: Optional[dict] = None

class PermissionUpdateRequest(BaseModel):
    """Request model for updating role permissions"""
    role_key: str
    permissions: dict

class RoleResponse(BaseModel):
    """Response model for role data"""
    roles: list
    permissions: dict

# ------------------- Role Management Services -------------------

def get_roles_service(token: str) -> dict:
    """Get all roles and their permissions"""
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid or expired token")
    require_super_admin(current_user)
    
    if DEV_MODE:
        # Mock implementation - use in-memory roles storage
        if not hasattr(get_roles_service, 'roles_db'):
            get_roles_service.roles_db = []
        if not hasattr(get_roles_service, 'permissions_db'):
            get_roles_service.permissions_db = {}
        
        return {
            "roles": get_roles_service.roles_db,
            "permissions": get_roles_service.permissions_db
        }
    else:
        # Database implementation
        try:
            from stored_procedures.role_service import role_service
            roles_data = role_service.get_all_roles()
            return roles_data
        except Exception as e:
            app_logger.error(f"Failed to get roles: {e}")
            raise APIError.internal("Failed to get roles")

def create_role_service(token: str, role_request: RoleRequest) -> dict:
    """Create a new role"""
    import re
    
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid or expired token")
    require_super_admin(current_user)
    
    role_name = role_request.role_name.strip()
    if not role_name:
        raise APIError.bad_request("Role name is required")
    
    # Convert role name to key format
    role_key = re.sub(r'\s+', '_', role_name.lower())
    
    if DEV_MODE:
        # Mock implementation
        if not hasattr(get_roles_service, 'roles_db'):
            get_roles_service.roles_db = []
        if not hasattr(get_roles_service, 'permissions_db'):
            get_roles_service.permissions_db = {}
        
        # Check if role already exists
        if role_key in get_roles_service.roles_db:
            raise APIError.bad_request("Role already exists")
        
        # Add role
        get_roles_service.roles_db.append(role_key)
        
        # Initialize default permissions
        modules = ["role_management", "campaigns", "analytics", "leads", "channels", "scheduler"]
        default_permissions = {}
        for module in modules:
            default_permissions[module] = {
                "Create": False,
                "Read": False, 
                "Update": False,
                "Delete": False
            }
        
        get_roles_service.permissions_db[role_key] = default_permissions
        
        app_logger.info(f"Role {role_name} created successfully")
        return {"message": f"Role '{role_name}' created successfully", "role_key": role_key}
    else:
        # Database implementation
        try:
            from stored_procedures.role_service import role_service
            result = role_service.create_role(role_name, role_request.permissions or {})
            app_logger.info(f"Role {role_name} created successfully")
            return result
        except Exception as e:
            app_logger.error(f"Failed to create role: {e}")
            raise APIError.internal("Failed to create role")

def update_role_service(token: str, role_key: str, role_request: RoleRequest) -> dict:
    """Update an existing role"""
    import re
    
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid or expired token")
    require_super_admin(current_user)
    
    new_role_name = role_request.role_name.strip()
    if not new_role_name:
        raise APIError.bad_request("Role name is required")
    
    new_role_key = re.sub(r'\s+', '_', new_role_name.lower())
    
    if DEV_MODE:
        # Mock implementation
        if not hasattr(get_roles_service, 'roles_db'):
            get_roles_service.roles_db = []
        if not hasattr(get_roles_service, 'permissions_db'):
            get_roles_service.permissions_db = {}
        
        # Check if role exists
        if role_key not in get_roles_service.roles_db:
            raise APIError.not_found("Role not found")
        
        # Check if new role name conflicts with existing role (excluding current role)
        if new_role_key != role_key and new_role_key in get_roles_service.roles_db:
            raise APIError.bad_request("Role with this name already exists")
        
        # Update role key if changed
        if new_role_key != role_key:
            # Remove old role key and add new one
            get_roles_service.roles_db.remove(role_key)
            get_roles_service.roles_db.append(new_role_key)
            
            # Transfer permissions
            get_roles_service.permissions_db[new_role_key] = get_roles_service.permissions_db[role_key]
            del get_roles_service.permissions_db[role_key]
        
        app_logger.info(f"Role {new_role_name} updated successfully")
        return {"message": f"Role '{new_role_name}' updated successfully", "role_key": new_role_key}
    else:
        # Database implementation
        try:
            from stored_procedures.role_service import role_service
            result = role_service.update_role(role_key, new_role_name, role_request.permissions or {})
            app_logger.info(f"Role {new_role_name} updated successfully")
            return result
        except Exception as e:
            app_logger.error(f"Failed to update role: {e}")
            raise APIError.internal("Failed to update role")

def delete_role_service(token: str, role_key: str) -> dict:
    """Delete a role"""
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid or expired token")
    require_super_admin(current_user)
    
    if DEV_MODE:
        # Mock implementation
        if not hasattr(get_roles_service, 'roles_db'):
            get_roles_service.roles_db = []
        if not hasattr(get_roles_service, 'permissions_db'):
            get_roles_service.permissions_db = {}
        
        # Check if role exists
        if role_key not in get_roles_service.roles_db:
            raise APIError.not_found("Role not found")
        
        # Remove role
        get_roles_service.roles_db.remove(role_key)
        if role_key in get_roles_service.permissions_db:
            del get_roles_service.permissions_db[role_key]
        
        app_logger.info(f"Role {role_key} deleted successfully")
        return {"message": f"Role deleted successfully"}
    else:
        # Database implementation
        try:
            from stored_procedures.role_service import role_service
            result = role_service.delete_role(role_key)
            app_logger.info(f"Role {role_key} deleted successfully")
            return result
        except Exception as e:
            app_logger.error(f"Failed to delete role: {e}")
            raise APIError.internal("Failed to delete role")

def update_permissions_service(token: str, permission_request: PermissionUpdateRequest) -> dict:
    """Update permissions for a specific role"""
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid or expired token")
    require_super_admin(current_user)
    
    role_key = permission_request.role_key
    permissions = permission_request.permissions
    
    if DEV_MODE:
        # Mock implementation
        if not hasattr(get_roles_service, 'permissions_db'):
            get_roles_service.permissions_db = {}
        
        # Check if role exists
        if role_key not in get_roles_service.permissions_db:
            raise APIError.not_found("Role not found")
        
        # Update permissions
        get_roles_service.permissions_db[role_key] = permissions
        
        app_logger.info(f"Permissions updated for role {role_key}")
        return {"message": f"Permissions for '{role_key}' updated successfully"}
    else:
        # Database implementation
        try:
            from stored_procedures.role_service import role_service
            result = role_service.update_role_permissions(role_key, permissions)
            app_logger.info(f"Permissions updated for role {role_key}")
            return result
        except Exception as e:
            app_logger.error(f"Failed to update permissions: {e}")
            raise APIError.internal("Failed to update permissions")
