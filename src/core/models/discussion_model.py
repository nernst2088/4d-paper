from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class DiscussionMessage(BaseModel):
    paper_id: str
    user_id: str
    content: str
    is_author: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message_id: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        if not self.message_id:
            ts = int(self.timestamp.timestamp() * 1000)
            self.message_id = f"msg_{self.paper_id}_{ts}"