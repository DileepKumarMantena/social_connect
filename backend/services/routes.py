from fastapi import status
from pydantic import BaseModel
from typing import Optional
from constants import users_db, otp_storage
from services.util import (
    verify_password, hash_password, generate_otp, store_otp, 
    verify_stored_otp, find_user_by_email, cleanup_otp, send_otp_email
)
from services.response import LoginResponse, OTPResponse, PasswordResetResponse
from services.error import APIError

class APIRequest(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    otp: Optional[str] = None

def login_user(request: APIRequest) -> LoginResponse:
    """Authenticate user and return login response"""
    username = request.username
    password = request.password
    
    # Validate required fields
    if not username or not password:
        raise APIError.bad_request("Username and password are required")
    
    # Check if user exists
    if username not in users_db:
        raise APIError.unauthorized("Invalid credentials")
    
    # Verify password
    user = users_db[username]
    if not verify_password(password, user["password_hash"]):
        raise APIError.unauthorized("Invalid credentials")
    
    return LoginResponse(
        message="Login successful",
        user={
            "username": user["username"],
            "email": user["email"]
        }
    )

def send_forgot_password_otp(request: APIRequest) -> OTPResponse:
    """Send OTP for password reset"""
    email = request.email
    
    # Validate required field
    if not email:
        raise APIError.bad_request("Email is required")
    
    # Check if email exists in our mock database
    user_exists = any(user["email"] == email for user in users_db.values())
    
    if not user_exists:
        # For security, don't reveal if email exists or not
        return OTPResponse(message="OTP sent to your email")
    
    # Generate and store OTP
    otp = generate_otp()
    store_otp(otp_storage, email, otp)
    
    # Send email with OTP
    email_sent = send_otp_email(email, otp)
    
    if email_sent:
        print(f"OTP {otp} sent successfully to {email}")
    else:
        print(f"Failed to send OTP to {email}. OTP: {otp}")
    
    return OTPResponse(message="OTP sent to your email")

def verify_otp(request: APIRequest) -> OTPResponse:
    """Verify OTP for password reset"""
    email = request.email
    otp = request.otp
    
    # Validate required fields
    if not email or not otp:
        raise APIError.bad_request("Email and OTP are required")
    
    if not verify_stored_otp(otp_storage, email, otp):
        raise APIError.bad_request("Invalid or expired OTP")
    
    return OTPResponse(message="OTP verified successfully")

def reset_password(request: APIRequest) -> PasswordResetResponse:
    """Reset password with new credentials"""
    email = request.email
    new_password = request.password
    
    # Validate required fields
    if not email or not new_password:
        raise APIError.bad_request("Email and password are required")
    
    # Find user by email
    username_to_update, user_to_update = find_user_by_email(users_db, email)
    
    if not user_to_update:
        raise APIError.not_found("User not found")
    
    # Update password
    users_db[username_to_update]["password_hash"] = hash_password(new_password)
    
    # Clean up OTP
    cleanup_otp(otp_storage, email)
    
    return PasswordResetResponse(message="Password reset successfully")
