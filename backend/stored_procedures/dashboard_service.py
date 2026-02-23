from .database import db_manager
from services.logger import app_logger

class DashboardService:
    def __init__(self):
        self.db = db_manager
    
    def get_channels(self):
        """Get all channels"""
        try:
            query = "SELECT * FROM channels ORDER BY id"
            channels = self.db.execute_query(query, fetch=True)
            app_logger.info(f"Retrieved {len(channels)} channels from database")
            return channels
            
        except Exception as e:
            app_logger.error(f"Failed to get channels: {e}")
            raise e
    
    def get_campaigns(self):
        """Get all campaigns"""
        try:
            query = "SELECT * FROM campaigns ORDER BY id"
            campaigns = self.db.execute_query(query, fetch=True)
            app_logger.info(f"Retrieved {len(campaigns)} campaigns from database")
            return campaigns
            
        except Exception as e:
            app_logger.error(f"Failed to get campaigns: {e}")
            raise e
    
    def get_leads(self):
        """Get all leads"""
        try:
            query = """
            SELECT l.*, c.name as campaign_name 
            FROM leads l 
            LEFT JOIN campaigns c ON l.campaign_id = c.id 
            ORDER BY l.id
            """
            leads = self.db.execute_query(query, fetch=True)
            app_logger.info(f"Retrieved {len(leads)} leads from database")
            return leads
            
        except Exception as e:
            app_logger.error(f"Failed to get leads: {e}")
            raise e
    
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        try:
            # Get connected channels count
            channels_query = "SELECT COUNT(*) as count FROM channels WHERE connected = TRUE"
            channels_result = self.db.execute_query(channels_query, fetch=True)
            connected_channels = channels_result[0]['count']
            
            # Get active campaigns count
            campaigns_query = "SELECT COUNT(*) as count FROM campaigns WHERE status = 'active'"
            campaigns_result = self.db.execute_query(campaigns_query, fetch=True)
            active_campaigns = campaigns_result[0]['count']
            
            # Get total leads count
            leads_query = "SELECT COUNT(*) as count FROM leads"
            leads_result = self.db.execute_query(leads_query, fetch=True)
            total_leads = leads_result[0]['count']
            
            stats = {
                "channels": connected_channels,
                "campaigns": active_campaigns,
                "leads": total_leads
            }
            
            app_logger.info(f"Dashboard stats retrieved: {stats}")
            return stats
            
        except Exception as e:
            app_logger.error(f"Failed to get dashboard stats: {e}")
            raise e

# Global dashboard service instance
dashboard_service = DashboardService()
