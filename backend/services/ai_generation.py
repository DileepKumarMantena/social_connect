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

from fastapi import Response
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
        
        if not companies:
            raise HTTPException(status_code=404, detail="No companies found")
        
        # Create CSV content
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Company ID', 'Name', 'Domain', 'Industry', 'Size', 'Founded', 'Revenue', 'Phone', 'Address', 'Created At'])
        
        # Write company data
        for company in companies:
            writer.writerow([
                company.get('id', ''),
                company.get('name', ''),
                company.get('domain', ''),
                company.get('industry', ''),
                company.get('size', ''),
                company.get('founded', ''),
                company.get('revenue', ''),
                company.get('phone', ''),
                company.get('address', {}).get('full_address', ''),
                company.get('created_at', '')
            ])
        
        # Create response
        response = Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=companies_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
        
        app_logger.info(f"Exported {len(companies)} companies to CSV")
        
        return response
        
    except Exception as e:
        app_logger.error(f"Error exporting companies to CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export companies: {str(e)}")

@app.get("/api/v1/ai/export/campaigns/csv")
async def ai_export_campaigns_csv_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Export all campaigns as CSV"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    try:
        # Get all campaigns from database
        from services.mongo_db import mongo_db
        campaigns = mongo_db.get_campaigns()
        
        if not campaigns:
            raise HTTPException(status_code=404, detail="No campaigns found")
        
        # Create CSV content
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Campaign ID', 'Name', 'Description', 'Industry', 'Budget', 'Duration', 'Status', 'Created At'])
        
        # Write campaign data
        for campaign in campaigns:
            writer.writerow([
                campaign.get('id', ''),
                campaign.get('name', ''),
                campaign.get('description', ''),
                campaign.get('industry', ''),
                campaign.get('budget', ''),
                campaign.get('duration', ''),
                campaign.get('status', ''),
                campaign.get('created_at', '')
            ])
        
        # Create response
        response = Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=campaigns_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
        
        app_logger.info(f"Exported {len(campaigns)} campaigns to CSV")
        
        return response
        
    except Exception as e:
        app_logger.error(f"Error exporting campaigns to CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export campaigns: {str(e)}")

@app.get("/api/v1/ai/export/leads/csv")
async def ai_export_leads_csv_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Export all leads as CSV"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    try:
        # Get all leads from database
        from services.mongo_db import mongo_db
        leads = mongo_db.get_leads()
        
        if not leads:
            raise HTTPException(status_code=404, detail="No leads found")
        
        # Create CSV content
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Lead ID', 'Name', 'Email', 'Phone', 'Company', 'Status', 'Source', 'Created At'])
        
        # Write lead data
        for lead in leads:
            writer.writerow([
                lead.get('id', ''),
                lead.get('name', ''),
                lead.get('email', ''),
                lead.get('phone', ''),
                lead.get('company', ''),
                lead.get('status', ''),
                lead.get('source', ''),
                lead.get('created_at', '')
            ])
        
        # Create response
        response = Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=leads_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
        
        app_logger.info(f"Exported {len(leads)} leads to CSV")
        
        return response
        
    except Exception as e:
        app_logger.error(f"Error exporting leads to CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export leads: {str(e)}")

@app.get("/api/v1/ai/export/analytics/csv")
async def ai_export_analytics_csv_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Export all analytics as CSV"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    try:
        # Get all analytics from database
        from services.mongo_db import mongo_db
        analytics = mongo_db.get_analytics()
        
        if not analytics:
            raise HTTPException(status_code=404, detail="No analytics found")
        
        # Create CSV content
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Analytics ID', 'Metric Name', 'Value', 'Date', 'Campaign ID', 'Created At'])
        
        # Write analytics data
        for analytic in analytics:
            writer.writerow([
                analytic.get('id', ''),
                analytic.get('metric_name', ''),
                analytic.get('value', ''),
                analytic.get('date', ''),
                analytic.get('campaign_id', ''),
                analytic.get('created_at', '')
            ])
        
        # Create response
        response = Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=analytics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
        
        app_logger.info(f"Exported {len(analytics)} analytics to CSV")
        
        return response
        
    except Exception as e:
        app_logger.error(f"Error exporting analytics to CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export analytics: {str(e)}")

@app.get("/api/v1/ai/export/schedules/csv")
async def ai_export_schedules_csv_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Export all schedules as CSV"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    try:
        # Get all schedules from database
        from services.mongo_db import mongo_db
        schedules = mongo_db.get_schedules()
        
        if not schedules:
            raise HTTPException(status_code=404, detail="No schedules found")
        
        # Create CSV content
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Schedule ID', 'Name', 'Description', 'Start Time', 'End Time', 'Status', 'Campaign ID', 'Created At'])
        
        # Write schedule data
        for schedule in schedules:
            writer.writerow([
                schedule.get('id', ''),
                schedule.get('name', ''),
                schedule.get('description', ''),
                schedule.get('start_time', ''),
                schedule.get('end_time', ''),
                schedule.get('status', ''),
                schedule.get('campaign_id', ''),
                schedule.get('created_at', '')
            ])
        
        # Create response
        response = Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=schedules_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
        
        app_logger.info(f"Exported {len(schedules)} schedules to CSV")
        
        return response
        
    except Exception as e:
        app_logger.error(f"Error exporting schedules to CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export schedules: {str(e)}")

@app.get("/api/v1/ai/export/channels/csv")
async def ai_export_channels_csv_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Export all channels as CSV"""
    current_user = get_user_from_token(credentials.credentials)
    require_minimum_admin(current_user)
    
    try:
        # Get all channels from database
        from services.mongo_db import mongo_db
        channels = mongo_db.get_channels()
        
        if not channels:
            raise HTTPException(status_code=404, detail="No channels found")
        
        # Create CSV content
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Channel ID', 'Name', 'Type', 'Description', 'Status', 'Created At'])
        
        # Write channel data
        for channel in channels:
            writer.writerow([
                channel.get('id', ''),
                channel.get('name', ''),
                channel.get('type', ''),
                channel.get('description', ''),
                channel.get('status', ''),
                channel.get('created_at', '')
            ])
        
        # Create response
        response = Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=channels_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
        
        app_logger.info(f"Exported {len(channels)} channels to CSV")
        
        return response
        
    except Exception as e:
        app_logger.error(f"Error exporting channels to CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export channels: {str(e)}")
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
