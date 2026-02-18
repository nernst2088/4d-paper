import os
import json
from datetime import datetime
from typing import List, Dict, Optional
import logging
from src.core.models.discussion_model import DiscussionMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DiscussionManager")

class DiscussionManager:
    """Manager for reader-author discussions"""
    
    def __init__(self, storage_path="./storage/discussions"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    def _get_file_path(self, paper_id: str) -> str:
        """Get path to discussion file for a paper"""
        return os.path.join(self.storage_path, f"{paper_id}.json")

    def add_message(
        self,
        paper_id: str,
        user_id: str,
        content: str,
        is_author: bool = False
    ) -> DiscussionMessage:
        """
        Add new message to discussion
        
        Args:
            paper_id: Paper ID
            user_id: User ID
            content: Message content
            is_author: Whether the user is the paper author
            
        Returns:
            Created DiscussionMessage object
        """
        # Create message object
        msg = DiscussionMessage(
            paper_id=paper_id,
            user_id=user_id,
            content=content,
            is_author=is_author
        )

        # Load existing messages
        messages = self.get_all_messages(paper_id)
        messages.append(msg)

        # Save messages
        with open(self._get_file_path(paper_id), "w", encoding="utf-8") as f:
            json.dump([m.dict() for m in messages], f, indent=2, default=str)
        
        logger.info(f"Added message to paper {paper_id} (user: {user_id}, author: {is_author})")
        return msg

    def get_all_messages(self, paper_id: str) -> List[DiscussionMessage]:
        """
        Get all messages for a paper
        
        Args:
            paper_id: Paper ID
            
        Returns:
            List of DiscussionMessage objects
        """
        path = self._get_file_path(paper_id)
        if not os.path.exists(path):
            return []
        
        with open(path, "r", encoding="utf-8") as f:
            items = json.load(f)
        
        # Convert dicts to DiscussionMessage objects
        return [DiscussionMessage(**item) for item in items]
    
    def get_message(self, paper_id: str, message_id: str) -> Optional[DiscussionMessage]:
        """
        Get specific message by ID
        
        Args:
            paper_id: Paper ID
            message_id: Message ID
            
        Returns:
            DiscussionMessage object or None if not found
        """
        messages = self.get_all_messages(paper_id)
        for msg in messages:
            if msg.message_id == message_id:
                return msg
        return None
    
    def delete_message(self, paper_id: str, message_id: str, user_id: str, is_admin: bool = False) -> bool:
        """
        Delete message (only author, message creator, or admin can delete)
        
        Args:
            paper_id: Paper ID
            message_id: Message ID
            user_id: User ID requesting deletion
            is_admin: Whether user is admin
            
        Returns:
            True if deleted, False otherwise
        """
        messages = self.get_all_messages(paper_id)
        new_messages = []
        deleted = False
        
        for msg in messages:
            if msg.message_id == message_id:
                # Check if user is allowed to delete
                if msg.user_id == user_id or msg.is_author or is_admin:
                    deleted = True
                    logger.info(f"Deleted message {message_id} from paper {paper_id} (user: {user_id})")
                    continue
                else:
                    # Not allowed to delete
                    new_messages.append(msg)
            else:
                new_messages.append(msg)
        
        # Save updated messages
        with open(self._get_file_path(paper_id), "w", encoding="utf-8") as f:
            json.dump([m.dict() for m in new_messages], f, indent=2, default=str)
        
        return deleted