import hashlib
from .database import db_manager
from services.logger import app_logger

class UserService:
    def __init__(self):
        self.db = db_manager
    
    def create_user(self, username, email, password):
        """Create a new user"""
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            query = """
            INSERT INTO users (username, email, password_hash) 
            VALUES (%s, %s, %s)
            """
            params = (username, email, password_hash)
            
            user_id = self.db.execute_query(query, params)
            app_logger.info(f"User created successfully: {username}")
            return user_id
            
        except Exception as e:
            app_logger.error(f"Failed to create user {username}: {e}")
            raise e
    
    def get_user_by_username(self, username):
        """Get user by username"""
        try:
            query = "SELECT * FROM users WHERE username = %s"
            params = (username,)
            
            users = self.db.execute_query(query, params, fetch=True)
            return users[0] if users else None
            
        except Exception as e:
            app_logger.error(f"Failed to get user by username {username}: {e}")
            raise e
    
    def get_user_by_email(self, email):
        """Get user by email"""
        try:
            query = "SELECT * FROM users WHERE email = %s"
            params = (email,)
            
            users = self.db.execute_query(query, params, fetch=True)
            return users[0] if users else None
            
        except Exception as e:
            app_logger.error(f"Failed to get user by email {email}: {e}")
            raise e
    
    def update_password(self, email, new_password):
        """Update user password"""
        try:
            password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            query = "UPDATE users SET password_hash = %s WHERE email = %s"
            params = (password_hash, email)
            
            rows_affected = self.db.execute_query(query, params)
            app_logger.info(f"Password updated for email: {email}")
            return rows_affected
            
        except Exception as e:
            app_logger.error(f"Failed to update password for {email}: {e}")
            raise e
    
    def verify_user_credentials(self, username, password):
        """Verify user credentials"""
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            query = "SELECT * FROM users WHERE username = %s AND password_hash = %s"
            params = (username, password_hash)
            
            users = self.db.execute_query(query, params, fetch=True)
            return users[0] if users else None
            
        except Exception as e:
            app_logger.error(f"Failed to verify credentials for {username}: {e}")
            raise e

# Global user service instance
user_service = UserService()
