from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from services.routes import (
    login_user, send_forgot_password_otp, 
    verify_otp, reset_password, get_user_profile, APIRequest,
    get_channels, get_campaigns, get_leads, get_dashboard_stats,
    create_user, get_users, extend_user_access, deactivate_user,
    clear_all_data, get_user_profile_service, health_check,
    CreateUserRequest, ExtendAccessRequest
)
from services.response import StandardResponse
from services.logger import app_logger
from stored_procedures.database import init_database, seed_initial_data
from constants import API_TITLE, API_VERSION, API_HOST, API_PORT, ALLOWED_ORIGINS, DEV_MODE

app = FastAPI(title=API_TITLE, version=API_VERSION)

# Security
security = HTTPBearer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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
async def login(request: APIRequest):
    """Login endpoint"""
    app_logger.info(f"Login attempt for user: {request.username}")
    result = login_user(request)
    app_logger.info(f"Login result: {result.message}")
    return result

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
async def get_channels_endpoint():
    """Get all channels"""
    app_logger.info("Channels data requested")
    result = get_channels()
    app_logger.info(f"Returned {len(result.channels)} channels")
    return result

@app.get("/api/v1/campaigns")
async def get_campaigns_endpoint():
    """Get all campaigns"""
    app_logger.info("Campaigns data requested")
    result = get_campaigns()
    app_logger.info(f"Returned {len(result.campaigns)} campaigns")
    return result

@app.get("/api/v1/leads")
async def get_leads_endpoint():
    """Get all leads"""
    app_logger.info("Leads data requested")
    result = get_leads()
    app_logger.info(f"Returned {len(result.leads)} leads")
    return result

@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats_endpoint():
    """Get dashboard statistics"""
    app_logger.info("Dashboard stats requested")
    result = get_dashboard_stats()
    app_logger.info(f"Dashboard stats: {result.stats}")
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

if __name__ == "__main__":
    import uvicorn
    
    # Initialize database and seed data if not in DEV_MODE
    if not DEV_MODE:
        app_logger.info("Initializing database (DEV_MODE=False)")
        try:
            init_database()
            seed_initial_data()
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
