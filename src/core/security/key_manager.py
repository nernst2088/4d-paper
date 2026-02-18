import os
import json
from typing import Optional, Dict
import logging
from src.core.security.encryption import derive_encryption_key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KeyManager")

class KeyManager:
    """Manager for user-specific encryption keys"""
    
    def __init__(self, storage_path: str = "./storage/keys"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.keys_file = os.path.join(storage_path, "user_keys.json")
        self._load_keys()
    
    def _load_keys(self):
        """
        Load user keys from storage
        """
        if os.path.exists(self.keys_file):
            with open(self.keys_file, "r", encoding="utf-8") as f:
                self.keys = json.load(f)
        else:
            self.keys = {}
    
    def _save_keys(self):
        """
        Save user keys to storage
        """
        with open(self.keys_file, "w", encoding="utf-8") as f:
            json.dump(self.keys, f, indent=2)
    
    def get_user_key(self, user_id: str, password: str) -> bytes:
        """
        Get or create user-specific encryption key
        
        Args:
            user_id: User ID
            password: User password (used to derive key)
            
        Returns:
            User-specific encryption key
        """
        if user_id not in self.keys:
            # Create new key for user
            key, salt = derive_encryption_key(password)
            self.keys[user_id] = {
                "salt": salt.hex(),
                "key": key.decode("utf-8")
            }
            self._save_keys()
            logger.info(f"Created new encryption key for user: {user_id}")
        else:
            # Get existing key
            salt = bytes.fromhex(self.keys[user_id]["salt"])
            key, _ = derive_encryption_key(password, salt)
            logger.info(f"Retrieved encryption key for user: {user_id}")
        
        return key
    
    def rotate_user_key(self, user_id: str, old_password: str, new_password: str) -> bytes:
        """
        Rotate user encryption key
        
        Args:
            user_id: User ID
            old_password: Old password
            new_password: New password
            
        Returns:
            New encryption key
        """
        if user_id not in self.keys:
            raise ValueError(f"User not found: {user_id}")
        
        # Verify old password
        old_salt = bytes.fromhex(self.keys[user_id]["salt"])
        old_key, _ = derive_encryption_key(old_password, old_salt)
        
        # Create new key
        new_key, new_salt = derive_encryption_key(new_password)
        
        # Update key storage
        self.keys[user_id] = {
            "salt": new_salt.hex(),
            "key": new_key.decode("utf-8")
        }
        self._save_keys()
        
        logger.info(f"Rotated encryption key for user: {user_id}")
        return new_key
    
    def delete_user_key(self, user_id: str):
        """
        Delete user encryption key
        
        Args:
            user_id: User ID
        """
        if user_id in self.keys:
            del self.keys[user_id]
            self._save_keys()
            logger.info(f"Deleted encryption key for user: {user_id}")
    
    def has_user_key(self, user_id: str) -> bool:
        """
        Check if user has encryption key
        
        Args:
            user_id: User ID
            
        Returns:
            True if user has key, False otherwise
        """
        return user_id in self.keys
