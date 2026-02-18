import os
import json
import schedule
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from src.agents.data_management.data_deduplication import DataDeduplication

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DeduplicationScheduler")

class DeduplicationScheduler:
    """Scheduler for data deduplication tasks"""
    
    def __init__(self, config_path: str = "./config/config.yaml"):
        """
        Initialize deduplication scheduler
        
        Args:
            config_path: Path to configuration file
        """
        self.deduplication_service = DataDeduplication()
        self.config_path = config_path
        self.schedule_config = self._load_schedule_config()
        self.is_running = False
    
    def _load_schedule_config(self) -> Dict[str, Any]:
        """
        Load schedule configuration from file
        
        Returns:
            Schedule configuration
        """
        try:
            import yaml
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            return config.get("deduplication", {}).get("schedule", {})
        except Exception as e:
            logger.error(f"Error loading schedule config: {e}")
            return {
                "enabled": False,
                "interval": "daily",
                "time": "00:00"
            }
    
    def configure_schedule(self, interval: str = "daily", time: str = "00:00"):
        """
        Configure deduplication schedule
        
        Args:
            interval: Schedule interval (daily, weekly, monthly)
            time: Time to run (HH:MM format)
        """
        self.schedule_config = {
            "enabled": True,
            "interval": interval,
            "time": time
        }
        logger.info(f"Configured deduplication schedule: {interval} at {time}")
    
    def start_scheduler(self):
        """
        Start the deduplication scheduler
        """
        if not self.schedule_config.get("enabled", False):
            logger.info("Deduplication scheduler is disabled in config")
            return
        
        interval = self.schedule_config.get("interval", "daily")
        run_time = self.schedule_config.get("time", "00:00")
        
        # Schedule the job
        if interval == "daily":
            schedule.every().day.at(run_time).do(self.run_deduplication)
        elif interval == "weekly":
            schedule.every().monday.at(run_time).do(self.run_deduplication)
        elif interval == "monthly":
            # For monthly, run on the first day of the month
            schedule.every().month.at(run_time).do(self.run_deduplication)
        
        self.is_running = True
        logger.info(f"Started deduplication scheduler: {interval} at {run_time}")
    
    def stop_scheduler(self):
        """
        Stop the deduplication scheduler
        """
        self.is_running = False
        schedule.clear()
        logger.info("Stopped deduplication scheduler")
    
    def run_scheduler(self):
        """
        Run the scheduler loop
        """
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def run_deduplication(self, data_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run deduplication task
        
        Args:
            data_ids: List of data IDs to check (None for all data)
            
        Returns:
            Deduplication result
        """
        logger.info(f"Starting deduplication task at {datetime.utcnow()}")
        
        # Get all data entries from index
        data_entries = self.deduplication_service.data_index.items()
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_data": len(data_entries),
            "checked_data": 0,
            "duplicate_found": 0,
            "similar_found": 0,
            "details": []
        }
        
        # Import notifier
        from src.agents.notification.user_notifier import UserNotifier
        notifier = UserNotifier()
        
        # Check each data entry
        for entry_id, entry in data_entries:
            # Skip if data_ids is specified and entry_id not in list
            if data_ids and entry_id not in data_ids:
                continue
            
            # Check for duplicates of this entry using existing hash
            duplicate_check = self.deduplication_service.check_duplication_by_hash(
                data_hash=entry.get("hash"),
                data_type=entry.get("data_type"),
                paper_id=entry.get("paper_id"),
                user_id=entry.get("user_id")
            )
            
            # Update results
            results["checked_data"] += 1
            if duplicate_check.get("has_duplicate"):
                results["duplicate_found"] += 1
                # Send deduplication alert
                import asyncio
                duplicate_info = {
                    "duplicates": duplicate_check.get("similar_data", []),
                    "data_hash": duplicate_check.get("data_hash"),
                    "data_type": duplicate_check.get("data_type")
                }
                asyncio.run(notifier.send_deduplication_alert(
                    user_id=entry.get("user_id"),
                    message=f"Exact duplicate found during scheduled deduplication",
                    duplicate_info=duplicate_info
                ))
            if duplicate_check.get("has_similar"):
                results["similar_found"] += 1
                # Send deduplication alert
                import asyncio
                similar_info = {
                    "similar_items": duplicate_check.get("similar_data", []),
                    "data_hash": duplicate_check.get("data_hash"),
                    "data_type": duplicate_check.get("data_type")
                }
                asyncio.run(notifier.send_deduplication_alert(
                    user_id=entry.get("user_id"),
                    message=f"Similar data found during scheduled deduplication",
                    similar_info=similar_info
                ))
            
            # Add details
            results["details"].append({
                "entry_id": entry_id,
                "paper_id": entry.get("paper_id"),
                "user_id": entry.get("user_id"),
                "data_type": entry.get("data_type"),
                "timestamp": entry.get("timestamp"),
                "has_duplicate": duplicate_check.get("has_duplicate"),
                "has_similar": duplicate_check.get("has_similar"),
                "recommendation": duplicate_check.get("recommendation")
            })
        
        # Save results to log
        self._save_deduplication_results(results)
        
        logger.info(f"Deduplication task completed: {results['checked_data']} data checked, {results['duplicate_found']} duplicates found")
        return results
    
    def _save_deduplication_results(self, results: Dict[str, Any]):
        """
        Save deduplication results to log file
        
        Args:
            results: Deduplication results
        """
        log_dir = os.path.join(os.path.dirname(__file__), "..", "..", "storage", "deduplication", "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"deduplication_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json")
        
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Saved deduplication results to: {log_file}")
    
    def trigger_manual_deduplication(self, data_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Trigger manual deduplication
        
        Args:
            data_ids: List of data IDs to check (None for all data)
            
        Returns:
            Deduplication result
        """
        logger.info(f"Manual deduplication triggered for data IDs: {data_ids or 'all'}")
        return self.run_deduplication(data_ids)
