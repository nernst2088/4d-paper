import os
from typing import Optional
import logging
from src.core.security.encryption import derive_encryption_key, encrypt_content, decrypt_content

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DataEncryptionService")

class DataEncryptionService:
    """Service for encrypting/decrypting research data and papers"""
    
    def __init__(self, salt_storage_path: str = "./storage/salt"):
        self.salt_storage_path = salt_storage_path
        os.makedirs(salt_storage_path, exist_ok=True)
    
    def get_user_encryption_key(self, user_id: str, password: str) -> bytes:
        """
        Get or create encryption key for user
        
        Args:
            user_id: User ID
            password: User password
            
        Returns:
            Encryption key
        """
        salt_path = os.path.join(self.salt_storage_path, f"{user_id}.salt")
        
        # Load existing salt or generate new one
        if os.path.exists(salt_path):
            with open(salt_path, "rb") as f:
                salt = f.read()
        else:
            # Generate and save new salt
            key, salt = derive_encryption_key(password)
            with open(salt_path, "wb") as f:
                f.write(salt)
            return key
        
        # Derive key with existing salt
        key, _ = derive_encryption_key(password, salt)
        return key
    
    def encrypt_file(self, file_path: str, key: bytes, output_path: Optional[str] = None) -> str:
        """
        Encrypt a file
        
        Args:
            file_path: Path to file to encrypt
            key: Encryption key
            output_path: Output path (defaults to file_path + .enc)
            
        Returns:
            Path to encrypted file
        """
        if output_path is None:
            output_path = f"{file_path}.enc"
        
        # Read file content
        with open(file_path, "rb") as f:
            content = f.read()
        
        # Encrypt content
        encrypted_content = encrypt_content(content, key)
        
        # Save encrypted content
        with open(output_path, "wb") as f:
            f.write(encrypted_content)
        
        logger.info(f"File encrypted: {file_path} -> {output_path}")
        return output_path
    
    def decrypt_file(self, encrypted_path: str, key: bytes, output_path: Optional[str] = None) -> str:
        """
        Decrypt a file
        
        Args:
            encrypted_path: Path to encrypted file
            key: Decryption key
            output_path: Output path (defaults to encrypted_path without .enc)
            
        Returns:
            Path to decrypted file
        """
        if output_path is None:
            if encrypted_path.endswith(".enc"):
                output_path = encrypted_path[:-4]
            else:
                output_path = f"{encrypted_path}.dec"
        
        # Read encrypted content
        with open(encrypted_path, "rb") as f:
            encrypted_content = f.read()
        
        # Decrypt content
        decrypted_content = decrypt_content(encrypted_content, key)
        
        # Save decrypted content
        with open(output_path, "wb") as f:
            f.write(decrypted_content)
        
        logger.info(f"File decrypted: {encrypted_path} -> {output_path}")
        return output_path