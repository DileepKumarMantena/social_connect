"""
Simple AI Generation for Users and Companies
Integrated into existing forms
"""

from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from typing import Dict, List, Optional
import json
import random
import hashlib
from datetime import datetime, timedelta

from extension import app, security, get_user_from_token, require_minimum_admin, app_logger
from services.ai_user_generator import ai_generator

@app.post("/api/v1/ai/generate-user")
async def ai_generate_user_endpoint(
    request: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Generate a single user with AI assistance"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    # Extract parameters from request body
    role = request.get("role", "user")
    company_id = request.get("company_id")
    company_domain = request.get("company_domain")
    
    app_logger.info(f"AI generation request - role: {role}, company_id: {company_id}, company_domain: {company_domain}")
    
    try:
        user = ai_generator.generate_user(role, company_id, company_domain)
        
        app_logger.info(f"AI generated user: {user['username']} with role: {role} and company_id: {user.get('companyid')}")
        
        return {
            "success": True,
            "message": "User generated successfully",
            "user": user
        }
    except Exception as e:
        app_logger.error(f"Error generating user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate user: {str(e)}")

@app.post("/api/v1/ai/generate-company")
async def ai_generate_company_endpoint(
    industry: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Generate a single company with AI assistance"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    try:
        company = ai_generator.generate_company(industry)
        
        app_logger.info(f"AI generated company: {company['name']}")
        
        return {
            "success": True,
            "message": "Company generated successfully",
            "company": company
        }
    except Exception as e:
        app_logger.error(f"Error generating company: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate company: {str(e)}")

@app.get("/api/v1/ai/export/users/csv")
async def ai_export_users_csv_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Export all users as CSV"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    try:
        # Get all users from database
        from services.mongo_db import mongo_db
        users = mongo_db.get_users()
        
        # Create CSV content
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        header = [
            "username", "email", "name", "role", "companyid", "user_type",
            "activitystatus", "access_expires_at", "created_by", "phone",
            "address", "job_title", "department", "hire_date", "salary"
        ]
        writer.writerow(header)
        
        # Write user data
        for user in users:
            row = [
                user.get("username", ""),
                user.get("email", ""),
                user.get("name", ""),
                user.get("role", ""),
                user.get("companyid", ""),
                user.get("user_type", ""),
                user.get("activitystatus", ""),
                user.get("access_expires_at", ""),
                user.get("created_by", ""),
                user.get("phone", ""),
                user.get("address", {}).get("full_address", "") if user.get("address") else "",
                user.get("job_title", ""),
                user.get("department", ""),
                user.get("hire_date", ""),
                user.get("salary", "")
            ]
            writer.writerow(row)
        
        # Prepare response
        csv_content = output.getvalue()
        output.close()
        
        from fastapi.responses import Response
        response = Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
        
        app_logger.info(f"Exported {len(users)} users to CSV")
        
        return response
        
    except Exception as e:
        app_logger.error(f"Error exporting users to CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export users: {str(e)}")

@app.get("/api/v1/ai/export/companies/csv")
async def ai_export_companies_csv_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Export all companies as CSV"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    try:
        # Get all companies from database
        from services.mongo_db import mongo_db
        companies = mongo_db.get_companies()
        
        # Create CSV content
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        header = [
            "name", "domain", "industry", "size", "description",
            "address", "phone", "founded", "revenue"
        ]
        writer.writerow(header)
        
        # Write company data
        for company in companies:
            row = [
                company.get("name", ""),
                company.get("domain", ""),
                company.get("industry", ""),
                company.get("size", ""),
                company.get("description", ""),
                company.get("address", {}).get("full_address", "") if company.get("address") else "",
                company.get("phone", ""),
                company.get("founded", ""),
                company.get("revenue", "")
            ]
            writer.writerow(row)
        
        # Prepare response
        csv_content = output.getvalue()
        output.close()
        
        from fastapi.responses import Response
        response = Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=companies_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
        
        app_logger.info(f"Exported {len(companies)} companies to CSV")
        
        return response
        
    except Exception as e:
        app_logger.error(f"Error exporting companies to CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export companies: {str(e)}")
