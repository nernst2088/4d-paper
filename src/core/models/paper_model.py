from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import hashlib

class SpaceCoordinate(BaseModel):
    """Spatial coordinate model supporting multiple coordinate systems"""
    latitude: float = Field(description="Latitude in decimal degrees")
    longitude: float = Field(description="Longitude in decimal degrees")
    altitude: Optional[float] = Field(default=0.0, description="Altitude in meters above sea level")
    coordinate_system: str = Field(default="WGS84", description="Coordinate reference system")

class FourDDataReference(BaseModel):
    """4D data reference model (3D spatial + time dimension)"""
    data_id: str = Field(description="Unique identifier for the data")
    timestamp: datetime = Field(description="Timestamp when data was recorded")
    space_coordinate: Optional[SpaceCoordinate] = Field(default=None, description="Spatial coordinates of data collection")
    data_hash: str = Field(description="SHA-256 hash of the raw data")
    data_type: str = Field(description="Type of data: table/3d_model/video/audio/etc")
    description: Optional[str] = Field(default="", description="Human-readable data description")

class PaperVersion(BaseModel):
    """Paper version model for version control"""
    version_id: str = Field(description="Unique version identifier")
    version_number: int = Field(description="Sequential version number")
    create_time: datetime = Field(default_factory=datetime.utcnow, description="Version creation time (UTC)")
    update_reason: str = Field(description="Reason for this version update")
    four_d_data_references: List[FourDDataReference] = Field(description="4D data references for this version")
    paper_content_hash: str = Field(description="SHA-256 hash of paper content")
    author_team: List[str] = Field(description="Author user IDs for this version")
    space_context: Optional[SpaceCoordinate] = Field(default=None, description="Spatial context of this version creation")

class DynamicPaper(BaseModel):
    """Core dynamic paper model supporting 4D/multi-dimensional data"""
    paper_id: str = Field(description="Unique paper identifier")
    title: str = Field(description="Paper title")
    research_purpose: str = Field(description="Core research objective")
    creator: str = Field(description="Original creator user ID")
    create_time: datetime = Field(default_factory=datetime.utcnow, description="Paper creation time (UTC)")
    latest_version: int = Field(default=1, description="Latest version number")
    versions: List[PaperVersion] = Field(default=[], description="Complete version history")
    is_encrypted: bool = Field(default=True, description="Whether paper is stored encrypted")
    access_permissions: Dict[str, str] = Field(default={}, description="Permissions: user_id -> permission level (read/write/admin)")
    long_term_tracking: bool = Field(default=True, description="Enable long-term (10k+ years) tracking")

    def generate_paper_hash(self, version_content: str) -> str:
        """Generate SHA-256 hash for paper content to prevent tampering"""
        return hashlib.sha256(version_content.encode("utf-8")).hexdigest()

    def add_new_version(self, version: PaperVersion):
        """Add new version (enforces sequential version numbering)"""
        if version.version_number != self.latest_version + 1:
            raise ValueError(f"Invalid version number: expected {self.latest_version + 1}, got {version.version_number}")
        self.versions.append(version)
        self.latest_version = version.version_number