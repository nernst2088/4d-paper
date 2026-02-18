import hashlib
from typing import Any

def calculate_data_hash(data: Any) -> str:
    """
    Calculate SHA-256 hash of any data type
    
    Args:
        data: Data to hash (str, bytes, dict, list, etc.)
        
    Returns:
        Hexadecimal SHA-256 hash string
    """
    if isinstance(data, str):
        data_bytes = data.encode("utf-8")
    elif isinstance(data, bytes):
        data_bytes = data
    else:
        # Convert complex types to string representation
        data_bytes = str(data).encode("utf-8")
    
    return hashlib.sha256(data_bytes).hexdigest()

def hash_password(password: str) -> str:
    """
    Hash password using SHA-256 (for user authentication)
    
    Args:
        password: Plain text password
        
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return hash_password(plain_password) == hashed_password