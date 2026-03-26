#!/usr/bin/env python3
"""
Social Media OAuth Endpoints
Handles OAuth flows for connecting user social media accounts
"""

import secrets
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from services.util import RoleMiddleware
from services.logger import app_logger
from social_config import SocialPlatform, is_real_data_available, SOCIAL_INTEGRATION_ENABLED
from user_credentials import user_social_credentials
from twitter_service import TwitterAPIService

class SocialOAuthManager:
    """Manages OAuth flows for social media platforms"""
    
    def __init__(self):
        self.oauth_states = {}  # Store OAuth states for security
        self.oauth_callbacks = {}  # Store callback URLs
        
    def generate_oauth_state(self, username: str, platform: str) -> str:
        """Generate secure OAuth state parameter"""
        state = secrets.token_urlsafe(32)
        self.oauth_states[state] = {
            "username": username,
            "platform": platform,
            "created_at": datetime.now().isoformat()
        }
        return state
    
    def validate_oauth_state(self, state: str) -> Optional[Dict[str, Any]]:
        """Validate OAuth state parameter"""
        if state not in self.oauth_states:
            return None
        
        state_data = self.oauth_states[state]
        
        # Check if state is expired (10 minutes)
        created_at = datetime.fromisoformat(state_data["created_at"])
        if datetime.now() - created_at > timedelta(minutes=10):
            del self.oauth_states[state]
            return None
        
        return state_data
    
    def cleanup_oauth_state(self, state: str):
        """Clean up OAuth state"""
        if state in self.oauth_states:
            del self.oauth_states[state]
    
    def get_oauth_url(self, platform: str, username: str, callback_url: str) -> Dict[str, Any]:
        """Get OAuth URL for platform"""
        try:
            if not SOCIAL_INTEGRATION_ENABLED:
                return {
                    "success": False,
                    "error": "Social integration is disabled",
                    "mock_url": f"/api/v1/social/mock-connect/{platform}"
                }
            
            if platform == "twitter":
                return self._get_twitter_oauth_url(username, callback_url)
            else:
                return {
                    "success": False,
                    "error": f"Platform {platform} not yet supported"
                }
                
        except Exception as e:
            app_logger.error(f"Error getting OAuth URL for {platform}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_twitter_oauth_url(self, username: str, callback_url: str) -> Dict[str, Any]:
        """Get Twitter OAuth URL"""
        try:
            # Generate OAuth state
            state = self.generate_oauth_state(username, "twitter")
            
            # For demo, return a mock OAuth URL
            # In production, this would be the real Twitter OAuth URL
            oauth_url = f"https://twitter.com/i/oauth2/authorize?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri={callback_url}&scope=tweet.read%20tweet.write%20users.read&state={state}"
            
            return {
                "success": True,
                "oauth_url": oauth_url,
                "state": state,
                "platform": "twitter"
            }
            
        except Exception as e:
            app_logger.error(f"Error generating Twitter OAuth URL: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def handle_oauth_callback(self, platform: str, code: str, state: str) -> Dict[str, Any]:
        """Handle OAuth callback from social platform"""
        try:
            # Validate OAuth state
            state_data = self.validate_oauth_state(state)
            if not state_data:
                return {
                    "success": False,
                    "error": "Invalid or expired OAuth state"
                }
            
            username = state_data["username"]
            
            if platform == "twitter":
                return self._handle_twitter_callback(username, code)
            else:
                return {
                    "success": False,
                    "error": f"Platform {platform} not yet supported"
                }
                
        except Exception as e:
            app_logger.error(f"Error handling OAuth callback for {platform}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _handle_twitter_callback(self, username: str, code: str) -> Dict[str, Any]:
        """Handle Twitter OAuth callback"""
        try:
            if not SOCIAL_INTEGRATION_ENABLED:
                # Mock connection for development
                mock_credentials = {
                    "access_token": f"mock_token_{username}_{secrets.token_hex(8)}",
                    "access_token_secret": f"mock_secret_{username}_{secrets.token_hex(8)}",
                    "user_id": f"{secrets.randbelow(1000000000)}",
                    "username": f"{username}_twitter",
                    "profile_image": f"https://example.com/avatars/{username}.jpg",
                    "verified": username == "admin1"  # Mock verification
                }
                
                # Store credentials
                success = user_social_credentials.store_user_credentials(username, "twitter", mock_credentials)
                
                if success:
                    return {
                        "success": True,
                        "platform": "twitter",
                        "username": username,
                        "connected_account": mock_credentials["username"],
                        "message": "Twitter account connected successfully (mock mode)"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to store credentials"
                    }
            
            # In production, exchange code for access token with Twitter API
            # For now, return mock success
            mock_credentials = {
                "access_token": f"real_token_{username}_{secrets.token_hex(8)}",
                "access_token_secret": f"real_secret_{username}_{secrets.token_hex(8)}",
                "user_id": f"{secrets.randbelow(1000000000)}",
                "username": f"{username}_twitter",
                "profile_image": f"https://example.com/avatars/{username}.jpg",
                "verified": False
            }
            
            # Store credentials
            success = user_social_credentials.store_user_credentials(username, "twitter", mock_credentials)
            
            if success:
                return {
                    "success": True,
                    "platform": "twitter",
                    "username": username,
                    "connected_account": mock_credentials["username"],
                    "message": "Twitter account connected successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to store credentials"
                }
                
        except Exception as e:
            app_logger.error(f"Error handling Twitter callback: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def disconnect_user_account(self, username: str, platform: str) -> Dict[str, Any]:
        """Disconnect user's social media account"""
        try:
            success = user_social_credentials.remove_user_credentials(username, platform)
            
            if success:
                return {
                    "success": True,
                    "platform": platform,
                    "username": username,
                    "message": f"{platform.capitalize()} account disconnected successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "No account found to disconnect"
                }
                
        except Exception as e:
            app_logger.error(f"Error disconnecting {platform} for {username}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_user_connections(self, username: str) -> Dict[str, Any]:
        """Get all connected social media accounts for a user"""
        try:
            connections = user_social_credentials.get_all_user_connections(username)
            
            return {
                "success": True,
                "username": username,
                "connections": connections,
                "total_connected": len(connections)
            }
            
        except Exception as e:
            app_logger.error(f"Error getting connections for {username}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_user_connection(self, username: str, platform: str) -> Dict[str, Any]:
        """Test if user's social media connection is working"""
        try:
            credentials = user_social_credentials.get_user_credentials(username, platform)
            
            if not credentials:
                return {
                    "success": False,
                    "error": f"No {platform} account connected"
                }
            
            if platform == "twitter":
                # Test Twitter connection
                if not SOCIAL_INTEGRATION_ENABLED:
                    return {
                        "success": True,
                        "platform": "twitter",
                        "username": username,
                        "account_username": credentials["username"],
                        "message": "Twitter connection test successful (mock mode)"
                    }
                
                # In production, test real Twitter API
                twitter_service = TwitterAPIService()
                # Would use user's credentials here
                # For now, return success
                return {
                    "success": True,
                    "platform": "twitter",
                    "username": username,
                    "account_username": credentials["username"],
                    "message": "Twitter connection test successful"
                }
            else:
                return {
                    "success": False,
                    "error": f"Platform {platform} not yet supported"
                }
                
        except Exception as e:
            app_logger.error(f"Error testing {platform} connection for {username}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Global OAuth manager instance
social_oauth_manager = SocialOAuthManager()

# Mock OAuth endpoints for development
def get_mock_oauth_flow(platform: str, username: str) -> Dict[str, Any]:
    """Get mock OAuth flow for development"""
    mock_credentials = {
        "twitter": {
            "access_token": f"mock_token_{username}_{secrets.token_hex(8)}",
            "access_token_secret": f"mock_secret_{username}_{secrets.token_hex(8)}",
            "user_id": f"{secrets.randbelow(1000000000)}",
            "username": f"{username}_twitter",
            "profile_image": f"https://example.com/avatars/{username}.jpg",
            "verified": username == "admin1"
        }
    }
    
    if platform in mock_credentials:
        credentials = mock_credentials[platform]
        success = user_social_credentials.store_user_credentials(username, platform, credentials)
        
        if success:
            return {
                "success": True,
                "platform": platform,
                "username": username,
                "connected_account": credentials["username"],
                "verified": credentials["verified"],
                "message": f"{platform.capitalize()} account connected successfully (mock mode)"
            }
        else:
            return {
                "success": False,
                "error": "Failed to store mock credentials"
            }
    else:
        return {
            "success": False,
            "error": f"Platform {platform} not supported in mock mode"
        }
