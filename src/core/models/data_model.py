from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from src.core.models.paper_model import SpaceCoordinate

class DataIngestionRequest(BaseModel):
    """Request model for data ingestion"""
    user_id: str
    paper_id: str
    data_path: str
    data_type: str = Field(default="tabular")
    description: Optional[str] = ""
    space_coordinate: Optional[SpaceCoordinate] = None

class DataIngestionResponse(BaseModel):
    """Response model for data ingestion"""
    data_id: str
    data_hash: str
    data_type: str
    storage_path: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    success: bool = True