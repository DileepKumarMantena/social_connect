from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.routes import (
    login_user, send_forgot_password_otp, 
    verify_otp, reset_password, APIRequest
)
from constants import API_TITLE, API_VERSION, API_HOST, API_PORT, ALLOWED_ORIGINS

app = FastAPI(title=API_TITLE, version=API_VERSION)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.post("/api/v1/login")
async def login(request: APIRequest):
    """Login endpoint"""
    return login_user(request)

@app.post("/api/v1/forgot-password")
async def forgot_password(request: APIRequest):
    """Send OTP for password reset"""
    return send_forgot_password_otp(request)

@app.post("/api/v1/verify-otp")
async def verify_otp_endpoint(request: APIRequest):
    """Verify OTP for password reset"""
    return verify_otp(request)

@app.post("/api/v1/reset-password")
async def reset_password_endpoint(request: APIRequest):
    """Reset password with new credentials"""
    return reset_password(request)

@app.get("/")
async def root():
    return {"message": "Social Connect API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
