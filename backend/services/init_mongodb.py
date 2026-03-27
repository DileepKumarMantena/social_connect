#!/usr/bin/env python3
"""
MongoDB Database Initialization Script for Social Connect
Populates MongoDB with initial data from constants.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from services.constants import (
    users_db, channels_db, campaigns_db, leads_db, 
    analytics_db, scheduler_db, user_settings_db,
    MONGODB_URL, MONGODB_DB_NAME
)
from services.logger import app_logger

def init_mongodb():
    """Initialize MongoDB with mock data"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URL)
        client.admin.command('ping')
        db = client[MONGODB_DB_NAME]
        
        app_logger.info(f"Connected to MongoDB: {MONGODB_DB_NAME}")
        
        # Clear existing collections
        db.users.delete_many({})
        db.channels.delete_many({})
        db.campaigns.delete_many({})
        db.leads.delete_many({})
        db.analytics.delete_many({})
        db.scheduler.delete_many({})
        db.settings.delete_many({})
        
        # Insert users data
        users_data = list(users_db.values())
        if users_data:
            db.users.insert_many(users_data)
            app_logger.info(f"Inserted {len(users_data)} users")
        
        # Insert channels data
        if channels_db:
            db.channels.insert_many(channels_db)
            app_logger.info(f"Inserted {len(channels_db)} channels")
        
        # Insert campaigns data
        if campaigns_db:
            db.campaigns.insert_many(campaigns_db)
            app_logger.info(f"Inserted {len(campaigns_db)} campaigns")
        
        # Insert leads data
        if leads_db:
            db.leads.insert_many(leads_db)
            app_logger.info(f"Inserted {len(leads_db)} leads")
        
        # Insert analytics data
        if analytics_db:
            db.analytics.insert_many(analytics_db)
            app_logger.info(f"Inserted {len(analytics_db)} analytics records")
        
        # Insert scheduler data
        if scheduler_db:
            db.scheduler.insert_many(scheduler_db)
            app_logger.info(f"Inserted {len(scheduler_db)} scheduler records")
        
        # Insert settings data
        settings_data = []
        for username, settings in user_settings_db.items():
            settings_data.append({
                "username": username,
                **settings
            })
        if settings_data:
            db.settings.insert_many(settings_data)
            app_logger.info(f"Inserted {len(settings_data)} user settings")
        
        app_logger.info("MongoDB initialization completed successfully!")
        
        # Create indexes for better performance
        db.users.create_index("username", unique=True)
        db.users.create_index("email", unique=True)
        db.channels.create_index("created_by")
        db.campaigns.create_index("created_by")
        db.leads.create_index("created_by")
        db.analytics.create_index("created_by")
        db.scheduler.create_index("created_by")
        db.settings.create_index("username", unique=True)
        
        app_logger.info("Database indexes created successfully!")
        
    except ConnectionFailure as e:
        app_logger.error(f"Failed to connect to MongoDB: {e}")
        print("Make sure MongoDB is running and accessible at:", MONGODB_URL)
        return False
    except Exception as e:
        app_logger.error(f"Error initializing MongoDB: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()
    
    return True

if __name__ == "__main__":
    print("Initializing MongoDB database...")
    success = init_mongodb()
    if success:
        print("✅ MongoDB initialization completed successfully!")
        print(f"Database: {MONGODB_DB_NAME}")
        print(f"Connection: {MONGODB_URL}")
    else:
        print("❌ MongoDB initialization failed!")
        sys.exit(1)
