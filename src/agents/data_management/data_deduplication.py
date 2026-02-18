import os
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DataDeduplication")

class DataDeduplication:
    """Service for detecting duplicate or similar data"""
    
    def __init__(self, storage_path: str = "./storage/deduplication"):
        """
        Initialize data deduplication service
        
        Args:
            storage_path: Path to store deduplication metadata
        """
        self.storage_path = storage_path
        self._ensure_storage_dir()
        self.data_index_path = os.path.join(self.storage_path, "data_index.json")
        self._load_data_index()
    
    def _ensure_storage_dir(self):
        """Ensure storage directory exists"""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
    
    def _load_data_index(self):
        """Load data index from file"""
        if os.path.exists(self.data_index_path):
            try:
                with open(self.data_index_path, "r", encoding="utf-8") as f:
                    self.data_index = json.load(f)
            except Exception as e:
                logger.error(f"Error loading data index: {e}")
                self.data_index = {}
        else:
            self.data_index = {}
    
    def _save_data_index(self):
        """Save data index to file"""
        try:
            with open(self.data_index_path, "w", encoding="utf-8") as f:
                json.dump(self.data_index, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving data index: {e}")
    
    def calculate_data_hash(self, data: Any) -> str:
        """
        Calculate hash for data
        
        Args:
            data: Data to hash
            
        Returns:
            Hash string
        """
        try:
            if isinstance(data, pd.DataFrame):
                # For DataFrame, sort columns and values for consistent hash
                sorted_df = data.sort_index(axis=0).sort_index(axis=1)
                # Convert to CSV string, handling object types
                data_str = sorted_df.to_csv(index=False, encoding='utf-8')
            elif isinstance(data, np.ndarray):
                # For numpy array, sort and convert to string
                if data.size > 0:
                    # Handle different data types
                    if np.issubdtype(data.dtype, np.object_):
                        # For object arrays, sort and convert to string
                        sorted_array = np.sort(data.flatten())
                        data_str = str(sorted_array)
                    else:
                        # For numeric arrays, use numpy's tostring
                        sorted_array = np.sort(data.flatten())
                        data_str = sorted_array.tostring().hex()
                else:
                    data_str = "empty_array"
            elif isinstance(data, dict):
                # For dict, sort keys for consistent hash
                sorted_dict = {k: self.calculate_data_hash(v) for k, v in sorted(data.items())}
                data_str = json.dumps(sorted_dict, ensure_ascii=False)
            else:
                # For other types, convert to string
                data_str = str(data)
        except Exception as e:
            # If hashing fails, use error message as fallback
            logger.warning(f"Error calculating hash: {e}")
            data_str = f"error_{str(e)}"
        
        return hashlib.sha256(data_str.encode("utf-8")).hexdigest()
    
    def find_similar_data(self, data_hash: str, data_type: str) -> List[Dict[str, Any]]:
        """
        Find similar data in index
        
        Args:
            data_hash: Hash of the data
            data_type: Type of the data
            
        Returns:
            List of similar data entries
        """
        similar_data = []
        
        for entry_id, entry in self.data_index.items():
            # Check exact hash match
            if entry.get("hash") == data_hash:
                similar_data.append({
                    "entry_id": entry_id,
                    "paper_id": entry.get("paper_id"),
                    "user_id": entry.get("user_id"),
                    "data_type": entry.get("data_type"),
                    "timestamp": entry.get("timestamp"),
                    "similarity": 1.0,  # Exact match
                    "match_type": "exact"
                })
            # Check data type similarity
            elif entry.get("data_type") == data_type:
                # For same data type, consider as potentially similar
                similar_data.append({
                    "entry_id": entry_id,
                    "paper_id": entry.get("paper_id"),
                    "user_id": entry.get("user_id"),
                    "data_type": entry.get("data_type"),
                    "timestamp": entry.get("timestamp"),
                    "similarity": 0.5,  # Partial match
                    "match_type": "type"
                })
        
        return similar_data
    
    def add_data_to_index(self, data_hash: str, data_type: str, paper_id: str, user_id: str) -> str:
        """
        Add data to index
        
        Args:
            data_hash: Hash of the data
            data_type: Type of the data
            paper_id: Paper ID
            user_id: User ID
            
        Returns:
            Entry ID
        """
        entry_id = f"entry_{paper_id}_{user_id}_{datetime.utcnow().timestamp()}"
        self.data_index[entry_id] = {
            "hash": data_hash,
            "data_type": data_type,
            "paper_id": paper_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        self._save_data_index()
        return entry_id
    
    def check_duplication(self, data: Any, data_type: str, paper_id: str, user_id: str) -> Dict[str, Any]:
        """
        Check if data is duplicate or similar to existing data
        
        Args:
            data: Data to check
            data_type: Type of the data
            paper_id: Paper ID
            user_id: User ID
            
        Returns:
            Duplication check result
        """
        # Calculate data hash
        data_hash = self.calculate_data_hash(data)
        logger.info(f"Checking data duplication for hash: {data_hash[:10]}...")
        
        return self.check_duplication_by_hash(data_hash, data_type, paper_id, user_id)
    
    def check_duplication_by_hash(self, data_hash: str, data_type: str, paper_id: str, user_id: str) -> Dict[str, Any]:
        """
        Check if data is duplicate or similar to existing data using a pre-calculated hash
        
        Args:
            data_hash: Hash of the data
            data_type: Type of the data
            paper_id: Paper ID
            user_id: User ID
            
        Returns:
            Duplication check result
        """
        logger.info(f"Checking data duplication by hash: {data_hash[:10]}...")
        
        # Find similar data
        similar_data = self.find_similar_data(data_hash, data_type)
        
        # Determine duplication status
        has_exact_match = any(item["similarity"] == 1.0 for item in similar_data)
        has_similar_match = len(similar_data) > 0
        
        result = {
            "data_hash": data_hash,
            "data_type": data_type,
            "has_duplicate": has_exact_match,
            "has_similar": has_similar_match,
            "similar_data": similar_data,
            "recommendation": self._generate_recommendation(has_exact_match, has_similar_match)
        }
        
        logger.info(f"Duplication check result: duplicate={has_exact_match}, similar={has_similar_match}")
        return result
    
    def _generate_recommendation(self, has_duplicate: bool, has_similar: bool) -> str:
        """
        Generate recommendation based on duplication check
        
        Args:
            has_duplicate: Whether there's an exact duplicate
            has_similar: Whether there's similar data
            
        Returns:
            Recommendation string
        """
        if has_duplicate:
            return "Exact duplicate found. Consider using existing data instead of uploading again."
        elif has_similar:
            return "Similar data found. Review existing data to avoid redundancy."
        else:
            return "No duplicate or similar data found. Safe to upload."
    
    def remove_data_from_index(self, entry_id: str) -> bool:
        """
        Remove data from index
        
        Args:
            entry_id: Entry ID to remove
            
        Returns:
            True if removed, False otherwise
        """
        if entry_id in self.data_index:
            del self.data_index[entry_id]
            self._save_data_index()
            return True
        return False
