from typing import Dict, List, Optional, Set
from enum import Enum
from pydantic import BaseModel, Field, validator
from datetime import datetime

class PrivacyLevel(str, Enum):
    """Privacy protection levels"""
    LOW = "low"      # Basic privacy protection
    MEDIUM = "medium"  # Enhanced privacy protection
    HIGH = "high"    # Maximum privacy protection

class AttributionType(str, Enum):
    """Types of attribution for pattern contributions"""
    ANONYMOUS = "anonymous"      # No attribution
    PSEUDONYMOUS = "pseudonymous"  # Pseudonymized attribution
    FULL = "full"               # Full attribution

class PatternType(str, Enum):
    """Types of patterns that can be shared"""
    SOLUTION = "solution"
    ERROR_RECOVERY = "error_recovery"
    WORKFLOW = "workflow"
    TOOL_USAGE = "tool_usage"

class CustomPrivacyParameter(BaseModel):
    """Custom privacy parameter with validation rules"""
    name: str = Field(..., description="Name of the privacy parameter")
    value: float = Field(..., description="Value of the privacy parameter")
    min_value: float = Field(..., description="Minimum allowed value")
    max_value: float = Field(..., description="Maximum allowed value")
    description: str = Field(..., description="Description of the parameter's purpose")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    @validator('value')
    def validate_value_range(cls, v, values):
        if 'min_value' in values and 'max_value' in values:
            if not values['min_value'] <= v <= values['max_value']:
                raise ValueError(f"Value must be between {values['min_value']} and {values['max_value']}")
        return v

class PrivacySettings(BaseModel):
    """User preferences for pattern collection and privacy protection"""
    # Basic settings
    enabled: bool = Field(default=True, description="Whether pattern collection is enabled")
    privacy_level: PrivacyLevel = Field(default=PrivacyLevel.MEDIUM, description="Overall privacy protection level")
    attribution_type: AttributionType = Field(default=AttributionType.PSEUDONYMOUS, description="Type of attribution for contributions")
    
    # Pattern type controls
    shared_pattern_types: Set[PatternType] = Field(
        default_factory=lambda: {PatternType.SOLUTION, PatternType.ERROR_RECOVERY},
        description="Pattern types that can be shared"
    )
    
    # Exclusion lists
    excluded_projects: List[str] = Field(
        default_factory=list,
        description="Projects excluded from pattern collection"
    )
    excluded_languages: List[str] = Field(
        default_factory=list,
        description="Programming languages excluded from pattern collection"
    )
    
    # Custom privacy parameters
    custom_parameters: Dict[str, CustomPrivacyParameter] = Field(
        default_factory=dict,
        description="Custom privacy parameters"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Settings creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    version: str = Field(default="1.0", description="Settings version")

    @property
    def epsilon(self) -> float:
        """
        Calculate the epsilon value for differential privacy based on privacy level.
        Lower epsilon means stronger privacy protection.
        """
        epsilon_values = {
            PrivacyLevel.LOW: 1.0,
            PrivacyLevel.MEDIUM: 0.5,
            PrivacyLevel.HIGH: 0.1
        }
        return epsilon_values[self.privacy_level]

    @property
    def is_anonymous(self) -> bool:
        """Check if the settings enforce anonymous pattern sharing"""
        return self.attribution_type == AttributionType.ANONYMOUS

    @property
    def is_pseudonymous(self) -> bool:
        """Check if the settings enforce pseudonymous pattern sharing"""
        return self.attribution_type == AttributionType.PSEUDONYMOUS

    def can_share_pattern_type(self, pattern_type: PatternType) -> bool:
        """
        Check if a specific pattern type can be shared based on current settings.
        
        Args:
            pattern_type: The pattern type to check
            
        Returns:
            bool: Whether the pattern type can be shared
        """
        return pattern_type in self.shared_pattern_types

    def is_project_excluded(self, project_name: str) -> bool:
        """
        Check if a project is excluded from pattern collection.
        
        Args:
            project_name: Name of the project to check
            
        Returns:
            bool: Whether the project is excluded
        """
        return project_name in self.excluded_projects

    def is_language_excluded(self, language: str) -> bool:
        """
        Check if a programming language is excluded from pattern collection.
        
        Args:
            language: Name of the programming language to check
            
        Returns:
            bool: Whether the language is excluded
        """
        return language in self.excluded_languages

    def get_custom_parameter(self, name: str) -> Optional[CustomPrivacyParameter]:
        """
        Get a custom privacy parameter by name.
        
        Args:
            name: Name of the parameter to retrieve
            
        Returns:
            Optional[CustomPrivacyParameter]: The parameter if found, None otherwise
        """
        return self.custom_parameters.get(name)

    def update_custom_parameter(self, name: str, value: float) -> None:
        """
        Update a custom privacy parameter value.
        
        Args:
            name: Name of the parameter to update
            value: New value for the parameter
            
        Raises:
            ValueError: If the parameter doesn't exist or the value is invalid
        """
        if name not in self.custom_parameters:
            raise ValueError(f"Custom parameter '{name}' not found")
        
        param = self.custom_parameters[name]
        param.value = value
        param.last_updated = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict:
        """
        Convert settings to a dictionary format.
        
        Returns:
            Dict: Dictionary representation of the settings
        """
        return {
            "enabled": self.enabled,
            "privacy_level": self.privacy_level,
            "attribution_type": self.attribution_type,
            "shared_pattern_types": list(self.shared_pattern_types),
            "excluded_projects": self.excluded_projects,
            "excluded_languages": self.excluded_languages,
            "custom_parameters": {
                name: {
                    "value": param.value,
                    "min_value": param.min_value,
                    "max_value": param.max_value,
                    "description": param.description,
                    "last_updated": param.last_updated.isoformat()
                }
                for name, param in self.custom_parameters.items()
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'PrivacySettings':
        """
        Create settings from a dictionary format.
        
        Args:
            data: Dictionary containing settings data
            
        Returns:
            PrivacySettings: New settings instance
        """
        # Convert custom parameters back to CustomPrivacyParameter objects
        if "custom_parameters" in data:
            data["custom_parameters"] = {
                name: CustomPrivacyParameter(
                    name=name,
                    value=param["value"],
                    min_value=param["min_value"],
                    max_value=param["max_value"],
                    description=param["description"],
                    last_updated=datetime.fromisoformat(param["last_updated"])
                )
                for name, param in data["custom_parameters"].items()
            }
        
        # Convert timestamps
        if "created_at" in data:
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        
        # Convert shared pattern types to set
        if "shared_pattern_types" in data:
            data["shared_pattern_types"] = set(data["shared_pattern_types"])
        
        return cls(**data) 