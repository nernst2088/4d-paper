import h5py
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
import logging
from src.core.models.paper_model import SpaceCoordinate
from src.core.security.encryption import encrypt_content, decrypt_content
from src.core.security.hash_utils import calculate_data_hash

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FourDDataHandler")

class FourDDataHandler:
    """4D data handler for storage, retrieval and tracing of 3D+time dimension data"""
    
    def __init__(self, storage_path: str = "./storage/four_d_data"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        # HDF5 is industry standard for multidimensional/timeseries data (encrypted)
        self.hdf5_ext = ".h5.enc"  # Encrypted HDF5 file extension

    def save_four_d_data(
        self,
        data_content: Any,  # Supports DataFrame/3D arrays/video frames/etc
        data_id: str,
        user_id: str,
        paper_id: str,
        timestamp: datetime,
        space_coordinate: Optional[SpaceCoordinate] = None,
        encryption_key: bytes = None
    ) -> str:
        """
        Save 4D data with encryption and temporal/spatial metadata
        
        Args:
            data_content: Raw data (pandas DataFrame/3D array/binary)
            data_id: Unique data identifier
            user_id: Owner user ID
            paper_id: Associated paper ID
            timestamp: Data collection timestamp
            space_coordinate: Spatial coordinates of collection
            encryption_key: AES-256 encryption key
            
        Returns:
            Path to encrypted data file
        """
        # 1. Create 4D metadata
        metadata = {
            "data_id": data_id,
            "user_id": user_id,
            "paper_id": paper_id,
            "timestamp": timestamp.isoformat(),
            "space_coordinate": space_coordinate.dict() if space_coordinate else None,
            "data_hash": calculate_data_hash(str(data_content)),
            "create_time": datetime.utcnow().isoformat()
        }

        # 2. Store data in HDF5 format (supports multidimensional data)
        hdf5_path = os.path.join(self.storage_path, f"{data_id}.h5")
        with h5py.File(hdf5_path, "w") as f:
            # Store metadata as attributes
            f.attrs["metadata"] = json.dumps(metadata)
            # Store actual data
            if isinstance(data_content, dict):
                for key, value in data_content.items():
                    f.create_dataset(key, data=value)
            else:
                f.create_dataset("data", data=data_content)

        # 3. Encrypt the HDF5 file
        with open(hdf5_path, "rb") as f:
            raw_data = f.read()
        encrypted_data = encrypt_content(raw_data, encryption_key)
        encrypted_path = os.path.join(self.storage_path, f"{data_id}{self.hdf5_ext}")
        with open(encrypted_path, "wb") as f:
            f.write(encrypted_data)

        # 4. Remove unencrypted temporary file
        os.remove(hdf5_path)
        
        logger.info(f"4D data saved: {data_id} (paper: {paper_id}, user: {user_id})")
        return encrypted_path

    def load_four_d_data(
        self,
        data_id: str,
        encryption_key: bytes,
        timestamp: Optional[datetime] = None,  # Optional: filter by timestamp
        space_coordinate: Optional[SpaceCoordinate] = None  # Optional: filter by location
    ) -> Dict[str, Any]:
        """
        Load and decrypt 4D data with optional temporal/spatial filtering
        
        Args:
            data_id: Unique data identifier
            encryption_key: AES-256 decryption key
            timestamp: Filter by exact timestamp
            space_coordinate: Filter by exact spatial coordinates
            
        Returns:
            Dictionary containing metadata and raw data
        """
        # 1. Validate file exists
        encrypted_path = os.path.join(self.storage_path, f"{data_id}{self.hdf5_ext}")
        if not os.path.exists(encrypted_path):
            raise FileNotFoundError(f"4D data {data_id} not found")
        
        # 2. Decrypt the file
        with open(encrypted_path, "rb") as f:
            encrypted_data = f.read()
        decrypted_data = decrypt_content(encrypted_data, encryption_key)

        # 3. Create temporary HDF5 file for reading
        temp_hdf5_path = os.path.join(self.storage_path, f"{data_id}_temp.h5")
        with open(temp_hdf5_path, "wb") as f:
            f.write(decrypted_data)

        # 4. Read metadata and data
        result = {}
        with h5py.File(temp_hdf5_path, "r") as f:
            # Read metadata
            metadata = json.loads(f.attrs["metadata"])
            result["metadata"] = metadata
            
            # Apply temporal filter if specified
            if timestamp:
                data_timestamp = datetime.fromisoformat(metadata["timestamp"])
                if data_timestamp != timestamp:
                    raise ValueError(f"Timestamp mismatch: expected {timestamp}, got {data_timestamp}")
            
            # Apply spatial filter if specified
            if space_coordinate:
                data_space = metadata["space_coordinate"]
                if data_space != space_coordinate.dict():
                    raise ValueError(f"Spatial coordinate mismatch: expected {space_coordinate}, got {data_space}")
            
            # Read actual data
            data = {}
            for key in f.keys():
                data[key] = f[key][:]
            result["data"] = data if len(data) > 1 else data["data"]

        # 5. Clean up temporary file
        os.remove(temp_hdf5_path)
        
        logger.info(f"4D data loaded: {data_id}")
        return result

    def trace_four_d_data_by_time(
        self,
        paper_id: str,
        start_time: datetime,
        end_time: datetime,
        user_id: str,
        encryption_key: bytes
    ) -> Dict[str, Any]:
        """
        Trace 4D data for a paper across a time range (supports 10k+ year tracking)
        
        Args:
            paper_id: Target paper ID
            start_time: Start of time range
            end_time: End of time range
            user_id: Requesting user ID (permission check)
            encryption_key: Decryption key
            
        Returns:
            Dictionary of data IDs mapped to their complete data/metadata
        """
        # Traverse storage directory and filter matching data
        traced_data = {}
        for filename in os.listdir(self.storage_path):
            if not filename.endswith(self.hdf5_ext):
                continue
            
            data_id = filename.replace(self.hdf5_ext, "")
            try:
                # Extract metadata without full decryption for efficiency
                encrypted_path = os.path.join(self.storage_path, filename)
                with open(encrypted_path, "rb") as f:
                    encrypted_data = f.read()
                decrypted_metadata = self._extract_metadata_without_decrypt(encrypted_data, encryption_key)
                
                # Apply filters
                if (decrypted_metadata["paper_id"] == paper_id and
                    decrypted_metadata["user_id"] == user_id):
                    
                    data_timestamp = datetime.fromisoformat(decrypted_metadata["timestamp"])
                    if start_time <= data_timestamp <= end_time:
                        # Load complete data for matches
                        traced_data[data_id] = self.load_four_d_data(data_id, encryption_key)
                        
            except Exception as e:
                logger.warning(f"Failed to process data {data_id}: {str(e)}")
                continue
        
        logger.info(f"Traced {len(traced_data)} 4D data entries for paper {paper_id} ({start_time} to {end_time})")
        return traced_data

    def _extract_metadata_without_decrypt(self, encrypted_data: bytes, key: bytes) -> Dict[str, Any]:
        """Efficient metadata extraction without full data decryption"""
        # In production, store metadata separately for even better performance
        decrypted_data = decrypt_content(encrypted_data, key)
        temp_path = os.path.join(self.storage_path, "temp_metadata.h5")
        
        with open(temp_path, "wb") as f:
            f.write(decrypted_data)
            
        with h5py.File(temp_path, "r") as f:
            metadata = json.loads(f.attrs["metadata"])
            
        os.remove(temp_path)
        return metadata