from typing import Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

from ...utils.logging import get_logger
from ...config import Config
from ..learning.models.privacy_settings import PrivacySettings

logger = get_logger(__name__)

class UserPreferences:
    """User preferences management"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize user preferences.
        
        Args:
            config: Optional configuration object
        """
        self.config = config or Config()
        self._initialize_preferences()
        
    def _initialize_preferences(self) -> None:
        """Initialize preferences state"""
        # Load preferences
        self.preferences = self._load_preferences()
        
        # Initialize privacy settings if not present
        if "privacy_settings" not in self.preferences:
            self.preferences["privacy_settings"] = PrivacySettings().dict()
    
    def _load_preferences(self) -> Dict[str, Any]:
        """Load preferences from storage"""
        try:
            prefs_file = Path(self.config.storage_path) / "user_preferences.json"
            if not prefs_file.exists():
                return {}
                
            with open(prefs_file, "r") as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Error loading preferences: {str(e)}")
            return {}
    
    def _save_preferences(self) -> None:
        """Save preferences to storage"""
        try:
            prefs_file = Path(self.config.storage_path) / "user_preferences.json"
            prefs_dir = prefs_file.parent
            
            # Ensure directory exists
            if not prefs_dir.exists():
                prefs_dir.mkdir(parents=True)
            
            # Save preferences
            with open(prefs_file, "w") as f:
                json.dump(self.preferences, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error saving preferences: {str(e)}")
            raise
    
    def get_privacy_settings(self) -> PrivacySettings:
        """
        Get privacy settings.
        
        Returns:
            PrivacySettings: Current privacy settings
        """
        try:
            settings_data = self.preferences.get("privacy_settings", {})
            return PrivacySettings(**settings_data)
            
        except Exception as e:
            logger.error(f"Error getting privacy settings: {str(e)}")
            return PrivacySettings()
    
    def update_privacy_settings(
        self,
        settings: PrivacySettings,
        modified_by: str = "user"
    ) -> None:
        """
        Update privacy settings.
        
        Args:
            settings: New privacy settings
            modified_by: Identifier of who modified the settings
        """
        try:
            # Update settings
            self.preferences["privacy_settings"] = settings.dict()
            
            # Update metadata
            self.preferences["last_updated"] = datetime.utcnow()
            self.preferences["modified_by"] = modified_by
            
            # Save changes
            self._save_preferences()
            logger.info(f"Updated privacy settings (modified by: {modified_by})")
            
        except Exception as e:
            logger.error(f"Error updating privacy settings: {str(e)}")
            raise
    
    def reset_privacy_settings(self, modified_by: str = "user") -> None:
        """
        Reset privacy settings to defaults.
        
        Args:
            modified_by: Identifier of who reset the settings
        """
        try:
            self.update_privacy_settings(
                PrivacySettings(),
                modified_by
            )
            
        except Exception as e:
            logger.error(f"Error resetting privacy settings: {str(e)}")
            raise 