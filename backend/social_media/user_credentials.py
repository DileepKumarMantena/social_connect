#!/usr/bin/env python3
"""
User Social Media Credentials Service
Manages per-user social media platform credentials and connections
"""

import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from services.logger import app_logger
from services.mongo_db import mongo_db
from services.constants import DEV_MODE

class UserSocialCredentials:
    """Manages user-specific social media credentials"""
    
    def __init__(self):
        self.collection_name = "user_social_credentials"
        
        # Mock storage for DEV_MODE
        self.mock_credentials = {}
        
    def _hash_sensitive_data(self, data: str) -> str:
        """Hash sensitive data for storage"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _encrypt_credential(self, credential: str) -> str:
        """Encrypt credential for storage (simple hashing for demo)"""
        return self._hash_sensitive_data(credential)
    
    def _decrypt_credential(self, hashed_credential: str) -> str:
        """In production, use proper decryption. For demo, return placeholder."""
        return "encrypted_value"
    
    def store_user_credentials(self, username: str, platform: str, credentials: Dict[str, Any]) -> bool:
        """Store social media credentials for a specific user"""
        try:
            credential_data = {
                "username": username,
                "platform": platform.lower(),
                "credentials": {
                    # Encrypt sensitive data
                    "access_token": self._encrypt_credential(credentials.get("access_token", "")),
                    "access_token_secret": self._encrypt_credential(credentials.get("access_token_secret", "")),
                    "user_id": credentials.get("user_id"),
                    "username": credentials.get("username"),
                    "profile_image": credentials.get("profile_image", ""),
                    "verified": credentials.get("verified", False)
                },
                "connected_at": datetime.now().isoformat(),
                "last_used": datetime.now().isoformat(),
                "status": "connected"
            }
            
            if DEV_MODE:
                # Store in mock storage
                if username not in self.mock_credentials:
                    self.mock_credentials[username] = {}
                self.mock_credentials[username][platform.lower()] = credential_data
                app_logger.info(f"Stored mock credentials for {username} on {platform}")
                return True
            else:
                # Store in MongoDB
                collection = mongo_db.get_collection(self.collection_name)
                
                # Remove existing credentials for this user and platform
                collection.delete_many({"username": username, "platform": platform.lower()})
                
                # Insert new credentials
                result = collection.insert_one(credential_data)
                success = result.acknowledged
                
                if success:
                    app_logger.info(f"Stored credentials for {username} on {platform}")
                return success
                
        except Exception as e:
            app_logger.error(f"Error storing credentials for {username} on {platform}: {e}")
            return False
    
    def get_user_credentials(self, username: str, platform: str) -> Optional[Dict[str, Any]]:
        """Get social media credentials for a specific user and platform"""
        try:
            if DEV_MODE:
                # Get from mock storage
                user_creds = self.mock_credentials.get(username, {})
                platform_creds = user_creds.get(platform.lower())
                
                if platform_creds:
                    # For demo, return mock credentials
                    return {
                        "access_token": "mock_token_for_testing",
                        "access_token_secret": "mock_secret_for_testing",
                        "user_id": platform_creds["credentials"]["user_id"],
                        "username": platform_creds["credentials"]["username"],
                        "profile_image": platform_creds["credentials"]["profile_image"],
                        "verified": platform_creds["credentials"]["verified"]
                    }
                return None
            else:
                # Get from MongoDB
                collection = mongo_db.get_collection(self.collection_name)
                credential_doc = collection.find_one({
                    "username": username, 
                    "platform": platform.lower()
                })
                
                if credential_doc:
                    # In production, decrypt credentials here
                    return {
                        "access_token": "decrypted_token",  # Would decrypt stored value
                        "access_token_secret": "decrypted_secret",  # Would decrypt stored value
                        "user_id": credential_doc["credentials"]["user_id"],
                        "username": credential_doc["credentials"]["username"],
                        "profile_image": credential_doc["credentials"]["profile_image"],
                        "verified": credential_doc["credentials"]["verified"]
                    }
                return None
                
        except Exception as e:
            app_logger.error(f"Error retrieving credentials for {username} on {platform}: {e}")
            return None
    
    def get_user_connected_platforms(self, username: str) -> List[str]:
        """Get list of platforms a user has connected"""
        try:
            if DEV_MODE:
                # Get from mock storage
                user_creds = self.mock_credentials.get(username, {})
                return list(user_creds.keys())
            else:
                # Get from MongoDB
                collection = mongo_db.get_collection(self.collection_name)
                credentials = collection.find({"username": username})
                return [cred["platform"] for cred in credentials]
                
        except Exception as e:
            app_logger.error(f"Error getting connected platforms for {username}: {e}")
            return []
    
    def remove_user_credentials(self, username: str, platform: str) -> bool:
        """Remove social media credentials for a specific user and platform"""
        try:
            if DEV_MODE:
                # Remove from mock storage
                if username in self.mock_credentials and platform.lower() in self.mock_credentials[username]:
                    del self.mock_credentials[username][platform.lower()]
                    app_logger.info(f"Removed mock credentials for {username} on {platform}")
                    return True
                return False
            else:
                # Remove from MongoDB
                collection = mongo_db.get_collection(self.collection_name)
                result = collection.delete_many({
                    "username": username, 
                    "platform": platform.lower()
                })
                success = result.deleted_count > 0
                
                if success:
                    app_logger.info(f"Removed credentials for {username} on {platform}")
                return success
                
        except Exception as e:
            app_logger.error(f"Error removing credentials for {username} on {platform}: {e}")
            return False
    
    def update_last_used(self, username: str, platform: str) -> bool:
        """Update the last used timestamp for user credentials"""
        try:
            if DEV_MODE:
                # Update mock storage
                if username in self.mock_credentials and platform.lower() in self.mock_credentials[username]:
                    self.mock_credentials[username][platform.lower()]["last_used"] = datetime.now().isoformat()
                    return True
                return False
            else:
                # Update MongoDB
                collection = mongo_db.get_collection(self.collection_name)
                result = collection.update_one(
                    {"username": username, "platform": platform.lower()},
                    {"$set": {"last_used": datetime.now().isoformat()}}
                )
                return result.modified_count > 0
                
        except Exception as e:
            app_logger.error(f"Error updating last used for {username} on {platform}: {e}")
            return False
    
    def get_all_user_connections(self, username: str) -> List[Dict[str, Any]]:
        """Get all social media connections for a user"""
        try:
            connections = []
            
            if DEV_MODE:
                # Get from mock storage
                user_creds = self.mock_credentials.get(username, {})
                for platform, cred_data in user_creds.items():
                    connections.append({
                        "platform": platform,
                        "username": cred_data["credentials"]["username"],
                        "user_id": cred_data["credentials"]["user_id"],
                        "profile_image": cred_data["credentials"]["profile_image"],
                        "verified": cred_data["credentials"]["verified"],
                        "connected_at": cred_data["connected_at"],
                        "last_used": cred_data["last_used"],
                        "status": cred_data["status"]
                    })
            else:
                # Get from MongoDB
                collection = mongo_db.get_collection(self.collection_name)
                credentials = collection.find({"username": username})
                
                for cred in credentials:
                    connections.append({
                        "platform": cred["platform"],
                        "username": cred["credentials"]["username"],
                        "user_id": cred["credentials"]["user_id"],
                        "profile_image": cred["credentials"]["profile_image"],
                        "verified": cred["credentials"]["verified"],
                        "connected_at": cred["connected_at"],
                        "last_used": cred["last_used"],
                        "status": cred["status"]
                    })
            
            return connections
            
        except Exception as e:
            app_logger.error(f"Error getting all connections for {username}: {e}")
            return []
    
    def is_user_connected(self, username: str, platform: str) -> bool:
        """Check if a user is connected to a specific platform"""
        credentials = self.get_user_credentials(username, platform)
        return credentials is not None
    
    def store_oauth_data(self, username: str, platform: str, oauth_data: Dict[str, Any]) -> bool:
        """Store temporary OAuth data for authentication flow"""
        try:
            oauth_session = {
                "username": username,
                "platform": platform.lower(),
                "oauth_data": oauth_data,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(minutes=10)).isoformat()
            }
            
            if DEV_MODE:
                # Store in mock storage
                if "oauth_sessions" not in self.mock_credentials:
                    self.mock_credentials["oauth_sessions"] = {}
                session_key = f"{username}_{platform}"
                self.mock_credentials["oauth_sessions"][session_key] = oauth_session
                app_logger.info(f"Stored mock OAuth data for {username} on {platform}")
                return True
            else:
                # Store in MongoDB
                collection = mongo_db.get_collection("oauth_sessions")
                
                # Remove existing sessions for this user and platform
                collection.delete_many({"username": username, "platform": platform.lower()})
                
                # Insert new session
                result = collection.insert_one(oauth_session)
                success = result.acknowledged
                
                if success:
                    app_logger.info(f"Stored OAuth data for {username} on {platform}")
                return success
                
        except Exception as e:
            app_logger.error(f"Error storing OAuth data for {username} on {platform}: {e}")
            return False
    
    def get_oauth_data(self, username: str, platform: str) -> Optional[Dict[str, Any]]:
        """Get temporary OAuth data for authentication flow"""
        try:
            if DEV_MODE:
                # Get from mock storage
                if "oauth_sessions" not in self.mock_credentials:
                    return None
                session_key = f"{username}_{platform}"
                session = self.mock_credentials["oauth_sessions"].get(session_key)
                
                if session:
                    return session["oauth_data"]
                return None
            else:
                # Get from MongoDB
                collection = mongo_db.get_collection("oauth_sessions")
                session_doc = collection.find_one({
                    "username": username, 
                    "platform": platform.lower()
                })
                
                if session_doc:
                    return session_doc["oauth_data"]
                return None
                
        except Exception as e:
            app_logger.error(f"Error retrieving OAuth data for {username} on {platform}: {e}")
            return None
    
    def clear_oauth_data(self, username: str, platform: str) -> bool:
        """Clear temporary OAuth data after authentication"""
        try:
            if DEV_MODE:
                # Remove from mock storage
                if "oauth_sessions" in self.mock_credentials:
                    session_key = f"{username}_{platform}"
                    if session_key in self.mock_credentials["oauth_sessions"]:
                        del self.mock_credentials["oauth_sessions"][session_key]
                        app_logger.info(f"Cleared OAuth data for {username} on {platform}")
                        return True
                return False
            else:
                # Remove from MongoDB
                collection = mongo_db.get_collection("oauth_sessions")
                result = collection.delete_many({
                    "username": username, 
                    "platform": platform.lower()
                })
                success = result.deleted_count > 0
                
                if success:
                    app_logger.info(f"Cleared OAuth data for {username} on {platform}")
                return success
                
        except Exception as e:
            app_logger.error(f"Error clearing OAuth data for {username} on {platform}: {e}")
            return False

# Global instance
user_social_credentials = UserSocialCredentials()

# Mock data for testing
def create_mock_user_credentials():
    """Create mock user credentials for testing"""
    if DEV_MODE:
        # Mock credentials for testing
        mock_users = {
            "admin1": {
                "twitter": {
                    "access_token": "mock_admin1_twitter_token",
                    "access_token_secret": "mock_admin1_twitter_secret",
                    "user_id": "123456789",
                    "username": "admin1_twitter",
                    "profile_image": "https://example.com/admin1_avatar.jpg",
                    "verified": True
                }
            },
            "user1": {
                "twitter": {
                    "access_token": "mock_user1_twitter_token",
                    "access_token_secret": "mock_user1_twitter_secret",
                    "user_id": "987654321",
                    "username": "user1_twitter",
                    "profile_image": "https://example.com/user1_avatar.jpg",
                    "verified": False
                }
            }
        }
        
        for username, platforms in mock_users.items():
            for platform, creds in platforms.items():
                user_social_credentials.store_user_credentials(username, platform, creds)
        
        app_logger.info("Created mock user credentials for testing")

# Initialize mock data if in DEV_MODE
if DEV_MODE:
    create_mock_user_credentials()
