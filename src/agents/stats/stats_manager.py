import os
import json
from datetime import datetime
import logging
from src.core.models.stats_model import PaperStats, PaperAccessPermission

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StatsManager")

class StatsManager:
    """Manager for paper view/download statistics and access permissions"""
    
    def __init__(self, storage_path="./storage/stats"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    def _stats_path(self, paper_id: str) -> str:
        """Get path to paper statistics file"""
        return os.path.join(self.storage_path, f"{paper_id}_stats.json")

    def _perm_path(self, paper_id: str) -> str:
        """Get path to paper access permission file"""
        return os.path.join(self.storage_path, f"{paper_id}_perm.json")

    # ------------------------------
    # View Count Related
    # ------------------------------
    def increment_view(self, paper_id: str):
        """
        Increment paper view count
        
        Args:
            paper_id: Paper ID
        """
        stats = self.get_stats(paper_id)
        stats.view_count += 1
        stats.last_view_time = datetime.utcnow()
        self._save_stats(stats)
        logger.info(f"Incremented view count for paper {paper_id} (total: {stats.view_count})")

    def get_stats(self, paper_id: str) -> PaperStats:
        """
        Get paper statistics
        
        Args:
            paper_id: Paper ID
            
        Returns:
            PaperStats object
        """
        path = self._stats_path(paper_id)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                stats_data = json.load(f)
                # Convert timestamps back to datetime
                if stats_data.get("last_view_time"):
                    stats_data["last_view_time"] = datetime.fromisoformat(stats_data["last_view_time"])
                if stats_data.get("last_download_time"):
                    stats_data["last_download_time"] = datetime.fromisoformat(stats_data["last_download_time"])
                return PaperStats(**stats_data)
        # Return empty stats if none exist
        return PaperStats(paper_id=paper_id)

    def _save_stats(self, stats: PaperStats):
        """
        Save paper statistics
        
        Args:
            stats: PaperStats object
        """
        with open(self._stats_path(stats.paper_id), "w", encoding="utf-8") as f:
            json.dump(stats.dict(), f, indent=2, default=str)

    # ------------------------------
    # Download Permission + Download Count Related
    # ------------------------------
    def set_download_permission(self, paper_id: str, allow: bool):
        """
        Set paper download permission (author-controlled)
        
        Args:
            paper_id: Paper ID
            allow: Whether to allow downloads (default: False)
        """
        perm = PaperAccessPermission(
            paper_id=paper_id,
            allow_download=allow,
            updated_at=datetime.utcnow()
        )
        with open(self._perm_path(paper_id), "w", encoding="utf-8") as f:
            json.dump(perm.dict(), f, indent=2, default=str)
        logger.info(f"Set download permission for paper {paper_id} to: {allow}")

    def can_download(self, paper_id: str) -> bool:
        """
        Check if paper can be downloaded
        
        Args:
            paper_id: Paper ID
            
        Returns:
            True if download is allowed, False otherwise (default: False)
        """
        path = self._perm_path(paper_id)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                perm_data = json.load(f)
                perm = PaperAccessPermission(**perm_data)
                return perm.allow_download
        return False

    def increment_download(self, paper_id: str):
        """
        Increment paper download count
        
        Args:
            paper_id: Paper ID
        """
        # Check if download is allowed
        if not self.can_download(paper_id):
            raise PermissionError(f"Download not allowed for paper {paper_id}")
        
        stats = self.get_stats(paper_id)
        stats.download_count += 1
        stats.last_download_time = datetime.utcnow()
        self._save_stats(stats)
        logger.info(f"Incremented download count for paper {paper_id} (total: {stats.download_count})")