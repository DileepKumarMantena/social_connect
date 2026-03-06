"""
JSON Database Handler for Social Connect
Reads all mock data from JSON files instead of in-memory dictionaries
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from services.logger import app_logger

class JSONDatabase:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
            app_logger.info(f"Created data directory: {self.data_dir}")
    
    def _read_json(self, filename: str) -> Dict[str, Any]:
        """Read JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                app_logger.debug(f"Loaded {filename}: {len(data)} items")
                return data
        except FileNotFoundError:
            app_logger.warning(f"File not found: {filepath}, creating empty structure")
            return self._get_empty_structure(filename)
        except json.JSONDecodeError as e:
            app_logger.error(f"JSON decode error in {filename}: {e}")
            return self._get_empty_structure(filename)
    
    def _write_json(self, filename: str, data: Dict[str, Any]) -> bool:
        """Write JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            app_logger.debug(f"Saved {filename}: {len(data)} items")
            return True
        except Exception as e:
            app_logger.error(f"Failed to save {filename}: {e}")
            return False
    
    def _get_empty_structure(self, filename: str) -> Dict[str, Any]:
        """Get empty structure for each file type"""
        structures = {
            "users.json": {"users": []},
            "channels.json": {"channels": []},
            "campaigns.json": {"campaigns": []},
            "leads.json": {"leads": []},
            "analytics.json": {"analytics": []},
            "scheduler.json": {"scheduler": []},
            "settings.json": {"settings": []}
        }
        return structures.get(filename, {})
    
    def get_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        data = self._read_json("users.json")
        return data.get("users", [])
    
    def save_users(self, users: List[Dict[str, Any]]) -> bool:
        """Save users to JSON"""
        return self._write_json("users.json", {"users": users})
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        users = self.get_users()
        for user in users:
            if user.get("username") == username:
                return user
        return None
    
    def add_user(self, user: Dict[str, Any]) -> bool:
        """Add new user"""
        users = self.get_users()
        
        # Check if username already exists
        if self.get_user_by_username(user.get("username")):
            app_logger.warning(f"User {user.get('username')} already exists")
            return False
        
        # Assign new ID
        if users:
            max_id = max(u.get("id", 0) for u in users)
            user["id"] = max_id + 1
        else:
            user["id"] = 1
        
        # Add created_at if not present
        if "created_at" not in user:
            user["created_at"] = datetime.utcnow().isoformat() + "Z"
        
        users.append(user)
        return self.save_users(users)
    
    def update_user(self, username: str, updates: Dict[str, Any]) -> bool:
        """Update user by username"""
        users = self.get_users()
        for i, user in enumerate(users):
            if user.get("username") == username:
                users[i].update(updates)
                users[i]["updated_at"] = datetime.utcnow().isoformat() + "Z"
                return self.save_users(users)
        return False
    
    def delete_user(self, username: str) -> bool:
        """Delete user by username"""
        users = self.get_users()
        users = [u for u in users if u.get("username") != username]
        return self.save_users(users)
    
    def get_channels(self) -> List[Dict[str, Any]]:
        """Get all channels"""
        data = self._read_json("channels.json")
        return data.get("channels", [])
    
    def get_campaigns(self) -> List[Dict[str, Any]]:
        """Get all campaigns"""
        data = self._read_json("campaigns.json")
        return data.get("campaigns", [])
    
    def get_leads(self) -> List[Dict[str, Any]]:
        """Get all leads"""
        data = self._read_json("leads.json")
        return data.get("leads", [])
    
    def get_analytics(self) -> List[Dict[str, Any]]:
        """Get all analytics"""
        data = self._read_json("analytics.json")
        return data.get("analytics", [])
    
    def get_scheduler(self) -> List[Dict[str, Any]]:
        """Get all scheduler items"""
        data = self._read_json("scheduler.json")
        return data.get("scheduler", [])
    
    def get_settings(self) -> List[Dict[str, Any]]:
        """Get all settings"""
        data = self._read_json("settings.json")
        return data.get("settings", [])
    
    def get_roles(self) -> Dict[str, Any]:
        """Get all roles"""
        data = self._read_json("roles.json")
        return data.get("roles", {})
    
    def add_role(self, role_key: str, role_data: Dict[str, Any]) -> bool:
        """Add a new role"""
        try:
            data = self._read_json("roles.json")
            if "roles" not in data:
                data["roles"] = {}
            
            data["roles"][role_key] = role_data
            self._write_json("roles.json", data)
            app_logger.info(f"Role {role_key} added successfully")
            return True
        except Exception as e:
            app_logger.error(f"Failed to add role {role_key}: {e}")
            return False

# Global JSON database instance
json_db = JSONDatabase()
