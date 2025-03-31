from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

class VersionMetadata(BaseModel):
    """Metadata for a versioned analysis result"""
    version_id: str
    timestamp: datetime
    author: str
    description: str
    tags: List[str] = []
    dependencies: Dict[str, str] = {}
    metadata: Dict[str, Any] = {}

class VersionedResult(BaseModel):
    """Versioned analysis result"""
    content: Dict[str, Any]
    metadata: VersionMetadata
    previous_version: Optional[str] = None
    changes: List[Dict[str, Any]] = []
    hash: str

class VersioningSystem:
    """System for managing versioned analysis results"""
    
    def __init__(self):
        self.versions: Dict[str, VersionedResult] = {}
        self.version_history: Dict[str, List[str]] = {}
        
    def create_version(
        self,
        content: Dict[str, Any],
        author: str,
        description: str,
        tags: List[str] = None,
        dependencies: Dict[str, str] = None,
        metadata: Dict[str, Any] = None,
        previous_version: Optional[str] = None
    ) -> VersionedResult:
        """Create a new version of analysis results"""
        try:
            # Generate version ID
            version_id = self._generate_version_id(content)
            
            # Create version metadata
            version_metadata = VersionMetadata(
                version_id=version_id,
                timestamp=datetime.now(),
                author=author,
                description=description,
                tags=tags or [],
                dependencies=dependencies or {},
                metadata=metadata or {}
            )
            
            # Calculate content hash
            content_hash = self._calculate_content_hash(content)
            
            # Create versioned result
            versioned_result = VersionedResult(
                content=content,
                metadata=version_metadata,
                previous_version=previous_version,
                changes=self._calculate_changes(content, previous_version),
                hash=content_hash
            )
            
            # Store version
            self.versions[version_id] = versioned_result
            
            # Update version history
            if previous_version:
                if previous_version not in self.version_history:
                    self.version_history[previous_version] = []
                self.version_history[previous_version].append(version_id)
            else:
                self.version_history[version_id] = []
                
            return versioned_result
            
        except Exception as e:
            logger.error(f"Error creating version: {str(e)}")
            raise
            
    def get_version(self, version_id: str) -> Optional[VersionedResult]:
        """Get a specific version by ID"""
        return self.versions.get(version_id)
        
    def get_version_history(self, version_id: str) -> List[VersionedResult]:
        """Get the history of a version"""
        history = []
        current_version = version_id
        
        while current_version:
            version = self.versions.get(current_version)
            if version:
                history.append(version)
                current_version = version.previous_version
            else:
                break
                
        return history
        
    def get_latest_version(self) -> Optional[VersionedResult]:
        """Get the latest version"""
        if not self.versions:
            return None
            
        # Find version with no successors
        latest = None
        for version_id in self.versions:
            if version_id not in self.version_history:
                latest = self.versions[version_id]
                break
                
        return latest
        
    def _generate_version_id(self, content: Dict[str, Any]) -> str:
        """Generate a unique version ID"""
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()[:12]
        
    def _calculate_content_hash(self, content: Dict[str, Any]) -> str:
        """Calculate hash of content"""
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()
        
    def _calculate_changes(
        self,
        content: Dict[str, Any],
        previous_version: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Calculate changes from previous version"""
        if not previous_version:
            return []
            
        previous = self.versions.get(previous_version)
        if not previous:
            return []
            
        changes = []
        for key, value in content.items():
            if key not in previous.content:
                changes.append({
                    "type": "added",
                    "key": key,
                    "value": value
                })
            elif previous.content[key] != value:
                changes.append({
                    "type": "modified",
                    "key": key,
                    "old_value": previous.content[key],
                    "new_value": value
                })
                
        for key in previous.content:
            if key not in content:
                changes.append({
                    "type": "removed",
                    "key": key,
                    "value": previous.content[key]
                })
                
        return changes 