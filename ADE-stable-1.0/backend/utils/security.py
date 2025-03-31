import secrets
import hashlib
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import json
import base64
from ..config.settings import settings
from ..config.logging_config import logger

logger = logging.getLogger(__name__)

# Initialize encryption key
try:
    encryption_key = settings.ENCRYPTION_KEY.encode()
    fernet = Fernet(encryption_key)
except Exception as e:
    logger.error(f"Error initializing encryption: {str(e)}")
    raise

def generate_api_key(length: int = 32) -> str:
    """Generate a secure API key"""
    try:
        return secrets.token_urlsafe(length)
    except Exception as e:
        logger.error(f"Error generating API key: {str(e)}")
        raise

def hash_api_key(key: str) -> str:
    """Hash an API key for storage"""
    try:
        return hashlib.sha256(key.encode()).hexdigest()
    except Exception as e:
        logger.error(f"Error hashing API key: {str(e)}")
        raise

def verify_api_key(key: str, hashed_key: str) -> bool:
    """Verify an API key against its hash"""
    try:
        return hash_api_key(key) == hashed_key
    except Exception as e:
        logger.error(f"Error verifying API key: {str(e)}")
        raise

def generate_password_hash(password: str) -> str:
    """Generate a secure password hash"""
    try:
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256()
        hash_obj.update(salt.encode())
        hash_obj.update(password.encode())
        return f"{salt}:{hash_obj.hexdigest()}"
    except Exception as e:
        logger.error(f"Error generating password hash: {str(e)}")
        raise

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    try:
        salt, stored_hash = password_hash.split(':')
        hash_obj = hashlib.sha256()
        hash_obj.update(salt.encode())
        hash_obj.update(password.encode())
        return hash_obj.hexdigest() == stored_hash
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        raise

def generate_session_token() -> str:
    """Generate a secure session token"""
    try:
        return secrets.token_urlsafe(32)
    except Exception as e:
        logger.error(f"Error generating session token: {str(e)}")
        raise

def validate_password_strength(password: str) -> Dict[str, bool]:
    """Validate password strength requirements"""
    try:
        return {
            "length": len(password) >= 8,
            "uppercase": any(c.isupper() for c in password),
            "lowercase": any(c.islower() for c in password),
            "numbers": any(c.isdigit() for c in password),
            "special": any(not c.isalnum() for c in password)
        }
    except Exception as e:
        logger.error(f"Error validating password strength: {str(e)}")
        raise

def generate_mfa_secret() -> str:
    """Generate a secret for MFA"""
    try:
        return secrets.token_hex(20)
    except Exception as e:
        logger.error(f"Error generating MFA secret: {str(e)}")
        raise

def validate_ip_whitelist(ip_address: str, whitelist: List[str]) -> bool:
    """Validate if an IP address is in the whitelist"""
    try:
        return ip_address in whitelist
    except Exception as e:
        logger.error(f"Error validating IP whitelist: {str(e)}")
        raise

def generate_csrf_token() -> str:
    """Generate a CSRF token"""
    try:
        return secrets.token_urlsafe(32)
    except Exception as e:
        logger.error(f"Error generating CSRF token: {str(e)}")
        raise

def validate_csrf_token(token: str, stored_token: str) -> bool:
    """Validate a CSRF token"""
    try:
        return secrets.compare_digest(token, stored_token)
    except Exception as e:
        logger.error(f"Error validating CSRF token: {str(e)}")
        raise

def generate_password_reset_token() -> str:
    """Generate a password reset token"""
    try:
        return secrets.token_urlsafe(32)
    except Exception as e:
        logger.error(f"Error generating password reset token: {str(e)}")
        raise

def validate_password_reset_token(token: str, stored_token: str, expiry: datetime) -> bool:
    """Validate a password reset token"""
    try:
        if datetime.utcnow() > expiry:
            return False
        return secrets.compare_digest(token, stored_token)
    except Exception as e:
        logger.error(f"Error validating password reset token: {str(e)}")
        raise

def generate_verification_code() -> str:
    """Generate a verification code for email/phone verification"""
    try:
        return ''.join(secrets.choice('0123456789') for _ in range(6))
    except Exception as e:
        logger.error(f"Error generating verification code: {str(e)}")
        raise

def validate_verification_code(code: str, stored_code: str, expiry: datetime) -> bool:
    """Validate a verification code"""
    try:
        if datetime.utcnow() > expiry:
            return False
        return secrets.compare_digest(code, stored_code)
    except Exception as e:
        logger.error(f"Error validating verification code: {str(e)}")
        raise

def generate_remember_me_token() -> str:
    """Generate a remember me token"""
    try:
        return secrets.token_urlsafe(32)
    except Exception as e:
        logger.error(f"Error generating remember me token: {str(e)}")
        raise

def validate_remember_me_token(token: str, stored_token: str, expiry: datetime) -> bool:
    """Validate a remember me token"""
    try:
        if datetime.utcnow() > expiry:
            return False
        return secrets.compare_digest(token, stored_token)
    except Exception as e:
        logger.error(f"Error validating remember me token: {str(e)}")
        raise

def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data using Fernet symmetric encryption"""
    try:
        return fernet.encrypt(data.encode()).decode()
    except Exception as e:
        logger.error(f"Error encrypting data: {str(e)}")
        raise

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data using Fernet symmetric encryption"""
    try:
        return fernet.decrypt(encrypted_data.encode()).decode()
    except Exception as e:
        logger.error(f"Error decrypting data: {str(e)}")
        raise

def validate_notification_data(notification: Any) -> bool:
    """Validate notification data for security and integrity"""
    try:
        # Check for malicious content in title and message
        if not notification.title or len(notification.title) > 255:
            raise ValueError("Invalid title length")
        
        if not notification.message or len(notification.message) > 5000:
            raise ValueError("Invalid message length")

        # Validate metadata structure
        if notification.metadata:
            if not isinstance(notification.metadata, dict):
                raise ValueError("Metadata must be a dictionary")
            
            # Check metadata size
            metadata_size = len(json.dumps(notification.metadata))
            if metadata_size > 10000:  # 10KB limit
                raise ValueError("Metadata too large")

            # Validate action URL if present
            if "action_url" in notification.metadata:
                if not isinstance(notification.metadata["action_url"], str):
                    raise ValueError("Action URL must be a string")
                if len(notification.metadata["action_url"]) > 512:
                    raise ValueError("Action URL too long")

        # Validate priority
        if notification.priority not in ["low", "medium", "high", "urgent"]:
            raise ValueError("Invalid priority level")

        # Validate type
        if notification.type not in ["system", "security", "user", "support", "marketplace", "deployment"]:
            raise ValueError("Invalid notification type")

        return True
    except Exception as e:
        logger.error(f"Error validating notification data: {str(e)}")
        raise

def sanitize_input(data: str) -> str:
    """Sanitize input data to prevent XSS and injection attacks"""
    try:
        # Remove potentially dangerous characters
        sanitized = data.replace("<", "&lt;").replace(">", "&gt;")
        sanitized = sanitized.replace("'", "&#39;").replace('"', "&quot;")
        sanitized = sanitized.replace("&", "&amp;")
        return sanitized
    except Exception as e:
        logger.error(f"Error sanitizing input: {str(e)}")
        raise

def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    try:
        return base64.urlsafe_b64encode(fernet.generate_key()).decode()[:length]
    except Exception as e:
        logger.error(f"Error generating secure token: {str(e)}")
        raise

def validate_api_key(api_key: str) -> bool:
    """Validate API key format and structure"""
    try:
        # Check length
        if len(api_key) != 64:
            return False

        # Check format (should be base64url encoded)
        try:
            base64.urlsafe_b64decode(api_key)
            return True
        except:
            return False
    except Exception as e:
        logger.error(f"Error validating API key: {str(e)}")
        return False 