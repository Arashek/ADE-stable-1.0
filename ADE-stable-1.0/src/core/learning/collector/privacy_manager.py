from typing import Dict, Any, Optional, Set
from datetime import datetime
import json
from pathlib import Path
import logging
import threading
from dataclasses import dataclass, asdict

from ...utils.logging import get_logger
from ...config import Config
from ..models.privacy_settings import PrivacySettings, PrivacyLevel, AttributionType, PatternType
from ..models.pattern import PatternType as BasePatternType

logger = get_logger(__name__)

@dataclass
class PrivacySettingsMetadata:
    """Metadata for privacy settings"""
    created_at: datetime
    last_updated: datetime
    version: str
    modified_by: str

class PrivacyManager:
    """Component for managing user privacy settings"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the privacy manager.
        
        Args:
            config: Optional configuration object
        """
        self.config = config or Config()
        self._initialize_manager()
        
    def _initialize_manager(self) -> None:
        """Initialize manager state and resources"""
        # Settings storage
        self.settings: Optional[PrivacySettings] = None
        self.metadata: Optional[PrivacySettingsMetadata] = None
        
        # Threading support
        self._lock = threading.Lock()
        
        # Load existing settings if available
        self._load_settings()
        
    def _load_settings(self) -> None:
        """Load privacy settings from storage"""
        try:
            settings_file = Path(self.config.storage_path) / "privacy_settings.json"
            if not settings_file.exists():
                self._create_default_settings()
                return
                
            with open(settings_file, "r") as f:
                data = json.load(f)
                
                # Parse settings
                settings_data = data.get("settings", {})
                self.settings = PrivacySettings(**settings_data)
                
                # Parse metadata
                metadata_data = data.get("metadata", {})
                self.metadata = PrivacySettingsMetadata(
                    created_at=datetime.fromisoformat(metadata_data.get("created_at")),
                    last_updated=datetime.fromisoformat(metadata_data.get("last_updated")),
                    version=metadata_data.get("version", "1.0"),
                    modified_by=metadata_data.get("modified_by", "system")
                )
                
                logger.info("Loaded privacy settings")
                
        except Exception as e:
            logger.error(f"Error loading privacy settings: {str(e)}")
            self._create_default_settings()
    
    def _create_default_settings(self) -> None:
        """Create default privacy settings"""
        try:
            self.settings = PrivacySettings()
            self.metadata = PrivacySettingsMetadata(
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                version="1.0",
                modified_by="system"
            )
            
            # Save default settings
            self._save_settings()
            logger.info("Created default privacy settings")
            
        except Exception as e:
            logger.error(f"Error creating default settings: {str(e)}")
            raise
    
    def _save_settings(self) -> None:
        """
        Save privacy settings to storage.
        
        Raises:
            Exception: If settings cannot be saved
        """
        try:
            settings_file = Path(self.config.storage_path) / "privacy_settings.json"
            settings_dir = settings_file.parent
            
            # Ensure directory exists
            if not settings_dir.exists():
                settings_dir.mkdir(parents=True)
            
            # Prepare data
            data = {
                "settings": self.settings.dict(),
                "metadata": asdict(self.metadata)
            }
            
            # Save to file
            with open(settings_file, "w") as f:
                json.dump(data, f, indent=2, default=str)
                
            logger.info("Saved privacy settings")
            
        except Exception as e:
            logger.error(f"Error saving privacy settings: {str(e)}")
            raise
    
    def get_settings(self) -> PrivacySettings:
        """
        Get current privacy settings.
        
        Returns:
            PrivacySettings: Current privacy settings
        """
        with self._lock:
            if not self.settings:
                self._create_default_settings()
            return self.settings
    
    def get_metadata(self) -> PrivacySettingsMetadata:
        """
        Get settings metadata.
        
        Returns:
            PrivacySettingsMetadata: Settings metadata
        """
        with self._lock:
            if not self.metadata:
                self._create_default_settings()
            return self.metadata
    
    def update_settings(
        self,
        new_settings: PrivacySettings,
        modified_by: str = "user"
    ) -> None:
        """
        Update privacy settings.
        
        Args:
            new_settings: New privacy settings
            modified_by: Identifier of who modified the settings
            
        Raises:
            Exception: If settings cannot be updated
        """
        with self._lock:
            try:
                # Update settings
                self.settings = new_settings
                
                # Update metadata
                self.metadata.last_updated = datetime.utcnow()
                self.metadata.modified_by = modified_by
                
                # Save changes
                self._save_settings()
                logger.info(f"Updated privacy settings (modified by: {modified_by})")
                
            except Exception as e:
                logger.error(f"Error updating privacy settings: {str(e)}")
                raise
    
    def update_privacy_level(
        self,
        level: PrivacyLevel,
        modified_by: str = "user"
    ) -> None:
        """
        Update privacy level.
        
        Args:
            level: New privacy level
            modified_by: Identifier of who modified the settings
        """
        with self._lock:
            try:
                current_settings = self.get_settings()
                current_settings.privacy_level = level
                self.update_settings(current_settings, modified_by)
                
            except Exception as e:
                logger.error(f"Error updating privacy level: {str(e)}")
                raise
    
    def update_attribution_type(
        self,
        attribution_type: AttributionType,
        modified_by: str = "user"
    ) -> None:
        """
        Update attribution type.
        
        Args:
            attribution_type: New attribution type
            modified_by: Identifier of who modified the settings
        """
        with self._lock:
            try:
                current_settings = self.get_settings()
                current_settings.attribution_type = attribution_type
                self.update_settings(current_settings, modified_by)
                
            except Exception as e:
                logger.error(f"Error updating attribution type: {str(e)}")
                raise
    
    def update_shared_pattern_types(
        self,
        pattern_types: Set[PatternType],
        modified_by: str = "user"
    ) -> None:
        """
        Update shared pattern types.
        
        Args:
            pattern_types: New set of shared pattern types
            modified_by: Identifier of who modified the settings
        """
        with self._lock:
            try:
                current_settings = self.get_settings()
                current_settings.shared_pattern_types = pattern_types
                self.update_settings(current_settings, modified_by)
                
            except Exception as e:
                logger.error(f"Error updating shared pattern types: {str(e)}")
                raise
    
    def update_excluded_projects(
        self,
        project_ids: Set[str],
        modified_by: str = "user"
    ) -> None:
        """
        Update excluded projects.
        
        Args:
            project_ids: New set of excluded project IDs
            modified_by: Identifier of who modified the settings
        """
        with self._lock:
            try:
                current_settings = self.get_settings()
                current_settings.excluded_projects = project_ids
                self.update_settings(current_settings, modified_by)
                
            except Exception as e:
                logger.error(f"Error updating excluded projects: {str(e)}")
                raise
    
    def update_excluded_languages(
        self,
        languages: Set[str],
        modified_by: str = "user"
    ) -> None:
        """
        Update excluded languages.
        
        Args:
            languages: New set of excluded languages
            modified_by: Identifier of who modified the settings
        """
        with self._lock:
            try:
                current_settings = self.get_settings()
                current_settings.excluded_languages = languages
                self.update_settings(current_settings, modified_by)
                
            except Exception as e:
                logger.error(f"Error updating excluded languages: {str(e)}")
                raise
    
    def update_custom_parameter(
        self,
        name: str,
        value: float,
        modified_by: str = "user"
    ) -> None:
        """
        Update custom privacy parameter.
        
        Args:
            name: Parameter name
            value: Parameter value
            modified_by: Identifier of who modified the settings
        """
        with self._lock:
            try:
                current_settings = self.get_settings()
                current_settings.custom_parameters[name] = value
                self.update_settings(current_settings, modified_by)
                
            except Exception as e:
                logger.error(f"Error updating custom parameter {name}: {str(e)}")
                raise
    
    def reset_to_defaults(self, modified_by: str = "user") -> None:
        """
        Reset settings to defaults.
        
        Args:
            modified_by: Identifier of who reset the settings
        """
        with self._lock:
            try:
                self._create_default_settings()
                self.metadata.modified_by = modified_by
                self._save_settings()
                logger.info(f"Reset privacy settings to defaults (modified by: {modified_by})")
                
            except Exception as e:
                logger.error(f"Error resetting privacy settings: {str(e)}")
                raise
    
    def is_pattern_type_shared(self, pattern_type: BasePatternType) -> bool:
        """
        Check if a pattern type is shared.
        
        Args:
            pattern_type: Pattern type to check
            
        Returns:
            bool: True if pattern type is shared
        """
        with self._lock:
            return pattern_type in self.get_settings().shared_pattern_types
    
    def is_project_excluded(self, project_id: str) -> bool:
        """
        Check if a project is excluded.
        
        Args:
            project_id: Project ID to check
            
        Returns:
            bool: True if project is excluded
        """
        with self._lock:
            return project_id in self.get_settings().excluded_projects
    
    def is_language_excluded(self, language: str) -> bool:
        """
        Check if a language is excluded.
        
        Args:
            language: Language to check
            
        Returns:
            bool: True if language is excluded
        """
        with self._lock:
            return language in self.get_settings().excluded_languages 