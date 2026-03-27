from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, Request, File
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime, timedelta
from services.util import get_user_from_token, verify_token, RoleMiddleware, require_minimum_admin, require_super_admin
from services.error import APIError
from services.routes import CampaignResponse
import os
import logging
import json
from fastapi.responses import JSONResponse, Response
from collections import defaultdict
from datetime import datetime, timedelta
import time
import asyncio
import threading

from services.routes import (
    get_campaigns, get_leads, get_channels,
    get_analytics, get_scheduler, get_settings,
    login_user, send_forgot_password_otp, verify_otp, reset_password,
    create_access_token, APIRequest, CreateUserRequest, ExtendAccessRequest, RoleRequest, PermissionUpdateRequest,
    get_dashboard_stats, get_roles_service, get_users, create_user, extend_user_access, deactivate_user, delete_user, clear_all_data,
    create_role_service, update_role_service, delete_role_service, update_permissions_service, health_check,
    get_user_profile_service, update_user_profile_service
)
try:
    from social_media.connection_manager import initialize_connections, shutdown_connections, connection_manager
    from social_media.social_config import social_integration_manager, SocialPlatform, SOCIAL_INTEGRATION_ENABLED
    from social_media.social_data_service import social_data_service
    from social_media.oauth_manager import social_oauth_manager, get_mock_oauth_flow
    from social_media.twitter_oauth import twitter_oauth
    SOCIAL_MEDIA_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Social media modules not available - {e}")
    SOCIAL_MEDIA_AVAILABLE = False
    # Create placeholder objects
    class MockSocialIntegrationManager:
        def get_all_connections(self): return {}
        def get_platform_status(self, platform): return "disconnected"
    social_integration_manager = MockSocialIntegrationManager()
    SocialPlatform = type('SocialPlatform', (), {'TWITTER': 'twitter', 'LINKEDIN': 'linkedin'})()
    SOCIAL_INTEGRATION_ENABLED = False
    connection_manager = type('ConnectionManager', (), {
        'initialize_connections': lambda: None, 
        'shutdown_connections': lambda: None,
        'get_connection_summary': lambda: {'platforms': {}, 'total_connected': 0}
    })()
    social_data_service = type('SocialDataService', (), {'get_platform_data': lambda x: None})()
    social_oauth_manager = type('SocialOAuthManager', (), {'get_oauth_url': lambda x: None})()
    twitter_oauth = type('TwitterOAuth', (), {'get_auth_url': lambda: None})()
from services.util import (
    verify_password, hash_password, generate_otp, store_otp, 
    verify_stored_otp, find_user_by_email, cleanup_otp, send_otp_email,
    send_user_created_email, send_lead_created_email, send_campaign_created_email,
    send_access_expiring_email, send_access_expired_email,
    create_access_token, get_user_from_token, validate_password_strength,
    RoleMiddleware, require_super_admin, require_admin, require_minimum_admin
)
from fastapi import HTTPException
from services.response import LoginResponse, OTPResponse, PasswordResetResponse, UserProfileResponse, ChannelResponse, CampaignResponse, LeadResponse, DashboardStatsResponse, AnalyticsResponse, SchedulerResponse, SettingsResponse
from services.error import APIError
from services.logger import app_logger
from services.json_db import json_db
from services.mongo_db import mongo_db
from services.constants import API_TITLE, API_VERSION, API_HOST, API_PORT, ALLOWED_ORIGINS, campaigns_db, leads_db, channels_db, scheduler_db, user_settings_db

# Security
oauth2_scheme = HTTPBearer()
security = HTTPBearer()

# Rate limiting storage
login_attempts = defaultdict(list)
MAX_LOGIN_ATTEMPTS = 5
LOGIN_WINDOW_MINUTES = 1

class RateLimitMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        # Rate limiting logic here would go
        # For now, we'll handle rate limiting in the login endpoint itself
        await self.app(scope, receive, send)

def is_rate_limited(ip: str) -> tuple[bool, int]:
    """Check if IP is rate limited for login attempts"""
    now = time.time()
    window_start = now - (LOGIN_WINDOW_MINUTES * 60)
    
    # Clean old attempts
    login_attempts[ip] = [attempt_time for attempt_time in login_attempts[ip] if attempt_time > window_start]
    
    # Check if too many attempts
    recent_attempts = len(login_attempts[ip])
    return recent_attempts >= MAX_LOGIN_ATTEMPTS, recent_attempts

app = FastAPI(title=API_TITLE, version=API_VERSION)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get current user
def get_user_from_token_dependency(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to validate JWT token and get current user"""
    if not credentials or not hasattr(credentials, 'credentials'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    from services.routes import get_user_from_token
    user = get_user_from_token(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# API Endpoints
@app.post("/api/v1/login")
async def login(request: APIRequest, http_request: Request):
    """Login endpoint with optional OTP verification"""
    client_ip = http_request.client.host
    # Temporarily disable rate limiting for testing
    # is_limited, attempts = is_rate_limited(client_ip)
    # 
    # if is_limited:
    #     app_logger.warning(f"Rate limit exceeded for IP: {client_ip}, attempts: {attempts}")
    #     raise HTTPException(
    #         status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    #         detail=f"Too many login attempts. Try again in {LOGIN_WINDOW_MINUTES} minutes.",
    #         headers={"Retry-After": str(LOGIN_WINDOW_MINUTES * 60)}
    #     )
    
    app_logger.info(f"Login attempt for user: {request.username} from IP: {client_ip}")
    
    # Record this attempt
    login_attempts[client_ip].append(time.time())
    
    try:
        result = login_user(request)
        app_logger.info(f"Login result: {result.message}")
        
        # Check if result is LoginResponse (with token) or OTPResponse (with OTP)
        if hasattr(result, 'access_token'):
            # Login successful with OTP - create secure response with token
            response = JSONResponse(content=result.dict())
            response.set_cookie(
                key="access_token",
                value=result.access_token,
                max_age=1800,  # 30 minutes
                expires=timedelta(minutes=30),
                path="/",
                domain=None,
                secure=True,  # HTTPS only
                httponly=True,  # Prevent XSS
                samesite="lax"  # CSRF protection
            )
            
            # Clear rate limit on successful login
            if client_ip in login_attempts:
                del login_attempts[client_ip]
            
            return response
        else:
            # OTP sent - return OTP response
            return JSONResponse(content=result.dict())
        
    except Exception as e:
        app_logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@app.options("/api/v1/login")
async def login_options():
    """Handle OPTIONS preflight request"""
    return JSONResponse(
        content={"message": "OK"},
        status_code=200
    )

@app.post("/api/v1/refresh-token")
async def refresh_token(http_request: Request):
    """Refresh access token"""
    # Get token from cookie
    token = http_request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided"
        )
    
    # Validate current token
    current_user = get_user_from_token_dependency(credentials)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided"
        )
    
    # Generate new token
    from services.routes import create_access_token
    user_data = {
        "sub": current_user["username"],
        "username": current_user["username"],
        "email": current_user["email"],
        "role": current_user["role"]
    }
    new_token = create_access_token(user_data)
    
    # Create secure response with new httpOnly cookie
    response = JSONResponse(content={
        "message": "Token refreshed successfully",
        "access_token": new_token,
        "token_type": "bearer"
    })
    response.set_cookie(
        key="access_token",
        value=new_token,
        max_age=1800,  # 30 minutes
        expires=timedelta(minutes=30),
        path="/",
        domain=None,
        secure=True,
        httponly=True,
        samesite="lax"
    )
    
    app_logger.info(f"Token refreshed for user: {current_user['username']}")
    return response

@app.post("/api/v1/logout")
async def logout(http_request: Request):
    """Logout and clear secure cookie"""
    # Create response that clears the httpOnly cookie
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie(
        key="access_token",
        path="/",
        domain=None,
        secure=True,
        httponly=True,
        samesite="lax"
    )
    
    app_logger.info("User logged out")
    return response

@app.get("/api/v1/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Test endpoint working"}

@app.get("/api/v1/verify-token")
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify and return decoded token information with role-based permissions"""
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided"
        )
    
    try:
        # Validate token and get user
        current_user = RoleMiddleware.get_current_user(token)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        # Get user's role and permissions
        user_role = current_user.get("role", "")
        
        # Mock role-based permissions (in production, this would come from database)
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
            }
        }
        
        # Get permissions for current user's role
        user_permissions = role_permissions.get(user_role, {
            "roleId": user_role,
            "roleName": user_role.replace("_", " ").title(),
            "permissions": {
                "campaigns": {"Create": False, "Read": False, "Update": False, "Delete": False},
                "analytics": {"Create": False, "Read": False, "Update": False, "Delete": False},
                "leads": {"Create": False, "Read": False, "Update": False, "Delete": False},
                "channels": {"Create": False, "Read": False, "Update": False, "Delete": False},
                "scheduler": {"Create": False, "Read": False, "Update": False, "Delete": False}
            }
        })
        
        # Return user info with role-based permissions and user type
        return {
            "message": "Token verified successfully",
            "valid": True,
            "data": {
                "name": current_user.get("name", ""),
                "companyId": current_user.get("companyid", 0),
                "role": user_role,
                "username": current_user.get("username", ""),
                "email": current_user.get("email", ""),
                "activitystatus": current_user.get("activitystatus", True),
                "user_type": current_user.get("user_type", "platform_owner"),
                "roleId": user_permissions["roleId"],
                "roleName": user_permissions["roleName"],
                "permissions": user_permissions["permissions"]
            }
        }
    except Exception as e:
        app_logger.error(f"Error in verify_token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/api/v1/forgot-password")
async def forgot_password(request: APIRequest):
    """Send OTP for password reset"""
    app_logger.info(f"Password reset request for email: {request.email}")
    result = send_forgot_password_otp(request)
    app_logger.info(f"Password reset result: {result.message}")
    return result

@app.post("/api/v1/verify-otp")
async def verify_otp_endpoint(request: APIRequest):
    """Verify OTP for password reset"""
    app_logger.info(f"OTP verification request for email: {request.email}")
    result = verify_otp(request)
    app_logger.info(f"OTP verification result: {result.message}")
    return result

@app.post("/api/v1/reset-password")
async def reset_password_endpoint(request: APIRequest):
    """Reset password with new credentials"""
    app_logger.info(f"Password reset confirmation for email: {request.email}")
    result = reset_password(request)
    app_logger.info(f"Password reset result: {result.message}")
    return result

@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats_endpoint():
    """Get dashboard statistics"""
    app_logger.info("Dashboard stats requested")
    result = get_dashboard_stats()
    app_logger.info(f"Dashboard stats: {result.stats}")
    return result

@app.get("/api/v1/health")
async def health_endpoint():
    """Health check endpoint"""
    app_logger.info("Health check requested")
    return {"message": "Social Connect API is running"}

@app.get("/")
async def root():
    """Health check endpoint"""
    app_logger.info("Health check requested")
    return {"message": "Social Connect API is running"}

# Dashboard endpoints
@app.get("/api/v1/channels")
async def get_channels_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all channels"""
    app_logger.info("Channels data requested")
    result = get_channels(credentials.credentials)
    app_logger.info(f"Returned {len(result.channels)} channels")
    return result

@app.get("/api/v1/campaigns")
async def get_campaigns_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all campaigns"""
    app_logger.info("Campaigns data requested")
    result = get_campaigns(credentials.credentials)
    app_logger.info(f"Returned {len(result.campaigns)} campaigns")
    return result

@app.get("/api/v1/leads")
async def get_leads_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all leads"""
    app_logger.info("Leads data requested")
    result = get_leads(credentials.credentials)
    app_logger.info(f"Returned {len(result.leads)} leads")
    return result

@app.post("/api/v1/leads")
async def create_lead_endpoint(request: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new lead"""
    app_logger.info(f"Lead creation request: {request}")
    
    # Get current user from token
    current_user = get_user_from_token(credentials.credentials)
    
    # Create lead in MongoDB
    from services.mongo_db import mongo_db
    
    lead_data = {
        "name": request.get("name", "New Lead"),
        "email": request.get("email", ""),
        "phone": request.get("phone", ""),
        "campaign_id": request.get("campaign_id"),
        "created_by": current_user["username"] if current_user else "unknown"
    }
    
    success = mongo_db.create_lead(lead_data)
    
    if success:
        # The lead_data object now has the generated ID, but remove the MongoDB _id
        lead_response = lead_data.copy()
        lead_response.pop('_id', None)  # Remove MongoDB _id field
        
        app_logger.info(f"Lead created successfully: {lead_response['name']}")
        
        return {
            "message": "Lead created successfully",
            "success": True,
            "lead": lead_response
        }
    else:
        app_logger.error("Failed to create lead")
        return {
            "message": "Failed to create lead",
            "success": False
        }

@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats_endpoint():
    """Get dashboard statistics"""
    app_logger.info("Dashboard stats requested")
    result = get_dashboard_stats()
    app_logger.info(f"Dashboard stats: {result.stats}")
    return result

@app.get("/api/v1/analytics")
async def get_analytics_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get analytics data"""
    app_logger.info("Analytics data requested")
    result = get_analytics(credentials.credentials)
    app_logger.info(f"Returned {len(result.analytics)} analytics")
    return result

@app.get("/api/v1/scheduler")
async def get_scheduler_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get scheduler data"""
    app_logger.info("Scheduler data requested")
    result = get_scheduler(credentials.credentials)
    app_logger.info(f"Returned {len(result.schedules)} schedules")
    return result

@app.get("/api/v1/settings")
async def get_settings_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get user settings"""
    app_logger.info("Settings data requested")
    result = get_settings(credentials.credentials)
    app_logger.info("Settings retrieved successfully")
    return result

# Role-based management endpoints with company filtering
@app.post("/api/v1/admin/roles/{company_id}")
async def create_role_endpoint(company_id: int, request: RoleRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new role for a specific company (super_admin only)"""
    app_logger.info(f"Role creation request for company {company_id}: {request.role_name}")
    current_user = get_user_from_token(credentials.credentials)
    require_super_admin(current_user)
    
    # Add company_id to role data
    role_data = {
        "roleId": request.role_key,
        "roleName": request.role_name,
        "permissions": request.permissions,
        "companyid": company_id
    }
    
    # Create role in MongoDB
    from services.mongo_db import mongo_db
    success = mongo_db.create_role(role_data)
    if not success:
        raise HTTPException(status_code=400, detail=f"Role {request.role_key} already exists or failed to create")
    
    return {
        "message": f"Role {request.role_name} created successfully for company {company_id}",
        "role": {
            "roleId": request.role_key,
            "roleName": request.role_name,
            "permissions": request.permissions,
            "companyid": company_id
        }
    }

@app.get("/api/v1/admin/roles/{company_id}")
async def get_roles_endpoint(company_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get roles for a specific company (super_admin only)"""
    app_logger.info(f"Roles requested for company {company_id}")
    current_user = get_user_from_token(credentials.credentials)
    require_super_admin(current_user)
    
    # Get roles from MongoDB for specific company
    from services.mongo_db import mongo_db
    all_roles = mongo_db.get_roles()
    
    # Filter roles by company_id
    company_roles = {}
    for role_key, role_data in all_roles.items():
        if role_data.get("companyid") == company_id:
            company_roles[role_key] = role_data
    
    return {
        "message": f"Roles retrieved successfully for company {company_id}",
        "roles": company_roles
    }

@app.put("/api/v1/admin/roles/{company_id}/{role_key}")
async def update_role_endpoint(company_id: int, role_key: str, request: RoleRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update an existing role for a specific company (super_admin only)"""
    app_logger.info(f"Role update request for company {company_id}: {role_key}")
    current_user = get_user_from_token(credentials.credentials)
    require_super_admin(current_user)
    
    # Update role in MongoDB
    from services.mongo_db import mongo_db
    updates = {
        "roleName": request.role_name,
        "permissions": request.permissions
    }
    
    success = mongo_db.update_role(role_key, updates)
    if not success:
        raise HTTPException(status_code=404, detail=f"Role {role_key} not found or failed to update")
    
    return {
        "message": f"Role {request.role_name} updated successfully for company {company_id}",
        "role": {
            "roleId": role_key,
            "roleName": request.role_name,
            "permissions": request.permissions,
            "companyid": company_id
        }
    }

@app.put("/api/v1/admin/roles/{company_id}/{role_key}/deactivate")
async def deactivate_role_endpoint(company_id: int, role_key: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Deactivate a role for a specific company (soft delete)"""
    app_logger.info(f"Role deactivation request for company {company_id}: {role_key}")
    current_user = get_user_from_token(credentials.credentials)
    require_super_admin(current_user)
    
    # Soft delete role in MongoDB (set status to inactive)
    from services.mongo_db import mongo_db
    updates = {"status": "inactive"}
    
    success = mongo_db.update_role(role_key, updates)
    if not success:
        raise HTTPException(status_code=404, detail=f"Role {role_key} not found or failed to deactivate")
    
    return {
        "message": f"Role {role_key} deactivated successfully for company {company_id}"
    }

@app.put("/api/v1/admin/roles/{company_id}/{role_key}/activate")
async def activate_role_endpoint(company_id: int, role_key: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Activate a role for a specific company"""
    app_logger.info(f"Role activation request for company {company_id}: {role_key}")
    current_user = get_user_from_token(credentials.credentials)
    require_super_admin(current_user)
    
    # Activate role in MongoDB (set status to active)
    from services.mongo_db import mongo_db
    updates = {"status": "active"}
    
    success = mongo_db.update_role(role_key, updates)
    if not success:
        raise HTTPException(status_code=404, detail=f"Role {role_key} not found or failed to activate")
    
    return {
        "message": f"Role {role_key} activated successfully for company {company_id}"
    }

@app.put("/api/v1/admin/users/{company_id}/{user_id}")
async def update_user_endpoint(company_id: int, user_id: str, request: CreateUserRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update an existing user in a specific company (super_admin and admin only)"""
    app_logger.info(f"User update request for company {company_id}: {user_id}")
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    # Check if user exists and belongs to the specified company
    from services.constants import DEV_MODE, users_db
    from services.mongo_db import mongo_db
    target_user = mongo_db.get_user_by_username(user_id) if not DEV_MODE else users_db.get(user_id)
    
    if not target_user or target_user.get("companyid") != company_id:
        raise HTTPException(status_code=404, detail="User not found in this company")
    
    # Additional check: admin can only update users from their own company
    if current_user["role"] == "admin" and current_user["companyid"] != company_id:
        raise HTTPException(status_code=403, detail="Admin can only update users from their own company")
    
    # For now, we'll implement a basic update
    return {
        "message": f"User {user_id} updated successfully in company {company_id}",
        "user": {
            "username": request.username,
            "email": request.email,
            "name": request.name,
            "role": request.role,
            "companyid": company_id
        }
    }

@app.get("/api/v1/admin/users/{company_id}")
async def get_users_endpoint(company_id: int, role_filter: Optional[str] = None, include_inactive: Optional[bool] = False, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get users for a specific company (super_admin and admin only)"""
    app_logger.info(f"Users list requested for company {company_id} with filter: {role_filter}, include_inactive: {include_inactive}")
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    from services.mongo_db import mongo_db
    
    # Get all users from database
    all_users = mongo_db.get_users()
    app_logger.info(f"Total users in database: {len(all_users)}")
    
    # Filter users based on company and role
    if current_user["role"] == "super_admin":
        # Super admin can see all users in the specified company
        if company_id == 0:
            # Company 0 means show all users
            users_list = all_users
        else:
            # Show users for specific company
            users_list = [u for u in all_users if u.get("companyid") == company_id]
    else:
        # Admin can only see users they created in their company
        users_list = [u for u in all_users 
                     if u.get("created_by") == current_user["username"] and u.get("companyid") == company_id]
    
    app_logger.info(f"Filtered users for company {company_id}: {len(users_list)}")
    
    # Apply role filter if provided
    if role_filter:
        users_list = [u for u in users_list if u.get("role") == role_filter]
        app_logger.info(f"Users after role filter '{role_filter}': {len(users_list)}")
    
    # Filter out inactive users only if include_inactive is False
    if not include_inactive:
        users_list = [u for u in users_list if u.get("activitystatus", True) != False]
        app_logger.info(f"Users after filtering inactive users: {len(users_list)}")
    else:
        app_logger.info(f"Including inactive users in results: {len(users_list)}")
    
    # Remove sensitive information
    safe_users = []
    for user in users_list:
        safe_user = {
            "username": user.get("username"),
            "email": user.get("email"),
            "name": user.get("name"),
            "role": user.get("role"),
            "companyid": user.get("companyid"),
            "user_type": user.get("user_type", "platform_owner"),
            "activitystatus": user.get("activitystatus"),
            "access_expires_at": user.get("access_expires_at"),
            "created_by": user.get("created_by")
        }
        safe_users.append(safe_user)
    
    return {
        "message": f"Users retrieved successfully for company {company_id}",
        "users": safe_users,
        "total": len(safe_users)
    }

@app.post("/api/v1/admin/users/extend-access")
async def extend_user_access_endpoint(request: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extend user access (super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_super_admin(current_user)
    
    app_logger.info(f"Extending user access with data: {request}")
    
    # Handle user_id that might be string or int
    user_id = request.get("user_id")
    if isinstance(user_id, str):
        # Try to convert to int, if fails try to find user by username
        try:
            user_id = int(user_id)
        except ValueError:
            # Find user by username
            from services.mongo_db import mongo_db
            users = mongo_db.get_users()
            found_user = None
            for user in users:
                if user.get("username") == user_id:
                    found_user = user
                    break
            if found_user:
                user_id = found_user.get("id")
            else:
                raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    
    # Create proper request object - handle both int and string user_id
    try:
        extend_request = ExtendAccessRequest(user_id=user_id, hours=request.get("hours"))
        result = extend_user_access(extend_request, credentials.credentials)
    except Exception as e:
        # Fallback to dict approach for string user_id
        app_logger.error(f"Error with ExtendAccessRequest: {e}, using dict approach")
        extend_request = {"user_id": user_id, "hours": request.get("hours")}
        result = extend_user_access(extend_request, credentials.credentials)
    
    if result['success']:
        return {
            "message": result['message'],
            "user": result.get('user')
        }
    else:
        app_logger.error(f"Failed to extend user access: {result['message']}")
        raise HTTPException(status_code=500, detail=result['message'])

@app.post("/api/v1/admin/users/{company_id}")
async def create_user_endpoint(company_id: int, request: CreateUserRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new user for a specific company (super_admin and admin only)"""
    app_logger.info(f"User creation request for company {company_id}: {request.username}")
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    # Override companyid with the one from URL
    user_data = request.dict()
    user_data["companyid"] = company_id
    
    # Create a new CreateUserRequest with the updated companyid
    from services.routes import CreateUserRequest
    updated_request = CreateUserRequest(**user_data)
    
    result = create_user(updated_request, credentials.credentials)
    app_logger.info(f"User creation result: {result['message']}")
    return result

@app.delete("/api/v1/admin/users/{company_id}/{user_id}")
async def deactivate_user_endpoint(company_id: int, user_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Deactivate a user in a specific company (super_admin and admin only)"""
    app_logger.info(f"User deactivation request for company {company_id}: {user_id}")
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    # Check if user exists and belongs to the specified company
    from services.constants import DEV_MODE, users_db
    from services.mongo_db import mongo_db
    target_user = mongo_db.get_user_by_username(user_id) if not DEV_MODE else users_db.get(user_id)
    
    if not target_user or target_user.get("companyid") != company_id:
        raise HTTPException(status_code=404, detail="User not found in this company")
    
    # Additional check: admin can only delete users from their own company
    if current_user["role"] == "admin" and current_user["companyid"] != company_id:
        raise HTTPException(status_code=403, detail="Admin can only delete users from their own company")
    
    result = deactivate_user(user_id, credentials.credentials)
    app_logger.info(f"User deactivation result: {result['message']}")
    return result

@app.post("/api/v1/admin/users/{company_id}/{user_id}/reactivate")
async def reactivate_user_endpoint(company_id: int, user_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Reactivate a user in a specific company (super_admin and admin only)"""
    app_logger.info(f"User reactivation request for company {company_id}: {user_id}")
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    # Check if user exists and belongs to the specified company
    from services.constants import DEV_MODE, users_db
    from services.mongo_db import mongo_db
    target_user = mongo_db.get_user_by_username(user_id) if not DEV_MODE else users_db.get(user_id)
    
    if not target_user or target_user.get("companyid") != company_id:
        raise HTTPException(status_code=404, detail="User not found in this company")
    
    # Additional check: admin can only reactivate users from their own company
    if current_user["role"] == "admin" and current_user["companyid"] != company_id:
        raise HTTPException(status_code=403, detail="Admin can only reactivate users from their own company")
    
    # Reactivate user by setting activitystatus to True
    if DEV_MODE:
        # Mock implementation - set activitystatus to True
        if user_id in users_db:
            if users_db[user_id].get("activitystatus", True) == True:
                raise HTTPException(status_code=400, detail="User is already active")
            users_db[user_id]["activitystatus"] = True
            success = True
        else:
            success = False
    else:
        # MongoDB implementation - use username to find user
        # Check if user is already active first
        current_user_data = mongo_db.get_user_by_username(user_id)
        if current_user_data and current_user_data.get("activitystatus", True) == True:
            raise HTTPException(status_code=400, detail="User is already active")
        
        success = mongo_db.update_user_activity(user_id, True)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to reactivate user")
    
    app_logger.info(f"User {user_id} reactivated successfully")
    return {"message": f"User {user_id} reactivated successfully"}

# Campaign CRUD endpoints
@app.post("/api/v1/campaigns")
async def create_campaign_endpoint(request: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new campaign (admin and super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    # Create campaign in MongoDB
    from services.mongo_db import mongo_db
    
    campaign_data = {
        "name": request.get("name"),
        "status": request.get("status", "draft"),
        "created_by": current_user["username"],
        "type": request.get("type", "sale"),
        "target_audience": request.get("target_audience", "all_customers"),
        "duration_days": request.get("duration_days", 14),
        "budget_range": request.get("budget_range", "$500-1000"),
        "platforms": request.get("platforms", ["facebook", "instagram"]),
        "goal": request.get("goal", "sales"),
        "special_offers": request.get("special_offers", ""),
        "visual_theme": request.get("visual_theme", "blue_ocean"),
        "call_to_action": request.get("call_to_action", "Learn More"),
        "poster_url": request.get("poster_url", "/posters/default_campaign.png"),
        "suggested_hashtags": request.get("suggested_hashtags", []),
        "optimal_posting_times": request.get("optimal_posting_times", ["9:00 AM", "6:00 PM"]),
        "ad_copy_variations": request.get("ad_copy_variations", []),
        "platform_strategies": request.get("platform_strategies", {}),
        "content_focus": request.get("content_focus", "general promotion")
    }
    
    app_logger.info(f"Creating campaign with data: {campaign_data}")
    
    success = mongo_db.create_campaign(campaign_data)
    
    if success:
        app_logger.info(f"Campaign created successfully: {campaign_data}")
        # The campaign_data object now has the generated ID, but remove the MongoDB _id
        campaign_response = campaign_data.copy()
        campaign_response.pop('_id', None)  # Remove MongoDB _id field
        
        return {
            "message": "Campaign created successfully",
            "campaign": campaign_response
        }
    else:
        app_logger.error("Failed to create campaign")
        raise HTTPException(status_code=500, detail="Failed to create campaign")

@app.post("/api/v1/campaigns/chatbot-create")
async def create_campaign_chatbot_endpoint(request: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a campaign via chatbot (admin and super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    # Use chatbot service to create campaign
    from services.campaign_chatbot import campaign_chatbot
    
    app_logger.info(f"Creating campaign via chatbot with data: {request}")
    
    result = campaign_chatbot.create_campaign_from_chat(request, credentials.credentials)
    
    if result['success']:
        return {
            "message": result['message'],
            "campaign": result['campaign']
        }
    else:
        app_logger.error(f"Chatbot campaign creation failed: {result['error']}")
        raise HTTPException(status_code=500, detail=result['message'])

@app.post("/api/v1/users")
async def create_user_endpoint(request: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new user (super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_super_admin(current_user)
    
    # Create user in MongoDB
    from services.mongo_db import mongo_db
    user_data = {
        "username": request.get("username"),
        "email": request.get("email"),
        "password": request.get("password"),
        "name": request.get("name"),
        "role": request.get("role", "user"),
        "companyid": request.get("companyid", current_user.get("companyid")),
        "activitystatus": "active"
    }
    
    if mongo_db.create_user(user_data):
        app_logger.info(f"User created successfully: {user_data['username']}")
        return {
            "message": "User created successfully",
            "user": {
                "username": user_data["username"],
                "email": user_data["email"],
                "name": user_data["name"],
                "role": user_data["role"],
                "companyid": user_data["companyid"]
            }
        }
    else:
        app_logger.error(f"Failed to create user: {user_data['username']}")
        raise HTTPException(status_code=500, detail="Failed to create user")

@app.get("/api/v1/users")
async def get_users_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all users (super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_super_admin(current_user)
    
    # Get users from MongoDB
    from services.mongo_db import mongo_db
    users = mongo_db.get_users()
    
    # Remove password from response for security
    safe_users = []
    for user in users:
        safe_user = user.copy()
        safe_user.pop("password", None)
        safe_users.append(safe_user)
    
    return {
        "message": "Users retrieved successfully",
        "users": safe_users,
        "total": len(safe_users)
    }

@app.get("/api/v1/users/export")
async def export_users_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Export all users to CSV (super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_super_admin(current_user)
    
    # Get users from MongoDB
    from services.mongo_db import mongo_db
    users = mongo_db.get_users()
    
    # Create CSV content
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(["username", "email", "name", "role", "companyid", "activitystatus", "created_at"])
    
    # Write user data
    for user in users:
        writer.writerow([
            user.get("username", ""),
            user.get("email", ""),
            user.get("name", ""),
            user.get("role", ""),
            user.get("companyid", ""),
            user.get("activitystatus", ""),
            user.get("created_at", "")
        ])
    
    # Create CSV response
    csv_content = output.getvalue()
    
    from fastapi.responses import Response
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users_export.csv"}
    )

@app.post("/api/v1/companies")
async def create_company_endpoint(request: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new company (super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_super_admin(current_user)
    
    # Handle logo upload
    company_logo = request.get("logo_url", "")
    
    # Create company in MongoDB
    from services.mongo_db import mongo_db
    company_data = {
        "name": request.get("name"),
        "description": request.get("description", ""),
        "logo_url": company_logo,
        "created_by": current_user["username"],
        "created_at": datetime.utcnow().isoformat()
    }
    
    if mongo_db.create_company(company_data):
        app_logger.info(f"Company created successfully: {company_data['name']}")
        return {
            "message": "Company created successfully",
            "company": company_data
        }
    else:
        app_logger.error(f"Failed to create company: {company_data['name']}")
        raise HTTPException(status_code=500, detail="Failed to create company")

@app.get("/api/v1/companies")
async def get_companies_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all companies (super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_super_admin(current_user)
    
    # Get companies from MongoDB
    from services.mongo_db import mongo_db
    companies = mongo_db.get_companies()
    
    return {
        "message": "Companies retrieved successfully",
        "companies": companies,
        "total": len(companies)
    }

@app.put("/api/v1/users/{user_id}")
async def update_user_endpoint(user_id, request: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update an existing user (super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_super_admin(current_user)
    
    app_logger.info(f"User update request for user_id: {user_id} (type: {type(user_id)})")
    
    # Handle both string and int user_id
    if isinstance(user_id, str):
        # Try to convert to int, if fails try to find user by username
        try:
            user_id = int(user_id)
        except ValueError:
            # Find user by username
            from services.mongo_db import mongo_db
            users = mongo_db.get_users()
            found_user = None
            for user in users:
                if user.get("username") == user_id:
                    found_user = user
                    break
            if found_user:
                user_id = found_user.get("id")
            else:
                raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    
    # Update user in MongoDB
    from services.mongo_db import mongo_db
    success = mongo_db.update_user(user_id, request)
    
    if success:
        app_logger.info(f"User updated successfully: {user_id}")
        return {"message": "User updated successfully"}
    else:
        app_logger.error(f"Failed to update user: {user_id}")
        raise HTTPException(status_code=500, detail="Failed to update user")

@app.delete("/api/v1/users/{user_id}")
async def delete_user_endpoint(user_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete a user (super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_super_admin(current_user)
    
    # Delete user from MongoDB
    from services.mongo_db import mongo_db
    success = mongo_db.delete_user(user_id)
    
    if success:
        app_logger.info(f"User deleted successfully: {user_id}")
        return {"message": "User deleted successfully"}
    else:
        app_logger.error(f"Failed to delete user: {user_id}")
        raise HTTPException(status_code=500, detail="Failed to delete user")

@app.post("/api/v1/upload/logo")
async def upload_logo_endpoint(file: UploadFile = File(...), credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Upload company logo (super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_super_admin(current_user)
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Only image files are allowed")
    
    # Save uploaded file
    import os
    import uuid
    
    # Create uploads directory if it doesn't exist
    upload_dir = "../public/logos"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    
    logo_url = f"/logos/{unique_filename}"
    app_logger.info(f"Logo uploaded successfully: {logo_url}")
    
    return {
        "message": "Logo uploaded successfully",
        "logo_url": logo_url
    }

@app.put("/api/v1/campaigns/{campaign_id}")
async def update_campaign_endpoint(campaign_id: int, request: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update an existing campaign (admin and super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    # Update campaign in MongoDB
    from services.mongo_db import mongo_db
    success = mongo_db.update_campaign(campaign_id, request)
    
    if success:
        # Get the updated campaign to return
        updated_campaign = None
        campaigns = mongo_db.get_campaigns()
        for campaign in campaigns:
            if campaign["id"] == campaign_id:
                updated_campaign = campaign
                break
        
        if updated_campaign:
            return {
                "message": "Campaign updated successfully",
                "campaign": updated_campaign
            }
        else:
            return {"message": "Campaign updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Campaign not found")

@app.delete("/api/v1/campaigns/{campaign_id}")
async def delete_campaign_endpoint(campaign_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete a campaign (admin and super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    # Delete campaign from MongoDB
    from services.mongo_db import mongo_db
    success = mongo_db.delete_campaign(campaign_id)
    
    if success:
        return {
            "message": "Campaign deleted successfully",
            "success": True
        }
    else:
        raise HTTPException(status_code=404, detail="Campaign not found")

# Leads CRUD endpoints
@app.put("/api/v1/leads/{lead_id}")
async def update_lead_endpoint(lead_id: int, request: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update an existing lead (admin and super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    # Update lead in MongoDB
    from services.mongo_db import mongo_db
    success = mongo_db.update_lead(lead_id, request)
    
    if success:
        # Get the updated lead to return
        updated_lead = None
        leads = mongo_db.get_leads()
        for lead in leads:
            if lead["id"] == lead_id:
                updated_lead = lead
                break
        
        if updated_lead:
            return {
                "message": "Lead updated successfully",
                "success": True,
                "lead": updated_lead
            }
        else:
            return {
                "message": "Lead updated successfully",
                "success": True
            }
    else:
        raise HTTPException(status_code=404, detail="Lead not found")

@app.delete("/api/v1/leads/{lead_id}")
async def delete_lead_endpoint(lead_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete a lead (admin and super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    # Delete lead from MongoDB
    from services.mongo_db import mongo_db
    success = mongo_db.delete_lead(lead_id)
    
    if success:
        return {
            "message": "Lead deleted successfully",
            "success": True
        }
    else:
        raise HTTPException(status_code=404, detail="Lead not found")

# Channels CRUD endpoints
@app.post("/api/v1/channels")
async def create_channel_endpoint(request: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new channel (admin and super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    # Create channel in MongoDB
    from services.mongo_db import mongo_db
    
    channel_data = {
        "name": request.get("name"),
        "connected": request.get("connected", False),
        "active": request.get("active", False),
        "followers": request.get("followers", 0),
        "created_by": current_user["username"]
    }
    
    success = mongo_db.create_channel(channel_data)
    
    if success:
        # The channel_data object now has the generated ID, but remove the MongoDB _id
        channel_response = channel_data.copy()
        channel_response.pop('_id', None)  # Remove MongoDB _id field
        
        return {
            "message": "Channel created successfully",
            "success": True,
            "channel": channel_response
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to create channel")

@app.put("/api/v1/channels/{channel_id}")
async def update_channel_endpoint(channel_id: int, request: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update an existing channel (admin and super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    # Update channel in MongoDB
    from services.mongo_db import mongo_db
    success = mongo_db.update_channel(channel_id, request)
    
    if success:
        # Get the updated channel to return
        updated_channel = None
        channels = mongo_db.get_channels()
        for channel in channels:
            if channel["id"] == channel_id:
                updated_channel = channel
                break
        
        if updated_channel:
            return {
                "message": "Channel updated successfully",
                "channel": updated_channel
            }
        else:
            return {"message": "Channel updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Channel not found")

@app.delete("/api/v1/channels/{channel_id}")
async def delete_channel_endpoint(channel_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete a channel (admin and super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    # Delete channel from MongoDB
    from services.mongo_db import mongo_db
    success = mongo_db.delete_channel(channel_id)
    
    if success:
        return {"message": "Channel deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Channel not found")

@app.post("/api/v1/channels/{channel_id}/connect")
async def connect_channel_endpoint(channel_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Connect a channel (admin and super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    # Connect channel in MongoDB
    from services.mongo_db import mongo_db
    success = mongo_db.connect_channel(channel_id)
    
    if success:
        # Get the updated channel to return
        channels = mongo_db.get_channels()
        updated_channel = None
        for channel in channels:
            if channel["id"] == channel_id:
                updated_channel = channel
                break
        
        return {
            "message": "Channel connected successfully",
            "channel": updated_channel
        }
    else:
        raise HTTPException(status_code=404, detail="Channel not found")

@app.post("/api/v1/channels/{channel_id}/disconnect")
async def disconnect_channel_endpoint(channel_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Disconnect a channel (admin and super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    # Disconnect channel in MongoDB
    from services.mongo_db import mongo_db
    success = mongo_db.disconnect_channel(channel_id)
    
    if success:
        # Get the updated channel to return
        channels = mongo_db.get_channels()
        updated_channel = None
        for channel in channels:
            if channel["id"] == channel_id:
                updated_channel = channel
                break
        
        return {
            "message": "Channel disconnected successfully",
            "channel": updated_channel
        }
    else:
        raise HTTPException(status_code=404, detail="Channel not found")

# Scheduler CRUD endpoints
@app.post("/api/v1/scheduler")
async def create_schedule_endpoint(request: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new schedule (admin and super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    # Create schedule in MongoDB
    from services.mongo_db import mongo_db
    
    schedule_data = {
        "campaign_id": request.get("campaign_id"),
        "task_name": request.get("task_name"),
        "scheduled_date": request.get("scheduled_date"),
        "scheduled_time": request.get("scheduled_time"),
        "status": request.get("status", "pending"),
        "priority": request.get("priority", "medium"),
        "created_by": current_user["username"]
    }
    
    success = mongo_db.create_schedule(schedule_data)
    
    if success:
        # The schedule_data object now has the generated ID, but remove the MongoDB _id
        schedule_response = schedule_data.copy()
        schedule_response.pop('_id', None)  # Remove MongoDB _id field
        
        return {
            "message": "Schedule created successfully",
            "schedule": schedule_response
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to create schedule")

@app.put("/api/v1/scheduler/{schedule_id}")
async def update_schedule_endpoint(schedule_id: int, request: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update an existing schedule (admin and super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    # Update schedule in MongoDB
    from services.mongo_db import mongo_db
    success = mongo_db.update_schedule(schedule_id, request)
    
    if success:
        # Get the updated schedule to return
        schedules = mongo_db.get_scheduler()
        updated_schedule = None
        for schedule in schedules:
            if schedule["id"] == schedule_id:
                updated_schedule = schedule
                break
        
        return {
            "message": "Schedule updated successfully",
            "schedule": updated_schedule
        }
    else:
        raise HTTPException(status_code=404, detail="Schedule not found")

@app.delete("/api/v1/scheduler/{schedule_id}")
async def delete_schedule_endpoint(schedule_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete a schedule (admin and super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    # Delete schedule from MongoDB
    from services.mongo_db import mongo_db
    success = mongo_db.delete_schedule(schedule_id)
    
    if success:
        return {"message": "Schedule deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Schedule not found")

@app.get("/api/v1/user/profile")
async def get_user_profile_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user profile"""
    app_logger.info("User profile requested")
    result = get_user_profile_service(credentials.credentials)
    app_logger.info(f"User profile result: {result['message']}")
    return result

@app.put("/api/v1/user/profile")
async def update_user_profile_endpoint(request: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update current user profile"""
    app_logger.info("User profile update requested")
    result = update_user_profile_service(request, credentials.credentials)
    app_logger.info(f"User profile update result: {result['message']}")
    return result

@app.get("/api/v1/health")
async def health_check_endpoint():
    """System health check"""
    app_logger.info("Health check requested")
    result = health_check()
    app_logger.info(f"Health check result: {result['status']}")
    return result

# Role Management endpoints
@app.get("/api/v1/admin/roles")
async def get_roles_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all roles and permissions (super_admin only)"""
    app_logger.info("Roles data requested")
    result = get_roles_service(credentials.credentials)
    app_logger.info(f"Returned {len(result['roles'])} roles")
    return result

@app.post("/api/v1/admin/roles")
async def create_role_endpoint(request: RoleRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new role (super_admin only)"""
    app_logger.info(f"Role creation request: {request.role_name}")
    result = create_role_service(credentials.credentials, request)
    app_logger.info(f"Role creation result: {result['message']}")
    return result

@app.put("/api/v1/admin/roles/{role_key}")
async def update_role_endpoint(role_key: str, request: RoleRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update an existing role (super_admin only)"""
    app_logger.info(f"Role update request for {role_key}: {request.role_name}")
    result = update_role_service(credentials.credentials, role_key, request)
    app_logger.info(f"Role update result: {result['message']}")
    return result

@app.delete("/api/v1/admin/roles/{role_key}")
async def delete_role_endpoint(role_key: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete a role (super_admin only)"""
    app_logger.info(f"Role deletion request for: {role_key}")
    try:
        result = delete_role_service(credentials.credentials, role_key)
        app_logger.info(f"Role deletion result: {result['message']}")
        return result
    except Exception as e:
        app_logger.error(f"Failed to delete role {role_key}: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=f"Role '{role_key}' not found or cannot be deleted"
        )

@app.put("/api/v1/admin/roles/{role_key}/permissions")
async def update_permissions_endpoint(role_key: str, request: PermissionUpdateRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update permissions for a role (super_admin only)"""
    app_logger.info(f"Permissions update request for role: {role_key}")
    # Set the role_key in the request to match the URL parameter
    request.role_key = role_key
    result = update_permissions_service(credentials.credentials, request)
    app_logger.info(f"Permissions update result: {result['message']}")
    return result

@app.post("/api/v1/trigger-refresh")
async def trigger_refresh_endpoint():
    """Trigger frontend refresh after data changes"""
    app_logger.info("Refresh trigger received - notifying frontend clients")
    return {
        "message": "Refresh triggered successfully",
        "timestamp": datetime.utcnow().isoformat(),
        "type": "data_update"
    }

@app.get("/api/v1/check-refresh")
async def check_refresh_endpoint():
    """Check if refresh is needed (for polling)"""
    # Simple implementation - always return no refresh needed
    # In a real implementation, this would check for recent changes
    return {
        "type": "no_refresh",
        "message": "No refresh needed",
        "timestamp": datetime.utcnow().isoformat()
    }

def check_expiring_users():
    """Background job to check for users with expiring access"""
    from services.util import RoleMiddleware
    from services.mongo_db import mongo_db
    from services.constants import DEV_MODE
    
    try:
        if DEV_MODE:
            users = users_db.values()
        else:
            users = mongo_db.get_all_users()
        
        for user in users:
            if not RoleMiddleware.check_access_expiration(user):
                # User is expired, send expired email
                send_access_expired_email(user)
                app_logger.warning(f"Access expired email sent to user: {user.get('username', 'Unknown')}")
            else:
                # Check if access expires in next 24 hours
                access_expires_at = user.get("access_expires_at")
                if access_expires_at:
                    from datetime import datetime
                    expiry_time = datetime.fromisoformat(access_expires_at.replace('Z', '+00:00'))
                    hours_remaining = (expiry_time - datetime.utcnow()).total_seconds() / 3600
                    
                    if hours_remaining <= 24 and hours_remaining > 0:
                        send_access_expiring_email(user, int(hours_remaining))
                        app_logger.info(f"Access expiring email sent to user: {user.get('username', 'Unknown')} ({hours_remaining:.1f} hours remaining)")
                        
    except Exception as e:
        app_logger.error(f"Error in expiring users check: {e}")

def start_expiring_users_scheduler():
    """Start background scheduler to check expiring users"""
    import asyncio
    
    async def scheduler_task():
        while True:
            try:
                check_expiring_users()
                app_logger.info("Completed expiring users check")
            except Exception as e:
                app_logger.error(f"Error in scheduler: {e}")
            
            # Check every hour (3600 seconds)
            await asyncio.sleep(3600)
    
    # Run scheduler in background
    scheduler_thread = threading.Thread(target=lambda: asyncio.run(scheduler_task()), daemon=True)
    scheduler_thread.start()
    app_logger.info("Expiring users scheduler started (checks every hour)")

# Company Management Endpoints
# Company endpoints will be implemented fresh

@app.get("/api/v1/admin/companies")
async def get_companies_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all companies (super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_super_admin(current_user)
    
    from services.mongo_db import mongo_db
    companies = mongo_db.get_companies()
    
    return {
        "message": "Companies retrieved successfully",
        "companies": companies
    }

@app.get("/api/v1/admin/companies/accessible")
async def get_accessible_companies_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get companies accessible to current user (admin and super_admin)"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    from services.mongo_db import mongo_db
    companies = mongo_db.get_companies()
    
    if current_user["role"] == "super_admin":
        # Super admin can see all companies
        return {
            "message": "Companies retrieved successfully",
            "companies": companies
        }
    elif current_user["role"] == "admin":
        # Admin can see their own company and potentially others
        # For now, return all companies but this can be restricted as needed
        return {
            "message": "Companies retrieved successfully",
            "companies": companies
        }
    else:
        # Other roles shouldn't access this endpoint
        raise HTTPException(status_code=403, detail="Access denied")

@app.post("/api/v1/admin/companies")
async def create_company_endpoint(request: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new company + admin user (super_admin only)"""
    current_user = get_user_from_token(credentials.credentials)
    require_super_admin(current_user)
    
    # Validate required fields
    required_fields = ["name", "adminUsername", "adminEmail"]
    for field in required_fields:
        if not request.get(field):
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    # Prepare company data
    company_data = {
        "name": request["name"].strip(),
        "companyId": request.get("companyId"),
        "adminUsername": request["adminUsername"].strip(),
        "adminEmail": request["adminEmail"].strip().lower(),
        "subscription": request.get("subscription", "basic"),
        "startDate": request.get("startDate"),
        "endDate": request.get("endDate")
    }
    
    # Create company
    from services.mongo_db import mongo_db
    try:
        created_company = mongo_db.create_company(company_data)
        app_logger.info(f"✅ Company created: {created_company['name']} with ID {created_company['id']}")
    except Exception as e:
        app_logger.error(f"❌ Company creation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    # Create admin user with correct company ID
    admin_user_data = {
        "username": request["adminUsername"].strip(),
        "email": request["adminEmail"].strip().lower(),
        "password": request.get("adminPassword", "TempPassword123!"),
        "name": request.get("adminName", f"Admin of {request['name']}").strip(),
        "role": "admin",
        "companyid": created_company["id"],  # Use the generated company ID
        "user_type": "tenant_user",
        "created_by": current_user["username"]
    }
    
    app_logger.info(f"🔄 Creating admin user with company ID {created_company['id']}")
    
    from services.routes import create_user_service
    admin_user = create_user_service(
        admin_user_data["username"], 
        admin_user_data["email"], 
        admin_user_data["password"],
        admin_user_data["name"], 
        admin_user_data["role"], 
        admin_user_data["companyid"],
        admin_user_data["created_by"], 
        None, 
        admin_user_data["user_type"]
    )
    
    if not admin_user:
        raise HTTPException(status_code=500, detail="Failed to create admin user")
    
    app_logger.info(f"✅ Admin user created: {admin_user['username']} for company {created_company['id']}")
    
    return {
        "message": f"Company {created_company['name']} created successfully",
        "success": True,
        "data": {
            "company": created_company,
            "admin_user": {
                "username": admin_user["username"],
                "email": admin_user["email"],
                "name": admin_user["name"],
                "role": admin_user["role"],
                "companyid": admin_user["companyid"],
                "user_type": admin_user["user_type"],
                "created_by": admin_user["created_by"]
            }
        }
    }

@app.put("/api/v1/admin/companies/{company_id}")
async def update_company_endpoint(company_id: int, request: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update a company (super_admin only)"""
    app_logger.info(f"Company update request for company ID: {company_id}")
    current_user = get_user_from_token(credentials.credentials)
    require_super_admin(current_user)
    
    # Update company in MongoDB
    from services.mongo_db import mongo_db
    
    # Get existing company
    companies = mongo_db.get_companies()
    existing_company = None
    for company in companies:
        if company.get("id") == company_id:
            existing_company = company
            break
    
    if not existing_company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Update allowed fields
    update_data = {}
    allowed_fields = ["name", "adminUsername", "adminEmail", "subscription", "status"]
    for field in allowed_fields:
        if field in request:
            update_data[field] = request[field]
    
    success = mongo_db.update_company(company_id, update_data)
    if not success:
        raise HTTPException(status_code=400, detail="Company update failed")
    
    return {
        "message": f"Company {company_id} updated successfully",
        "company": update_data
    }

@app.delete("/api/v1/admin/companies/{company_id}")
async def delete_company_endpoint(company_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete a company + all related users (super_admin only)"""
    app_logger.info(f"Company deletion request for company ID: {company_id}")
    current_user = get_user_from_token(credentials.credentials)
    require_super_admin(current_user)
    
    # Delete company in MongoDB
    from services.mongo_db import mongo_db
    success = mongo_db.delete_company(company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Company not found or deletion failed")
    
    # Cascade delete users from the company
    users_deleted = mongo_db.delete_users_by_company(company_id)
    
    return {
        "message": f"Company {company_id} and {users_deleted} related users deleted successfully"
    }

@app.on_event("startup")
async def startup_event():
    """Initialize MongoDB roles and data on startup"""
    try:
        from services.constants import DEV_MODE
        
        if not DEV_MODE:
            app_logger.info("Initializing MongoDB roles collection...")
            success = mongo_db.initialize_default_roles()
            if success:
                app_logger.info("MongoDB roles initialization completed successfully")
            else:
                app_logger.error("Failed to initialize MongoDB roles")
            
            app_logger.info("Initializing MongoDB default data...")
            success = mongo_db.initialize_default_data()
            if success:
                app_logger.info("MongoDB default data initialization completed successfully")
            else:
                app_logger.error("Failed to initialize MongoDB default data")
        else:
            app_logger.info("Running in DEV_MODE - skipping MongoDB initialization")
        
        # Initialize social media connections
        app_logger.info("Initializing social media connections...")
        initialize_connections()
        
        # Test social media connections
        connection_summary = connection_manager.get_connection_summary()
        app_logger.info(f"Social media connection summary: {connection_summary}")
        
        # Start the expiring users scheduler
        start_expiring_users_scheduler()
        
    except Exception as e:
        app_logger.error(f"Error during startup initialization: {e}")

# Import AI Generation endpoints
try:
    from services.ai_generation import *
    AI_GENERATION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AI Generation module not available - {e}")
    AI_GENERATION_AVAILABLE = False

# Social Media Integration Endpoints

@app.get("/api/v1/social/status")
async def get_social_status(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get social media integration status"""
    try:
        app_logger.info("Social media status requested")
        status_summary = connection_manager.get_connection_summary()
        return {
            "success": True,
            "data": status_summary,
            "message": "Social media status retrieved successfully"
        }
    except Exception as e:
        app_logger.error(f"Error getting social status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/social/platforms")
async def get_supported_platforms(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get list of supported social media platforms"""
    try:
        app_logger.info("Supported platforms requested")
        platforms_status = social_integration_manager.get_all_platforms_status()
        return {
            "success": True,
            "data": platforms_status,
            "message": "Supported platforms retrieved successfully"
        }
    except Exception as e:
        app_logger.error(f"Error getting supported platforms: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/social/test-connection/{platform}")
async def test_platform_connection(platform: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Test connection to a specific social media platform"""
    try:
        app_logger.info(f"Testing connection to platform: {platform}")
        
        try:
            social_platform = SocialPlatform(platform.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
        
        success = connection_manager.reconnect_platform(social_platform)
        
        return {
            "success": success,
            "platform": platform,
            "message": f"Connection test {'successful' if success else 'failed'}"
        }
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error testing platform connection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/social/post")
async def post_to_social_media(
    request: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Post content to social media platforms"""
    try:
        app_logger.info("Social media post requested")
        
        content = request.get("content")
        platform = request.get("platform")
        campaign_id = request.get("campaign_id")
        
        if not content or not platform:
            raise HTTPException(status_code=400, detail="Content and platform are required")
        
        try:
            social_platform = SocialPlatform(platform.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
        
        result = social_data_service.post_content(content, social_platform, campaign_id)
        
        return {
            "success": result["success"],
            "data": result,
            "message": f"Post {'successful' if result['success'] else 'failed'}"
        }
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error posting to social media: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/social/data-source")
async def get_data_source_info(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get information about current data sources"""
    try:
        app_logger.info("Data source info requested")
        data_source_info = social_data_service.get_data_source_info()
        
        return {
            "success": True,
            "data": data_source_info,
            "message": "Data source information retrieved successfully"
        }
    except Exception as e:
        app_logger.error(f"Error getting data source info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# User Social Media Connection Management Endpoints

@app.post("/api/v1/social/connect/{platform}")
async def connect_social_account(platform: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Initiate social media account connection for current user"""
    try:
        current_user = RoleMiddleware.get_current_user(credentials.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        username = current_user["username"]
        app_logger.info(f"User {username} initiating {platform} connection")
        
        # For now, use mock OAuth flow
        result = get_mock_oauth_flow(platform, username)
        
        return {
            "success": result["success"],
            "data": result if result["success"] else None,
            "message": result.get("message", result.get("error", ""))
        }
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error connecting {platform} account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/social/disconnect/{platform}")
async def disconnect_social_account(platform: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Disconnect social media account for current user"""
    try:
        current_user = RoleMiddleware.get_current_user(credentials.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        username = current_user["username"]
        app_logger.info(f"User {username} disconnecting {platform} account")
        
        result = social_oauth_manager.disconnect_user_account(username, platform)
        
        return {
            "success": result["success"],
            "data": result if result["success"] else None,
            "message": result.get("message", result.get("error", ""))
        }
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error disconnecting {platform} account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/social/connections")
async def get_user_connections(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user's social media connections"""
    try:
        current_user = RoleMiddleware.get_current_user(credentials.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        username = current_user["username"]
        app_logger.info(f"Getting connections for user {username}")
        
        result = social_oauth_manager.get_user_connections(username)
        
        return {
            "success": result["success"],
            "data": result if result["success"] else None,
            "message": result.get("message", result.get("error", ""))
        }
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error getting user connections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/social/test-connection/{platform}")
async def test_user_connection(platform: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Test current user's social media connection"""
    try:
        current_user = RoleMiddleware.get_current_user(credentials.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        username = current_user["username"]
        app_logger.info(f"Testing {platform} connection for user {username}")
        
        result = social_oauth_manager.test_user_connection(username, platform)
        
        return {
            "success": result["success"],
            "data": result if result["success"] else None,
            "message": result.get("message", result.get("error", ""))
        }
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error testing user connection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/social/oauth-url/{platform}")
async def get_oauth_url(platform: str, request: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get OAuth URL for social media platform"""
    try:
        current_user = RoleMiddleware.get_current_user(credentials.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        username = current_user["username"]
        callback_url = request.get("callback_url", f"http://localhost:3001/social/{platform}/callback")
        
        app_logger.info(f"Getting OAuth URL for {platform} for user {username}")
        
        if platform == "twitter" and SOCIAL_INTEGRATION_ENABLED:
            # Use real Twitter OAuth
            result = twitter_oauth.get_authorization_url(username, callback_url)
        else:
            # Use mock OAuth flow
            result = social_oauth_manager.get_oauth_url(platform, username, callback_url)
        
        return {
            "success": result["success"],
            "data": result if result["success"] else None,
            "message": result.get("message", result.get("error", ""))
        }
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error getting OAuth URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/social/oauth-callback/{platform}")
async def handle_oauth_callback(platform: str, request: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Handle OAuth callback from social media platform"""
    try:
        current_user = RoleMiddleware.get_current_user(credentials.credentials)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        username = current_user["username"]
        code = request.get("code")
        state = request.get("state")
        callback_url = request.get("callback_url", f"http://localhost:3001/social/{platform}/callback")
        
        app_logger.info(f"Handling OAuth callback for {platform} for user {username}")
        
        if platform == "twitter" and SOCIAL_INTEGRATION_ENABLED:
            # Use real Twitter OAuth
            result = twitter_oauth.exchange_code_for_token(username, code, state, callback_url)
        else:
            # Use mock OAuth flow
            result = social_oauth_manager.handle_oauth_callback(platform, code, state)
        
        return {
            "success": result["success"],
            "data": result if result["success"] else None,
            "message": result.get("message", result.get("error", ""))
        }
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error handling OAuth callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        app_logger.info("Shutting down social media connections...")
        shutdown_connections()
        app_logger.info("Social media connections shutdown complete")
    except Exception as e:
        app_logger.error(f"Error during shutdown: {e}")

if __name__ == "__main__":
    import uvicorn
    
    # Start server with proper configuration
    app_logger.info(f"Starting Social Connect API server on port {API_PORT}")
    uvicorn.run(
        "extension:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info",
        log_config=None,  # Disable default uvicorn logging to use our custom logger
        access_log=None  # Disable access log to prevent backend.log creation
    )
