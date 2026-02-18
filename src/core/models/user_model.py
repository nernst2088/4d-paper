from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class User(BaseModel):
    """User model for authentication and authorization"""
    user_id: str
    username: str
    email: str
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    papers: List[str] = Field(default=[], description="List of paper IDs owned by user")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None