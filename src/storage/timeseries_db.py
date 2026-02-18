import os
import json
import h5py
from datetime import datetime
from typing import Dict, Any, List
import logging
from src.core.models.paper_model import PaperVersion

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TimeSeriesDB")

class TimeSeriesDB:
    """Time-series database for long-term (10k+ years) tracking of paper versions"""
    
    def __init__(self, db_path: str = "./storage/timeseries_db"):
        self.db_path = db_path
        self.hdf5_path = os.path.join(db_path, "paper_versions.h5")
        os.makedirs(db_path, exist_ok=True)
        
        # Initialize HDF5 database if not exists
        if not os.path.exists(self.hdf5_path):
            with h5py.File(self.hdf5_path, "w") as f:
                # Create root groups
                f.create_group("papers")
                f.create_group("timestamps")
                logger.info(f"Initialized time-series database at {self.hdf5_path}")
    
    async def insert_paper_version(
        self,
        paper_id: str,
        version: PaperVersion,
        timestamp: datetime
    ):
        """
        Insert paper version into time-series database
        
        Args:
            paper_id: Paper ID
            version: PaperVersion object
            timestamp: Timestamp of insertion
        """
        # Convert version to serializable dict
        version_dict = version.dict()
        
        # Convert datetime objects to ISO strings
        for key, value in version_dict.items():
            if isinstance(value, datetime):
                version_dict[key] = value.isoformat()
        
        # Generate unique timestamp key (supports 10k+ years)
        ts_key = f"{timestamp.strftime('%Y%m%d_%H%M%S_%f')}_{version.version_number}"
        
        # Open HDF5 file in append mode
        with h5py.File(self.hdf5_path, "a") as f:
            # Create paper group if not exists
            if paper_id not in f["papers"]:
                f["papers"].create_group(paper_id)
            
            # Create dataset for this version
            paper_group = f[f"papers/{paper_id}"]
            paper_group.create_dataset(
                ts_key,
                data=json.dumps(version_dict),
                dtype=h5py.string_dtype(encoding='utf-8')
            )
            
            # Also index by timestamp for time-range queries
            year = timestamp.strftime("%Y")
            if year not in f["timestamps"]:
                f["timestamps"].create_group(year)
            
            year_group = f[f"timestamps/{year}"]
            year_group.attrs[ts_key] = f"papers/{paper_id}/{ts_key}"
        
        logger.info(f"Inserted version {version.version_number} of paper {paper_id} into time-series DB")
    
    async def get_versions_by_time_range(
        self,
        paper_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get paper versions within a time range (supports 10k+ years)
        
        Args:
            paper_id: Paper ID
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            List of version dictionaries
        """
        versions = []
        
        with h5py.File(self.hdf5_path, "r") as f:
            # Check if paper exists
            if paper_id not in f["papers"]:
                logger.warning(f"Paper {paper_id} not found in time-series DB")
                return versions
            
            # Iterate through all versions of the paper
            paper_group = f[f"papers/{paper_id}"]
            for ts_key in paper_group.keys():
                # Parse timestamp from key
                try:
                    ts_str = ts_key.split("_")[0] + "_" + ts_key.split("_")[1] + "_" + ts_key.split("_")[2]
                    version_ts = datetime.strptime(ts_str, "%Y%m%d_%H%M%S_%f")
                    
                    # Check if timestamp is within range
                    if start_time <= version_ts <= end_time:
                        # Read version data
                        version_data = json.loads(paper_group[ts_key][()])
                        version_data["timestamp"] = version_ts.isoformat()
                        versions.append(version_data)
                except Exception as e:
                    logger.warning(f"Failed to parse timestamp for key {ts_key}: {str(e)}")
                    continue
        
        # Sort versions by timestamp
        versions.sort(key=lambda x: x["timestamp"])
        
        logger.info(f"Found {len(versions)} versions for paper {paper_id} in time range {start_time} to {end_time}")
        return versions
    
    async def get_all_versions(self, paper_id: str) -> List[Dict[str, Any]]:
        """
        Get all versions of a paper
        
        Args:
            paper_id: Paper ID
            
        Returns:
            List of version dictionaries
        """
        versions = []
        
        with h5py.File(self.hdf5_path, "r") as f:
            # Check if paper exists
            if paper_id not in f["papers"]:
                logger.warning(f"Paper {paper_id} not found in time-series DB")
                return versions
            
            # Iterate through all versions of the paper
            paper_group = f[f"papers/{paper_id}"]
            for ts_key in paper_group.keys():
                try:
                    # Read version data
                    version_data = json.loads(paper_group[ts_key][()])
                    versions.append(version_data)
                except Exception as e:
                    logger.warning(f"Failed to read version {ts_key}: {str(e)}")
                    continue
        
        # Sort versions by version number
        versions.sort(key=lambda x: x["version_number"])
        
        logger.info(f"Found {len(versions)} total versions for paper {paper_id}")
        return versions
    
    async def get_version_by_timestamp(
        self,
        paper_id: str,
        timestamp: datetime
    ) -> Optional[Dict[str, Any]]:
        """
        Get paper version by exact timestamp
        
        Args:
            paper_id: Paper ID
            timestamp: Exact timestamp
            
        Returns:
            Version dictionary or None if not found
        """
        # Generate timestamp key pattern
        ts_pattern = timestamp.strftime("%Y%m%d_%H%M%S_%f")
        
        with h5py.File(self.hdf5_path, "r") as f:
            # Check if paper exists
            if paper_id not in f["papers"]:
                return None
            
            # Search for matching timestamp key
            paper_group = f[f"papers/{paper_id}"]
            for ts_key in paper_group.keys():
                if ts_key.startswith(ts_pattern):
                    try:
                        version_data = json.loads(paper_group[ts_key][()])
                        return version_data
                    except Exception as e:
                        logger.warning(f"Failed to read version {ts_key}: {str(e)}")
                        return None
        
        return None