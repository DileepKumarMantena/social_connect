import logging
import os
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
import glob

class DailyRotatingLogger:
    def __init__(self, log_dir='logs', backup_count=7):
        self.log_dir = log_dir
        self.backup_count = backup_count
        
        # Create logs directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Setup logger
        self.logger = logging.getLogger('social_connect')
        self.logger.setLevel(logging.INFO)  # Set to INFO level
        
        # Create handler for daily rotation with date in filename
        log_filename = self._get_todays_log_filename()
        handler = TimedRotatingFileHandler(
            log_filename,
            when='midnight',  # Rotate at midnight
            interval=1,        # Daily
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        
        # Set format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(handler)
        
        # Also add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def _get_todays_log_filename(self):
        """Generate today's log filename with date"""
        today = datetime.now().strftime('%Y-%m-%d')
        return os.path.join(self.log_dir, f'social_connect_{today}.log')
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def error(self, message):
        """Log error message"""
        self.logger.error(message)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
    
    def cleanup_old_logs(self):
        """Clean up log files older than 7 days"""
        log_pattern = os.path.join(self.log_dir, 'social_connect_*.log')
        log_files = glob.glob(log_pattern)
        
        for log_file in log_files:
            try:
                # Get file modification time
                file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
                if datetime.now() - file_time > timedelta(days=7):
                    os.remove(log_file)
                    self.info(f"Deleted old log file: {log_file}")
            except Exception as e:
                self.error(f"Error deleting log file {log_file}: {e}")

# Create global logger instance
app_logger = DailyRotatingLogger()
