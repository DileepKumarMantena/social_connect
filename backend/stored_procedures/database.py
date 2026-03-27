try:
    import pymysql
    from pymysql import Error
    MYSQL_AVAILABLE = True
except ImportError as e:
    print(f"PyMySQL not available: {e}")
    print("Please install pymysql: pip install pymysql")
    MYSQL_AVAILABLE = False

# Try SQLite fallback
try:
    import sqlite3
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

from contextlib import contextmanager
import hashlib
from services.logger import app_logger
from services.constants import DB_CONFIG, SQLITE_DB_PATH

class DatabaseManager:
    def __init__(self):
        self.config = DB_CONFIG
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        if MYSQL_AVAILABLE:
            try:
                self.connection = pymysql.connect(**self.config)
                app_logger.info("MySQL connection established successfully")
                return True
            except Exception as e:
                app_logger.error(f"MySQL connection failed: {e}")
                app_logger.info("Falling back to SQLite")
        
        # Fallback to SQLite
        if SQLITE_AVAILABLE:
            try:
                from database import db
                self.connection = db
                app_logger.info("SQLite fallback connection established")
                return True
            except Exception as e:
                app_logger.error(f"SQLite connection failed: {e}")
        
        return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            app_logger.info("Database connection closed")
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute SQL query with optional parameters"""
        cursor = None
        try:
            if hasattr(self.connection, 'cursor'):
                if MYSQL_AVAILABLE:
                    cursor = self.connection.cursor()
                else:
                    cursor = self.connection.get_connection().cursor()
            else:
                app_logger.error("No valid database connection")
                return None
            
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                self.connection.commit()
                return cursor.lastrowid
                
        except Exception as e:
            app_logger.error(f"Query execution failed: {e}")
            if self.connection:
                self.connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
    
    @contextmanager
    def get_cursor(self):
        """Get database cursor context manager"""
        cursor = None
        try:
            if hasattr(self.connection, 'cursor'):
                if MYSQL_AVAILABLE:
                    cursor = self.connection.cursor()
                else:
                    cursor = self.connection.get_connection().cursor()
            
            yield cursor
        finally:
            if cursor:
                cursor.close()

# Global database instance
db_manager = DatabaseManager()

def init_database():
    """Initialize database and create tables"""
    try:
        # Try MySQL first
        if MYSQL_AVAILABLE:
            temp_config = DB_CONFIG.copy()
            temp_config.pop('database', None)
            
            connection = pymysql.connect(**temp_config)
            cursor = connection.cursor()
            
            # Create database if not exists
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
            cursor.execute(f"USE {DB_CONFIG['database']}")
            
            # Create tables and seed data
            _create_mysql_tables(cursor)
            connection.close()
            app_logger.info("MySQL database initialized successfully")
            return True
        
    except Exception as e:
        app_logger.error(f"MySQL initialization failed: {e}")
        
        # Fallback to SQLite
        if SQLITE_AVAILABLE:
            try:
                from database import db
                app_logger.info("Using SQLite fallback database")
                return True
            except Exception as e:
                app_logger.error(f"SQLite fallback failed: {e}")
        
        return False

def _create_mysql_tables(cursor):
    """Create MySQL tables and seed data"""
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            name VARCHAR(100),
            role ENUM('super_admin', 'admin', 'user') DEFAULT 'user',
            companyid INT DEFAULT 0,
            activitystatus BOOLEAN DEFAULT TRUE,
            access_expires_at TIMESTAMP NULL,
            created_by INT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """)
    
    # Insert mock users
    users_data = [
        ('superadmin', 'deelipkumar261997@gmail.com', 'd357150517d3e65ae84985f7b705ad9fdc38372a22ece0a8ecaf8a20a249', 'Super Admin', 'super_admin', 0, None),
        ('admin1', 'admin1@company.com', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Admin One', 'admin', 1, 1),
        ('user1', 'user1@company.com', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'User One', 'user', 1, 2)
    ]
    
    cursor.executemany("""
        INSERT IGNORE INTO users (username, email, password_hash, name, role, companyid, created_by)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, users_data)
    
    # Create other tables as needed
    # ... (channels, campaigns, leads, etc.)
