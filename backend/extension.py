from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from fastapi.responses import JSONResponse, Response
from typing import Optional
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
    create_role_service, update_role_service, delete_role_service, update_permissions_service, health_check
)
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
from constants import API_TITLE, API_VERSION, API_HOST, API_PORT, ALLOWED_ORIGINS, campaigns_db, leads_db, channels_db, scheduler_db, user_settings_db

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
    if not credentials:
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
    is_limited, attempts = is_rate_limited(client_ip)
    
    if is_limited:
        app_logger.warning(f"Rate limit exceeded for IP: {client_ip}, attempts: {attempts}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many login attempts. Try again in {LOGIN_WINDOW_MINUTES} minutes.",
            headers={"Retry-After": str(LOGIN_WINDOW_MINUTES * 60)}
        )
    
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
    current_user = RoleMiddleware.get_current_user(token)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
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
        
        # Return user info with role-based permissions
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

@app.get("/api/v1/profile")
async def get_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user profile (protected endpoint)"""
    if not credentials:
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
    
    app_logger.info(f"Profile request for user: {user.get('username', 'unknown')}")
    
    # Get user's role and permissions
    user_role = user.get("role", "")
    
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
                "scheduler": {"Create": True, "Read": True, "Update": False, "Delete": False}
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
    
    # Return user profile data with permissions
    return {
        "username": user["username"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "companyid": user["companyid"],
        "activitystatus": user["activitystatus"],
        "access_expires_at": user.get("access_expires_at"),
        "created_by": user.get("created_by"),
        "roleId": user_permissions["roleId"],
        "roleName": user_permissions["roleName"],
        "permissions": user_permissions["permissions"]
    }

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

# Role-based management endpoints
@app.post("/api/v1/admin/users")
async def create_user_endpoint(request: CreateUserRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new user (super_admin and admin only)"""
    app_logger.info(f"User creation request by admin: {request.username}")
    result = create_user(request, credentials.credentials)
    app_logger.info(f"User creation result: {result['message']}")
    return result

@app.put("/api/v1/admin/users/{user_id}")
async def update_user_endpoint(user_id: str, request: CreateUserRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update an existing user (super_admin and admin only)"""
    app_logger.info(f"User update request for: {user_id}")
    # For now, we'll implement a basic update
    # In a real implementation, you'd have a separate update function
    try:
        # Get current user to verify permissions
        current_user = get_user_from_token(credentials.credentials)
        require_minimum_admin(current_user)
        
        # For mock implementation, just return success
        return {
            "message": f"User {user_id} updated successfully",
            "user": {
                "username": request.username,
                "email": request.email,
                "name": request.name,
                "role": request.role,
                "companyid": request.companyid
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/admin/users")
async def get_users_endpoint(role_filter: Optional[str] = None, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get users created by current user (super_admin and admin only)"""
    app_logger.info(f"Users list requested with filter: {role_filter}")
    result = get_users(credentials.credentials, role_filter)
    app_logger.info(f"Returned {len(result['users'])} users")
    return result

@app.post("/api/v1/admin/users/extend-access")
async def extend_user_access_endpoint(request: ExtendAccessRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extend user access (super_admin only)"""
    app_logger.info(f"Access extension request for user ID: {request.user_id}")
    result = extend_user_access(request, credentials.credentials)
    app_logger.info(f"Access extension result: {result['message']}")
    return result

@app.delete("/api/v1/admin/users/{user_id}")
async def deactivate_user_endpoint(user_id, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete a user completely (super_admin only)"""
    app_logger.info(f"User deletion request for: {user_id}")
    result = delete_user(user_id, credentials.credentials)
    app_logger.info(f"User deletion result: {result['message']}")
    return result

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
        "created_by": current_user["username"]
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
        return {"message": "Campaign deleted successfully"}
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
                "lead": updated_lead
            }
        else:
            return {"message": "Lead updated successfully"}
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
        return {"message": "Lead deleted successfully"}
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
    from constants import DEV_MODE
    
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

@app.on_event("startup")
async def startup_event():
    """Initialize MongoDB roles and data on startup"""
    try:
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
        
        # Start the expiring users scheduler
        start_expiring_users_scheduler()
        
    except Exception as e:
        app_logger.error(f"Error during startup initialization: {e}")

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
