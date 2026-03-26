#!/usr/bin/env python3
"""
Real Twitter OAuth 2.0 Implementation
Handles actual Twitter API v2 authentication with PKCE flow
"""

import base64
import hashlib
import secrets
import json
import requests
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlencode
from datetime import datetime, timedelta
from services.logger import app_logger
from social_config import SocialPlatform, social_integration_manager
from user_credentials import user_social_credentials

class TwitterOAuth2:
    """Real Twitter OAuth 2.0 implementation with PKCE"""
    
    def __init__(self):
        self.platform = SocialPlatform.TWITTER
        self.auth_url = "https://twitter.com/i/oauth2/authorize"
        self.token_url = "https://api.twitter.com/2/oauth2/token"
        self.revoke_url = "https://api.twitter.com/2/oauth2/revoke"
        self.user_info_url = "https://api.twitter.com/2/users/me"
        
        # OAuth 2.0 with PKCE
        self.code_verifier_length = 128
        self.state_length = 32
        
    def _get_client_credentials(self) -> Dict[str, str]:
        """Get Twitter client credentials from configuration"""
        config = social_integration_manager.platforms[self.platform]
        return {
            "client_id": config.api_key,
            "client_secret": config.api_secret,
            "redirect_uri": config.redirect_uri or "http://localhost:3001/social/twitter/callback"
        }
    
    def generate_pkce_challenge(self) -> Tuple[str, str]:
        """Generate PKCE code verifier and challenge"""
        code_verifier = base64.urlsafe_b64encode(
            secrets.token_bytes(self.code_verifier_length)
        ).decode('utf-8').rstrip('=')
        
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        return code_verifier, code_challenge
    
    def generate_state(self) -> str:
        """Generate secure OAuth state parameter"""
        return secrets.token_urlsafe(self.state_length)
    
    def get_authorization_url(self, username: str, callback_url: Optional[str] = None) -> Dict[str, Any]:
        """Generate Twitter OAuth 2.0 authorization URL"""
        try:
            if not social_integration_manager.is_platform_enabled(self.platform):
                return {
                    "success": False,
                    "error": "Twitter platform not enabled",
                    "error_code": "PLATFORM_DISABLED"
                }
            
            credentials = self._get_client_credentials()
            code_verifier, code_challenge = self.generate_pkce_challenge()
            state = self.generate_state()
            
            # Store PKCE data for callback validation
            oauth_data = {
                "username": username,
                "code_verifier": code_verifier,
                "state": state,
                "created_at": datetime.now().isoformat()
            }
            
            # Store in user credentials temporarily
            user_social_credentials.store_oauth_data(username, "twitter", oauth_data)
            
            # Build authorization URL parameters
            params = {
                "response_type": "code",
                "client_id": credentials["client_id"],
                "redirect_uri": callback_url or credentials["redirect_uri"],
                "scope": "tweet.read tweet.write users.read offline.access",
                "state": state,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256"
            }
            
            auth_url = f"{self.auth_url}?{urlencode(params)}"
            
            return {
                "success": True,
                "authorization_url": auth_url,
                "state": state,
                "code_challenge": code_challenge,
                "scope": params["scope"],
                "expires_in": 600,  # 10 minutes
                "message": "Twitter authorization URL generated successfully"
            }
            
        except Exception as e:
            app_logger.error(f"Error generating Twitter authorization URL: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "AUTH_URL_GENERATION_FAILED"
            }
    
    def exchange_code_for_token(self, username: str, code: str, state: str, callback_url: Optional[str] = None) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            # Retrieve stored OAuth data
            oauth_data = user_social_credentials.get_oauth_data(username, "twitter")
            
            if not oauth_data:
                return {
                    "success": False,
                    "error": "OAuth session not found or expired",
                    "error_code": "SESSION_NOT_FOUND"
                }
            
            # Validate state
            if oauth_data["state"] != state:
                return {
                    "success": False,
                    "error": "Invalid state parameter",
                    "error_code": "INVALID_STATE"
                }
            
            # Check if session expired (10 minutes)
            created_at = datetime.fromisoformat(oauth_data["created_at"])
            if datetime.now() - created_at > timedelta(minutes=10):
                user_social_credentials.clear_oauth_data(username, "twitter")
                return {
                    "success": False,
                    "error": "OAuth session expired",
                    "error_code": "SESSION_EXPIRED"
                }
            
            credentials = self._get_client_credentials()
            code_verifier = oauth_data["code_verifier"]
            
            # Exchange code for token
            token_data = {
                "grant_type": "authorization_code",
                "client_id": credentials["client_id"],
                "code": code,
                "redirect_uri": callback_url or credentials["redirect_uri"],
                "code_verifier": code_verifier
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # Make token request
            response = requests.post(
                self.token_url,
                data=token_data,
                headers=headers,
                auth=(credentials["client_id"], credentials["client_secret"])
            )
            
            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                return {
                    "success": False,
                    "error": error_data.get("error_description", "Token exchange failed"),
                    "error_code": "TOKEN_EXCHANGE_FAILED",
                    "status_code": response.status_code
                }
            
            token_response = response.json()
            
            # Get user information
            user_info = self.get_user_info(token_response["access_token"])
            
            if not user_info["success"]:
                return {
                    "success": False,
                    "error": "Failed to retrieve user information",
                    "error_code": "USER_INFO_FAILED"
                }
            
            # Store user credentials
            user_credentials = {
                "access_token": token_response["access_token"],
                "refresh_token": token_response.get("refresh_token"),
                "token_type": token_response["token_type"],
                "expires_in": token_response.get("expires_in"),
                "scope": token_response.get("scope"),
                "user_id": user_info["data"]["id"],
                "username": user_info["data"]["username"],
                "name": user_info["data"]["name"],
                "profile_image": user_info["data"].get("profile_image_url", ""),
                "verified": user_info["data"].get("verified", False),
                "public_metrics": user_info["data"].get("public_metrics", {}),
                "connected_at": datetime.now().isoformat()
            }
            
            # Store credentials
            success = user_social_credentials.store_user_credentials(username, "twitter", user_credentials)
            
            # Clean up OAuth data
            user_social_credentials.clear_oauth_data(username, "twitter")
            
            if success:
                return {
                    "success": True,
                    "data": {
                        "platform": "twitter",
                        "username": username,
                        "connected_account": user_info["data"]["username"],
                        "user_id": user_info["data"]["id"],
                        "name": user_info["data"]["name"],
                        "verified": user_info["data"].get("verified", False),
                        "profile_image": user_info["data"].get("profile_image_url", ""),
                        "followers": user_info["data"].get("public_metrics", {}).get("followers_count", 0),
                        "token_type": token_response["token_type"],
                        "expires_in": token_response.get("expires_in"),
                        "scope": token_response.get("scope")
                    },
                    "message": "Twitter account connected successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to store user credentials",
                    "error_code": "STORAGE_FAILED"
                }
                
        except Exception as e:
            app_logger.error(f"Error exchanging Twitter code for token: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "EXCEPTION_OCCURRED"
            }
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Twitter API v2"""
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            params = {
                "user.fields": "created_at,description,location,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,verified_type"
            }
            
            response = requests.get(
                f"{self.user_info_url}?{urlencode(params)}",
                headers=headers
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to get user info: {response.status_code}",
                    "status_code": response.status_code
                }
            
            user_data = response.json()
            
            return {
                "success": True,
                "data": user_data.get("data", {}),
                "includes": user_data.get("includes", {})
            }
            
        except Exception as e:
            app_logger.error(f"Error getting Twitter user info: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def refresh_access_token(self, username: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        try:
            credentials = user_social_credentials.get_user_credentials(username, "twitter")
            
            if not credentials or not credentials.get("refresh_token"):
                return {
                    "success": False,
                    "error": "No refresh token available",
                    "error_code": "NO_REFRESH_TOKEN"
                }
            
            client_creds = self._get_client_credentials()
            
            refresh_data = {
                "grant_type": "refresh_token",
                "refresh_token": credentials["refresh_token"],
                "client_id": client_creds["client_id"]
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            response = requests.post(
                self.token_url,
                data=refresh_data,
                headers=headers,
                auth=(client_creds["client_id"], client_creds["client_secret"])
            )
            
            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                return {
                    "success": False,
                    "error": error_data.get("error_description", "Token refresh failed"),
                    "error_code": "REFRESH_FAILED",
                    "status_code": response.status_code
                }
            
            token_response = response.json()
            
            # Update stored credentials
            updated_credentials = credentials.copy()
            updated_credentials.update({
                "access_token": token_response["access_token"],
                "refresh_token": token_response.get("refresh_token", credentials["refresh_token"]),
                "token_type": token_response["token_type"],
                "expires_in": token_response.get("expires_in"),
                "scope": token_response.get("scope"),
                "last_refreshed": datetime.now().isoformat()
            })
            
            success = user_social_credentials.store_user_credentials(username, "twitter", updated_credentials)
            
            return {
                "success": success,
                "data": {
                    "access_token": token_response["access_token"],
                    "token_type": token_response["token_type"],
                    "expires_in": token_response.get("expires_in"),
                    "scope": token_response.get("scope")
                },
                "message": "Access token refreshed successfully" if success else "Failed to store refreshed token"
            }
            
        except Exception as e:
            app_logger.error(f"Error refreshing Twitter access token: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "EXCEPTION_OCCURRED"
            }
    
    def revoke_access_token(self, username: str) -> Dict[str, Any]:
        """Revoke access token"""
        try:
            credentials = user_social_credentials.get_user_credentials(username, "twitter")
            
            if not credentials:
                return {
                    "success": False,
                    "error": "No credentials found to revoke",
                    "error_code": "NO_CREDENTIALS"
                }
            
            client_creds = self._get_client_credentials()
            
            revoke_data = {
                "token": credentials["access_token"],
                "client_id": client_creds["client_id"]
            }
            
            response = requests.post(
                self.revoke_url,
                data=revoke_data,
                auth=(client_creds["client_id"], client_creds["client_secret"])
            )
            
            # Remove stored credentials regardless of revoke response
            user_social_credentials.remove_user_credentials(username, "twitter")
            
            if response.status_code in [200, 204]:
                return {
                    "success": True,
                    "message": "Twitter access token revoked successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to revoke token with Twitter",
                    "error_code": "REVOKE_FAILED",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            app_logger.error(f"Error revoking Twitter access token: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "EXCEPTION_OCCURRED"
            }

# Global OAuth instance
twitter_oauth = TwitterOAuth2()
