from fastapi import status
from pydantic import BaseModel
from typing import Optional, Union
from datetime import datetime, timedelta
import hashlib
from constants import (
    users_db, channels_db, campaigns_db, leads_db, analytics_db, 
    scheduler_db, otp_storage, USE_JSON_DB, DEV_MODE, API_TITLE, 
    API_VERSION, API_HOST, API_PORT, ALLOWED_ORIGINS, OTP_EXPIRY_MINUTES, 
    OTP_LENGTH, SMTP_EMAIL, SMTP_PASSWORD, SMTP_SERVER, SMTP_PORT,
    SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, DEFAULT_USERNAME,
    DEFAULT_EMAIL, DEFAULT_PASSWORD, created_users, created_roles, deleted_roles
)
from services.util import (
    verify_password, hash_password, generate_otp, store_otp, 
    verify_stored_otp, find_user_by_email, cleanup_otp, send_otp_email,
    create_access_token, get_user_from_token, validate_password_strength,
    RoleMiddleware, require_super_admin, require_admin, require_minimum_admin
)
from services.response import LoginResponse, OTPResponse, PasswordResetResponse, UserProfileResponse, ChannelResponse, CampaignResponse, LeadResponse, DashboardStatsResponse, AnalyticsResponse, SchedulerResponse, SettingsResponse
from services.error import APIError
from services.logger import app_logger
from services.json_db import json_db

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
    companyid: int
    access_hours: Optional[int] = None

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
def create_user_service(username, email, password, name, role, companyid, created_by, access_hours=None):
    """Create a new user with optional time-based access"""
    try:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Calculate access expiration if specified
        access_expires_at = None
        if access_hours and role != 'super_admin':  # Super admins don't expire
            access_expires_at = datetime.utcnow() + timedelta(hours=access_hours)
        
        if USE_JSON_DB:
            # JSON database implementation
            if json_db.get_user_by_username(username):
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
            
            if json_db.add_user(new_user):
                app_logger.info(f"User {username} created with role {role}")
                
                # Trigger frontend refresh
                try:
                    import requests
                    refresh_response = requests.post("http://localhost:3000/refresh", 
                        json={"type": "user_created", "data": {"username": username}},
                        timeout=2
                    )
                    app_logger.info("Frontend refresh triggered")
                except Exception as e:
                    app_logger.warning(f"Failed to trigger frontend refresh: {e}")
                
                return new_user
            else:
                raise Exception("Failed to create user")
        else:
            # Mock implementation - add to created users for session persistence
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
            
            created_users[username] = new_user
            app_logger.info(f"User {username} created and added to session tracking")
            
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
def login_user(request: APIRequest) -> LoginResponse:
    """Authenticate user and return JWT token"""
    username = request.username
    password = request.password
    
    if not username or not password:
        raise APIError.bad_request("Username and password are required")
    
    if USE_JSON_DB:
        app_logger.info("Using JSON database for login")
        # JSON database authentication
        user = json_db.get_user_by_username(username)
        if not user or not verify_password(password, user["password_hash"]):
            raise APIError.unauthorized("Invalid username or password")
    else:
        app_logger.info("Using mock data for login")
        # Mock authentication - check both default users and created users
        user = users_db.get(username)
        if not user:
            user = created_users.get(username)
        
        if not user or not verify_password(password, user["password_hash"]):
            raise APIError.unauthorized("Invalid username or password")
    
    # Generate JWT token with complete user data
    # Add 'sub' field for JWT standard compliance
    user_data = user.copy()
    user_data["sub"] = user["username"]
    
    token = create_access_token(user_data)
    
    app_logger.info(f"Login successful for user: {username}")
    
    return LoginResponse(
        message="Login successful",
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
        }
    )

def send_forgot_password_otp(request: APIRequest) -> OTPResponse:
    """Send OTP for password reset"""
    if not email:
        raise APIError.bad_request("Email is required")
    
    app_logger.info("Using mock data for OTP generation")
    # Mock user check
    username, user = find_user_by_email(users_db, email)
    if not user:
        raise APIError.not_found("Email not found")
    
    # Generate and store OTP
    otp = generate_otp()
    store_otp(otp_storage, email, otp)
    
    # In development, log OTP (in production, send email)
    app_logger.info(f"OTP for {email}: {otp} (development mode)")
    
    try:
        send_otp_email(email, otp)
    except Exception as e:
        app_logger.error(f"Failed to send OTP email: {e}")
    
    return OTPResponse(
        message="OTP sent successfully",
        success=True,
        otp=otp  # Only in development
    )

def verify_otp(request: APIRequest) -> OTPResponse:
    """Verify OTP for password reset"""
    if not email or not otp:
        raise APIError.bad_request("Email and OTP are required")
    
    app_logger.info("Using mock data for OTP verification")
    # Mock OTP verification
    if not verify_stored_otp(otp_storage, email, otp):
        raise APIError.unauthorized("Invalid or expired OTP")
    
    cleanup_otp(otp_storage, email)
    
    return OTPResponse(
        message="OTP verified successfully",
        success=True
    )

def reset_password(request: APIRequest) -> PasswordResetResponse:
    """Reset password with new credentials"""
    if not validate_password_strength(new_password):
        raise APIError.bad_request("Password must be at least 8 characters long and contain uppercase, lowercase, and numbers")
    
    app_logger.info("Using mock data for password reset")
    # Mock password reset
    username, user = find_user_by_email(users_db, email)
    if not user:
        raise APIError.not_found("Email not found")
    
    # Update password in mock database
    user["password_hash"] = hash_password(new_password)
    
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
    
    app_logger.info("Using JSON database for channels" if USE_JSON_DB else "Using mock data for channels")
    
    # Get channels from appropriate source
    channels_data = json_db.get_channels() if USE_JSON_DB else channels_db
    
    # Filter channels based on user role
    if current_user["role"] == "super_admin":
        # Super admin sees all channels
        filtered_channels = channels_data
    elif current_user["role"] == "admin":
        # Admin sees channels they created + channels created by super_admin + channels from same company
        filtered_channels = [channel for channel in channels_data 
                            if channel.get("created_by") == current_user["username"] or 
                               channel.get("created_by") == "superadmin" or
                               channel.get("created_by") and channel.get("created_by") != "superadmin" and 
                               channel.get("companyid") == current_user.get("companyid")]
    else:
        # Other roles see channels based on permissions
        filtered_channels = channels_data  # For now, show all - can be enhanced with permissions
    
    return ChannelResponse(
        message="Channels retrieved successfully (mock data)",
        success=True,
        channels=filtered_channels
    )

def get_campaigns(token: str) -> CampaignResponse:
    """Get campaigns based on user role and permissions"""
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid or expired token")
    
    app_logger.info("Using JSON database for campaigns" if USE_JSON_DB else "Using mock data for campaigns")
    
    # Get campaigns from appropriate source
    campaigns_data = json_db.get_campaigns() if USE_JSON_DB else campaigns_db
    
    # Filter campaigns based on user role
    if current_user["role"] == "super_admin":
        # Super admin sees all campaigns
        filtered_campaigns = campaigns_data
    elif current_user["role"] == "admin":
        # Admin sees campaigns they created + campaigns created by super_admin + campaigns from same company
        filtered_campaigns = [campaign for campaign in campaigns_data 
                             if campaign.get("created_by") == current_user["username"] or 
                                campaign.get("created_by") == "superadmin" or
                                campaign.get("companyid") == current_user.get("companyid")]
    else:
        # Other roles see campaigns based on permissions
        filtered_campaigns = [campaign for campaign in campaigns_data 
                             if campaign.get("companyid") == current_user.get("companyid")]
    
    return CampaignResponse(
        message="Campaigns retrieved successfully (mock data)",
        success=True,
        campaigns=filtered_campaigns
    )

def get_leads(token: str) -> LeadResponse:
    """Get leads based on user role and permissions"""
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid or expired token")
    
    app_logger.info("Using JSON database for leads" if USE_JSON_DB else "Using mock data for leads")
    
    # Get leads from appropriate source
    leads_data = json_db.get_leads() if USE_JSON_DB else leads_db
    
    # Filter leads based on user role
    if current_user["role"] == "super_admin":
        # Super admin sees all data
        filtered_leads = leads_data
        filtered_campaigns = campaigns_data
        filtered_channels = channels_data
    elif current_user["role"] == "admin":
        # Admin sees all data from their company + can edit their own created data
        filtered_leads = [lead for lead in leads_data 
                         if lead.get("created_by") == current_user["username"] or 
                            lead.get("created_by") == "superadmin" or
                            lead.get("created_by") and lead.get("created_by") != "superadmin" and 
                            lead.get("companyid") == current_user.get("companyid")]
        filtered_campaigns = [campaign for campaign in campaigns_data 
                             if campaign.get("created_by") == current_user["username"] or 
                                campaign.get("created_by") == "superadmin" or
                                campaign.get("created_by") and campaign.get("created_by") != "superadmin" and 
                                campaign.get("companyid") == current_user.get("companyid")]
        filtered_channels = [channel for channel in channels_data 
                            if channel.get("created_by") == current_user["username"] or 
                               channel.get("created_by") == "superadmin" or
                               channel.get("created_by") and channel.get("created_by") != "superadmin" and 
                               channel.get("companyid") == current_user.get("companyid")]
    else:
        # Other roles see data based on permissions
        filtered_leads = leads_data  # For now, show all - can be enhanced with permissions
    
    return LeadResponse(
        message="Leads retrieved successfully (mock data)",
        success=True,
        leads=filtered_leads
    )

def get_dashboard_stats() -> DashboardStatsResponse:
    """Get dashboard statistics"""
    app_logger.info("Using JSON database for dashboard stats" if USE_JSON_DB else "Using mock data for dashboard stats")
    
    # Get data from appropriate source
    channels_data = json_db.get_channels() if USE_JSON_DB else channels_db
    campaigns_data = json_db.get_campaigns() if USE_JSON_DB else campaigns_db
    leads_data = json_db.get_leads() if USE_JSON_DB else leads_db
    
    connected_channels = len([ch for ch in channels_data if ch.get("connected", False)])
    active_campaigns = len([ca for ca in campaigns_data if ca.get("status") == "active"])
    total_leads = len(leads_data)
    
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
    
    app_logger.info("Using mock data for analytics")
    
    # Filter analytics based on user role
    if current_user["role"] == "super_admin":
        # Super admin sees all analytics
        filtered_analytics = analytics_db
    elif current_user["role"] == "admin":
        # Admin sees analytics they created + analytics created by super_admin
        filtered_analytics = [analytic for analytic in analytics_db 
                           if analytic.get("created_by") == current_user["username"] or analytic.get("created_by") == "superadmin"]
    else:
        # Other roles see analytics based on permissions
        filtered_analytics = analytics_db  # For now, show all - can be enhanced with permissions
    
    return AnalyticsResponse(
        message="Analytics retrieved successfully (mock data)",
        success=True,
        analytics=filtered_analytics
    )

def get_scheduler(token: str) -> SchedulerResponse:
    """Get scheduler data based on user role and permissions"""
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise APIError.unauthorized("Invalid or expired token")
    
    app_logger.info("Using mock data for scheduler")
    
    # Filter schedules based on user role
    if current_user["role"] == "super_admin":
        # Super admin sees all schedules
        filtered_schedules = scheduler_db
    elif current_user["role"] == "admin":
        # Admin sees schedules they created + schedules created by super_admin
        filtered_schedules = [schedule for schedule in scheduler_db 
                          if schedule.get("created_by") == current_user["username"] or schedule.get("created_by") == "superadmin"]
    else:
        # Other roles see schedules based on permissions
        filtered_schedules = scheduler_db  # For now, show all - can be enhanced with permissions
    
    return SchedulerResponse(
        message="Scheduler data retrieved successfully (mock data)",
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
    
    # Use JSON database
    if USE_JSON_DB:
        roles_data = json_db.get_roles()
        app_logger.info(f"Retrieved {len(roles_data)} roles from JSON database")
        return {
            "message": "Roles retrieved successfully",
            "data": {
                "roles": roles_data
            }
        }
    else:
        # Mock role-based permissions
        role_permissions = {
            "super_admin": {
                "roleId": "super_admin",
                "roleName": "Super Admin",
                "permissions": {
                    "role_management": {"Create": True, "Read": True, "Update": True, "Delete": True},
                    "campaigns": {"Create": True, "Read": True, "Update": True, "Delete": True},
                    "analytics": {"Create": True, "Read": True, "Update": True, "Delete": True},
                    "leads": {"Create": True, "Read": True, "Update": True, "Delete": True},
                    "channels": {"Create": True, "Read": True, "Update": True, "Delete": True},
                    "scheduler": {"Create": True, "Read": True, "Update": True, "Delete": True}
                }
            },
            "admin": {
                "roleId": "admin",
                "roleName": "Admin",
                "permissions": {
                    "campaigns": {"Create": True, "Read": True, "Update": True, "Delete": True},
                    "analytics": {"Create": False, "Read": True, "Update": False, "Delete": False},
                    "leads": {"Create": True, "Read": True, "Update": True, "Delete": True},
                    "channels": {"Create": True, "Read": True, "Update": True, "Delete": True},
                    "scheduler": {"Create": True, "Read": True, "Update": True, "Delete": True}
                }
            },
            "marketing_manager": {
                "roleId": "marketing_manager",
                "roleName": "Marketing Manager",
                "permissions": {
                    "campaigns": {"Create": True, "Read": True, "Update": False, "Delete": False},
                    "analytics": {"Create": False, "Read": True, "Update": False, "Delete": False},
                    "leads": {"Create": True, "Read": True, "Update": True, "Delete": False},
                    "channels": {"Create": False, "Read": True, "Update": False, "Delete": False},
                    "scheduler": {"Create": True, "Read": True, "Update": True, "Delete": False}
                }
            },
            "content_editor": {
                "roleId": "content_editor",
                "roleName": "Content Editor",
                "permissions": {
                    "campaigns": {"Create": False, "Read": True, "Update": True, "Delete": False},
                    "analytics": {"Create": False, "Read": True, "Update": False, "Delete": False},
                    "leads": {"Create": False, "Read": True, "Update": False, "Delete": False},
                    "channels": {"Create": False, "Read": True, "Update": False, "Delete": False},
                    "scheduler": {"Create": False, "Read": True, "Update": False, "Delete": False}
                }
            },
            "sales_manager": {
                "roleId": "sales_manager",
                "roleName": "Sales Manager",
                "permissions": {
                    "campaigns": {"Create": False, "Read": True, "Update": False, "Delete": False},
                    "analytics": {"Create": False, "Read": True, "Update": False, "Delete": False},
                    "leads": {"Create": True, "Read": True, "Update": True, "Delete": True},
                    "channels": {"Create": False, "Read": True, "Update": False, "Delete": False},
                    "scheduler": {"Create": False, "Read": True, "Update": False, "Delete": False}
                }
            },
            "user": {
                "roleId": "user",
                "roleName": "User",
                "permissions": {
                    "campaigns": {"Create": False, "Read": True, "Update": False, "Delete": False},
                    "analytics": {"Create": False, "Read": False, "Update": False, "Delete": False},
                    "leads": {"Create": False, "Read": True, "Update": False, "Delete": False},
                    "channels": {"Create": False, "Read": True, "Update": False, "Delete": False},
                    "scheduler": {"Create": False, "Read": True, "Update": False, "Delete": False}
                }
            }
        }
        
        # Filter out super_admin and deleted roles, add created roles
        filtered_roles = {k: v for k, v in role_permissions.items() if k != "super_admin" and k not in deleted_roles}
        # Add newly created roles
        filtered_roles.update(created_roles)
        
        return {
            "message": "Roles retrieved successfully",
            "data": {
                "roles": filtered_roles
            }
        }

def create_user(request: CreateUserRequest, token: str) -> dict:
    """Create a new user (super_admin and admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_minimum_admin(current_user)
    
    # Create mock user
    new_user = create_user_service(
        request.username, request.email, request.password,
        request.name, request.role, request.companyid,
        current_user["username"], request.access_hours
    )
    
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
    
    # Mock implementation - only show created users, not default mock users
    if current_user["role"] == "super_admin":
        # Super admin can see all created users
        users_list = list(created_users.values())
    else:
        # Admin can only see users they created
        users_list = [u for u in created_users.values() 
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
    
    # Mock implementation - check created_users
    user_found = False
    for user in created_users.values():
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

def delete_user(user_id, token: str) -> dict:
    """Delete a user completely (super_admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_super_admin(current_user)
    
    # Mock implementation - remove from created_users
    user_found = False
    username_to_delete = None
    for user in created_users.values():
        # Handle both numeric ID and username
        if (user.get("id") == user_id or 
            user["username"] == str(user_id) or 
            user["username"] == user_id):
            user_found = True
            username_to_delete = user["username"]
            break
    
    if not user_found:
        raise APIError.not_found("User not found")
    
    # Remove the user from created_users
    if username_to_delete in created_users:
        del created_users[username_to_delete]
        app_logger.info(f"User {username_to_delete} deleted completely")
    
    return {"message": "User deleted successfully"}

def create_role_service(token: str, request: RoleRequest) -> dict:
    """Create a new role (super_admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_super_admin(current_user)
    
    # Use JSON database
    if USE_JSON_DB:
        role_data = {
            "roleId": request.role_key,
            "roleName": request.role_name,
            "permissions": request.permissions
        }
        
        if json_db.add_role(request.role_key, role_data):
            return {
                "message": f"Role {request.role_name} created successfully",
                "role": {
                    "role_key": request.role_key,
                    "role_name": request.role_name,
                    "permissions": request.permissions
                }
            }
        else:
            return {
                "message": f"Failed to create role {request.role_name}",
                "error": "Database error"
            }
    else:
        # Mock implementation - add to created roles for session persistence
        role_data = {
            "roleId": request.role_key,
            "roleName": request.role_name,
            "permissions": request.permissions
        }
        created_roles[request.role_key] = role_data
        app_logger.info(f"Role {request.role_key} created and added to session tracking")
        
        return {
            "message": f"Role {request.role_name} created successfully",
            "role": {
                "role_key": request.role_key,
                "role_name": request.role_name,
                "permissions": request.permissions
            }
        }

def update_role_service(token: str, role_key: str, request: RoleRequest) -> dict:
    """Update an existing role (super_admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_super_admin(current_user)
    
    # In mock implementation, just return success
    return {
        "message": f"Role {request.role_name} updated successfully",
        "role": {
            "role_key": role_key,
            "role_name": request.role_name,
            "permissions": request.permissions
        }
    }

def delete_role_service(token: str, role_key: str) -> dict:
    """Delete a role (super_admin only)"""
    current_user = RoleMiddleware.get_current_user(token)
    require_super_admin(current_user)
    
    # Protect core roles that cannot be deleted
    protected_roles = ["super_admin"]
    if role_key in protected_roles:
        return {
            "message": f"Cannot delete protected role '{role_key}'",
            "error": "Protected role cannot be deleted"
        }
    
    # Add to deleted roles and remove from created roles if it exists there
    deleted_roles.add(role_key)
    if role_key in created_roles:
        del created_roles[role_key]
    app_logger.info(f"Role {role_key} deleted and added to deleted tracking")
    
    return {
        "message": f"Role {role_key} deleted successfully"
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
