from fastapi import status, HTTPException
from pydantic import BaseModel
from typing import Optional, Union
from datetime import datetime, timedelta
import hashlib
from constants import users_db, otp_storage, channels_db, campaigns_db, leads_db, analytics_db, scheduler_db, user_settings_db, DEV_MODE
from services.mongo_db import mongo_db
from services.util import (
    verify_password, hash_password, generate_otp, store_otp, 
    verify_stored_otp, find_user_by_email, cleanup_otp, send_otp_email,
    create_access_token, get_user_from_token, validate_password_strength,
    RoleMiddleware, require_super_admin, require_admin, require_minimum_admin,
    send_user_created_email
)
from services.response import LoginResponse, OTPResponse, PasswordResetResponse, UserProfileResponse, ChannelResponse, CampaignResponse, LeadResponse, DashboardStatsResponse, AnalyticsResponse, SchedulerResponse, SettingsResponse
from services.error import APIError
from services.logger import app_logger

# Request Models
class APIRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    otp: Optional[str] = None
    new_password: Optional[str] = None

class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str
    name: str
    role: str
    companyid: Optional[int] = None
    access_hours: Optional[int] = None
    user_type: Optional[str] = None

class ExtendAccessRequest(BaseModel):
    user_id: int
    hours: int

class RoleRequest(BaseModel):
    role_name: str
    role_key: str
    permissions: dict

class PermissionUpdateRequest(BaseModel):
    role_key: str
    permissions: dict

# User Management Functions
def create_user_service(username, email, password, name, role, companyid, created_by, access_hours=None, user_type=None):
    """Create a new user with optional time-based access and user type"""
    try:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Calculate access expiration if specified
        access_expires_at = None
        if access_hours and role != 'super_admin':  # Super admins don't expire
            access_expires_at = datetime.utcnow() + timedelta(hours=access_hours)
        
        # Always determine user_type dynamically based on role, companyid, and created_by
        if role == "super_admin":
            user_type = "platform_owner"
        elif companyid == 0:
            user_type = "self_company_employee"
        elif created_by and created_by != "superadmin":
            user_type = "tenant_employee"
        else:
            user_type = "tenant_user"
        
        # For custom roles (not in predefined types), treat as tenant_user by default
        predefined_roles = ["super_admin", "admin", "user"]
        if role not in predefined_roles:
            # Custom role - determine based on company context
            if companyid == 0:
                user_type = "self_company_employee"
            elif created_by and created_by != "superadmin":
                user_type = "tenant_employee"
            else:
                user_type = "tenant_user"
        
        # Check if we should use MongoDB or mock data
        from constants import DEV_MODE
        from services.mongo_db import mongo_db
        
        new_user = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "name": name,
            "role": role,
            "companyid": companyid,
            "user_type": user_type,
            "activitystatus": True,
            "access_expires_at": access_expires_at.isoformat() if access_expires_at else None,
            "created_by": created_by
        }
        
        if DEV_MODE:
            # Mock implementation
            if username in users_db:
                raise Exception("Username already exists")
            users_db[username] = new_user
        else:
            # MongoDB implementation
            existing_user = mongo_db.get_user_by_username(username)
            if existing_user:
                raise Exception("Username already exists")
            # Create user in MongoDB
            collection = mongo_db.get_collection("users")
            collection.insert_one(new_user)
        
        app_logger.info(f"User {username} created with role {role} and user_type {user_type}")
        return new_user
            
    except Exception as e:
        app_logger.error(f"Failed to create user {username}: {e}")
        raise e

def get_user_profile_service(token: str) -> dict:
    """Get current user profile"""
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid token")
    
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

def health_check() -> dict:
    """System health check"""
    try:
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
        return status
            
    except Exception as e:
        app_logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": "Service unavailable",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "environment": "development",
            "error": str(e)
        }

# Authentication Functions
def login_user(request: APIRequest) -> Union[OTPResponse, LoginResponse]:
    """Authenticate user with optional OTP verification"""
    username = request.username
    password = request.password
    otp = request.otp
    
    if not username or not password:
        raise APIError.bad_request("Username and password are required")
    
    if DEV_MODE:
        app_logger.info("Using mock data for login")
        user = users_db.get(username)
    else:
        app_logger.info("Using MongoDB for login")
        user = mongo_db.get_user_by_username(username)
    
    if not user or not verify_password(password, user["password_hash"]):
        raise APIError.unauthorized("Invalid username or password")
    
    # Check if user access has expired BEFORE allowing login
    try:
        RoleMiddleware.check_access_expiration(user)
    except HTTPException as e:
        raise APIError.unauthorized("Access has expired. Please contact administrator.")
    
    # If OTP is provided, verify it and return JWT token
    if otp:
        # Verify OTP
        if not verify_stored_otp(otp_storage, user["email"], otp):
            raise APIError.unauthorized("Invalid or expired OTP")
        
        cleanup_otp(otp_storage, user["email"])
        
        # Generate JWT token with complete user data including user_type
        user_data = user.copy() if isinstance(user, dict) else dict(user)
        user_data["sub"] = user["username"]
        
        # Always determine user_type dynamically based on role, companyid, and created_by
        if user.get("role") == "super_admin":
            user_data["user_type"] = "platform_owner"
        elif user.get("companyid") == 0:
            user_data["user_type"] = "self_company_employee"
        elif user.get("created_by") and user.get("created_by") != "superadmin":
            user_data["user_type"] = "tenant_employee"
        else:
            user_data["user_type"] = "tenant_user"
        
        # For custom roles (not in predefined types), treat as tenant_user by default
        predefined_roles = ["super_admin", "admin", "user"]
        if user.get("role") not in predefined_roles:
            # Custom role - determine based on company context
            if user.get("companyid") == 0:
                user_data["user_type"] = "self_company_employee"
            elif user.get("created_by") and user.get("created_by") != "superadmin":
                user_data["user_type"] = "tenant_employee"
            else:
                user_data["user_type"] = "tenant_user"
        
        token = create_access_token(user_data)
        
        app_logger.info(f"Login with OTP successful for user: {username}")
        
        return LoginResponse(
            message="Login successful with OTP",
            success=True,
            access_token=token,
            token_type="bearer",
            user={
                "username": user["username"],
                "email": user["email"],
                "name": user["name"],
                "role": user["role"],
                "companyid": user["companyid"],
                "activitystatus": user["activitystatus"]
            },
            # Original superadmin email gets true, others get role-based flags
            is_super_admin=user["email"] == "deelipkumar261997@gmail.com",
            is_admin=user["role"] == "admin",
            is_user=user["role"] == "user"
        )
    else:
        # No OTP provided, generate and send OTP
        otp_code = generate_otp()
        store_otp(otp_storage, user["email"], otp_code)
        
        # In development, log OTP (in production, send email)
        app_logger.info(f"Login OTP for {user['email']}: {otp_code} (development mode)")
        
        try:
            send_otp_email(user["email"], otp_code)
        except Exception as e:
            app_logger.error(f"Failed to send login OTP email: {e}")
        
        app_logger.info(f"Login OTP sent for user: {username}")
        
        return OTPResponse(
            message="Password verified. OTP sent for login verification",
            success=True,
            otp=otp_code  # Only in development
        )

def send_forgot_password_otp(request: APIRequest) -> OTPResponse:
    """Send OTP for password reset"""
    if not request.email:
        raise APIError.bad_request("Email is required")
    
    # Check if we should use MongoDB or mock data
    from constants import DEV_MODE
    from services.mongo_db import mongo_db
    
    if DEV_MODE:
        app_logger.info("Using mock data for forgot password")
        username, user = find_user_by_email(users_db, request.email)
    else:
        app_logger.info("Using MongoDB for forgot password")
        user = mongo_db.get_user_by_email(request.email)
        username = user.get("username") if user else None
    
    if not user:
        raise APIError.not_found("No user found with this email")
    
    # Generate and store OTP
    otp = generate_otp()
    store_otp(otp_storage, request.email, otp)
    
    # In development, log OTP (in production, send email)
    app_logger.info(f"OTP for {request.email}: {otp} (development mode)")
    
    try:
        send_otp_email(request.email, otp, "forgot")
    except Exception as e:
        app_logger.error(f"Failed to send OTP email: {e}")
    
    return OTPResponse(
        message="OTP sent successfully",
        success=True,
        otp=otp  # Only in development
    )

def verify_otp(request: APIRequest) -> OTPResponse:
    """Verify OTP for password reset"""
    if not request.email or not request.otp:
        raise APIError.bad_request("Email and OTP are required")
    
    app_logger.info("Using mock data for OTP verification")
    # Mock OTP verification
    if not verify_stored_otp(otp_storage, request.email, request.otp):
        raise APIError.unauthorized("Invalid or expired OTP")
    
    cleanup_otp(otp_storage, request.email)
    
    return OTPResponse(
        message="OTP verified successfully",
        success=True
    )

def reset_password(request: APIRequest) -> PasswordResetResponse:
    """Reset password with new credentials"""
    if not validate_password_strength(request.new_password)[0]:
        raise APIError.bad_request("Password must be at least 8 characters long and contain uppercase, lowercase, and numbers")
    
    # Check if we should use MongoDB or mock data
    from constants import DEV_MODE
    from services.mongo_db import mongo_db
    
    if DEV_MODE:
        app_logger.info("Using mock data for password reset")
        username, user = find_user_by_email(users_db, request.email)
    else:
        app_logger.info("Using MongoDB for password reset")
        user = mongo_db.get_user_by_email(request.email)
        username = user.get("username") if user else None
    
    if not user:
        raise APIError.not_found("No user found with this email")
    
    # Update password in appropriate database
    new_password_hash = hash_password(request.new_password)
    
    if DEV_MODE:
        # Mock implementation
        user["password_hash"] = new_password_hash
    else:
        # MongoDB implementation
        mongo_db.update_user_password(username, new_password_hash)
    
    return PasswordResetResponse(
        message="Password reset successfully",
        success=True
    )

# Dashboard Functions
def get_channels(token: str) -> ChannelResponse:
    """Get channels based on user role and permissions"""
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid or expired token")
    
    if DEV_MODE:
        app_logger.info("Using mock data for channels")
        all_channels = channels_db
    else:
        app_logger.info("Using MongoDB for channels")
        all_channels = mongo_db.get_channels()
    
    # Filter channels based on user role
    if current_user["role"] == "super_admin":
        # Super admin sees all channels
        filtered_channels = all_channels
    elif current_user["role"] == "admin":
        # Admin sees only channels they created
        filtered_channels = [channel for channel in all_channels 
                           if channel.get("created_by") == current_user["username"]]
    else:
        # Other roles see channels based on permissions
        filtered_channels = all_channels  # For now, show all - can be enhanced with permissions
    
    return ChannelResponse(
        message=f"Channels retrieved successfully ({'mock data' if DEV_MODE else 'MongoDB'})",
        success=True,
        channels=filtered_channels
    )

def get_campaigns(token: str) -> CampaignResponse:
    """Get campaigns based on user role and permissions"""
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid or expired token")
    
    if DEV_MODE:
        app_logger.info("Using mock data for campaigns")
        all_campaigns = campaigns_db
    else:
        app_logger.info("Using MongoDB for campaigns")
        all_campaigns = mongo_db.get_campaigns()
    
    # Filter campaigns based on user role
    if current_user["role"] == "super_admin":
        # Super admin sees all campaigns
        filtered_campaigns = all_campaigns
    elif current_user["role"] == "admin":
        # Admin sees only campaigns they created
        filtered_campaigns = [campaign for campaign in all_campaigns 
                            if campaign.get("created_by") == current_user["username"]]
    else:
        # Other roles see campaigns based on permissions
        filtered_campaigns = all_campaigns  # For now, show all - can be enhanced with permissions
    
    return CampaignResponse(
        message=f"Campaigns retrieved successfully ({'mock data' if DEV_MODE else 'MongoDB'})",
        success=True,
        campaigns=filtered_campaigns
    )

def get_leads(token: str) -> LeadResponse:
    """Get leads based on user role and permissions"""
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid or expired token")
    
    if DEV_MODE:
        app_logger.info("Using mock data for leads")
        all_leads = leads_db
    else:
        app_logger.info("Using MongoDB for leads")
        all_leads = mongo_db.get_leads()
    
    # Filter leads based on user role
    if current_user["role"] == "super_admin":
        # Super admin sees all leads
        filtered_leads = all_leads
    elif current_user["role"] == "admin":
        # Admin sees only leads they created
        filtered_leads = [lead for lead in all_leads 
                         if lead.get("created_by") == current_user["username"]]
    else:
        # Other roles see leads based on permissions
        filtered_leads = all_leads  # For now, show all - can be enhanced with permissions
    
    return LeadResponse(
        message=f"Leads retrieved successfully ({'mock data' if DEV_MODE else 'MongoDB'})",
        success=True,
        leads=filtered_leads
    )

def get_dashboard_stats() -> DashboardStatsResponse:
    """Get dashboard statistics"""
    app_logger.info("Using mock data for dashboard stats")
    connected_channels = len([ch for ch in channels_db if ch.get("connected", False)])
    active_campaigns = len([ca for ca in campaigns_db if ca.get("status") == "active"])
    total_leads = len(leads_db)
    
    return DashboardStatsResponse(
        message="Dashboard stats retrieved successfully (mock data)",
        success=True,
        stats={
            "connected_channels": connected_channels,
            "active_campaigns": active_campaigns,
            "total_leads": total_leads
        }
    )

def get_analytics(token: str) -> AnalyticsResponse:
    """Get analytics based on user role and permissions"""
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid or expired token")
    
    # Use MongoDB for analytics
    from services.mongo_db import mongo_db
    analytics_data = mongo_db.get_analytics()
    
    app_logger.info(f"Using MongoDB for analytics - found {len(analytics_data)} records")
    
    # Filter analytics based on user role
    if current_user["role"] == "super_admin":
        # Super admin sees all analytics
        filtered_analytics = analytics_data
    elif current_user["role"] == "admin":
        # Admin sees only analytics they created
        filtered_analytics = [analytic for analytic in analytics_data 
                           if analytic.get("created_by") == current_user["username"]]
    else:
        # Other roles see analytics based on permissions
        filtered_analytics = analytics_data  # For now, show all - can be enhanced with permissions
    
    return AnalyticsResponse(
        message="Analytics retrieved successfully (MongoDB)",
        success=True,
        analytics=filtered_analytics
    )

def get_scheduler(token: str) -> SchedulerResponse:
    """Get scheduler data based on user role and permissions"""
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid or expired token")
    
    # Use MongoDB for scheduler
    from services.mongo_db import mongo_db
    scheduler_data = mongo_db.get_scheduler()
    
    app_logger.info(f"Using MongoDB for scheduler - found {len(scheduler_data)} records")
    
    # Filter schedules based on user role
    if current_user["role"] == "super_admin":
        # Super admin sees all schedules
        filtered_schedules = scheduler_data
    elif current_user["role"] == "admin":
        # Admin sees only schedules they created
        filtered_schedules = [schedule for schedule in scheduler_data 
                          if schedule.get("created_by") == current_user["username"]]
    else:
        # Other roles see schedules based on permissions
        filtered_schedules = scheduler_data  # For now, show all - can be enhanced with permissions
    
    return SchedulerResponse(
        message="Scheduler retrieved successfully (MongoDB)",
        success=True,
        schedules=filtered_schedules
    )

def get_settings(token: str) -> SettingsResponse:
    """Get user settings"""
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid or expired token")
    
    app_logger.info("Using mock data for settings")
    
    # Get user-specific settings
    username = current_user["username"]
    user_settings = user_settings_db.get(username, {
        "notifications": {"email_alerts": True, "sms_alerts": False, "push_notifications": True, "weekly_reports": True},
        "preferences": {"theme": "light", "language": "en", "timezone": "UTC", "date_format": "MM/DD/YYYY"},
        "security": {"session_timeout": 30, "two_factor_auth": False, "login_notifications": True}
    })
    
    return SettingsResponse(
        message="Settings retrieved successfully (mock data)",
        success=True,
        settings=user_settings
    )

# Role Management Functions
def get_roles_service(token: str) -> dict:
    """Get all roles and permissions (super_admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_super_admin(current_user)
    
    # Get roles from MongoDB
    from services.mongo_db import mongo_db
    roles = mongo_db.get_roles()
    
    return {
        "message": "Roles retrieved successfully from MongoDB",
        "roles": roles
    }

def create_user(request: CreateUserRequest, token: str) -> dict:
    """Create a new user (admin and super_admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_minimum_admin(current_user)
    
    # Create mock user with user_type
    new_user = create_user_service(
        request.username, request.email, request.password,
        request.name, request.role, request.companyid,
        current_user["username"], request.access_hours, request.user_type
    )
    
    # Send welcome email to the new user
    try:
        user_data = {
            "name": new_user["name"],
            "username": new_user["username"],
            "email": new_user["email"],
            "password": request.password,  # Include password in welcome email
            "role": new_user["role"]
        }
        send_user_created_email(new_user["email"], user_data)
        app_logger.info(f"Welcome email sent to new user: {new_user['username']}")
    except Exception as e:
        app_logger.error(f"Failed to send welcome email to {new_user['email']}: {e}")
    
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

def get_users(token: str, role_filter: Optional[str] = None) -> dict:
    """Get users created by current user (super_admin and admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_minimum_admin(current_user)
    
    # Check if we should use MongoDB or mock data
    from constants import DEV_MODE
    from services.mongo_db import mongo_db
    
    if DEV_MODE:
        # Mock implementation
        if current_user["role"] == "super_admin":
            # Super admin can see all users
            users_list = list(users_db.values())
        else:
            # Admin can only see users they created
            users_list = [u for u in users_db.values() 
                         if u.get("created_by") == current_user["username"]]
    else:
        # MongoDB implementation
        if current_user["role"] == "super_admin":
            # Super admin can see all users
            users_list = mongo_db.get_users()
        else:
            # Admin can only see users they created
            users_list = mongo_db.get_users()
            users_list = [u for u in users_list if u.get("created_by") == current_user["username"]]
    
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

def extend_user_access(request: ExtendAccessRequest, token: str) -> dict:
    """Extend user access (super_admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_super_admin(current_user)
    
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

def deactivate_user(user_id, token: str) -> dict:
    """Deactivate a user (super_admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_super_admin(current_user)
    
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

def create_role_service(token: str, request: RoleRequest) -> dict:
    """Create a new role (super_admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_super_admin(current_user)
    
    # Create role in MongoDB
    from services.mongo_db import mongo_db
    
    role_data = {
        "roleId": request.role_key,
        "roleName": request.role_name,
        "permissions": request.permissions
    }
    
    success = mongo_db.create_role(role_data)
    if not success:
        raise Exception(f"Role {request.role_key} already exists or failed to create")
    
    return {
        "message": f"Role {request.role_name} created successfully in MongoDB",
        "role": {
            "roleId": request.role_key,
            "roleName": request.role_name,
            "permissions": request.permissions
        }
    }

def update_role_service(token: str, role_key: str, request: RoleRequest) -> dict:
    """Update an existing role (super_admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_super_admin(current_user)
    
    # Update role in MongoDB
    from services.mongo_db import mongo_db
    
    updates = {
        "roleName": request.role_name,
        "permissions": request.permissions
    }
    
    success = mongo_db.update_role(role_key, updates)
    if not success:
        raise Exception(f"Role {role_key} not found or failed to update")
    
    return {
        "message": f"Role {request.role_name} updated successfully in MongoDB",
        "role": {
            "roleId": role_key,
            "roleName": request.role_name,
            "permissions": request.permissions
        }
    }

def delete_role_service(token: str, role_key: str) -> dict:
    """Delete a role (super_admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_super_admin(current_user)
    
    # Delete role from MongoDB
    from services.mongo_db import mongo_db
    
    success = mongo_db.delete_role(role_key)
    if not success:
        raise Exception(f"Role {role_key} not found or failed to delete")
    
    return {
        "message": f"Role {role_key} deleted successfully from MongoDB"
    }

def update_permissions_service(token: str, request: PermissionUpdateRequest) -> dict:
    """Update permissions for a role (super_admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_super_admin(current_user)
    
    # In mock implementation, just return success
    return {
        "message": f"Permissions updated for role {request.role_key}",
        "permissions": request.permissions
    }

def clear_all_data(token: str) -> dict:
    """Clear all mock data (super_admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_super_admin(current_user)
    
    # Clear all mock databases
    channels_db.clear()
    campaigns_db.clear()
    leads_db.clear()
    analytics_db.clear()
    scheduler_db.clear()
    
    # Keep users and settings
    
    return {
        "message": "All dashboard data cleared successfully",
        "cleared": {
            "channels": len(channels_db),
            "campaigns": len(campaigns_db),
            "leads": len(leads_db),
            "analytics": len(analytics_db),
            "scheduler": len(scheduler_db)
        }
    }

def delete_user(user_id: str, token: str) -> dict:
    """Delete a user (super_admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_super_admin(current_user)
    
    # Check if we should use MongoDB or mock data
    from constants import DEV_MODE
    from services.mongo_db import mongo_db
    
    if DEV_MODE:
        # Mock implementation - just remove from users_db
        if user_id in users_db:
            del users_db[user_id]
            success = True
        else:
            success = False
    else:
        # MongoDB implementation
        success = mongo_db.delete_user(user_id)
    
    if success:
        return {
            "message": f"User {user_id} deleted successfully"
        }
    else:
        return {
            "message": f"User {user_id} not found or deletion failed"
        }

def deactivate_user(user_id: str, token: str) -> dict:
    """Deactivate a user (super_admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_super_admin(current_user)
    
    # Check if we should use MongoDB or mock data
    from constants import DEV_MODE
    from services.mongo_db import mongo_db
    
    if DEV_MODE:
        # Mock implementation - set activitystatus to False
        if user_id in users_db:
            users_db[user_id]["activitystatus"] = False
            success = True
        else:
            success = False
    else:
        # MongoDB implementation - use username to find user
        success = mongo_db.update_user_activity(user_id, False)
        if not success:
            # Try to find user by checking if they exist
            user = mongo_db.get_user_by_username(user_id)
            if user:
                # User exists but update failed, try again
                success = mongo_db.update_user_activity(user_id, False)
            else:
                # User not found
                app_logger.error(f"User {user_id} not found in MongoDB")
                return {"message": f"User {user_id} not found"}
    
    if success:
        return {
            "message": f"User {user_id} deactivated successfully"
        }
    else:
        return {
            "message": f"User {user_id} not found or deactivation failed"
        }

def extend_user_access(request: ExtendAccessRequest, token: str) -> dict:
    """Extend user access (super_admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_super_admin(current_user)
    
    # In mock implementation, just return success
    return {
        "message": f"Access extended for user {request.user_id} by {request.hours} hours"
    }

def get_user_profile_service(token: str) -> dict:
    """Get current user profile"""
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid token")
    
    if DEV_MODE:
        user = users_db.get(current_user["username"])
    else:
        user = mongo_db.get_user_by_username(current_user["username"])
    
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
        "message": "Profile retrieved successfully"
    }
    
    return profile_data

def health_check() -> dict:
    """System health check"""
    return {
        "status": "healthy",
        "database": "MongoDB" if not DEV_MODE else "Mock Data",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
