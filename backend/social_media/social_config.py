#!/usr/bin/env python3
"""
Social Media Integration Configuration
Manages platform-specific settings, API credentials, and connection status
"""

import os
from typing import Dict, Any, Optional
from enum import Enum
from services.logger import app_logger

class SocialPlatform(Enum):
    """Supported social media platforms"""
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"

class ConnectionStatus(Enum):
    """Connection status for social platforms"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"

class SocialPlatformConfig:
    """Configuration for a social media platform"""
    
    def __init__(self, platform: SocialPlatform):
        self.platform = platform
        self.api_key = os.getenv(f"{platform.value.upper()}_API_KEY")
        self.api_secret = os.getenv(f"{platform.value.upper()}_API_SECRET")
        self.access_token = os.getenv(f"{platform.value.upper()}_ACCESS_TOKEN")
        self.access_token_secret = os.getenv(f"{platform.value.upper()}_ACCESS_TOKEN_SECRET")
        self.webhook_secret = os.getenv(f"{platform.value.upper()}_WEBHOOK_SECRET")
        self.app_id = os.getenv(f"{platform.value.upper()}_APP_ID")
        self.app_secret = os.getenv(f"{platform.value.upper()}_APP_SECRET")
        
    def is_configured(self) -> bool:
        """Check if platform has necessary credentials"""
        if self.platform == SocialPlatform.TWITTER:
            return bool(self.api_key and self.api_secret and self.access_token and self.access_token_secret)
        elif self.platform == SocialPlatform.LINKEDIN:
            return bool(self.app_id and self.app_secret and self.access_token)
        elif self.platform in [SocialPlatform.FACEBOOK, SocialPlatform.INSTAGRAM]:
            return bool(self.app_id and self.app_secret and self.access_token)
        return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary (without exposing sensitive data)"""
        return {
            "platform": self.platform.value,
            "configured": self.is_configured(),
            "has_api_key": bool(self.api_key),
            "has_api_secret": bool(self.api_secret),
            "has_access_token": bool(self.access_token),
            "has_app_id": bool(self.app_id),
            "has_app_secret": bool(self.app_secret)
        }

class SocialIntegrationManager:
    """Manages social media platform integrations and connections"""
    
    def __init__(self):
        self.platforms: Dict[SocialPlatform, SocialPlatformConfig] = {}
        self.connection_status: Dict[SocialPlatform, ConnectionStatus] = {}
        self.connection_errors: Dict[SocialPlatform, str] = {}
        self._initialize_platforms()
        
    def _initialize_platforms(self):
        """Initialize all supported platforms"""
        for platform in SocialPlatform:
            self.platforms[platform] = SocialPlatformConfig(platform)
            self.connection_status[platform] = (
                ConnectionStatus.CONNECTED 
                if self.platforms[platform].is_configured() 
                else ConnectionStatus.DISCONNECTED
            )
            self.connection_errors[platform] = ""
    
    def is_platform_enabled(self, platform: SocialPlatform) -> bool:
        """Check if a platform is enabled and configured"""
        return (
            platform in self.platforms and 
            self.platforms[platform].is_configured() and
            self.connection_status[platform] == ConnectionStatus.CONNECTED
        )
    
    def get_enabled_platforms(self) -> list[SocialPlatform]:
        """Get list of enabled platforms"""
        return [p for p in SocialPlatform if self.is_platform_enabled(p)]
    
    def set_connection_status(self, platform: SocialPlatform, status: ConnectionStatus, error: str = ""):
        """Update connection status for a platform"""
        self.connection_status[platform] = status
        self.connection_errors[platform] = error
        app_logger.info(f"Platform {platform.value} status: {status.value}" + (f" - {error}" if error else ""))
    
    def get_platform_status(self, platform: SocialPlatform) -> Dict[str, Any]:
        """Get detailed status for a platform"""
        config = self.platforms.get(platform)
        if not config:
            return {"platform": platform.value, "configured": False, "status": "not_supported"}
        
        return {
            "platform": platform.value,
            "configured": config.is_configured(),
            "status": self.connection_status[platform].value,
            "error": self.connection_errors[platform],
            "config_summary": config.get_config_summary()
        }
    
    def get_all_platforms_status(self) -> Dict[str, Any]:
        """Get status of all platforms"""
        return {
            "total_platforms": len(SocialPlatform),
            "enabled_platforms": len(self.get_enabled_platforms()),
            "platforms": {
                platform.value: self.get_platform_status(platform)
                for platform in SocialPlatform
            }
        }
    
    def test_platform_connection(self, platform: SocialPlatform) -> bool:
        """Test connection to a platform"""
        if not self.is_platform_enabled(platform):
            self.set_connection_status(platform, ConnectionStatus.DISCONNECTED, "Platform not configured")
            return False
        
        try:
            # Platform-specific connection testing will be implemented in individual platform services
            self.set_connection_status(platform, ConnectionStatus.CONNECTING)
            
            # For now, just validate configuration
            if self.platforms[platform].is_configured():
                self.set_connection_status(platform, ConnectionStatus.CONNECTED)
                return True
            else:
                self.set_connection_status(platform, ConnectionStatus.DISCONNECTED, "Missing credentials")
                return False
                
        except Exception as e:
            self.set_connection_status(platform, ConnectionStatus.ERROR, str(e))
            return False

# Global instance
social_integration_manager = SocialIntegrationManager()

# Feature flags for social media integration
SOCIAL_INTEGRATION_ENABLED = os.getenv("SOCIAL_INTEGRATION_ENABLED", "false").lower() == "true"

# Platform-specific feature flags
PLATFORM_FEATURES = {
    SocialPlatform.TWITTER: {
        "posting": True,
        "analytics": True,
        "engagement_tracking": True,
        "lead_generation": True
    },
    SocialPlatform.LINKEDIN: {
        "posting": True,
        "analytics": True,
        "engagement_tracking": False,
        "lead_generation": True
    },
    SocialPlatform.FACEBOOK: {
        "posting": True,
        "analytics": True,
        "engagement_tracking": True,
        "lead_generation": True
    },
    SocialPlatform.INSTAGRAM: {
        "posting": True,
        "analytics": True,
        "engagement_tracking": True,
        "lead_generation": False
    }
}

def get_platform_features(platform: SocialPlatform) -> Dict[str, bool]:
    """Get available features for a platform"""
    return PLATFORM_FEATURES.get(platform, {})

def is_real_data_available() -> bool:
    """Check if any real social media integration is available"""
    if not SOCIAL_INTEGRATION_ENABLED:
        return False
    
    return len(social_integration_manager.get_enabled_platforms()) > 0
