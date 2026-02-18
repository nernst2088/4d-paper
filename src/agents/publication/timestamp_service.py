import time
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TimestampService")

class TimestampService:
    """Service for creating and verifying timestamps for paper versions"""
    
    def __init__(self, storage_path: str = "./storage/timestamps"):
        import os
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    def create_timestamp(self, content: str, paper_id: str, version_number: int) -> Dict[str, Any]:
        """
        Create timestamp for paper version
        
        Args:
            content: Paper content
            paper_id: Paper ID
            version_number: Version number
            
        Returns:
            Timestamp metadata
        """
        # Generate content hash
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        
        # Create timestamp
        timestamp = {
            "timestamp_id": f"ts_{paper_id}_{version_number}_{int(time.time())}",
            "paper_id": paper_id,
            "version_number": version_number,
            "content_hash": content_hash,
            "timestamp": datetime.utcnow().isoformat(),
            "timestamp_unix": int(time.time()),
            "verification_code": self._generate_verification_code(content_hash, paper_id, version_number)
        }
        
        # Save timestamp
        self._save_timestamp(timestamp)
        
        logger.info(f"Timestamp created: {timestamp['timestamp_id']} for {paper_id} v{version_number}")
        return timestamp
    
    def verify_timestamp(self, timestamp_id: str) -> bool:
        """
        Verify timestamp integrity
        
        Args:
            timestamp_id: Timestamp ID
            
        Returns:
            True if timestamp is valid, False otherwise
        """
        # Load timestamp
        timestamp = self._load_timestamp(timestamp_id)
        if not timestamp:
            return False
        
        # Verify timestamp
        expected_verification_code = self._generate_verification_code(
            timestamp["content_hash"],
            timestamp["paper_id"],
            timestamp["version_number"]
        )
        
        if timestamp["verification_code"] != expected_verification_code:
            return False
        
        logger.info(f"Timestamp verified: {timestamp_id}")
        return True
    
    def _generate_verification_code(self, content_hash: str, paper_id: str, version_number: int) -> str:
        """
        Generate verification code for timestamp
        
        Args:
            content_hash: Content hash
            paper_id: Paper ID
            version_number: Version number
            
        Returns:
            Verification code
        """
        data = f"{content_hash}|{paper_id}|{version_number}|{int(time.time())}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()
    
    def _save_timestamp(self, timestamp: Dict[str, Any]):
        """
        Save timestamp to storage
        
        Args:
            timestamp: Timestamp metadata
        """
        import json
        timestamp_path = f"{self.storage_path}/{timestamp['timestamp_id']}.json"
        
        with open(timestamp_path, "w", encoding="utf-8") as f:
            json.dump(timestamp, f, indent=2)
    
    def _load_timestamp(self, timestamp_id: str) -> Optional[Dict[str, Any]]:
        """
        Load timestamp from storage
        
        Args:
            timestamp_id: Timestamp ID
            
        Returns:
            Timestamp metadata or None if not found
        """
        import json
        import os
        
        timestamp_path = f"{self.storage_path}/{timestamp_id}.json"
        if not os.path.exists(timestamp_path):
            return None
        
        with open(timestamp_path, "r", encoding="utf-8") as f:
            return json.load(f)
