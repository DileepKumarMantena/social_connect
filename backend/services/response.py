from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Union

class BaseResponse(BaseModel):
    """Base response class for all API responses"""
    message: str
    success: bool = True
    data: Optional[Dict[str, Any]] = None

class StandardResponse(BaseModel):
    """Standard response class for general API responses"""
    message: str
    success: bool = True
    data: Optional[Dict[str, Any]] = None

class LoginResponse(BaseModel):
    """Response for login endpoint"""
    message: str
    success: bool = True
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    user: Optional[Dict[str, Union[str, int, bool]]] = None

class OTPResponse(BaseModel):
    """Response for OTP related endpoints"""
    message: str
    success: bool = True
    otp: Optional[str] = None  # OTP field for development mode

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

class ChannelResponse(BaseModel):
    """Response for channel endpoint"""
    message: str
    success: bool = True
    channels: List[Dict[str, Any]] = []

class CampaignResponse(BaseModel):
    """Response for campaign endpoint"""
    message: str
    success: bool = True
    campaigns: List[Dict[str, Any]] = []

class LeadResponse(BaseModel):
    """Response for lead endpoint"""
    message: str
    success: bool = True
    leads: List[Dict[str, Any]] = []

class DashboardStatsResponse(BaseModel):
    """Response for dashboard stats endpoint"""
    message: str
    success: bool = True
    stats: Dict[str, int] = {}

class AnalyticsResponse(BaseModel):
    """Response for analytics endpoint"""
    message: str
    success: bool = True
    analytics: List[Dict[str, Any]] = []

class SchedulerResponse(BaseModel):
    """Response for scheduler endpoint"""
    message: str
    success: bool = True
    schedules: List[Dict[str, Any]] = []

class SettingsResponse(BaseModel):
    """Response for settings endpoint"""
    message: str
    success: bool = True
    settings: Dict[str, Any] = {}
