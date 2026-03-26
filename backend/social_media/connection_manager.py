#!/usr/bin/env python3
"""
Social Platform Connection Management
Handles connection status tracking, health checks, and reconnection logic
"""

import asyncio
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from services.logger import app_logger
from .social_config import (
    SocialPlatform, social_integration_manager, ConnectionStatus, 
    is_real_data_available, SOCIAL_INTEGRATION_ENABLED
)
from .twitter_service import twitter_service

class ConnectionHealthChecker:
    """Manages health checks for social platform connections"""
    
    def __init__(self):
        self.check_interval = 300  # 5 minutes
        self.health_thread = None
        self.running = False
        self.last_health_check = {}
        self.health_status = {}
        
    def start_health_checks(self):
        """Start background health checking"""
        if not SOCIAL_INTEGRATION_ENABLED:
            app_logger.info("Social integration disabled, skipping health checks")
            return
            
        if self.running:
            app_logger.warning("Health checks already running")
            return
            
        self.running = True
        self.health_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self.health_thread.start()
        app_logger.info("Started social platform health checks")
    
    def stop_health_checks(self):
        """Stop background health checking"""
        self.running = False
        if self.health_thread:
            self.health_thread.join(timeout=5)
        app_logger.info("Stopped social platform health checks")
    
    def _health_check_loop(self):
        """Background loop for health checks"""
        while self.running:
            try:
                self._perform_health_checks()
                threading.Event().wait(self.check_interval)
            except Exception as e:
                app_logger.error(f"Health check loop error: {e}")
                threading.Event().wait(60)  # Wait 1 minute on error
    
    def _perform_health_checks(self):
        """Perform health checks on all enabled platforms"""
        enabled_platforms = social_integration_manager.get_enabled_platforms()
        
        for platform in enabled_platforms:
            try:
                health_result = self._check_platform_health(platform)
                self.health_status[platform.value] = health_result
                self.last_health_check[platform.value] = datetime.now().isoformat()
                
                # Update connection status based on health check
                if health_result["healthy"]:
                    social_integration_manager.set_connection_status(platform, ConnectionStatus.CONNECTED)
                else:
                    social_integration_manager.set_connection_status(
                        platform, ConnectionStatus.ERROR, health_result["error"]
                    )
                    
            except Exception as e:
                app_logger.error(f"Health check failed for {platform.value}: {e}")
                self.health_status[platform.value] = {
                    "healthy": False,
                    "error": str(e),
                    "checked_at": datetime.now().isoformat()
                }
    
    def _check_platform_health(self, platform: SocialPlatform) -> Dict[str, Any]:
        """Check health of a specific platform"""
        try:
            if platform == SocialPlatform.TWITTER:
                return self._check_twitter_health()
            # Add other platforms as they are implemented
            else:
                return {
                    "healthy": False,
                    "error": f"Platform {platform.value} not yet implemented",
                    "checked_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "checked_at": datetime.now().isoformat()
            }
    
    def _check_twitter_health(self) -> Dict[str, Any]:
        """Check Twitter API health"""
        try:
            # Test connection with a simple API call
            success = twitter_service.test_connection()
            
            if success:
                user_info = twitter_service.get_user_info()
                return {
                    "healthy": True,
                    "user_id": user_info.get("id"),
                    "username": user_info.get("username"),
                    "followers": user_info.get("public_metrics", {}).get("followers_count", 0),
                    "checked_at": datetime.now().isoformat()
                }
            else:
                return {
                    "healthy": False,
                    "error": "Connection test failed",
                    "checked_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "checked_at": datetime.now().isoformat()
            }
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        return {
            "health_checks_enabled": self.running,
            "check_interval_seconds": self.check_interval,
            "last_checks": self.last_health_check,
            "platform_health": self.health_status,
            "overall_healthy": all(
                status.get("healthy", False) 
                for status in self.health_status.values()
            ) if self.health_status else True
        }

class ConnectionManager:
    """Manages social platform connections and reconnection logic"""
    
    def __init__(self):
        self.health_checker = ConnectionHealthChecker()
        self.connection_attempts = {}
        self.max_reconnect_attempts = 3
        self.reconnect_delay = 60  # seconds
        
    def initialize(self):
        """Initialize connection management"""
        if SOCIAL_INTEGRATION_ENABLED:
            self.health_checker.start_health_checks()
            app_logger.info("Connection manager initialized")
        else:
            app_logger.info("Social integration disabled, connection manager not started")
    
    def shutdown(self):
        """Shutdown connection management"""
        self.health_checker.stop_health_checks()
        app_logger.info("Connection manager shutdown")
    
    def test_all_connections(self) -> Dict[str, Any]:
        """Test all configured platform connections"""
        results = {}
        enabled_platforms = social_integration_manager.get_enabled_platforms()
        
        for platform in enabled_platforms:
            try:
                if platform == SocialPlatform.TWITTER:
                    success = twitter_service.test_connection()
                    results[platform.value] = {
                        "success": success,
                        "status": "connected" if success else "failed",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    results[platform.value] = {
                        "success": False,
                        "status": "not_implemented",
                        "timestamp": datetime.now().isoformat()
                    }
                    
            except Exception as e:
                results[platform.value] = {
                    "success": False,
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        return results
    
    def reconnect_platform(self, platform: SocialPlatform) -> bool:
        """Attempt to reconnect a platform"""
        if platform in self.connection_attempts:
            attempts = self.connection_attempts[platform].get("attempts", 0)
            if attempts >= self.max_reconnect_attempts:
                app_logger.warning(f"Max reconnection attempts reached for {platform.value}")
                return False
        
        try:
            app_logger.info(f"Attempting to reconnect {platform.value}")
            
            # Reset connection status
            social_integration_manager.set_connection_status(platform, ConnectionStatus.CONNECTING)
            
            # Test connection
            if platform == SocialPlatform.TWITTER:
                success = twitter_service.test_connection()
                if success:
                    social_integration_manager.set_connection_status(platform, ConnectionStatus.CONNECTED)
                    # Reset attempt counter on success
                    if platform in self.connection_attempts:
                        del self.connection_attempts[platform]
                    return True
                else:
                    social_integration_manager.set_connection_status(platform, ConnectionStatus.ERROR, "Reconnection failed")
            
            # Update attempt counter
            if platform not in self.connection_attempts:
                self.connection_attempts[platform] = {"attempts": 0, "last_attempt": None}
            
            self.connection_attempts[platform]["attempts"] += 1
            self.connection_attempts[platform]["last_attempt"] = datetime.now().isoformat()
            
            return False
            
        except Exception as e:
            app_logger.error(f"Reconnection failed for {platform.value}: {e}")
            social_integration_manager.set_connection_status(platform, ConnectionStatus.ERROR, str(e))
            return False
    
    def get_connection_summary(self) -> Dict[str, Any]:
        """Get comprehensive connection summary"""
        return {
            "social_integration_enabled": SOCIAL_INTEGRATION_ENABLED,
            "real_data_available": is_real_data_available(),
            "platform_status": social_integration_manager.get_all_platforms_status(),
            "health_summary": self.health_checker.get_health_summary(),
            "connection_attempts": self.connection_attempts,
            "enabled_platforms": [p.value for p in social_integration_manager.get_enabled_platforms()]
        }

# Global connection manager instance
connection_manager = ConnectionManager()

# Initialize on module import
def initialize_connections():
    """Initialize social platform connections"""
    connection_manager.initialize()

def shutdown_connections():
    """Shutdown social platform connections"""
    connection_manager.shutdown()
