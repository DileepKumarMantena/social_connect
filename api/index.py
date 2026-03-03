import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import sys
import subprocess

# Add backend to path
sys.path.append('/var/task/backend')

# Mock database for quick deployment
USERS = {
    "superadmin": {
        "username": "superadmin",
        "password": "SuperAdmin123!",
        "name": "Super Admin",
        "role": "super_admin",
        "email": "superadmin@company.com"
    },
    "admin1": {
        "username": "admin1", 
        "password": "Admin123!",
        "name": "Admin User",
        "role": "admin",
        "email": "admin1@company.com"
    },
    "user1": {
        "username": "user1",
        "password": "User123!",
        "name": "Regular User", 
        "role": "user",
        "email": "user1@company.com"
    }
}

CAMPAIGNS = [
    {"id": 1, "name": "Summer Sale", "status": "active", "leads": 45, "conversion_rate": 12.5, "created_by": "admin1"},
    {"id": 2, "name": "Product Launch", "status": "completed", "leads": 120, "conversion_rate": 8.3, "created_by": "admin1"},
    {"id": 3, "name": "Holiday Special", "status": "draft", "leads": 0, "conversion_rate": 0, "created_by": "superadmin"}
]

CHANNELS = [
    {"id": 1, "name": "facebook", "connected": True, "active": True, "followers": 1500, "created_by": "admin1"},
    {"id": 2, "name": "instagram", "connected": True, "active": False, "followers": 800, "created_by": "admin1"},
    {"id": 3, "name": "linkedin", "connected": False, "active": False, "followers": 0, "created_by": "superadmin"},
    {"id": 4, "name": "twitter", "connected": False, "active": False, "followers": 0, "created_by": "admin1"},
    {"id": 5, "name": "youtube", "connected": True, "active": True, "followers": 2500, "created_by": "superadmin"}
]

LEADS = [
    {"id": 1, "name": "John Doe", "email": "john@example.com", "status": "new", "campaign_id": 1, "created_by": "admin1"},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "status": "contacted", "campaign_id": 1, "created_by": "admin1"},
    {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "status": "converted", "campaign_id": 2, "created_by": "admin1"}
]

class APIHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/api/v1/health':
            response = {"status": "healthy", "database": "mock", "timestamp": "2026-03-04T10:00:00Z"}
        elif path == '/api/v1/channels':
            response = {"success": True, "channels": CHANNELS}
        elif path == '/api/v1/campaigns':
            response = {"success": True, "campaigns": CAMPAIGNS}
        elif path == '/api/v1/leads':
            response = {"success": True, "leads": LEADS}
        elif path.startswith('/api/v1/dashboard/stats'):
            connected_channels = len([ch for ch in CHANNELS if ch.get("connected", False)])
            active_campaigns = len([ca for ca in CAMPAIGNS if ca.get("status") == "active"])
            total_leads = len(LEADS)
            
            response = {
                "success": True,
                "stats": {
                    "connected_channels": connected_channels,
                    "active_campaigns": active_campaigns,
                    "total_leads": total_leads
                }
            }
        else:
            response = {"error": "Endpoint not found"}

        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/api/v1/login':
            try:
                data = json.loads(post_data.decode('utf-8'))
                username = data.get('username')
                password = data.get('password')
                
                if username in USERS and USERS[username]['password'] == password:
                    user = USERS[username]
                    response = {
                        "success": True,
                        "access_token": "mock_jwt_token_12345",
                        "user": {
                            "username": user["username"],
                            "name": user["name"],
                            "role": user["role"],
                            "email": user["email"]
                        }
                    }
                else:
                    response = {"success": False, "error": "Invalid credentials"}
            except:
                response = {"success": False, "error": "Invalid request"}
        else:
            response = {"success": True, "message": "Operation completed"}

        self.wfile.write(json.dumps(response).encode())

def handler(event):
    # For serverless deployment
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({"status": "healthy"})
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), APIHandler)
    print(f"Server running on port {port}")
    server.serve_forever()
