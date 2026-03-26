#!/usr/bin/env python3
"""
Twitter API Integration Service
Handles Twitter/X API v2 operations with OAuth authentication
"""

import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from services.logger import app_logger
from .social_config import SocialPlatform, social_integration_manager, ConnectionStatus

class TwitterAPIError(Exception):
    """Custom exception for Twitter API errors"""
    pass

class TwitterAPIService:
    """Twitter API v2 integration service"""
    
    def __init__(self, user_credentials: Optional[Dict[str, Any]] = None):
        self.platform = SocialPlatform.TWITTER
        self.base_url = "https://api.twitter.com/2"
        self.oauth_url = "https://api.twitter.com/oauth"
        self.rate_limits = {}
        self.last_request_time = {}
        
        # Use user-specific credentials if provided, otherwise use global config
        self.user_credentials = user_credentials
        
    def _get_credentials(self) -> Dict[str, str]:
        """Get Twitter API credentials - user-specific or global"""
        if self.user_credentials:
            # Use user-specific credentials
            return {
                "access_token": self.user_credentials.get("access_token"),
                "access_token_secret": self.user_credentials.get("access_token_secret"),
                "api_key": None,  # Not needed for user-specific calls
                "api_secret": None
            }
        else:
            # Use global configuration
            config = social_integration_manager.platforms[self.platform]
            return {
                "api_key": config.api_key,
                "api_secret": config.api_secret,
                "access_token": config.access_token,
                "access_token_secret": config.access_token_secret
            }
        
    def _check_rate_limit(self, endpoint: str) -> bool:
        """Check if we're rate limited for an endpoint"""
        if endpoint in self.rate_limits:
            limit_info = self.rate_limits[endpoint]
            if limit_info["remaining"] <= 0:
                reset_time = datetime.fromisoformat(limit_info["reset_time"])
                if datetime.now() < reset_time:
                    wait_time = (reset_time - datetime.now()).total_seconds()
                    app_logger.warning(f"Twitter rate limit hit for {endpoint}, wait {wait_time:.0f}s")
                    social_integration_manager.set_connection_status(
                        self.platform, ConnectionStatus.RATE_LIMITED, 
                        f"Rate limited. Reset in {wait_time:.0f} seconds"
                    )
                    return False
        return True
    
    def _update_rate_limit(self, endpoint: str, headers: Dict[str, str]):
        """Update rate limit information from response headers"""
        if "x-rate-limit-remaining" in headers and "x-rate-limit-reset" in headers:
            reset_timestamp = int(headers["x-rate-limit-reset"])
            reset_time = datetime.fromtimestamp(reset_timestamp)
            
            self.rate_limits[endpoint] = {
                "remaining": int(headers["x-rate-limit-remaining"]),
                "reset_time": reset_time.isoformat()
            }
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to Twitter API"""
        if not social_integration_manager.is_platform_enabled(self.platform):
            raise TwitterAPIError("Twitter platform not configured or connected")
        
        if not self._check_rate_limit(endpoint):
            raise TwitterAPIError("Rate limit exceeded")
        
        credentials = self._get_credentials()
        url = f"{self.base_url}/{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Content-Type": "application/json"
        }
        
        try:
            app_logger.info(f"Twitter API request: {method} {endpoint}")
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                raise TwitterAPIError(f"Unsupported HTTP method: {method}")
            
            # Update rate limit info
            self._update_rate_limit(endpoint, response.headers)
            
            # Handle response
            if response.status_code == 200:
                social_integration_manager.set_connection_status(self.platform, ConnectionStatus.CONNECTED)
                return response.json()
            elif response.status_code == 429:
                social_integration_manager.set_connection_status(self.platform, ConnectionStatus.RATE_LIMITED)
                raise TwitterAPIError("Rate limit exceeded")
            elif response.status_code == 401:
                social_integration_manager.set_connection_status(self.platform, ConnectionStatus.ERROR, "Authentication failed")
                raise TwitterAPIError("Authentication failed - check credentials")
            else:
                error_msg = f"Twitter API error: {response.status_code}"
                try:
                    error_detail = response.json()
                    if "detail" in error_detail:
                        error_msg += f" - {error_detail['detail']}"
                except:
                    pass
                social_integration_manager.set_connection_status(self.platform, ConnectionStatus.ERROR, error_msg)
                raise TwitterAPIError(error_msg)
                
        except requests.exceptions.RequestException as e:
            social_integration_manager.set_connection_status(self.platform, ConnectionStatus.ERROR, f"Network error: {str(e)}")
            raise TwitterAPIError(f"Network error: {str(e)}")
    
    def test_connection(self) -> bool:
        """Test Twitter API connection"""
        try:
            # Test with a simple user lookup
            response = self._make_request("GET", "users/me", params={"user.fields": "id,name,username"})
            return "data" in response
        except TwitterAPIError as e:
            app_logger.error(f"Twitter connection test failed: {e}")
            return False
    
    def get_user_info(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current user information or specific user info"""
        try:
            if user_id:
                endpoint = f"users/{user_id}"
            else:
                endpoint = "users/me"
            
            params = {
                "user.fields": "id,name,username,description,public_metrics,verified,created_at,profile_image_url"
            }
            
            response = self._make_request("GET", endpoint, params=params)
            return response.get("data", {})
            
        except TwitterAPIError as e:
            app_logger.error(f"Failed to get user info: {e}")
            return {}
    
    def get_user_tweets(self, user_id: Optional[str] = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get tweets from a user"""
        try:
            if not user_id:
                # Get current user ID first
                user_info = self.get_user_info()
                user_id = user_info.get("id")
                if not user_id:
                    raise TwitterAPIError("Could not determine user ID")
            
            params = {
                "max_results": min(max_results, 100),  # Twitter API limit
                "tweet.fields": "id,text,created_at,public_metrics,context_annotations,lang"
            }
            
            response = self._make_request("GET", f"users/{user_id}/tweets", params=params)
            return response.get("data", [])
            
        except TwitterAPIError as e:
            app_logger.error(f"Failed to get user tweets: {e}")
            return []
    
    def post_tweet(self, text: str, media_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Post a tweet"""
        try:
            if len(text) > 280:
                raise TwitterAPIError("Tweet text exceeds 280 characters")
            
            data = {"text": text}
            if media_ids:
                data["media"] = {"media_ids": media_ids}
            
            response = self._make_request("POST", "tweets", data=data)
            return response.get("data", {})
            
        except TwitterAPIError as e:
            app_logger.error(f"Failed to post tweet: {e}")
            return {}
    
    def delete_tweet(self, tweet_id: str) -> bool:
        """Delete a tweet"""
        try:
            response = self._make_request("DELETE", f"tweets/{tweet_id}")
            return response.get("data", {}).get("deleted", False)
            
        except TwitterAPIError as e:
            app_logger.error(f"Failed to delete tweet {tweet_id}: {e}")
            return False
    
    def get_tweet_metrics(self, tweet_id: str) -> Dict[str, Any]:
        """Get detailed metrics for a tweet"""
        try:
            params = {
                "tweet.fields": "public_metrics,non_public_metrics,organic_metrics"
            }
            
            response = self._make_request("GET", f"tweets/{tweet_id}", params=params)
            tweet_data = response.get("data", {})
            return tweet_data.get("public_metrics", {})
            
        except TwitterAPIError as e:
            app_logger.error(f"Failed to get tweet metrics: {e}")
            return {}
    
    def search_tweets(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for tweets"""
        try:
            params = {
                "query": query,
                "max_results": min(max_results, 100),
                "tweet.fields": "id,text,created_at,public_metrics,author_id,lang"
            }
            
            response = self._make_request("GET", "tweets/search/recent", params=params)
            return response.get("data", [])
            
        except TwitterAPIError as e:
            app_logger.error(f"Failed to search tweets: {e}")
            return []
    
    def get_followers_count(self, user_id: Optional[str] = None) -> int:
        """Get follower count for a user"""
        try:
            user_info = self.get_user_info(user_id)
            public_metrics = user_info.get("public_metrics", {})
            return public_metrics.get("followers_count", 0)
            
        except TwitterAPIError as e:
            app_logger.error(f"Failed to get followers count: {e}")
            return 0
    
    def get_engagement_data(self, tweet_id: str) -> Dict[str, Any]:
        """Get engagement data for a tweet (likes, retweets, replies)"""
        try:
            metrics = self.get_tweet_metrics(tweet_id)
            return {
                "likes": metrics.get("like_count", 0),
                "retweets": metrics.get("retweet_count", 0),
                "replies": metrics.get("reply_count", 0),
                "quotes": metrics.get("quote_count", 0),
                "impressions": metrics.get("impression_count", 0)
            }
            
        except TwitterAPIError as e:
            app_logger.error(f"Failed to get engagement data: {e}")
            return {}

# Global Twitter service instance
twitter_service = TwitterAPIService()

# Mock data fallback
class TwitterMockService:
    """Mock Twitter service for when real API is not available"""
    
    def __init__(self):
        self.mock_user = {
            "id": "123456789",
            "name": "Social Connect Demo",
            "username": "socialconnect_demo",
            "description": "Demo account for Social Connect platform",
            "verified": False,
            "public_metrics": {
                "followers_count": 1250,
                "following_count": 450,
                "tweet_count": 180,
                "listed_count": 12
            }
        }
        
        self.mock_tweets = [
            {
                "id": "1111111111111111111",
                "text": "Just launched our new social media management platform! 🚀 #SocialConnect #Marketing",
                "created_at": "2024-01-15T10:30:00.000Z",
                "public_metrics": {
                    "like_count": 45,
                    "retweet_count": 12,
                    "reply_count": 8,
                    "quote_count": 3
                }
            },
            {
                "id": "2222222222222222222",
                "text": "Pro tip: Consistent posting schedule is key to social media success! 💡",
                "created_at": "2024-01-14T15:45:00.000Z",
                "public_metrics": {
                    "like_count": 28,
                    "retweet_count": 7,
                    "reply_count": 5,
                    "quote_count": 1
                }
            }
        ]
    
    def test_connection(self) -> bool:
        return True  # Mock always works
    
    def get_user_info(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        return self.mock_user
    
    def get_user_tweets(self, user_id: Optional[str] = None, max_results: int = 10) -> List[Dict[str, Any]]:
        return self.mock_tweets[:max_results]
    
    def get_followers_count(self, user_id: Optional[str] = None) -> int:
        return self.mock_user["public_metrics"]["followers_count"]
    
    def get_engagement_data(self, tweet_id: str) -> Dict[str, Any]:
        for tweet in self.mock_tweets:
            if tweet["id"] == tweet_id:
                return {
                    "likes": tweet["public_metrics"]["like_count"],
                    "retweets": tweet["public_metrics"]["retweet_count"],
                    "replies": tweet["public_metrics"]["reply_count"],
                    "quotes": tweet["public_metrics"]["quote_count"],
                    "impressions": tweet["public_metrics"].get("impression_count", 500)
                }
        return {}

def get_twitter_service(username: Optional[str] = None) -> TwitterAPIService:
    """Get Twitter service (real or mock based on configuration)"""
    if social_integration_manager.is_platform_enabled(SocialPlatform.TWITTER) and username:
        # Try to get user-specific credentials
        from .user_credentials import user_social_credentials
        user_creds = user_social_credentials.get_user_credentials(username, "twitter")
        if user_creds:
            return TwitterAPIService(user_creds)
        else:
            # Fall back to global config
            return TwitterAPIService()
    elif social_integration_manager.is_platform_enabled(SocialPlatform.TWITTER):
        return TwitterAPIService()
    else:
        return TwitterMockService()
