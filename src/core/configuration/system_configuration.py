from typing import Dict, Any, Optional, List, Union, Type, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum
import os
import json
import yaml
import logging
import threading
import time
from pathlib import Path
from datetime import datetime
import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import jsonschema
from jsonschema import validate, ValidationError
import watchdog.observers
from watchdog.events import FileSystemEventHandler
import dotenv
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class ConfigurationError(Exception):
    """Base class for configuration errors."""
    pass

class ConfigurationValidationError(ConfigurationError):
    """Raised when configuration validation fails."""
    pass

class ConfigurationLoadError(ConfigurationError):
    """Raised when configuration loading fails."""
    pass

class SecureStorageError(ConfigurationError):
    """Raised when secure storage operations fail."""
    pass

@dataclass
class ConfigurationSchema:
    """Schema definition for configuration validation."""
    type: str
    properties: Dict[str, Any]
    required: List[str]
    additional_properties: bool = False

class SecureStorage:
    """Handles secure storage of sensitive configuration values."""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self._key = encryption_key or self._generate_key()
        self._fernet = Fernet(self._key)
        
    def _generate_key(self) -> bytes:
        """Generate encryption key using PBKDF2."""
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(os.urandom(32)))
        return key
        
    def encrypt(self, value: str) -> str:
        """Encrypt sensitive value."""
        try:
            return self._fernet.encrypt(value.encode()).decode()
        except Exception as e:
            raise SecureStorageError(f"Encryption failed: {str(e)}")
            
    def decrypt(self, encrypted_value: str) -> str:
        """Decrypt sensitive value."""
        try:
            return self._fernet.decrypt(encrypted_value.encode()).decode()
        except Exception as e:
            raise SecureStorageError(f"Decryption failed: {str(e)}")
            
    def hash_value(self, value: str) -> str:
        """Generate hash of value for comparison."""
        return hashlib.sha256(value.encode()).hexdigest()

class ConfigurationValidator:
    """Validates configuration against schema."""
    
    def __init__(self):
        self._schemas: Dict[str, ConfigurationSchema] = {}
        
    def add_schema(self, name: str, schema: ConfigurationSchema) -> None:
        """Add configuration schema."""
        self._schemas[name] = schema
        
    def validate(self, name: str, config: Dict[str, Any]) -> None:
        """Validate configuration against schema."""
        if name not in self._schemas:
            raise ConfigurationValidationError(f"Schema not found: {name}")
            
        schema = self._schemas[name]
        try:
            validate(instance=config, schema={
                "type": schema.type,
                "properties": schema.properties,
                "required": schema.required,
                "additionalProperties": schema.additional_properties
            })
        except ValidationError as e:
            raise ConfigurationValidationError(f"Validation failed: {str(e)}")

class ConfigurationWatcher(FileSystemEventHandler):
    """Watches for configuration file changes."""
    
    def __init__(self, callback: Callable[[], None]):
        self.callback = callback
        
    def on_modified(self, event):
        """Handle file modification event."""
        if not event.is_directory and event.src_path.endswith(('.yaml', '.yml', '.json')):
            self.callback()

class ConfigurationManager:
    """Manages system configuration with hot-reloading support."""
    
    def __init__(
        self,
        config_dir: str,
        environment: Environment = Environment.DEVELOPMENT,
        secure_storage: Optional[SecureStorage] = None
    ):
        self.config_dir = Path(config_dir)
        self.environment = environment
        self.secure_storage = secure_storage or SecureStorage()
        self.validator = ConfigurationValidator()
        self._config: Dict[str, Any] = {}
        self._last_load: Optional[datetime] = None
        self._lock = threading.Lock()
        self._observer = None
        self._setup_watcher()
        
    def _setup_watcher(self) -> None:
        """Setup file system watcher for hot-reloading."""
        self._observer = watchdog.observers.Observer()
        self._observer.schedule(
            ConfigurationWatcher(self.reload_configuration),
            str(self.config_dir),
            recursive=True
        )
        self._observer.start()
        
    def load_configuration(self) -> None:
        """Load configuration from files."""
        with self._lock:
            try:
                # Load environment variables
                load_dotenv()
                
                # Load base configuration
                base_config = self._load_file("base.yaml")
                
                # Load environment-specific configuration
                env_config = self._load_file(f"{self.environment.value}.yaml")
                
                # Merge configurations
                self._config = self._merge_configs(base_config, env_config)
                
                # Load secrets
                self._load_secrets()
                
                # Update last load time
                self._last_load = datetime.now()
                
                logger.info(f"Configuration loaded for environment: {self.environment.value}")
                
            except Exception as e:
                raise ConfigurationLoadError(f"Failed to load configuration: {str(e)}")
                
    def _load_file(self, filename: str) -> Dict[str, Any]:
        """Load configuration from file."""
        file_path = self.config_dir / filename
        if not file_path.exists():
            return {}
            
        with open(file_path) as f:
            if filename.endswith('.json'):
                return json.load(f)
            return yaml.safe_load(f)
            
    def _load_secrets(self) -> None:
        """Load and decrypt secrets."""
        secrets_file = self.config_dir / "secrets.yaml"
        if not secrets_file.exists():
            return
            
        with open(secrets_file) as f:
            secrets = yaml.safe_load(f)
            
        for key, value in secrets.items():
            if isinstance(value, str) and value.startswith("encrypted:"):
                encrypted_value = value[10:]  # Remove "encrypted:" prefix
                self._config[key] = self.secure_storage.decrypt(encrypted_value)
            else:
                self._config[key] = value
                
    def _merge_configs(self, base: Dict[str, Any], env: Dict[str, Any]) -> Dict[str, Any]:
        """Merge base and environment configurations."""
        merged = base.copy()
        for key, value in env.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        return merged
        
    def reload_configuration(self) -> None:
        """Reload configuration on file changes."""
        logger.info("Configuration change detected, reloading...")
        self.load_configuration()
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)
        
    def set(self, key: str, value: Any, encrypt: bool = False) -> None:
        """Set configuration value with optional encryption."""
        with self._lock:
            if encrypt and isinstance(value, str):
                value = f"encrypted:{self.secure_storage.encrypt(value)}"
            self._config[key] = value
            
    def validate(self, schema_name: str) -> None:
        """Validate current configuration against schema."""
        self.validator.validate(schema_name, self._config)
        
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self._config.copy()
        
    def get_environment(self) -> Environment:
        """Get current environment."""
        return self.environment
        
    def get_last_load(self) -> Optional[datetime]:
        """Get last configuration load time."""
        return self._last_load
        
    def close(self) -> None:
        """Clean up resources."""
        if self._observer:
            self._observer.stop()
            self._observer.join()

class ConfigurationBuilder:
    """Builder for creating configuration schemas."""
    
    @staticmethod
    def create_schema(
        properties: Dict[str, Any],
        required: List[str],
        additional_properties: bool = False
    ) -> ConfigurationSchema:
        """Create configuration schema."""
        return ConfigurationSchema(
            type="object",
            properties=properties,
            required=required,
            additional_properties=additional_properties
        )
        
    @staticmethod
    def string_property(description: str = "") -> Dict[str, Any]:
        """Create string property definition."""
        return {
            "type": "string",
            "description": description
        }
        
    @staticmethod
    def number_property(description: str = "") -> Dict[str, Any]:
        """Create number property definition."""
        return {
            "type": "number",
            "description": description
        }
        
    @staticmethod
    def boolean_property(description: str = "") -> Dict[str, Any]:
        """Create boolean property definition."""
        return {
            "type": "boolean",
            "description": description
        }
        
    @staticmethod
    def array_property(items: Dict[str, Any], description: str = "") -> Dict[str, Any]:
        """Create array property definition."""
        return {
            "type": "array",
            "items": items,
            "description": description
        }
        
    @staticmethod
    def object_property(properties: Dict[str, Any], required: List[str], description: str = "") -> Dict[str, Any]:
        """Create object property definition."""
        return {
            "type": "object",
            "properties": properties,
            "required": required,
            "description": description
        } 