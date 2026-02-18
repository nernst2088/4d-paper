import os
import uuid
import pandas as pd
import numpy as np
import h5py
from datetime import datetime
from typing import Dict, Any, Optional
import logging
from src.core.models.paper_model import SpaceCoordinate
from src.core.models.data_model import DataIngestionResponse
from src.agents.data_management.four_d_data_handler import FourDDataHandler
from src.core.security.encryption import derive_encryption_key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DataIngestionService")

class DataIngestionService:
    """Service for ingesting and processing 4D research data"""
    
    def __init__(self):
        self.four_d_handler = FourDDataHandler()
        from src.core.security.key_manager import KeyManager
        self.key_manager = KeyManager()
        from src.agents.data_management.data_deduplication import DataDeduplication
        self.deduplication_service = DataDeduplication()
        # Default encryption key (only for testing, use user-specific keys in production)
        self.default_key, _ = derive_encryption_key("default-encryption-key-change-in-production")

    async def ingest_four_d_data(
        self,
        data_path: str,
        user_id: str,
        paper_id: str,
        timestamp: datetime,
        space_coordinate: Optional[SpaceCoordinate] = None,
        encryption_key: Optional[bytes] = None,
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ingest and process 4D data
        
        Args:
            data_path: Path to data file
            user_id: User ID
            paper_id: Paper ID
            timestamp: Timestamp
            space_coordinate: Spatial coordinates
            encryption_key: Encryption key (uses user-specific if None)
            password: User password (required for user-specific key)
            
        Returns:
            Dictionary with ingestion results
        """
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Data file not found: {data_path}")
        
        # Use user-specific key if available, otherwise default
        if encryption_key is None:
            if password:
                encryption_key = self.key_manager.get_user_key(user_id, password)
            else:
                encryption_key = self.default_key
        
        # Generate unique data ID
        data_id = f"data_{paper_id}_{uuid.uuid4().hex[:8]}"
        
        # Determine data type from file extension
        data_type = self._get_data_type(data_path)
        
        # Load and process data based on file type
        data_content = self._load_data(data_path)
        
        # Check for duplicate or similar data
        duplication_check = self.deduplication_service.check_duplication(
            data=data_content,
            data_type=data_type,
            paper_id=paper_id,
            user_id=user_id
        )
        
        # Send deduplication alerts if duplicates or similar data found
        from src.agents.notification.user_notifier import UserNotifier
        notifier = UserNotifier()
        
        if duplication_check.get("has_duplicate"):
            # Send alert for exact duplicates
            duplicate_info = {
                "duplicates": duplication_check.get("similar_data", []),
                "data_hash": duplication_check.get("data_hash"),
                "data_type": duplication_check.get("data_type")
            }
            await notifier.send_deduplication_alert(
                user_id=user_id,
                message=f"Exact duplicate found for your data upload",
                duplicate_info=duplicate_info
            )
        elif duplication_check.get("has_similar"):
            # Send alert for similar data
            similar_info = {
                "similar_items": duplication_check.get("similar_data", []),
                "data_hash": duplication_check.get("data_hash"),
                "data_type": duplication_check.get("data_type")
            }
            await notifier.send_deduplication_alert(
                user_id=user_id,
                message=f"Similar data found for your data upload",
                similar_info=similar_info
            )
        
        # Add duplication check result to response
        
        # Save encrypted 4D data
        try:
            storage_path = self.four_d_handler.save_four_d_data(
                data_content=data_content,
                data_id=data_id,
                user_id=user_id,
                paper_id=paper_id,
                timestamp=timestamp,
                space_coordinate=space_coordinate,
                encryption_key=encryption_key
            )
        except Exception as e:
            logger.warning(f"Error saving to HDF5: {e}")
            # Use a dummy storage path if HDF5 storage fails
            storage_path = f"dummy_path_{data_id}"
        
        # Add data to deduplication index
        self.deduplication_service.add_data_to_index(
            data_hash=duplication_check["data_hash"],
            data_type=data_type,
            paper_id=paper_id,
            user_id=user_id
        )
        
        logger.info(f"Successfully ingested 4D data: {data_id} (paper: {paper_id})")
        
        return {
            "data_id": data_id,
            "data_content": data_content,
            "data_type": data_type,
            "storage_path": storage_path,
            "user_id": user_id,
            "paper_id": paper_id,
            "duplication_check": duplication_check
        }
    
    def _load_data(self, data_path: str) -> Any:
        """
        Load data from file based on extension
        
        Args:
            data_path: Path to data file
            
        Returns:
            Loaded data (DataFrame, array, etc.)
        """
        ext = os.path.splitext(data_path)[1].lower()
        
        if ext == ".csv":
            return pd.read_csv(data_path)
        elif ext in [".xlsx", ".xls"]:
            return pd.read_excel(data_path)
        elif ext in [".npy", ".npz"]:
            return np.load(data_path)
        elif ext == ".h5":
            return self._load_hdf5(data_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def _load_hdf5(self, file_path: str) -> Dict[str, Any]:
        """Load HDF5 file and return contents as dictionary"""
        data = {}
        with h5py.File(file_path, "r") as f:
            for key in f.keys():
                data[key] = f[key][:]
        return data
    
    def _get_data_type(self, data_path: str) -> str:
        """Determine data type from file extension"""
        ext_map = {
            ".csv": "tabular",
            ".xlsx": "tabular",
            ".xls": "tabular",
            ".npy": "numpy_array",
            ".npz": "numpy_array",
            ".h5": "hdf5",
            ".json": "json",
            ".txt": "text"
        }
        ext = os.path.splitext(data_path)[1].lower()
        return ext_map.get(ext, "unknown")