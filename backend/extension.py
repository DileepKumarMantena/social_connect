from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from fastapi.responses import JSONResponse
from typing import Optional
from collections import defaultdict
from datetime import datetime, timedelta
import time
from services.routes import (
    get_campaigns, get_leads, get_channels,
    get_analytics, get_scheduler, get_settings,
    login_user, send_forgot_password_otp, verify_otp, reset_password,
    create_access_token, APIRequest, CreateUserRequest, ExtendAccessRequest, RoleRequest, PermissionUpdateRequest,
    get_dashboard_stats, get_roles_service, get_users, create_user, extend_user_access, deactivate_user, clear_all_data,
    create_role_service, update_role_service, delete_role_service, update_permissions_service
)
from services.util import RoleMiddleware
from services.response import StandardResponse
from services.logger import app_logger
from stored_procedures.database import init_database
from constants import API_TITLE, API_VERSION, API_HOST, API_PORT, ALLOWED_ORIGINS, DEV_MODE

# Security
oauth2_scheme = HTTPBearer()
security = HTTPBearer()

# Rate limiting storage
login_attempts = defaultdict(list)
MAX_LOGIN_ATTEMPTS = 5
LOGIN_WINDOW_MINUTES = 15

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
def get_current_user_dependency(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to validate JWT token and get current user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    from services.routes import get_current_user
    user = get_current_user(credentials.credentials)
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
    """Login endpoint with rate limiting and secure cookies"""
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
        
        # Create secure response with httpOnly cookie
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
        
    except Exception as e:
        app_logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@app.options("/api/v1/login")
async def login_options():
    """Handle OPTIONS preflight request"""
    return {"message": "OK"}

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
async def get_profile(current_user = Depends(get_current_user_dependency)):
    """Get current user profile (protected endpoint)"""
    app_logger.info(f"Profile request for user: {current_user.get('username', 'unknown')}")
    return current_user

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
    """Create a new user (super_admin only)"""
    app_logger.info(f"User creation request by super_admin: {request.username}")
    result = create_user(request, credentials.credentials)
    app_logger.info(f"User creation result: {result['message']}")
    return result

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
async def deactivate_user_endpoint(user_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Deactivate a user (super_admin only)"""
    app_logger.info(f"User deactivation request for ID: {user_id}")
    result = deactivate_user(user_id, credentials.credentials)
    app_logger.info(f"User deactivation result: {result['message']}")
    return result

@app.get("/api/v1/user/profile", response_model=StandardResponse)
async def get_user_profile_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user profile"""
    app_logger.info("User profile requested")
    result = get_user_profile_service(credentials.credentials)
    app_logger.info(f"User profile result: {result['message']}")
    return result

@app.get("/api/v1/health", response_model=StandardResponse)
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
    result = delete_role_service(credentials.credentials, role_key)
    app_logger.info(f"Role deletion result: {result['message']}")
    return result

@app.put("/api/v1/admin/roles/{role_key}/permissions")
async def update_permissions_endpoint(role_key: str, request: PermissionUpdateRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update permissions for a role (super_admin only)"""
    app_logger.info(f"Permissions update request for role: {role_key}")
    # Set the role_key in the request to match the URL parameter
    request.role_key = role_key
    result = update_permissions_service(credentials.credentials, request)
    app_logger.info(f"Permissions update result: {result['message']}")
    return result

if __name__ == "__main__":
    import uvicorn
    
    # Initialize database and seed data if not in DEV_MODE
    if not DEV_MODE:
        app_logger.info("Initializing database (DEV_MODE=False)")
        try:
            init_database()
            app_logger.info("Database initialization completed successfully")
        except Exception as e:
            app_logger.error(f"Database initialization failed: {e}")
    
    # Start server on port 8001 to avoid conflicts
    app_logger.info(f"Starting Social Connect API server on port 8001")
    uvicorn.run(
        "extension:app",
        host=API_HOST,
        port=8001,  # Changed from API_PORT to avoid conflicts
        reload=True,
        log_level="info"
    )
