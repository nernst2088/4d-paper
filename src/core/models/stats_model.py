from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class PaperStats(BaseModel):
    paper_id: str
    view_count: int = Field(default=0)
    download_count: int = Field(default=0)
    last_view_time: Optional[datetime] = None
    last_download_time: Optional[datetime] = None

class PaperAccessPermission(BaseModel):
    paper_id: str
    allow_download: bool = Field(default=False)
    allow_discussion: bool = Field(default=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)