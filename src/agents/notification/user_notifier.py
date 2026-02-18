import logging
from datetime import datetime
from typing import Dict, Any, Optional
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UserNotifier")

class UserNotifier:
    """Notifier for sending progress/success/error notifications to users"""
    
    def __init__(self, notification_path: str = "./storage/notifications"):
        self.notification_path = notification_path
        os.makedirs(notification_path, exist_ok=True)
    
    def _get_user_notification_path(self, user_id: str) -> str:
        """Get path to user's notification file"""
        return os.path.join(self.notification_path, f"{user_id}_notifications.json")
    
    async def send_progress_notification(
        self,
        user_id: str,
        message: str,
        task_id: Optional[str] = None
    ):
        """
        Send progress notification to user
        
        Args:
            user_id: User ID
            message: Notification message
            task_id: Associated task ID (optional)
        """
        notification = {
            "type": "progress",
            "message": message,
            "task_id": task_id,
            "timestamp": datetime.utcnow().isoformat(),
            "read": False
        }
        self._save_notification(user_id, notification)
        logger.info(f"Progress notification sent to {user_id}: {message}")
    
    async def send_success_notification(
        self,
        user_id: str,
        message: str,
        task_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Send success notification to user
        
        Args:
            user_id: User ID
            message: Notification message
            task_id: Associated task ID (optional)
            data: Additional data (optional)
        """
        notification = {
            "type": "success",
            "message": message,
            "task_id": task_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "read": False
        }
        self._save_notification(user_id, notification)
        logger.info(f"Success notification sent to {user_id}: {message}")
    
    async def send_error_notification(
        self,
        user_id: str,
        message: str,
        task_id: Optional[str] = None,
        error_details: Optional[str] = None
    ):
        """
        Send error notification to user
        
        Args:
            user_id: User ID
            message: Notification message
            task_id: Associated task ID (optional)
            error_details: Detailed error information (optional)
        """
        notification = {
            "type": "error",
            "message": message,
            "task_id": task_id,
            "error_details": error_details,
            "timestamp": datetime.utcnow().isoformat(),
            "read": False
        }
        self._save_notification(user_id, notification)
        logger.error(f"Error notification sent to {user_id}: {message}")
    
    async def send_deduplication_alert(
        self,
        user_id: str,
        message: str,
        task_id: Optional[str] = None,
        duplicate_info: Optional[Dict[str, Any]] = None,
        similar_info: Optional[Dict[str, Any]] = None
    ):
        """
        Send deduplication alert to user with actionable options
        
        Args:
            user_id: User ID
            message: Notification message
            task_id: Associated task ID (optional)
            duplicate_info: Information about exact duplicates (optional)
            similar_info: Information about similar data (optional)
        """
        notification = {
            "type": "deduplication_alert",
            "message": message,
            "task_id": task_id,
            "duplicate_info": duplicate_info,
            "similar_info": similar_info,
            "timestamp": datetime.utcnow().isoformat(),
            "read": False,
            "actions": [
                {"id": "ignore", "label": "Ignore"},
                {"id": "replace", "label": "Replace with existing"},
                {"id": "merge", "label": "Merge data"},
                {"id": "review", "label": "Review manually"}
            ]
        }
        self._save_notification(user_id, notification)
        logger.info(f"Deduplication alert sent to {user_id}: {message}")
    
    def _save_notification(self, user_id: str, notification: Dict[str, Any]):
        """
        Save notification to user's notification file
        
        Args:
            user_id: User ID
            notification: Notification dictionary
        """
        path = self._get_user_notification_path(user_id)
        
        # Load existing notifications
        notifications = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                notifications = json.load(f)
        
        # Add new notification (prepend to keep newest first)
        notifications.insert(0, notification)
        
        # Keep only last 100 notifications to prevent file bloat
        if len(notifications) > 100:
            notifications = notifications[:100]
        
        # Save updated notifications
        with open(path, "w", encoding="utf-8") as f:
            json.dump(notifications, f, indent=2)
    
    def get_user_notifications(self, user_id: str, mark_as_read: bool = False) -> list:
        """
        Get all notifications for a user
        
        Args:
            user_id: User ID
            mark_as_read: Whether to mark notifications as read
            
        Returns:
            List of notifications
        """
        path = self._get_user_notification_path(user_id)
        
        if not os.path.exists(path):
            return []
        
        with open(path, "r", encoding="utf-8") as f:
            notifications = json.load(f)
        
        # Mark as read if requested
        if mark_as_read:
            for notification in notifications:
                notification["read"] = True
            with open(path, "w", encoding="utf-8") as f:
                json.dump(notifications, f, indent=2)
        
        return notifications
    
    def get_unread_count(self, user_id: str) -> int:
        """
        Get count of unread notifications for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Number of unread notifications
        """
        notifications = self.get_user_notifications(user_id)
        return sum(1 for n in notifications if not n.get("read", False))