"""Encryption utilities for securing sensitive data."""
from cryptography.fernet import Fernet
import os
import base64
import logging
from typing import Optional

# Configure logging
logger = logging.getLogger("ade-encryption")

def generate_key() -> str:
    """Generate a new Fernet key."""
    return base64.urlsafe_b64encode(os.urandom(32)).decode()

def get_encryption_key() -> str:
    """Get the encryption key from environment or generate a new one.
    
    Returns:
        The encryption key as a string.
    """
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        # In production, this key should be set in environment variables
        # Generate random key only for development
        logger.warning("No encryption key found in environment. Generating random key.")
        key = generate_key()
    
    # Ensure the key is properly padded
    if isinstance(key, str):
        # Add padding if necessary
        padding = len(key) % 4
        if padding:
            key += "=" * (4 - padding)
    
    return key

# Initialize encryption key
ENCRYPTION_KEY = get_encryption_key()

try:
    # Initialize Fernet with the key
    if isinstance(ENCRYPTION_KEY, str):
        key_bytes = ENCRYPTION_KEY.encode()
    else:
        key_bytes = ENCRYPTION_KEY

    _fernet = Fernet(key_bytes)
except Exception as e:
    logger.error(f"Failed to initialize encryption: {e}")
    # Generate a new key as fallback
    logger.warning("Using fallback encryption key")
    ENCRYPTION_KEY = generate_key()
    _fernet = Fernet(ENCRYPTION_KEY.encode())

def encrypt_value(value: Optional[str]) -> str:
    """Encrypt a string value.
    
    Args:
        value: The string value to encrypt. If None or empty, returns empty string.
        
    Returns:
        The encrypted value as a string.
        
    Raises:
        Exception: If encryption fails.
    """
    if not value:
        return ""
    
    try:
        return _fernet.encrypt(value.encode()).decode()
    except Exception as e:
        logger.error(f"Encryption error: {str(e)}")
        raise

def decrypt_value(encrypted_value: Optional[str]) -> str:
    """Decrypt an encrypted string value.
    
    Args:
        encrypted_value: The encrypted string value to decrypt. If None or empty, returns empty string.
        
    Returns:
        The decrypted value as a string.
        
    Raises:
        Exception: If decryption fails.
    """
    if not encrypted_value:
        return ""
    
    try:
        return _fernet.decrypt(encrypted_value.encode()).decode()
    except Exception as e:
        logger.error(f"Decryption error: {str(e)}")
        raise

def encrypt_dict(data: dict, fields_to_encrypt: list) -> dict:
    """Encrypt specific fields in a dictionary.
    
    Args:
        data: The dictionary containing fields to encrypt.
        fields_to_encrypt: List of field names to encrypt.
        
    Returns:
        Dictionary with specified fields encrypted.
    """
    encrypted_data = data.copy()
    for field in fields_to_encrypt:
        if field in encrypted_data and encrypted_data[field]:
            encrypted_data[field] = encrypt_value(encrypted_data[field])
    return encrypted_data

def decrypt_dict(data: dict, fields_to_decrypt: list) -> dict:
    """Decrypt specific fields in a dictionary.
    
    Args:
        data: The dictionary containing fields to decrypt.
        fields_to_decrypt: List of field names to decrypt.
        
    Returns:
        Dictionary with specified fields decrypted.
    """
    decrypted_data = data.copy()
    for field in fields_to_decrypt:
        if field in decrypted_data and decrypted_data[field]:
            decrypted_data[field] = decrypt_value(decrypted_data[field])
    return decrypted_data 