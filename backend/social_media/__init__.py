#!/usr/bin/env python3
"""
Social Media Integration Module
Contains all social media platform integrations and management services
"""

# Import core modules that don't have external dependencies
try:
    from .social_config import (
        SocialPlatform, ConnectionStatus, SocialPlatformConfig,
        SocialIntegrationManager, social_integration_manager,
        PLATFORM_FEATURES, get_platform_features, is_real_data_available,
        SOCIAL_INTEGRATION_ENABLED
    )
    CONFIG_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Social config not available - {e}")
    CONFIG_AVAILABLE = False
    # Create placeholder classes
    class SocialPlatform: 
        TWITTER = "twitter"
        LINKEDIN = "linkedin"
        FACEBOOK = "facebook"
        INSTAGRAM = "instagram"
    class ConnectionStatus: 
        DISCONNECTED = "disconnected"
        CONNECTING = "connecting"
        CONNECTED = "connected"
        ERROR = "error"
        RATE_LIMITED = "rate_limited"
    class SocialPlatformConfig: pass
    class SocialIntegrationManager: pass
    social_integration_manager = None
    PLATFORM_FEATURES = {}
    def get_platform_features(p): return {}
    def is_real_data_available(): return False
    SOCIAL_INTEGRATION_ENABLED = False

# Try to import modules with external dependencies
try:
    from .twitter_service import (
        TwitterAPIError, TwitterAPIService, TwitterMockService, get_twitter_service
    )
    TWITTER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Twitter service not available - {e}")
    TWITTER_AVAILABLE = False
    # Create placeholder classes
    class TwitterAPIError(Exception): pass
    class TwitterAPIService: pass
    class TwitterMockService: pass
    def get_twitter_service(): return None

try:
    from .connection_manager import (
        ConnectionHealthChecker, ConnectionManager, connection_manager,
        initialize_connections, shutdown_connections
    )
    CONNECTION_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Connection manager not available - {e}")
    CONNECTION_MANAGER_AVAILABLE = False
    # Create placeholder classes
    class ConnectionHealthChecker: pass
    class ConnectionManager: pass
    connection_manager = None
    def initialize_connections(): pass
    def shutdown_connections(): pass

try:
    from .user_credentials import UserSocialCredentials, user_social_credentials
    USER_CREDENTIALS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: User credentials service not available - {e}")
    USER_CREDENTIALS_AVAILABLE = False
    # Create placeholder classes
    class UserSocialCredentials: pass
    user_social_credentials = None

try:
    from .oauth_manager import SocialOAuthManager, social_oauth_manager, get_mock_oauth_flow
    OAUTH_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: OAuth manager not available - {e}")
    OAUTH_MANAGER_AVAILABLE = False
    # Create placeholder classes
    class SocialOAuthManager: pass
    social_oauth_manager = None
    def get_mock_oauth_flow(): return None

try:
    from .social_data_service import SocialDataService, social_data_service
    DATA_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Social data service not available - {e}")
    DATA_SERVICE_AVAILABLE = False
    # Create placeholder classes
    class SocialDataService: pass
    social_data_service = None

__all__ = [
    # Configuration
    'SocialPlatform', 'ConnectionStatus', 'SocialPlatformConfig',
    'SocialIntegrationManager', 'social_integration_manager',
    'PLATFORM_FEATURES', 'get_platform_features', 'is_real_data_available',
    'SOCIAL_INTEGRATION_ENABLED', 'CONFIG_AVAILABLE',
    
    # Twitter Service
    'TwitterAPIError', 'TwitterAPIService', 'TwitterMockService', 'get_twitter_service',
    'TWITTER_AVAILABLE',
    
    # Connection Management
    'ConnectionHealthChecker', 'ConnectionManager', 'connection_manager',
    'initialize_connections', 'shutdown_connections',
    'CONNECTION_MANAGER_AVAILABLE',
    
    # User Credentials
    'UserSocialCredentials', 'user_social_credentials',
    'USER_CREDENTIALS_AVAILABLE',
    
    # OAuth Management
    'SocialOAuthManager', 'social_oauth_manager', 'get_mock_oauth_flow',
    'OAUTH_MANAGER_AVAILABLE',
    
    # Data Service
    'SocialDataService', 'social_data_service',
    'DATA_SERVICE_AVAILABLE'
]
