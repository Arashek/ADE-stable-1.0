from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import re
from ..config.logging_config import logger

class ValidationError(Exception):
    """Exception raised when validation fails"""
    pass

def validate_email(email: str) -> bool:
    """Validate email format"""
    try:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    except Exception as e:
        logger.error(f"Error validating email: {str(e)}")
        raise

def validate_password(password: str) -> bool:
    """
    Validate password strength
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """
    try:
        if len(password) < 8:
            return False
        
        if not re.search(r'[A-Z]', password):
            return False
            
        if not re.search(r'[a-z]', password):
            return False
            
        if not re.search(r'\d', password):
            return False
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error validating password: {str(e)}")
        raise

def validate_username(username: str) -> bool:
    """
    Validate username format
    Requirements:
    - 3-30 characters
    - Alphanumeric and underscores only
    - Must start with a letter
    """
    try:
        pattern = r'^[a-zA-Z][a-zA-Z0-9_]{2,29}$'
        return bool(re.match(pattern, username))
    except Exception as e:
        logger.error(f"Error validating username: {str(e)}")
        raise

def validate_url(url: str) -> bool:
    """Validate URL format"""
    try:
        pattern = r'^https?://(?:[\w-]|(?=%[\da-fA-F]{2}))+[^\s]*$'
        return bool(re.match(pattern, url))
    except Exception as e:
        logger.error(f"Error validating URL: {str(e)}")
        raise

def validate_date(date_str: str) -> bool:
    """Validate date format (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False
    except Exception as e:
        logger.error(f"Error validating date: {str(e)}")
        raise

def validate_datetime(datetime_str: str) -> bool:
    """Validate datetime format (ISO 8601)"""
    try:
        datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False
    except Exception as e:
        logger.error(f"Error validating datetime: {str(e)}")
        raise

def validate_json(data: str) -> bool:
    """Validate JSON string format"""
    try:
        import json
        json.loads(data)
        return True
    except json.JSONDecodeError:
        return False
    except Exception as e:
        logger.error(f"Error validating JSON: {str(e)}")
        raise

def validate_phone_number(phone: str) -> bool:
    """Validate phone number format (E.164)"""
    try:
        pattern = r'^\+[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone))
    except Exception as e:
        logger.error(f"Error validating phone number: {str(e)}")
        raise

def validate_ip_address(ip: str) -> bool:
    """Validate IP address format (IPv4 or IPv6)"""
    try:
        import ipaddress
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False
    except Exception as e:
        logger.error(f"Error validating IP address: {str(e)}")
        raise

def validate_file_size(size_bytes: int, max_size_mb: int = 10) -> bool:
    """Validate file size is within limits"""
    try:
        max_size_bytes = max_size_mb * 1024 * 1024
        return size_bytes <= max_size_bytes
    except Exception as e:
        logger.error(f"Error validating file size: {str(e)}")
        raise

def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
    """Validate file extension is in allowed types"""
    try:
        extension = filename.lower().split('.')[-1]
        return extension in allowed_types
    except Exception as e:
        logger.error(f"Error validating file type: {str(e)}")
        raise

def sanitize_html(html: str) -> str:
    """Sanitize HTML content to prevent XSS attacks"""
    try:
        from bleach import clean
        return clean(html, tags=[], attributes={})
    except Exception as e:
        logger.error(f"Error sanitizing HTML: {str(e)}")
        raise

def validate_metadata(metadata: Dict[str, Any]) -> bool:
    """
    Validate metadata structure and content
    Requirements:
    - Must be a dictionary
    - Keys must be strings
    - Values must be basic types (str, int, float, bool, list, dict)
    - Maximum depth of 3 levels
    - Maximum size of 10KB
    """
    try:
        if not isinstance(metadata, dict):
            return False
            
        def check_value(value: Any, depth: int = 0) -> bool:
            if depth > 3:
                return False
                
            if isinstance(value, (str, int, float, bool)):
                return True
                
            if isinstance(value, list):
                return all(check_value(item, depth + 1) for item in value)
                
            if isinstance(value, dict):
                return all(
                    isinstance(k, str) and check_value(v, depth + 1)
                    for k, v in value.items()
                )
                
            return False
            
        if not all(isinstance(k, str) and check_value(v) for k, v in metadata.items()):
            return False
            
        # Check size
        import json
        size = len(json.dumps(metadata))
        if size > 10 * 1024:  # 10KB
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error validating metadata: {str(e)}")
        raise

def validate_pagination_params(
    page: int,
    page_size: int,
    max_page_size: int = 100
) -> bool:
    """Validate pagination parameters"""
    try:
        if page < 1:
            return False
        if page_size < 1 or page_size > max_page_size:
            return False
        return True
    except Exception as e:
        logger.error(f"Error validating pagination params: {str(e)}")
        raise 