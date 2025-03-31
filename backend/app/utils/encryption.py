"""Encryption utilities."""
import os
from cryptography.fernet import Fernet
from base64 import b64encode, b64decode

# Get encryption key from environment or generate one
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
_fernet = Fernet(ENCRYPTION_KEY)

def encrypt_value(value: str) -> str:
    """Encrypt a string value."""
    if not value:
        return ""
    return b64encode(_fernet.encrypt(value.encode())).decode()

def decrypt_value(encrypted_value: str) -> str:
    """Decrypt an encrypted string value."""
    if not encrypted_value:
        return ""
    try:
        return _fernet.decrypt(b64decode(encrypted_value)).decode()
    except Exception:
        return "" 