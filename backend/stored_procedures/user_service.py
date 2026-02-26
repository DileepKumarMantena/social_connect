"""
User Service for SQLite database operations
"""

import hashlib
from services.logger import app_logger
from database import db

class UserService:
    def __init__(self):
        self.db = db
    
    def verify_user_credentials(self, username: str, password: str):
        """Verify user credentials against SQLite database"""
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            app_logger.info(f"Attempting login for username: {username}")
            app_logger.info(f"Password hash: {password_hash}")
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Simple query to debug
                cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
                user = cursor.fetchone()
                
                app_logger.info(f"Database query result: {user}")
                app_logger.info(f"Expected hash: {password_hash}")
                
                if user:
                    # Convert to dict and handle Row object properly
                    user_dict = dict(user) if hasattr(user, 'keys') else dict(user)
                    stored_hash = user_dict.get('password_hash', '')
                    app_logger.info(f"Stored hash: {repr(stored_hash)}")
                    app_logger.info(f"Expected hash: {repr(password_hash)}")
                    app_logger.info(f"Hashes match: {stored_hash == password_hash}")
                    app_logger.info(f"Stored hash type: {type(stored_hash)}")
                    app_logger.info(f"Expected hash type: {type(password_hash)}")
                    
                    if stored_hash == password_hash:
                        # Check if access has expired
                        if user_dict.get('access_expires_at'):
                            from datetime import datetime
                            if datetime.utcnow() > datetime.fromisoformat(user_dict['access_expires_at'].replace('Z', '+00:00')):
                                app_logger.warning(f"Access expired for user: {username}")
                                return None
                        
                        app_logger.info(f"User authenticated successfully: {username}")
                        return user_dict
                
                app_logger.warning(f"No user found with matching credentials for: {username}")
                return None
                
        except Exception as e:
            app_logger.error(f"Failed to verify credentials for {username}: {e}")
            return None

# Global instance
user_service = UserService()
