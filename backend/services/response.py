from pydantic import BaseModel
from typing import Optional, Dict, Any

class BaseResponse(BaseModel):
    """Base response class for all API responses"""
    message: str
    success: bool = True
    data: Optional[Dict[str, Any]] = None

class LoginResponse(BaseModel):
    """Response for login endpoint"""
    message: str
    success: bool = True
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    user: Optional[Dict[str, str]] = None

class OTPResponse(BaseModel):
    """Response for OTP related endpoints"""
    message: str
    success: bool = True

class PasswordResetResponse(BaseModel):
    """Response for password reset endpoint"""
    message: str
    success: bool = True

class HealthResponse(BaseModel):
    """Response for health check endpoint"""
    message: str
    success: bool = True
    status: str = "running"

class UserProfileResponse(BaseModel):
    """Response for user profile endpoint"""
    message: str
    success: bool = True
    user: Optional[Dict[str, str]] = None
