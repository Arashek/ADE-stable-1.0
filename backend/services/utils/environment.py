import os
import logging
import json
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class EnvironmentManager:
    """
    Utility class for managing environment variables and runtime configurations
    """
    
    def __init__(self, env_file: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.env_file = env_file
        self._env_vars = {}
        self._runtime_configs = {}
        
        # Load environment variables from file if provided
        if env_file:
            self.load_env_file(env_file)
            
        # Load environment variables from OS
        self._load_os_env_vars()
        
    def load_env_file(self, env_file: str) -> bool:
        """
        Load environment variables from a .env file
        
        Args:
            env_file: Path to the .env file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Loading environment variables from {env_file}")
            
            if not os.path.exists(env_file):
                self.logger.warning(f"Environment file not found: {env_file}")
                return False
                
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                        
                    key_value = line.split("=", 1)
                    if len(key_value) != 2:
                        continue
                        
                    key, value = key_value
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                        
                    self._env_vars[key] = value
                    
            return True
                
        except Exception as e:
            self.logger.error(f"Error loading environment file: {str(e)}")
            return False
            
    def _load_os_env_vars(self) -> None:
        """Load environment variables from the OS"""
        for key, value in os.environ.items():
            if key not in self._env_vars:  # Don't override loaded .env values
                self._env_vars[key] = value
                
    def get_env(self, key: str, default: Any = None) -> Any:
        """
        Get an environment variable
        
        Args:
            key: The environment variable key
            default: Default value if the key doesn't exist
            
        Returns:
            The environment variable value or default
        """
        return self._env_vars.get(key, os.environ.get(key, default))
        
    def set_env(self, key: str, value: str) -> None:
        """
        Set an environment variable (runtime only, doesn't modify OS env)
        
        Args:
            key: The environment variable key
            value: The value to set
        """
        self._env_vars[key] = value
        
    def get_boolean(self, key: str, default: bool = False) -> bool:
        """
        Get a boolean environment variable
        
        Args:
            key: The environment variable key
            default: Default value if the key doesn't exist
            
        Returns:
            Boolean value of the environment variable
        """
        value = self.get_env(key)
        if value is None:
            return default
            
        return value.lower() in ("true", "1", "yes", "y", "t")
        
    def get_int(self, key: str, default: int = 0) -> int:
        """
        Get an integer environment variable
        
        Args:
            key: The environment variable key
            default: Default value if the key doesn't exist
            
        Returns:
            Integer value of the environment variable
        """
        value = self.get_env(key)
        if value is None:
            return default
            
        try:
            return int(value)
        except ValueError:
            return default
            
    def get_float(self, key: str, default: float = 0.0) -> float:
        """
        Get a float environment variable
        
        Args:
            key: The environment variable key
            default: Default value if the key doesn't exist
            
        Returns:
            Float value of the environment variable
        """
        value = self.get_env(key)
        if value is None:
            return default
            
        try:
            return float(value)
        except ValueError:
            return default
            
    def get_list(self, key: str, default: List = None, separator: str = ",") -> List:
        """
        Get a list environment variable
        
        Args:
            key: The environment variable key
            default: Default value if the key doesn't exist
            separator: The separator to split the list
            
        Returns:
            List value of the environment variable
        """
        if default is None:
            default = []
            
        value = self.get_env(key)
        if value is None:
            return default
            
        return [item.strip() for item in value.split(separator)]
        
    def get_json(self, key: str, default: Any = None) -> Any:
        """
        Get a JSON environment variable
        
        Args:
            key: The environment variable key
            default: Default value if the key doesn't exist
            
        Returns:
            Parsed JSON value of the environment variable
        """
        value = self.get_env(key)
        if value is None:
            return default
            
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return default
            
    def load_config_file(self, config_file: str) -> bool:
        """
        Load a configuration file into runtime config
        
        Args:
            config_file: Path to the configuration file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Loading configuration from {config_file}")
            
            if not os.path.exists(config_file):
                self.logger.warning(f"Configuration file not found: {config_file}")
                return False
                
            # Determine file type from extension
            ext = os.path.splitext(config_file)[1].lower()
            
            if ext == ".json":
                with open(config_file, "r") as f:
                    config = json.load(f)
                    self._runtime_configs.update(config)
                    return True
            elif ext in (".yaml", ".yml"):
                try:
                    import yaml
                    with open(config_file, "r") as f:
                        config = yaml.safe_load(f)
                        self._runtime_configs.update(config)
                        return True
                except ImportError:
                    self.logger.error("PyYAML is not installed. Cannot load YAML config.")
                    return False
            else:
                self.logger.warning(f"Unsupported configuration file format: {ext}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error loading configuration file: {str(e)}")
            return False
            
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get a runtime configuration value
        
        Args:
            key: The configuration key (dot notation supported)
            default: Default value if the key doesn't exist
            
        Returns:
            The configuration value or default
        """
        if "." in key:
            # Handle nested keys
            keys = key.split(".")
            value = self._runtime_configs
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
                    
            return value
        else:
            return self._runtime_configs.get(key, default)
            
    def set_config(self, key: str, value: Any) -> None:
        """
        Set a runtime configuration value
        
        Args:
            key: The configuration key (dot notation supported)
            value: The value to set
        """
        if "." in key:
            # Handle nested keys
            keys = key.split(".")
            config = self._runtime_configs
            
            # Navigate to the correct dict
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                elif not isinstance(config[k], dict):
                    # If the existing value is not a dict, replace it
                    config[k] = {}
                    
                config = config[k]
                
            # Set the value
            config[keys[-1]] = value
        else:
            self._runtime_configs[key] = value
            
    def save_config_file(self, config_file: str, format: str = "json") -> bool:
        """
        Save runtime configuration to a file
        
        Args:
            config_file: Path to the configuration file
            format: Format to save in (json or yaml)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Saving configuration to {config_file}")
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(config_file)), exist_ok=True)
            
            format = format.lower()
            
            if format == "json":
                with open(config_file, "w") as f:
                    json.dump(self._runtime_configs, f, indent=2)
                    return True
            elif format == "yaml":
                try:
                    import yaml
                    with open(config_file, "w") as f:
                        yaml.dump(self._runtime_configs, f)
                        return True
                except ImportError:
                    self.logger.error("PyYAML is not installed. Cannot save YAML config.")
                    return False
            else:
                self.logger.warning(f"Unsupported configuration file format: {format}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error saving configuration file: {str(e)}")
            return False
            
    def get_all_env_vars(self) -> Dict[str, str]:
        """
        Get all environment variables
        
        Returns:
            Dictionary of all environment variables
        """
        return self._env_vars.copy()
        
    def get_all_configs(self) -> Dict[str, Any]:
        """
        Get all runtime configurations
        
        Returns:
            Dictionary of all runtime configurations
        """
        return self._runtime_configs.copy()
        
    def get_runtime_env(self) -> str:
        """
        Get the current runtime environment (development, testing, production)
        
        Returns:
            The runtime environment
        """
        return self.get_env("ENV", "development").lower()
        
    def is_development(self) -> bool:
        """Check if runtime environment is development"""
        return self.get_runtime_env() in ("dev", "development")
        
    def is_testing(self) -> bool:
        """Check if runtime environment is testing"""
        return self.get_runtime_env() in ("test", "testing")
        
    def is_production(self) -> bool:
        """Check if runtime environment is production"""
        return self.get_runtime_env() in ("prod", "production")
        
    def get_log_level(self) -> str:
        """Get the current log level"""
        return self.get_env("LOG_LEVEL", "INFO").upper()
        
    def set_log_level(self, level: str) -> None:
        """
        Set the log level
        
        Args:
            level: The log level to set
        """
        level = level.upper()
        self.set_env("LOG_LEVEL", level)
        
        # Update root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)


# Global instance
_env_manager = None

def get_environment_manager(env_file: Optional[str] = None) -> EnvironmentManager:
    """
    Get the global environment manager instance
    
    Args:
        env_file: Path to the .env file
        
    Returns:
        EnvironmentManager instance
    """
    global _env_manager
    
    if _env_manager is None:
        _env_manager = EnvironmentManager(env_file)
        
    return _env_manager

def get_env(key: str, default: Any = None) -> Any:
    """
    Get an environment variable
    
    Args:
        key: The environment variable key
        default: Default value if the key doesn't exist
        
    Returns:
        The environment variable value or default
    """
    return get_environment_manager().get_env(key, default)

def get_boolean(key: str, default: bool = False) -> bool:
    """
    Get a boolean environment variable
    
    Args:
        key: The environment variable key
        default: Default value if the key doesn't exist
        
    Returns:
        Boolean value of the environment variable
    """
    return get_environment_manager().get_boolean(key, default)

def get_int(key: str, default: int = 0) -> int:
    """
    Get an integer environment variable
    
    Args:
        key: The environment variable key
        default: Default value if the key doesn't exist
        
    Returns:
        Integer value of the environment variable
    """
    return get_environment_manager().get_int(key, default)

def get_float(key: str, default: float = 0.0) -> float:
    """
    Get a float environment variable
    
    Args:
        key: The environment variable key
        default: Default value if the key doesn't exist
        
    Returns:
        Float value of the environment variable
    """
    return get_environment_manager().get_float(key, default)

def get_list(key: str, default: List = None, separator: str = ",") -> List:
    """
    Get a list environment variable
    
    Args:
        key: The environment variable key
        default: Default value if the key doesn't exist
        separator: The separator to split the list
        
    Returns:
        List value of the environment variable
    """
    return get_environment_manager().get_list(key, default, separator)

def get_json(key: str, default: Any = None) -> Any:
    """
    Get a JSON environment variable
    
    Args:
        key: The environment variable key
        default: Default value if the key doesn't exist
        
    Returns:
        Parsed JSON value of the environment variable
    """
    return get_environment_manager().get_json(key, default)

def get_runtime_env() -> str:
    """
    Get the current runtime environment (development, testing, production)
    
    Returns:
        The runtime environment
    """
    return get_environment_manager().get_runtime_env()

def is_development() -> bool:
    """Check if runtime environment is development"""
    return get_environment_manager().is_development()

def is_testing() -> bool:
    """Check if runtime environment is testing"""
    return get_environment_manager().is_testing()

def is_production() -> bool:
    """Check if runtime environment is production"""
    return get_environment_manager().is_production()
