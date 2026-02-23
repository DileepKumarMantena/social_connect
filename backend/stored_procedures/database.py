try:
    import pymysql
    from pymysql import Error
    MYSQL_AVAILABLE = True
except ImportError as e:
    print(f"PyMySQL not available: {e}")
    print("Please install pymysql: pip install pymysql")
    MYSQL_AVAILABLE = False
    raise e

from contextlib import contextmanager
import hashlib
from services.logger import app_logger
from constants import DB_CONFIG

class DatabaseManager:
    def __init__(self):
        self.config = DB_CONFIG
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = pymysql.connect(**self.config)
            app_logger.info("Database connection established successfully")
            return True
        except Exception as e:
            app_logger.error(f"Database connection failed: {e}")
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
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                app_logger.info(f"Query executed successfully, returned {len(result)} rows")
                return result
            else:
                self.connection.commit()
                app_logger.info("Query executed successfully, changes committed")
                return cursor.rowcount
                
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            app_logger.error(f"Query execution failed: {e}")
            raise e
        finally:
            if cursor:
                cursor.close()
    
    def execute_many(self, query, params_list):
        """Execute multiple queries with parameters"""
        cursor = None
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
            self.connection.commit()
            app_logger.info(f"Batch query executed successfully, {cursor.rowcount} rows affected")
            return cursor.rowcount
                
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            app_logger.error(f"Batch query execution failed: {e}")
            raise e
        finally:
            if cursor:
                cursor.close()
    
    @contextmanager
    def get_cursor(self):
        """Context manager for cursor operations"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        try:
            yield cursor
        finally:
            cursor.close()

# Global database instance
db_manager = DatabaseManager()

def init_database():
    """Initialize database and create tables"""
    try:
        # Connect to MySQL without database name
        temp_config = DB_CONFIG.copy()
        temp_config.pop('database', None)
        
        connection = pymysql.connect(**temp_config)
        cursor = connection.cursor()
        
        # Create database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        # Create tables
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
        
        create_channels_table = """
        CREATE TABLE IF NOT EXISTS channels (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            connected BOOLEAN DEFAULT FALSE,
            active BOOLEAN DEFAULT FALSE,
            followers INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        create_campaigns_table = """
        CREATE TABLE IF NOT EXISTS campaigns (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            status VARCHAR(20) DEFAULT 'draft',
            leads INT DEFAULT 0,
            conversion_rate DECIMAL(5,2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        create_leads_table = """
        CREATE TABLE IF NOT EXISTS leads (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            status VARCHAR(20) DEFAULT 'new',
            campaign_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
        )
        """
        
        cursor.execute(create_users_table)
        cursor.execute(create_channels_table)
        cursor.execute(create_campaigns_table)
        cursor.execute(create_leads_table)
        
        connection.commit()
        app_logger.info("Database and tables created successfully")
        
    except Exception as e:
        app_logger.error(f"Database initialization failed: {e}")
        raise e
    finally:
        if 'connection' in locals():
            connection.close()

def seed_initial_data():
    """Seed database with initial data"""
    try:
        # Seed users
        users_data = [
            ('testuser', 'test@example.com', hashlib.sha256("Password123!".encode()).hexdigest())
        ]
        db_manager.execute_many(
            "INSERT IGNORE INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            users_data
        )
        
        # Seed channels
        channels_data = [
            ('facebook', True, True, 1500),
            ('instagram', True, False, 800),
            ('linkedin', False, False, 0),
            ('twitter', False, False, 0)
        ]
        db_manager.execute_many(
            "INSERT IGNORE INTO channels (name, connected, active, followers) VALUES (%s, %s, %s, %s)",
            channels_data
        )
        
        # Seed campaigns
        campaigns_data = [
            ('Summer Sale', 'active', 45, 12.5),
            ('Product Launch', 'completed', 120, 8.3),
            ('Holiday Special', 'draft', 0, 0)
        ]
        db_manager.execute_many(
            "INSERT IGNORE INTO campaigns (name, status, leads, conversion_rate) VALUES (%s, %s, %s, %s)",
            campaigns_data
        )
        
        # Seed leads
        leads_data = [
            ('John Doe', 'john@example.com', 'new', 1),
            ('Jane Smith', 'jane@example.com', 'contacted', 1),
            ('Bob Johnson', 'bob@example.com', 'converted', 2),
            ('Alice Brown', 'alice@example.com', 'new', 1)
        ]
        db_manager.execute_many(
            "INSERT IGNORE INTO leads (name, email, status, campaign_id) VALUES (%s, %s, %s, %s)",
            leads_data
        )
        
        app_logger.info("Initial data seeded successfully")
        
    except Error as e:
        app_logger.error(f"Data seeding failed: {e}")
        raise e
