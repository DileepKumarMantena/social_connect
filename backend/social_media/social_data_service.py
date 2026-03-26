#!/usr/bin/env python3
"""
Unified Social Media Service Layer
Provides a unified interface for social media operations with automatic fallback
between real API integrations and mock data
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from services.logger import app_logger
from .social_config import (
    SocialPlatform, social_integration_manager, is_real_data_available,
    SOCIAL_INTEGRATION_ENABLED, get_platform_features
)
from .twitter_service import get_twitter_service
from .connection_manager import connection_manager

class SocialDataService:
    """Unified service for social media data with automatic fallback"""
    
    def __init__(self):
        self.mock_data_enabled = True
        self.real_data_enabled = is_real_data_available()
        
    def _should_use_real_data(self, platform: SocialPlatform) -> bool:
        """Determine if real data should be used for a platform"""
        if not SOCIAL_INTEGRATION_ENABLED:
            return False
        
        if not self.real_data_enabled:
            return False
            
        return social_integration_manager.is_platform_enabled(platform)
    
    def _get_fallback_data(self, data_type: str, platform: Optional[SocialPlatform] = None) -> Any:
        """Get mock/fallback data when real data is not available"""
        if data_type == "channels":
            return self._get_mock_channels()
        elif data_type == "campaigns":
            return self._get_mock_campaigns()
        elif data_type == "leads":
            return self._get_mock_leads()
        elif data_type == "analytics":
            return self._get_mock_analytics()
        elif data_type == "user_info":
            return self._get_mock_user_info(platform)
        elif data_type == "posts":
            return self._get_mock_posts(platform)
        else:
            return []
    
    def _get_mock_channels(self) -> List[Dict[str, Any]]:
        """Get mock social media channels"""
        return [
            {
                "id": 1,
                "name": "Twitter/X",
                "platform": "twitter",
                "connected": False,
                "active": False,
                "followers": 0,
                "username": "",
                "profile_image": "",
                "created_by": "superadmin",
                "created_at": datetime.now().isoformat(),
                "last_sync": None,
                "status": "disconnected"
            },
            {
                "id": 2,
                "name": "LinkedIn",
                "platform": "linkedin",
                "connected": False,
                "active": False,
                "followers": 0,
                "username": "",
                "profile_image": "",
                "created_by": "superadmin",
                "created_at": datetime.now().isoformat(),
                "last_sync": None,
                "status": "disconnected"
            },
            {
                "id": 3,
                "name": "Facebook",
                "platform": "facebook",
                "connected": False,
                "active": False,
                "followers": 0,
                "username": "",
                "profile_image": "",
                "created_by": "superadmin",
                "created_at": datetime.now().isoformat(),
                "last_sync": None,
                "status": "disconnected"
            }
        ]
    
    def _get_mock_campaigns(self) -> List[Dict[str, Any]]:
        """Get mock campaigns"""
        return [
            {
                "id": 1,
                "name": "Q1 Product Launch",
                "platform": "twitter",
                "status": "active",
                "target_audience": "Tech enthusiasts",
                "content": "Excited to announce our new product launch! 🚀",
                "scheduled_time": datetime.now().isoformat(),
                "created_by": "admin1",
                "created_at": datetime.now().isoformat(),
                "metrics": {
                    "impressions": 1500,
                    "engagements": 125,
                    "clicks": 45,
                    "leads": 8
                }
            },
            {
                "id": 2,
                "name": "Weekly Tips Series",
                "platform": "linkedin",
                "status": "scheduled",
                "target_audience": "Business professionals",
                "content": "Professional development tips for career growth",
                "scheduled_time": (datetime.now() + timedelta(days=1)).isoformat(),
                "created_by": "admin1",
                "created_at": datetime.now().isoformat(),
                "metrics": {
                    "impressions": 800,
                    "engagements": 65,
                    "clicks": 20,
                    "leads": 3
                }
            }
        ]
    
    def _get_mock_leads(self) -> List[Dict[str, Any]]:
        """Get mock leads"""
        return [
            {
                "id": 1,
                "name": "John Smith",
                "email": "john.smith@example.com",
                "phone": "+1-555-0123",
                "source": "twitter",
                "campaign_id": 1,
                "campaign_name": "Q1 Product Launch",
                "status": "new",
                "created_at": datetime.now().isoformat(),
                "notes": "Interested in product demo"
            },
            {
                "id": 2,
                "name": "Sarah Johnson",
                "email": "sarah.j@example.com",
                "phone": "+1-555-0124",
                "source": "linkedin",
                "campaign_id": 2,
                "campaign_name": "Weekly Tips Series",
                "status": "contacted",
                "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                "notes": "Requested more information"
            }
        ]
    
    def _get_mock_analytics(self) -> List[Dict[str, Any]]:
        """Get mock analytics data"""
        return [
            {
                "id": 1,
                "platform": "twitter",
                "metric_type": "engagement",
                "value": 125,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "campaign_id": 1,
                "created_at": datetime.now().isoformat()
            },
            {
                "id": 2,
                "platform": "linkedin",
                "metric_type": "impressions",
                "value": 800,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "campaign_id": 2,
                "created_at": datetime.now().isoformat()
            }
        ]
    
    def _get_mock_user_info(self, platform: Optional[SocialPlatform] = None) -> Dict[str, Any]:
        """Get mock user information"""
        return {
            "id": "mock_user_id",
            "name": "Mock User",
            "username": "mock_user",
            "description": "Mock user for demonstration",
            "followers_count": 1000,
            "following_count": 500,
            "verified": False,
            "profile_image_url": ""
        }
    
    def _get_mock_posts(self, platform: Optional[SocialPlatform] = None) -> List[Dict[str, Any]]:
        """Get mock posts/tweets"""
        return [
            {
                "id": "mock_post_1",
                "text": "This is a mock post for demonstration purposes",
                "created_at": datetime.now().isoformat(),
                "platform": platform.value if platform else "mock",
                "metrics": {
                    "likes": 25,
                    "retweets": 5,
                    "replies": 3,
                    "impressions": 500
                }
            }
        ]
    
    def get_channels(self, created_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get social media channels with real data fallback - supports multi-user"""
        channels = []
        
        # Get real channels from connected platforms
        if self.real_data_enabled and created_by:
            # Get user-specific connected platforms
            from .user_credentials import user_social_credentials
            user_platforms = user_social_credentials.get_user_connected_platforms(created_by)
            
            for platform_name in user_platforms:
                try:
                    platform = SocialPlatform(platform_name)
                    platform_channels = self._get_user_platform_channels(platform, created_by)
                    channels.extend(platform_channels)
                except Exception as e:
                    app_logger.error(f"Failed to get channels from {platform_name} for user {created_by}: {e}")
        elif self.real_data_enabled:
            # Get all channels from connected platforms (for super admin)
            for platform in social_integration_manager.get_enabled_platforms():
                try:
                    platform_channels = self._get_platform_channels(platform)
                    channels.extend(platform_channels)
                except Exception as e:
                    app_logger.error(f"Failed to get channels from {platform.value}: {e}")
        
        # Add mock channels if no real data or for non-connected platforms
        if not channels or self.mock_data_enabled:
            mock_channels = self._get_fallback_data("channels")
            for channel in mock_channels:
                # Update mock channel status based on real connections
                if created_by:
                    from .user_credentials import user_social_credentials
                    user_platforms = user_social_credentials.get_user_connected_platforms(created_by)
                    if channel["platform"] in user_platforms:
                        channel["connected"] = True
                        channel["active"] = True
                        # Get real user info for connected platforms
                        try:
                            platform = SocialPlatform(channel["platform"])
                            user_info = self._get_user_platform_info(platform, created_by)
                            channel.update({
                                "username": user_info.get("username", ""),
                                "followers": user_info.get("followers_count", 0),
                                "profile_image": user_info.get("profile_image_url", ""),
                                "status": "connected",
                                "created_by": created_by
                            })
                        except:
                            pass
                
                # Filter by created_by if specified
                if created_by is None or channel.get("created_by") == created_by:
                    channels.append(channel)
        
        return channels
    
    def _get_platform_channels(self, platform: SocialPlatform) -> List[Dict[str, Any]]:
        """Get channels from a specific platform"""
        if platform == SocialPlatform.TWITTER:
            twitter_service = get_twitter_service()
            user_info = twitter_service.get_user_info()
            
            return [{
                "id": f"twitter_{user_info.get('id')}",
                "name": f"Twitter/X - @{user_info.get('username')}",
                "platform": "twitter",
                "connected": True,
                "active": True,
                "followers": user_info.get("public_metrics", {}).get("followers_count", 0),
                "username": user_info.get("username", ""),
                "profile_image": user_info.get("profile_image_url", ""),
                "created_by": "system",
                "created_at": datetime.now().isoformat(),
                "last_sync": datetime.now().isoformat(),
                "status": "connected"
            }]
        
        return []
    
    def _get_user_platform_channels(self, platform: SocialPlatform, username: str) -> List[Dict[str, Any]]:
        """Get channels from a specific platform for a specific user"""
        if platform == SocialPlatform.TWITTER:
            twitter_service = get_twitter_service(username)
            user_info = twitter_service.get_user_info()
            
            return [{
                "id": f"twitter_{user_info.get('id')}_{username}",
                "name": f"Twitter/X - @{user_info.get('username')}",
                "platform": "twitter",
                "connected": True,
                "active": True,
                "followers": user_info.get("public_metrics", {}).get("followers_count", 0),
                "username": user_info.get("username", ""),
                "profile_image": user_info.get("profile_image_url", ""),
                "created_by": username,
                "created_at": datetime.now().isoformat(),
                "last_sync": datetime.now().isoformat(),
                "status": "connected"
            }]
        
        return []
    
    def get_campaigns(self, created_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get campaigns with real data when available"""
        campaigns = []
        
        # Try to get real campaigns from connected platforms
        if self.real_data_enabled:
            # For now, we'll use mock campaigns as real campaigns would need to be
            # stored in our database and tracked per platform
            pass
        
        # Fallback to mock data
        mock_campaigns = self._get_fallback_data("campaigns")
        for campaign in mock_campaigns:
            if created_by is None or campaign["created_by"] == created_by:
                campaigns.append(campaign)
        
        return campaigns
    
    def get_leads(self, created_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get leads with real data when available"""
        leads = []
        
        # Try to get real leads from connected platforms
        if self.real_data_enabled:
            # Real leads would come from platform-specific lead generation
            # For now, we'll use mock data
            pass
        
        # Fallback to mock data
        mock_leads = self._get_fallback_data("leads")
        for lead in mock_leads:
            if created_by is None or lead["created_by"] == created_by:
                leads.append(lead)
        
        return leads
    
    def get_analytics(self, created_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get analytics with real data when available"""
        analytics = []
        
        # Try to get real analytics from connected platforms
        if self.real_data_enabled:
            for platform in social_integration_manager.get_enabled_platforms():
                try:
                    platform_analytics = self._get_platform_analytics(platform)
                    analytics.extend(platform_analytics)
                except Exception as e:
                    app_logger.error(f"Failed to get analytics from {platform.value}: {e}")
        
        # Fallback to mock data
        if not analytics:
            mock_analytics = self._get_fallback_data("analytics")
            for analytic in mock_analytics:
                if created_by is None or analytic.get("created_by") == created_by:
                    analytics.append(analytic)
        
        return analytics
    
    def _get_platform_analytics(self, platform: SocialPlatform) -> List[Dict[str, Any]]:
        """Get analytics from a specific platform"""
        if platform == SocialPlatform.TWITTER:
            twitter_service = get_twitter_service()
            try:
                # Get recent tweets and their metrics
                tweets = twitter_service.get_user_tweets(max_results=10)
                analytics = []
                
                for tweet in tweets:
                    metrics = twitter_service.get_engagement_data(tweet["id"])
                    analytics.append({
                        "id": f"twitter_analytics_{tweet['id']}",
                        "platform": "twitter",
                        "metric_type": "engagement",
                        "value": metrics.get("likes", 0) + metrics.get("retweets", 0) + metrics.get("replies", 0),
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "campaign_id": None,  # Would need to map tweets to campaigns
                        "created_at": datetime.now().isoformat(),
                        "details": metrics
                    })
                
                return analytics
                
            except Exception as e:
                app_logger.error(f"Failed to get Twitter analytics: {e}")
                return []
        
        return []
    
    def _get_platform_user_info(self, platform: SocialPlatform) -> Dict[str, Any]:
        """Get user info from a specific platform"""
        if platform == SocialPlatform.TWITTER:
            twitter_service = get_twitter_service()
            return twitter_service.get_user_info()
        
        return self._get_mock_user_info(platform)
    
    def _get_user_platform_info(self, platform: SocialPlatform, username: str) -> Dict[str, Any]:
        """Get user info from a specific platform for a specific user"""
        if platform == SocialPlatform.TWITTER:
            twitter_service = get_twitter_service(username)
            return twitter_service.get_user_info()
        
        return self._get_mock_user_info(platform)
    
    def post_content(self, content: str, platform: SocialPlatform, campaign_id: Optional[int] = None) -> Dict[str, Any]:
        """Post content to a platform"""
        if not self._should_use_real_data(platform):
            # Mock posting
            return {
                "success": True,
                "post_id": f"mock_post_{datetime.now().timestamp()}",
                "platform": platform.value,
                "content": content,
                "posted_at": datetime.now().isoformat(),
                "mock": True
            }
        
        try:
            if platform == SocialPlatform.TWITTER:
                twitter_service = get_twitter_service()
                result = twitter_service.post_tweet(content)
                
                if result:
                    return {
                        "success": True,
                        "post_id": result.get("id"),
                        "platform": "twitter",
                        "content": content,
                        "posted_at": datetime.now().isoformat(),
                        "mock": False
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to post to Twitter",
                        "platform": "twitter",
                        "mock": False
                    }
            else:
                return {
                    "success": False,
                    "error": f"Platform {platform.value} not implemented",
                    "platform": platform.value,
                    "mock": False
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "platform": platform.value,
                "mock": False
            }
    
    def get_data_source_info(self) -> Dict[str, Any]:
        """Get information about data sources being used"""
        return {
            "social_integration_enabled": SOCIAL_INTEGRATION_ENABLED,
            "real_data_available": self.real_data_enabled,
            "mock_data_enabled": self.mock_data_enabled,
            "enabled_platforms": [p.value for p in social_integration_manager.get_enabled_platforms()],
            "platform_status": social_integration_manager.get_all_platforms_status(),
            "connection_summary": connection_manager.get_connection_summary()
        }

# Global service instance
social_data_service = SocialDataService()
