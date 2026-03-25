import logging
import hashlib
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import List, Dict, Any

# Configure logging
app_logger = logging.getLogger(__name__)

class MongoDB:
    def __init__(self):
        """Initialize MongoDB connection"""
        try:
            self.client = MongoClient("mongodb://localhost:27017")
            self.db = self.client["social_connect"]
            app_logger.info("Connected to MongoDB: social_connect")
        except Exception as e:
            app_logger.error(f"Failed to connect to MongoDB: {e}")
            raise e
    
    def get_collection(self, collection_name: str):
        """Get MongoDB collection"""
        return self.db[collection_name]
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users from database"""
        try:
            collection = self.get_collection("users")
            users = list(collection.find({}))
            
            # Convert ObjectId to string for consistency
            for user in users:
                if "_id" in user:
                    user["_id"] = str(user["_id"])
            
            return users
        except PyMongoError as e:
            app_logger.error(f"Error getting all users: {e}")
            return []
    
    def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """Get user by email"""
        try:
            collection = self.get_collection("users")
            user = collection.find_one({"email": email})
            if user:
                # Convert ObjectId to string for consistency
                user["_id"] = str(user["_id"])
                return user
            return None
        except PyMongoError as e:
            app_logger.error(f"Error getting user by email: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Dict[str, Any]:
        """Get user by username"""
        try:
            collection = self.get_collection("users")
            user = collection.find_one({"username": username})
            if user:
                # Convert ObjectId to string for consistency
                user["_id"] = str(user["_id"])
                return user
            return None
        except PyMongoError as e:
            app_logger.error(f"Error getting user {username}: {e}")
            return None
    
    def get_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        try:
            collection = self.get_collection("users")
            users = list(collection.find({}))
            # Convert ObjectId to string for consistency
            for user in users:
                user["_id"] = str(user["_id"])
            return users
        except PyMongoError as e:
            app_logger.error(f"Error getting users: {e}")
            return []
    
    def get_campaigns(self) -> List[Dict[str, Any]]:
        """Get all campaigns"""
        try:
            collection = self.get_collection("campaigns")
            return list(collection.find({}, {"_id": 0}))
        except PyMongoError as e:
            app_logger.error(f"Error getting campaigns: {e}")
            return []
    
    def get_analytics(self) -> List[Dict[str, Any]]:
        """Get all analytics"""
        try:
            collection = self.get_collection("analytics")
            return list(collection.find({}, {"_id": 0}))
        except PyMongoError as e:
            app_logger.error(f"Error getting analytics: {e}")
            return []
    
    def get_scheduler(self) -> List[Dict[str, Any]]:
        """Get all scheduler items"""
        try:
            collection = self.get_collection("scheduler")
            return list(collection.find({}, {"_id": 0}))
        except PyMongoError as e:
            app_logger.error(f"Error getting scheduler: {e}")
            return []
    
    def create_schedule(self, schedule_data: Dict[str, Any]) -> bool:
        """Create a new schedule"""
        try:
            collection = self.get_collection("scheduler")
            # Get the next ID by finding the maximum existing ID
            existing_schedules = list(collection.find({}, {"id": 1}).sort("id", -1).limit(1))
            next_id = (existing_schedules[0]["id"] + 1) if existing_schedules else 1
            
            # Add the generated ID and default values
            schedule_data["id"] = next_id
            schedule_data.setdefault("status", "pending")
            schedule_data.setdefault("priority", "medium")
            
            result = collection.insert_one(schedule_data)
            success = result.acknowledged
            if success:
                app_logger.info(f"Schedule {schedule_data.get('task_name', 'Unknown')} created successfully with ID {next_id}")
            return success
        except PyMongoError as e:
            app_logger.error(f"Error creating schedule: {e}")
            return False
    
    def update_schedule(self, schedule_id: int, updates: Dict[str, Any]) -> bool:
        """Update schedule by ID"""
        try:
            collection = self.get_collection("scheduler")
            result = collection.update_one(
                {"id": schedule_id},
                {"$set": updates}
            )
            success = result.modified_count > 0
            if success:
                app_logger.info(f"Schedule {schedule_id} updated successfully")
            return success
        except PyMongoError as e:
            app_logger.error(f"Error updating schedule {schedule_id}: {e}")
            return False
    
    def delete_schedule(self, schedule_id: int) -> bool:
        """Delete schedule by ID"""
        try:
            collection = self.get_collection("scheduler")
            result = collection.delete_one({"id": schedule_id})
            success = result.deleted_count > 0
            if success:
                app_logger.info(f"Schedule {schedule_id} deleted successfully")
            return success
        except PyMongoError as e:
            app_logger.error(f"Error deleting schedule {schedule_id}: {e}")
            return False
    
    def create_campaign(self, campaign_data: Dict[str, Any]) -> bool:
        """Create a new campaign"""
        try:
            collection = self.get_collection("campaigns")
            # Get the next ID by finding the maximum existing ID
            existing_campaigns = list(collection.find({}, {"id": 1}).sort("id", -1).limit(1))
            next_id = (existing_campaigns[0]["id"] + 1) if existing_campaigns else 1
            
            # Add the generated ID and default values
            campaign_data["id"] = next_id
            campaign_data.setdefault("leads", 0)
            campaign_data.setdefault("conversion_rate", 0)
            
            result = collection.insert_one(campaign_data)
            success = result.acknowledged
            if success:
                app_logger.info(f"Campaign {campaign_data['name']} created successfully with ID {next_id}")
            return success
        except PyMongoError as e:
            app_logger.error(f"Error creating campaign: {e}")
            return False
    
    def update_campaign(self, campaign_id: int, updates: Dict[str, Any]) -> bool:
        """Update campaign by ID"""
        try:
            collection = self.get_collection("campaigns")
            result = collection.update_one(
                {"id": campaign_id},
                {"$set": updates}
            )
            success = result.modified_count > 0
            if success:
                app_logger.info(f"Campaign {campaign_id} updated successfully")
            return success
        except PyMongoError as e:
            app_logger.error(f"Error updating campaign {campaign_id}: {e}")
            return False
    
    def delete_campaign(self, campaign_id: int) -> bool:
        """Delete campaign by ID"""
        try:
            collection = self.get_collection("campaigns")
            result = collection.delete_one({"id": campaign_id})
            success = result.deleted_count > 0
            if success:
                app_logger.info(f"Campaign {campaign_id} deleted successfully")
            return success
        except PyMongoError as e:
            app_logger.error(f"Error deleting campaign {campaign_id}: {e}")
            return False
    
    def get_channels(self) -> List[Dict[str, Any]]:
        """Get all channels"""
        try:
            collection = self.get_collection("channels")
            return list(collection.find({}, {"_id": 0}))
        except PyMongoError as e:
            app_logger.error(f"Error getting channels: {e}")
            return []
    
    def get_leads(self) -> List[Dict[str, Any]]:
        """Get all leads"""
        try:
            collection = self.get_collection("leads")
            return list(collection.find({}, {"_id": 0}))
        except PyMongoError as e:
            app_logger.error(f"Error getting leads: {e}")
            return []
    
    def create_lead(self, lead_data: Dict[str, Any]) -> bool:
        """Create a new lead"""
        try:
            collection = self.get_collection("leads")
            # Get the next ID by finding the maximum existing ID
            existing_leads = list(collection.find({}, {"id": 1}).sort("id", -1).limit(1))
            next_id = (existing_leads[0]["id"] + 1) if existing_leads else 1
            
            # Add the generated ID and default values
            lead_data["id"] = next_id
            lead_data.setdefault("status", "new")
            
            result = collection.insert_one(lead_data)
            success = result.acknowledged
            if success:
                app_logger.info(f"Lead {lead_data.get('name', 'Unknown')} created successfully with ID {next_id}")
            return success
        except PyMongoError as e:
            app_logger.error(f"Error creating lead: {e}")
            return False
    
    def update_lead(self, lead_id: int, updates: Dict[str, Any]) -> bool:
        """Update lead by ID"""
        try:
            collection = self.get_collection("leads")
            result = collection.update_one(
                {"id": lead_id},
                {"$set": updates}
            )
            success = result.modified_count > 0
            if success:
                app_logger.info(f"Lead {lead_id} updated successfully")
            return success
        except PyMongoError as e:
            app_logger.error(f"Error updating lead {lead_id}: {e}")
            return False
    
    def get_channels(self) -> List[Dict[str, Any]]:
        """Get all channels"""
        try:
            collection = self.get_collection("channels")
            return list(collection.find({}, {"_id": 0}))
        except PyMongoError as e:
            app_logger.error(f"Error getting channels: {e}")
            return []
    
    def create_channel(self, channel_data: Dict[str, Any]) -> bool:
        """Create a new channel"""
        try:
            collection = self.get_collection("channels")
            # Get the next ID by finding the maximum existing ID
            existing_channels = list(collection.find({}, {"id": 1}).sort("id", -1).limit(1))
            next_id = (existing_channels[0]["id"] + 1) if existing_channels else 1
            
            # Add the generated ID and default values
            channel_data["id"] = next_id
            channel_data.setdefault("connected", False)
            channel_data.setdefault("active", False)
            channel_data.setdefault("followers", 0)
            
            result = collection.insert_one(channel_data)
            success = result.acknowledged
            if success:
                app_logger.info(f"Channel {channel_data.get('name', 'Unknown')} created successfully with ID {next_id}")
            return success
        except PyMongoError as e:
            app_logger.error(f"Error creating channel: {e}")
            return False
    
    def delete_lead(self, lead_id: int) -> bool:
        """Delete lead by ID"""
        try:
            collection = self.get_collection("leads")
            result = collection.delete_one({"id": lead_id})
            success = result.deleted_count > 0
            if success:
                app_logger.info(f"Lead {lead_id} deleted successfully")
            return success
        except PyMongoError as e:
            app_logger.error(f"Error deleting lead {lead_id}: {e}")
            return False
    
    def update_channel(self, channel_id: int, updates: Dict[str, Any]) -> bool:
        """Update channel by ID"""
        try:
            collection = self.get_collection("channels")
            result = collection.update_one(
                {"id": channel_id},
                {"$set": updates}
            )
            success = result.modified_count > 0
            if success:
                app_logger.info(f"Channel {channel_id} updated successfully")
            return success
        except PyMongoError as e:
            app_logger.error(f"Error updating channel {channel_id}: {e}")
            return False
    
    def connect_channel(self, channel_id: int) -> bool:
        """Connect a channel by ID"""
        return self.update_channel(channel_id, {"connected": True, "active": True})
    
    def disconnect_channel(self, channel_id: int) -> bool:
        """Disconnect a channel by ID"""
        return self.update_channel(channel_id, {"connected": False, "active": False})
    
    def delete_channel(self, channel_id: int) -> bool:
        """Delete channel by ID"""
        try:
            collection = self.get_collection("channels")
            result = collection.delete_one({"id": channel_id})
            success = result.deleted_count > 0
            if success:
                app_logger.info(f"Channel {channel_id} deleted successfully")
            return success
        except PyMongoError as e:
            app_logger.error(f"Error deleting channel {channel_id}: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user by username"""
        try:
            collection = self.get_collection("users")
            result = collection.delete_one({"username": user_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            app_logger.error(f"Error deleting user {user_id}: {e}")
            return False
    
    # Company methods will be implemented fresh
    
    def create_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new company and return the created company data"""
        try:
            collection = self.get_collection("companies")
            
            # Check if company already exists
            existing = collection.find_one({"name": company_data["name"]})
            if existing:
                raise Exception(f"Company '{company_data['name']}' already exists")
            
            # Get next ID
            last_company = collection.find_one({}, sort=[("id", -1)])
            next_id = (last_company["id"] + 1) if last_company else 1
            
            # Prepare company document
            company_doc = {
                "id": next_id,
                "name": company_data["name"],
                "companyId": company_data.get("companyId"),
                "adminUsername": company_data.get("adminUsername"),
                "adminEmail": company_data.get("adminEmail"),
                "subscription": company_data.get("subscription", "basic"),
                "status": "active",
                "createdDate": datetime.now().isoformat(),
                "startDate": company_data.get("startDate"),
                "endDate": company_data.get("endDate")
            }
            
            # Remove None values
            company_doc = {k: v for k, v in company_doc.items() if v is not None}
            
            # Insert company
            result = collection.insert_one(company_doc)
            
            if result.acknowledged:
                # Return the created company without MongoDB _id
                company_doc.pop("_id", None)
                app_logger.info(f"✅ Company created and saved: {company_doc['name']} with ID {company_doc['id']}")
                
                # Verify it was saved
                verify = collection.find_one({"id": next_id})
                if verify:
                    app_logger.info(f"✅ Company verified in database: {verify['name']}")
                else:
                    app_logger.error(f"❌ Company NOT found in database after insertion")
                
                return company_doc
            else:
                raise Exception("Failed to insert company")
                
        except Exception as e:
            app_logger.error(f"❌ Error creating company: {e}")
            raise e
    
    def get_companies(self) -> List[Dict[str, Any]]:
        """Get all companies"""
        try:
            collection = self.get_collection("companies")
            companies = list(collection.find({}))
            
            # Convert ObjectId to string and remove it from response
            for company in companies:
                if "_id" in company:
                    company["_id"] = str(company["_id"])
            
            return companies
        except Exception as e:
            app_logger.error(f"Error getting companies: {e}")
            return []
    
    def update_company(self, company_id: int, update_data: Dict[str, Any]) -> bool:
        """Update a company by ID"""
        try:
            collection = self.get_collection("companies")
            result = collection.update_one(
                {"id": company_id},
                {"$set": update_data}
            )
            success = result.modified_count > 0
            if success:
                app_logger.info(f"Company {company_id} updated successfully")
            return success
        except PyMongoError as e:
            app_logger.error(f"Error updating company {company_id}: {e}")
            return False
    
    def delete_company(self, company_id: int) -> bool:
        """Delete a company by ID"""
        try:
            collection = self.get_collection("companies")
            result = collection.delete_one({"id": company_id})
            success = result.deleted_count > 0
            if success:
                app_logger.info(f"Company {company_id} deleted successfully")
            return success
        except PyMongoError as e:
            app_logger.error(f"Error deleting company {company_id}: {e}")
            return False
    
    def delete_users_by_company(self, company_id: int) -> int:
        """Delete all users belonging to a specific company"""
        try:
            collection = self.get_collection("users")
            result = collection.delete_many({"companyid": company_id})
            users_deleted = result.deleted_count
            if users_deleted > 0:
                app_logger.info(f"Deleted {users_deleted} users from company {company_id}")
            return users_deleted
        except PyMongoError as e:
            app_logger.error(f"Error deleting users from company {company_id}: {e}")
            return 0
    
    def update_user_activity(self, user_id: str, activity_status: bool) -> bool:
        """Update user activity status"""
        try:
            collection = self.get_collection("users")
            result = collection.update_one(
                {"username": user_id},
                {"$set": {"activitystatus": activity_status}}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            app_logger.error(f"Error updating user activity {user_id}: {e}")
            return False
    
    def update_user_password(self, username: str, password_hash: str) -> bool:
        """Update user password"""
        try:
            collection = self.get_collection("users")
            result = collection.update_one(
                {"username": username},
                {"$set": {"password_hash": password_hash}}
            )
            success = result.modified_count > 0
            if success:
                app_logger.info(f"Password updated successfully for user {username}")
            else:
                app_logger.error(f"Failed to update password for user {username}")
            return success
        except PyMongoError as e:
            app_logger.error(f"Error updating password for user {username}: {e}")
            return False
    
    def update_user(self, username: str, updates: Dict[str, Any]) -> bool:
        """Update user by username"""
        try:
            collection = self.get_collection("users")
            result = collection.update_one(
                {"username": username},
                {"$set": updates}
            )
            success = result.modified_count > 0
            if success:
                app_logger.info(f"User {username} updated successfully")
            else:
                app_logger.error(f"Failed to update user {username}")
            return success
        except PyMongoError as e:
            app_logger.error(f"Error updating user {username}: {e}")
            return False
    
    # Role Management Methods
    def get_roles(self) -> Dict[str, Any]:
        """Get all roles"""
        try:
            collection = self.get_collection("roles")
            roles = list(collection.find({}))  # Remove the filter to get all roles
            # Convert to dict format for compatibility
            roles_dict = {}
            for role in roles:
                role_key = role.get("roleId", role.get("roleKey"))
                if role_key:
                    role_data = {
                        "id": str(role.get("_id")),
                        "role_id": role_key,
                        "role_name": role.get("roleName"),
                        "companyid": role.get("companyid", 0)  # Add companyid with default 0
                    }
                    roles_dict[role_key] = role_data
            return roles_dict
        except PyMongoError as e:
            app_logger.error(f"Error getting roles: {e}")
            return {}
    
    def get_role_by_id(self, role_id: str) -> Dict[str, Any]:
        """Get role by role ID"""
        try:
            collection = self.get_collection("roles")
            role = collection.find_one({"roleId": role_id}, {"_id": 0})
            return role
        except PyMongoError as e:
            app_logger.error(f"Error getting role {role_id}: {e}")
            return None
    
    def create_role(self, role_data: Dict[str, Any]) -> bool:
        """Create a new role"""
        try:
            collection = self.get_collection("roles")
            # Check if role already exists
            existing_role = collection.find_one({"roleId": role_data["roleId"], "companyid": role_data.get("companyid", 0)})
            if existing_role:
                app_logger.warning(f"Role {role_data['roleId']} already exists for company {role_data.get('companyid', 0)}")
                return False
            
            # Add default status if not provided
            role_data.setdefault("status", "active")
            
            result = collection.insert_one(role_data)
            success = result.acknowledged
            if success:
                app_logger.info(f"Role {role_data['roleId']} created successfully for company {role_data.get('companyid', 0)}")
            return success
        except PyMongoError as e:
            app_logger.error(f"Error creating role: {e}")
            return False
    
    def update_role(self, role_id: str, updates: Dict[str, Any]) -> bool:
        """Update role by role ID"""
        try:
            collection = self.get_collection("roles")
            result = collection.update_one(
                {"roleId": role_id},
                {"$set": updates}
            )
            success = result.modified_count > 0
            if success:
                app_logger.info(f"Role {role_id} updated successfully")
            return success
        except PyMongoError as e:
            app_logger.error(f"Error updating role {role_id}: {e}")
            return False
    
    def delete_role(self, role_id: str) -> bool:
        """Delete role by role ID"""
        try:
            collection = self.get_collection("roles")
            result = collection.delete_one({"roleId": role_id})
            success = result.deleted_count > 0
            if success:
                app_logger.info(f"Role {role_id} deleted successfully")
            return success
        except PyMongoError as e:
            app_logger.error(f"Error deleting role {role_id}: {e}")
            return False
    
    def initialize_default_roles(self) -> bool:
        """Initialize default roles if they don't exist"""
        try:
            default_roles = {
                "super_admin": {
                    "roleId": "super_admin",
                    "roleName": "Super Admin",
                    "permissions": {
                        "role_management": {"Create": True, "Read": True, "Update": True, "Delete": True},
                        "campaigns": {"Create": True, "Read": True, "Update": True, "Delete": True},
                        "analytics": {"Create": True, "Read": True, "Update": True, "Delete": True},
                        "leads": {"Create": True, "Read": True, "Update": True, "Delete": True},
                        "channels": {"Create": True, "Read": True, "Update": True, "Delete": True},
                        "scheduler": {"Create": True, "Read": True, "Update": True, "Delete": True}
                    }
                },
                "admin": {
                    "roleId": "admin",
                    "roleName": "Admin",
                    "permissions": {
                        "campaigns": {"Create": True, "Read": True, "Update": True, "Delete": True},
                        "analytics": {"Create": False, "Read": True, "Update": False, "Delete": False},
                        "leads": {"Create": True, "Read": True, "Update": True, "Delete": True},
                        "channels": {"Create": True, "Read": True, "Update": True, "Delete": True},
                        "scheduler": {"Create": True, "Read": True, "Update": True, "Delete": True}
                    }
                },
                "user": {
                    "roleId": "user",
                    "roleName": "User",
                    "permissions": {
                        "campaigns": {"Create": False, "Read": True, "Update": False, "Delete": False},
                        "analytics": {"Create": False, "Read": True, "Update": False, "Delete": False},
                        "leads": {"Create": False, "Read": True, "Update": False, "Delete": False},
                        "channels": {"Create": False, "Read": True, "Update": False, "Delete": False},
                        "scheduler": {"Create": False, "Read": True, "Update": False, "Delete": False}
                    }
                },
                "marketing_manager": {
                    "roleId": "marketing_manager",
                    "roleName": "Marketing Manager",
                    "permissions": {
                        "campaigns": {"Create": True, "Read": True, "Update": True, "Delete": False},
                        "analytics": {"Create": True, "Read": True, "Update": True, "Delete": False},
                        "leads": {"Create": True, "Read": True, "Update": True, "Delete": False},
                        "channels": {"Create": False, "Read": True, "Update": False, "Delete": False},
                        "scheduler": {"Create": True, "Read": True, "Update": True, "Delete": False}
                    }
                },
                "content_editor": {
                    "roleId": "content_editor",
                    "roleName": "Content Editor",
                    "permissions": {
                        "campaigns": {"Create": True, "Read": True, "Update": True, "Delete": False},
                        "analytics": {"Create": False, "Read": True, "Update": False, "Delete": False},
                        "leads": {"Create": False, "Read": True, "Update": False, "Delete": False},
                        "channels": {"Create": False, "Read": True, "Update": False, "Delete": False},
                        "scheduler": {"Create": False, "Read": True, "Update": False, "Delete": False}
                    }
                },
                "sales_manager": {
                    "roleId": "sales_manager",
                    "roleName": "Sales Manager",
                    "permissions": {
                        "campaigns": {"Create": False, "Read": True, "Update": False, "Delete": False},
                        "analytics": {"Create": False, "Read": True, "Update": False, "Delete": False},
                        "leads": {"Create": True, "Read": True, "Update": True, "Delete": False},
                        "channels": {"Create": False, "Read": True, "Update": False, "Delete": False},
                        "scheduler": {"Create": False, "Read": True, "Update": False, "Delete": False}
                    }
                }
            }
            
            collection = self.get_collection("roles")
            existing_roles = set()
            for role in collection.find({}, {"roleId": 1, "roleName": 1}):
                # Handle both roleId and roleName fields
                role_id = role.get("roleId") or role.get("roleName", "").lower().replace(" ", "_")
                existing_roles.add(role_id)
            
            roles_created = 0
            for role_key, role_data in default_roles.items():
                if role_key not in existing_roles:
                    collection.insert_one(role_data)
                    roles_created += 1
                    app_logger.info(f"Created default role: {role_key}")
            
            if roles_created > 0:
                app_logger.info(f"Initialized {roles_created} default roles in MongoDB")
            else:
                app_logger.info("All default roles already exist in MongoDB")
            
            return True
        except PyMongoError as e:
            app_logger.error(f"Error initializing default roles: {e}")
            return False
    
    def initialize_default_data(self) -> bool:
        """Initialize default collections data if they don't exist"""
        try:
            # Initialize users
            users_collection = self.get_collection("users")
            if users_collection.count_documents({}) == 0:
                from constants import users_db
                default_users = [
                    {
                        "username": "superadmin",
                        "email": "deelipkumar261997@gmail.com",
                        "password_hash": hashlib.sha256("SuperAdmin123!".encode()).hexdigest(),
                        "name": "Super Admin",
                        "role": "super_admin",
                        "companyid": 0,
                        "user_type": "platform_owner",
                        "activitystatus": True,
                        "access_expires_at": None,
                        "created_by": None
                    },
                    {
                        "username": "admin1",
                        "email": "admin1@company.com",
                        "password_hash": hashlib.sha256("Admin123!".encode()).hexdigest(),
                        "name": "Admin One",
                        "role": "admin",
                        "companyid": 1,
                        "user_type": "tenant_user",
                        "activitystatus": True,
                        "access_expires_at": None,
                        "created_by": "superadmin"
                    },
                    {
                        "username": "user1",
                        "email": "user1@company.com",
                        "password_hash": hashlib.sha256("User123!".encode()).hexdigest(),
                        "name": "User One",
                        "role": "user",
                        "companyid": 1,
                        "user_type": "tenant_employee",
                        "activitystatus": True,
                        "access_expires_at": None,
                        "created_by": "admin1"
                    },
                    {
                        "username": "employee1",
                        "email": "employee1@platform.com",
                        "password_hash": hashlib.sha256("Employee123!".encode()).hexdigest(),
                        "name": "Platform Employee",
                        "role": "admin",
                        "companyid": 0,
                        "user_type": "self_company_employee",
                        "activitystatus": True,
                        "access_expires_at": None,
                        "created_by": "superadmin"
                    }
                ]
                users_collection.insert_many(default_users)
                app_logger.info("Initialized default users in MongoDB")
            
            # Initialize channels
            channels_collection = self.get_collection("channels")
            if channels_collection.count_documents({}) == 0:
                default_channels = [
                    {"id": 1, "name": "facebook", "connected": True, "active": True, "followers": 1500, "created_by": "admin1"},
                    {"id": 2, "name": "instagram", "connected": True, "active": False, "followers": 800, "created_by": "admin1"},
                    {"id": 3, "name": "linkedin", "connected": False, "active": False, "followers": 0, "created_by": "superadmin"},
                    {"id": 4, "name": "twitter", "connected": False, "active": False, "followers": 0, "created_by": "admin1"},
                    {"id": 5, "name": "youtube", "connected": True, "active": True, "followers": 2500, "created_by": "superadmin"}
                ]
                channels_collection.insert_many(default_channels)
                app_logger.info("Initialized default channels in MongoDB")
            
            # Initialize campaigns
            campaigns_collection = self.get_collection("campaigns")
            if campaigns_collection.count_documents({}) == 0:
                default_campaigns = [
                    {"id": 1, "name": "Summer Sale", "status": "active", "leads": 45, "conversion_rate": 12.5, "created_by": "admin1"},
                    {"id": 2, "name": "Product Launch", "status": "completed", "leads": 120, "conversion_rate": 8.3, "created_by": "admin1"},
                    {"id": 3, "name": "Holiday Special", "status": "draft", "leads": 0, "conversion_rate": 0, "created_by": "superadmin"},
                    {"id": 4, "name": "New Year Campaign", "status": "active", "leads": 25, "conversion_rate": 15.2, "created_by": "superadmin"},
                    {"id": 5, "name": "Admin Campaign", "status": "active", "leads": 30, "conversion_rate": 10.5, "created_by": "admin1"}
                ]
                campaigns_collection.insert_many(default_campaigns)
                app_logger.info("Initialized default campaigns in MongoDB")
            
            # Initialize leads
            leads_collection = self.get_collection("leads")
            if leads_collection.count_documents({}) == 0:
                default_leads = [
                    {"id": 1, "name": "John Doe", "email": "john@example.com", "status": "new", "campaign_id": 1, "created_by": "admin1"},
                    {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "status": "contacted", "campaign_id": 1, "created_by": "admin1"},
                    {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "status": "converted", "campaign_id": 2, "created_by": "admin1"},
                    {"id": 4, "name": "Alice Brown", "email": "alice@example.com", "status": "new", "campaign_id": 1, "created_by": "superadmin"},
                    {"id": 5, "name": "David Lee", "email": "david@example.com", "status": "new", "campaign_id": 4, "created_by": "superadmin"},
                    {"id": 6, "name": "Emma Wilson", "email": "emma@example.com", "status": "contacted", "campaign_id": 4, "created_by": "superadmin"}
                ]
                leads_collection.insert_many(default_leads)
                app_logger.info("Initialized default leads in MongoDB")
            
            # Initialize analytics
            analytics_collection = self.get_collection("analytics")
            if analytics_collection.count_documents({}) == 0:
                default_analytics = [
                    {"id": 1, "metric": "campaign_performance", "value": 85.2, "period": "monthly", "campaign_id": 1, "date": "2026-02-01", "created_by": "admin1"},
                    {"id": 2, "metric": "lead_conversion", "value": 12.5, "period": "weekly", "campaign_id": 1, "date": "2026-02-15", "created_by": "admin1"},
                    {"id": 3, "metric": "engagement_rate", "value": 68.4, "period": "monthly", "channel_id": 1, "date": "2026-02-01", "created_by": "admin1"},
                    {"id": 4, "metric": "roi", "value": 245.6, "period": "quarterly", "campaign_id": 2, "date": "2026-01-01", "created_by": "admin1"},
                    {"id": 5, "metric": "click_through_rate", "value": 8.9, "period": "weekly", "campaign_id": 1, "date": "2026-02-15", "created_by": "superadmin"},
                    {"id": 6, "metric": "cost_per_lead", "value": 45.3, "period": "monthly", "campaign_id": 3, "date": "2026-02-01", "created_by": "superadmin"}
                ]
                analytics_collection.insert_many(default_analytics)
                app_logger.info("Initialized default analytics in MongoDB")
            
            # Initialize scheduler
            scheduler_collection = self.get_collection("scheduler")
            if scheduler_collection.count_documents({}) == 0:
                default_scheduler = [
                    {"id": 1, "campaign_id": 1, "task_name": "Summer Sale Launch", "scheduled_date": "2026-03-01", "scheduled_time": "10:00", "status": "pending", "priority": "high", "created_by": "admin1"},
                    {"id": 2, "campaign_id": 2, "task_name": "Product Launch Email", "scheduled_date": "2026-02-28", "scheduled_time": "14:30", "status": "scheduled", "priority": "medium", "created_by": "admin1"},
                    {"id": 3, "campaign_id": 1, "task_name": "Social Media Posts", "scheduled_date": "2026-02-27", "scheduled_time": "09:00", "status": "completed", "priority": "low", "created_by": "admin1"},
                    {"id": 4, "campaign_id": 3, "task_name": "Holiday Special Prep", "scheduled_date": "2026-03-15", "scheduled_time": "11:00", "status": "pending", "priority": "high", "created_by": "superadmin"},
                    {"id": 5, "campaign_id": 1, "task_name": "Follow-up Campaign", "scheduled_date": "2026-03-05", "scheduled_time": "16:00", "status": "pending", "priority": "medium", "created_by": "superadmin"}
                ]
                scheduler_collection.insert_many(default_scheduler)
                app_logger.info("Initialized default scheduler in MongoDB")
            
            return True
        except PyMongoError as e:
            app_logger.error(f"Error initializing default data: {e}")
            return False

# Create singleton instance
mongo_db = MongoDB()
