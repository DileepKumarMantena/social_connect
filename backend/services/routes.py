from fastapi import status
from pydantic import BaseModel
from typing import Optional
from constants import users_db, otp_storage, channels_db, campaigns_db, leads_db, DEV_MODE
from services.util import (
    verify_password, hash_password, generate_otp, store_otp, 
    verify_stored_otp, find_user_by_email, cleanup_otp, send_otp_email,
    create_access_token, get_current_user, validate_password_strength
)
from services.response import LoginResponse, OTPResponse, PasswordResetResponse, UserProfileResponse, ChannelResponse, CampaignResponse, LeadResponse, DashboardStatsResponse
from services.error import APIError
from services.logger import app_logger
from stored_procedures.user_service import user_service
from stored_procedures.dashboard_service import dashboard_service

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
        user = user_service.verify_user_credentials(username, password)
        if not user:
            raise APIError.unauthorized("Invalid username or password")
    
    # Generate JWT token
    access_token = create_access_token(username)
    
    return LoginResponse(
        message="Login successful",
        access_token=access_token,
        token_type="bearer",
        user={
            "username": user["username"],
            "email": user["email"]
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
        user = find_user_by_email(users_db, email)
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
        user = find_user_by_email(users_db, email)
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

def get_channels() -> ChannelResponse:
    """Get all channels"""
    if DEV_MODE:
        app_logger.info("Using mock data for channels (DEV_MODE=True)")
        return ChannelResponse(
            message="Channels retrieved successfully (mock data)",
            channels=channels_db
        )
    else:
        app_logger.info("Using database for channels (DEV_MODE=False)")
        channels = dashboard_service.get_channels()
        return ChannelResponse(
            message="Channels retrieved successfully (database)",
            channels=channels
        )

def get_campaigns() -> CampaignResponse:
    """Get all campaigns"""
    if DEV_MODE:
        app_logger.info("Using mock data for campaigns (DEV_MODE=True)")
        return CampaignResponse(
            message="Campaigns retrieved successfully (mock data)",
            campaigns=campaigns_db
        )
    else:
        app_logger.info("Using database for campaigns (DEV_MODE=False)")
        campaigns = dashboard_service.get_campaigns()
        return CampaignResponse(
            message="Campaigns retrieved successfully (database)",
            campaigns=campaigns
        )

def get_leads() -> LeadResponse:
    """Get all leads"""
    if DEV_MODE:
        app_logger.info("Using mock data for leads (DEV_MODE=True)")
        return LeadResponse(
            message="Leads retrieved successfully (mock data)",
            leads=leads_db
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
