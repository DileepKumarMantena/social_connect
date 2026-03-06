import hashlib
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Mock user database
users_db = {
    "superadmin": {
        "username": "superadmin",
        "email": "deelipkumar261997@gmail.com",
        "password_hash": hashlib.sha256("SuperAdmin123!".encode()).hexdigest(),
        "name": "Super Admin",
        "role": "super_admin",
        "companyid": 0,
        "activitystatus": True,
        "access_expires_at": None,
        "created_by": None
    },
    "admin1": {
        "username": "admin1",
        "email": "admin1@company.com",
        "password_hash": hashlib.sha256("Admin123!".encode()).hexdigest(),
        "name": "Admin One",
        "role": "admin",
        "companyid": 1,
        "activitystatus": True,
        "access_expires_at": None,
        "created_by": "superadmin"
    },
    "user1": {
        "username": "user1",
        "email": "user1@company.com",
        "password_hash": hashlib.sha256("User123!".encode()).hexdigest(),
        "name": "User One",
        "role": "user",
        "companyid": 1,
        "activitystatus": True,
        "access_expires_at": None,
        "created_by": "admin1"
    }
}

# MongoDB Configuration
MONGODB_DB_NAME = "social_connect"

# API Configuration
API_TITLE = "Social Connect API"
API_VERSION = "1.0.0"
API_HOST = "0.0.0.0"
API_PORT = 8003

# CORS Configuration
ALLOWED_ORIGINS = ["http://localhost:3000", "http://localhost:3001", "http://192.168.1.6:3000"]

# OTP Configuration
OTP_EXPIRY_MINUTES = 10
OTP_LENGTH = 4

# Restricted OTP Patterns (avoid these for security)
RESTRICTED_OTP_PATTERNS = [
    '0000', '1111', '1234', '4321', '2222', '3333', '4444', '5555', 
    '6666', '7777', '8888', '9999', '1212', '1313', '1414', '1515',
    '2468', '1357', '2580', '1470', '2581', '3692'
]

# User Configuration
DEFAULT_USERNAME = "testuser"
DEFAULT_EMAIL = "test@example.com"
DEFAULT_PASSWORD = "Password123!"

# Brevo Email Configuration
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "YOUR_BREVO_API_KEY")  # Get from environment variable
BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL", "deelipkumar261997@gmail.com")  # Get from environment variable
BREVO_SENDER_NAME = os.getenv("BREVO_SENDER_NAME", "Social Connect")  # Get from environment variable

# Email Templates Configuration
EMAIL_TEMPLATES = {
    # Login OTP Email
    "login_otp": {
        "subject": "🔐 Social Connect - Login OTP Verification",
        "html_template": """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Social Connect - Login OTP</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f0f7ff;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 8px 32px rgba(0, 30, 60, 0.08);">
                <div style="background: linear-gradient(135deg, #1e4b8c 0%, #00b4d8 100%); padding: 40px 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 32px; font-weight: 700;">Social Connect</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">Secure Login Verification</p>
                </div>
                <div style="padding: 40px 30px;">
                    <h2 style="color: #023047; margin-top: 0; font-size: 24px;">Your Login OTP</h2>
                    <p style="color: #2b5f8a; font-size: 16px; line-height: 1.6;">Hi {name},</p>
                    <p style="color: #2b5f8a; font-size: 16px; line-height: 1.6;">You requested to login to your Social Connect account.</p>
                    <div style="background: #f8f9fa; padding: 30px; text-align: center; border-radius: 12px; margin: 30px 0; border: 2px dashed #00b4d8;">
                        <h1 style="color: #00b4d8; font-size: 36px; letter-spacing: 8px; margin: 0; font-weight: 700;">{otp}</h1>
                    </div>
                    <p style="color: #2b5f8a; font-size: 14px; line-height: 1.6;">This OTP will expire in <strong>10 minutes</strong>.</p>
                    <p style="color: #2b5f8a; font-size: 14px; line-height: 1.6;">If you didn't request this, please ignore this email.</p>
                </div>
                <div style="background: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e3f2fd;">
                    <p style="color: #6b7280; font-size: 12px; margin: 0;">Best regards,<br><strong>Social Connect Team</strong></p>
                    <p style="color: #9ca3af; font-size: 10px; margin: 10px 0 0 0;">This is an automated message. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """,
        "text_template": """
Social Connect - Login OTP Verification

Hello {name},

You requested to login to your Social Connect account.

Your OTP is: {otp}

This OTP will expire in 10 minutes.

If you didn't request this, please ignore this email.

Best regards,
Social Connect Team
        """
    },
    
    # Password Reset OTP Email
    "reset_otp": {
        "subject": "🔒 Social Connect - Password Reset OTP",
        "html_template": """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Social Connect - Password Reset</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #fff5f5;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 8px 32px rgba(220, 38, 38, 0.08);">
                <div style="background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); padding: 40px 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 32px; font-weight: 700;">Social Connect</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">Password Reset Request</p>
                </div>
                <div style="padding: 40px 30px;">
                    <h2 style="color: #991b1b; margin-top: 0; font-size: 24px;">Reset Your Password</h2>
                    <p style="color: #7f1d1d; font-size: 16px; line-height: 1.6;">Hi {name},</p>
                    <p style="color: #7f1d1d; font-size: 16px; line-height: 1.6;">You requested to reset your Social Connect account password.</p>
                    <div style="background: #fef2f2; padding: 30px; text-align: center; border-radius: 12px; margin: 30px 0; border: 2px dashed #ef4444;">
                        <h1 style="color: #dc2626; font-size: 36px; letter-spacing: 8px; margin: 0; font-weight: 700;">{otp}</h1>
                    </div>
                    <p style="color: #7f1d1d; font-size: 14px; line-height: 1.6;">This OTP will expire in <strong>10 minutes</strong>.</p>
                    <p style="color: #7f1d1d; font-size: 14px; line-height: 1.6;">If you didn't request this, please secure your account immediately.</p>
                </div>
                <div style="background: #fef2f2; padding: 30px; text-align: center; border-top: 1px solid #fecaca;">
                    <p style="color: #6b7280; font-size: 12px; margin: 0;">Best regards,<br><strong>Social Connect Team</strong></p>
                    <p style="color: #9ca3af; font-size: 10px; margin: 10px 0 0 0;">This is an automated message. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """,
        "text_template": """
Social Connect - Password Reset OTP

Hello {name},

You requested to reset your Social Connect account password.

Your OTP is: {otp}

This OTP will expire in 10 minutes.

If you didn't request this, please secure your account immediately.

Best regards,
Social Connect Team
        """
    },
    
    # User Creation Success Email
    "user_created": {
        "subject": "🎉 Welcome to Social Connect! Your Account is Ready",
        "html_template": """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Social Connect - Welcome</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f0fdf4;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 8px 32px rgba(34, 197, 94, 0.08);">
                <div style="background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%); padding: 40px 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 32px; font-weight: 700;">🎉 Welcome!</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">Your Social Connect Account is Ready</p>
                </div>
                <div style="padding: 40px 30px;">
                    <h2 style="color: #14532d; margin-top: 0; font-size: 24px;">Account Created Successfully</h2>
                    <p style="color: #166534; font-size: 16px; line-height: 1.6;">Hi {name},</p>
                    <p style="color: #166534; font-size: 16px; line-height: 1.6;">Welcome to Social Connect! Your account has been successfully created.</p>
                    
                    <div style="background: #f0fdf4; padding: 25px; border-radius: 12px; margin: 30px 0; border-left: 4px solid #22c55e;">
                        <h3 style="color: #14532d; margin: 0 0 15px 0; font-size: 18px;">📋 Your Login Details:</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0; color: #166534; font-weight: 600;">Username:</td>
                                <td style="padding: 8px 0; color: #166534;"><strong>{username}</strong></td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #166534; font-weight: 600;">Email:</td>
                                <td style="padding: 8px 0; color: #166534;"><strong>{email}</strong></td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #166534; font-weight: 600;">Password:</td>
                                <td style="padding: 8px 0; color: #166534;"><strong>{password}</strong></td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #166534; font-weight: 600;">Role:</td>
                                <td style="padding: 8px 0; color: #166534;"><strong>{role}</strong></td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background: #fef3c7; padding: 20px; border-radius: 12px; margin: 20px 0; border-left: 4px solid #f59e0b;">
                        <p style="color: #92400e; margin: 0; font-size: 14px; line-height: 1.6;">
                            <strong>🔐 Security Tip:</strong> Please change your password after first login for security.
                        </p>
                    </div>
                    
                    <p style="color: #166534; font-size: 16px; line-height: 1.6;">You can now login and start managing your social media campaigns!</p>
                </div>
                <div style="background: #f0fdf4; padding: 30px; text-align: center; border-top: 1px solid #bbf7d0;">
                    <p style="color: #6b7280; font-size: 12px; margin: 0;">Best regards,<br><strong>Social Connect Team</strong></p>
                    <p style="color: #9ca3af; font-size: 10px; margin: 10px 0 0 0;">This is an automated message. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """,
        "text_template": """
Social Connect - Welcome to Social Connect!

Hello {name},

Welcome to Social Connect! Your account has been successfully created.

Your Login Details:
Username: {username}
Email: {email}
Password: {password}
Role: {role}

Security Tip: Please change your password after first login for security.

You can now login and start managing your social media campaigns!

Best regards,
Social Connect Team
        """
    },
    
    # Lead Created Email
    "lead_created": {
        "subject": "🎯 New Lead Generated! - Social Connect",
        "html_template": """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Social Connect - New Lead</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #fef3c7;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 8px 32px rgba(245, 158, 11, 0.08);">
                <div style="background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%); padding: 40px 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 32px; font-weight: 700;">🎯 New Lead!</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">Lead Generated Successfully</p>
                </div>
                <div style="padding: 40px 30px;">
                    <h2 style="color: #78350f; margin-top: 0; font-size: 24px;">Lead Details</h2>
                    <p style="color: #92400e; font-size: 16px; line-height: 1.6;">Hi {name},</p>
                    <p style="color: #92400e; font-size: 16px; line-height: 1.6;">A new lead has been generated through your social media campaign!</p>
                    
                    <div style="background: #fffbeb; padding: 25px; border-radius: 12px; margin: 30px 0; border-left: 4px solid #f59e0b;">
                        <h3 style="color: #78350f; margin: 0 0 15px 0; font-size: 18px;">📊 Lead Information:</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0; color: #92400e; font-weight: 600;">Lead Name:</td>
                                <td style="padding: 8px 0; color: #92400e;"><strong>{lead_name}</strong></td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #92400e; font-weight: 600;">Email:</td>
                                <td style="padding: 8px 0; color: #92400e;"><strong>{lead_email}</strong></td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #92400e; font-weight: 600;">Phone:</td>
                                <td style="padding: 8px 0; color: #92400e;"><strong>{lead_phone}</strong></td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #92400e; font-weight: 600;">Source:</td>
                                <td style="padding: 8px 0; color: #92400e;"><strong>{campaign_name}</strong></td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #92400e; font-weight: 600;">Generated:</td>
                                <td style="padding: 8px 0; color: #92400e;"><strong>{timestamp}</strong></td>
                            </tr>
                        </table>
                    </div>
                    
                    <p style="color: #92400e; font-size: 16px; line-height: 1.6;">Follow up with this lead to convert them into a customer!</p>
                </div>
                <div style="background: #fffbeb; padding: 30px; text-align: center; border-top: 1px solid #fed7aa;">
                    <p style="color: #6b7280; font-size: 12px; margin: 0;">Best regards,<br><strong>Social Connect Team</strong></p>
                    <p style="color: #9ca3af; font-size: 10px; margin: 10px 0 0 0;">This is an automated message. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """,
        "text_template": """
Social Connect - New Lead Generated!

Hello {name},

A new lead has been generated through your social media campaign!

Lead Information:
Lead Name: {lead_name}
Email: {lead_email}
Phone: {lead_phone}
Source: {campaign_name}
Generated: {timestamp}

Follow up with this lead to convert them into a customer!

Best regards,
Social Connect Team
        """
    },
    
    # Campaign Created Email
    "campaign_created": {
        "subject": "🚀 New Campaign Launched! - Social Connect",
        "html_template": """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Social Connect - New Campaign</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f0f9ff;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 8px 32px rgba(59, 130, 246, 0.08);">
                <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 40px 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 32px; font-weight: 700;">🚀 Campaign Live!</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">New Campaign Successfully Launched</p>
                </div>
                <div style="padding: 40px 30px;">
                    <h2 style="color: #1e3a8a; margin-top: 0; font-size: 24px;">Campaign Details</h2>
                    <p style="color: #1e40af; font-size: 16px; line-height: 1.6;">Hi {name},</p>
                    <p style="color: #1e40af; font-size: 16px; line-height: 1.6;">Your new social media campaign has been successfully launched!</p>
                    
                    <div style="background: #eff6ff; padding: 25px; border-radius: 12px; margin: 30px 0; border-left: 4px solid #3b82f6;">
                        <h3 style="color: #1e3a8a; margin: 0 0 15px 0; font-size: 18px;">📢 Campaign Information:</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0; color: #1e40af; font-weight: 600;">Campaign Name:</td>
                                <td style="padding: 8px 0; color: #1e40af;"><strong>{campaign_name}</strong></td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #1e40af; font-weight: 600;">Platform:</td>
                                <td style="padding: 8px 0; color: #1e40af;"><strong>{platform}</strong></td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #1e40af; font-weight: 600;">Status:</td>
                                <td style="padding: 8px 0; color: #16a34a;"><strong>🟢 Active</strong></td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #1e40af; font-weight: 600;">Launch Date:</td>
                                <td style="padding: 8px 0; color: #1e40af;"><strong>{launch_date}</strong></td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #1e40af; font-weight: 600;">Target Audience:</td>
                                <td style="padding: 8px 0; color: #1e40af;"><strong>{target_audience}</strong></td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background: #dbeafe; padding: 20px; border-radius: 12px; margin: 20px 0; border-left: 4px solid #3b82f6;">
                        <p style="color: #1e3a8a; margin: 0; font-size: 14px; line-height: 1.6;">
                            <strong>📊 Next Steps:</strong> Monitor your campaign performance in the dashboard to track leads and engagement.
                        </p>
                    </div>
                    
                    <p style="color: #1e40af; font-size: 16px; line-height: 1.6;">Good luck with your campaign!</p>
                </div>
                <div style="background: #eff6ff; padding: 30px; text-align: center; border-top: 1px solid #bfdbfe;">
                    <p style="color: #6b7280; font-size: 12px; margin: 0;">Best regards,<br><strong>Social Connect Team</strong></p>
                    <p style="color: #9ca3af; font-size: 10px; margin: 10px 0 0 0;">This is an automated message. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """,
        "text_template": """
Social Connect - New Campaign Launched!

Hello {name},

Your new social media campaign has been successfully launched!

Campaign Information:
Campaign Name: {campaign_name}
Platform: {platform}
Status: 🟢 Active
Launch Date: {launch_date}
Target Audience: {target_audience}

Next Steps: Monitor your campaign performance in the dashboard to track leads and engagement.

Good luck with your campaign!

Best regards,
Social Connect Team
        """
    },
    
    # Access Expiring Email
    "access_expiring": {
        "subject": "⏰ Access Expiring Soon! - Social Connect",
        "html_template": """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Social Connect - Access Expiring</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #fffbeb;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 8px 32px rgba(251, 146, 60, 0.08);">
                <div style="background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%); padding: 40px 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 32px; font-weight: 700;">⏰ Access Expiring!</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">Your access will expire soon</p>
                </div>
                <div style="padding: 40px 30px;">
                    <h2 style="color: #92400e; margin-top: 0; font-size: 24px;">Action Required</h2>
                    <p style="color: #a16207; font-size: 16px; line-height: 1.6;">Hi {name},</p>
                    <p style="color: #a16207; font-size: 16px; line-height: 1.6;">Your Social Connect access will expire in <strong>{hours_remaining} hours</strong>.</p>
                    
                    <div style="background: #fef3c7; padding: 25px; border-radius: 12px; margin: 30px 0; border-left: 4px solid #f59e0b;">
                        <p style="color: #92400e; margin: 0; font-size: 14px; line-height: 1.6;">
                            <strong>📅 Expiry Date:</strong> {expiry_date}
                        </p>
                    </div>
                    
                    <p style="color: #a16207; font-size: 16px; line-height: 1.6;">Please contact your administrator to extend your access.</p>
                </div>
                <div style="background: #fffbeb; padding: 30px; text-align: center; border-top: 1px solid #fed7aa;">
                    <p style="color: #6b7280; font-size: 12px; margin: 0;">Best regards,<br><strong>Social Connect Team</strong></p>
                    <p style="color: #9ca3af; font-size: 10px; margin: 10px 0 0 0;">This is an automated message. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """,
        "text_template": """
Social Connect - Access Expiring Soon

Hello {name},

Your Social Connect access will expire in {hours_remaining} hours.

Expiry Date: {expiry_date}

Please contact your administrator to extend your access.

Best regards,
Social Connect Team
        """
    },
    
    # Access Expired Email
    "access_expired": {
        "subject": "🚫 Access Expired! - Social Connect",
        "html_template": """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Social Connect - Access Expired</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #fef2f2;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 8px 32px rgba(220, 38, 38, 0.08);">
                <div style="background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); padding: 40px 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 32px; font-weight: 700;">🚫 Access Expired!</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">Your access has expired</p>
                </div>
                <div style="padding: 40px 30px;">
                    <h2 style="color: #991b1b; margin-top: 0; font-size: 24px;">Access Denied</h2>
                    <p style="color: #7f1d1d; font-size: 16px; line-height: 1.6;">Hi {name},</p>
                    <p style="color: #7f1d1d; font-size: 16px; line-height: 1.6;">Your Social Connect access expired on <strong>{expiry_date}</strong>.</p>
                    
                    <div style="background: #fef2f2; padding: 25px; border-radius: 12px; margin: 30px 0; border-left: 4px solid #ef4444;">
                        <p style="color: #991b1b; margin: 0; font-size: 14px; line-height: 1.6;">
                            <strong>📅 Expired On:</strong> {expiry_date}
                        </p>
                    </div>
                    
                    <p style="color: #7f1d1d; font-size: 16px; line-height: 1.6;">Please contact your administrator to regain access.</p>
                </div>
                <div style="background: #fef2f2; padding: 30px; text-align: center; border-top: 1px solid #fecaca;">
                    <p style="color: #6b7280; font-size: 12px; margin: 0;">Best regards,<br><strong>Social Connect Team</strong></p>
                    <p style="color: #9ca3af; font-size: 10px; margin: 10px 0 0 0;">This is an automated message. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """,
        "text_template": """
Social Connect - Access Expired

Hello {name},

Your Social Connect access expired on {expiry_date}.

Please contact your administrator to regain access.

Best regards,
Social Connect Team
        """
    }
}

# In-memory tracking for mock mode (resets on server restart)
created_users = {}
created_roles = {}
deleted_roles = set()

# OTP storage (resets on server restart)
otp_storage = {}

# Mock databases (resets on server restart)
channels_db = {}
campaigns_db = {}
leads_db = {}
analytics_db = {}
scheduler_db = {}
user_settings_db = {}

# JWT Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Rate limiting configuration
LOGIN_WINDOW_MINUTES = 15
MAX_LOGIN_ATTEMPTS = 5

# MongoDB Collections
COLLECTIONS = {
    "users": "users",
    "roles": "roles", 
    "campaigns": "campaigns",
    "leads": "leads",
    "channels": "channels",
    "analytics": "analytics",
    "scheduler": "scheduler",
    "settings": "settings"
}

# Development mode
DEV_MODE = False  # Set to True for mock data, False for MongoDB
