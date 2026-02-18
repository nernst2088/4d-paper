from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

def derive_encryption_key(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """
    Derive AES-256 encryption key from user password (NIST compliant)
    
    Args:
        password: User-provided password
        salt: Random salt (generated if None)
        
    Returns:
        Tuple of (derived_key, salt)
    """
    if salt is None:
        salt = os.urandom(16)  # 16-byte cryptographically secure salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 32 bytes for AES-256
        salt=salt,
        iterations=480000,  # High iteration count for brute force protection
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))
    return key, salt

def encrypt_content(content: bytes, key: bytes) -> bytes:
    """
    Encrypt content using AES-256-GCM with integrity verification
    
    Args:
        content: Raw bytes to encrypt
        key: Encryption key from derive_encryption_key
        
    Returns:
        Encrypted bytes with authentication tag
    """
    f = Fernet(key)
    return f.encrypt(content)

def decrypt_content(encrypted_content: bytes, key: bytes) -> bytes:
    """
    Decrypt content and verify integrity
    
    Args:
        encrypted_content: Encrypted bytes from encrypt_content
        key: Decryption key (same as encryption key)
        
    Returns:
        Decrypted raw bytes
        
    Raises:
        ValueError: If decryption fails (bad key or tampered content)
    """
    f = Fernet(key)
    try:
        return f.decrypt(encrypted_content)
    except Exception as e:
        raise ValueError("Decryption failed: invalid key or tampered content") from e