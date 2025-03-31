from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import logging
import json
import yaml
from pathlib import Path
import hashlib
import difflib
from enum import Enum

logger = logging.getLogger(__name__)

class PatternStatus(Enum):
    """Status of a pattern in the knowledge base"""
    DRAFT = "draft"
    VALIDATED = "validated"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

@dataclass
class PatternVersion:
    """Version information for a pattern"""
    version: str
    timestamp: datetime
    author: str
    changes: List[str]
    status: PatternStatus
    metadata: Dict[str, Any]

class PatternKnowledgeBase:
    """System for managing pattern knowledge"""
    
    def __init__(self, storage_path: str = "src/core/patterns/data"):
        self.storage_path = Path(storage_path)
        self.patterns: Dict[str, Dict[str, Any]] = {}
        self.versions: Dict[str, List[PatternVersion]] = {}
        self.dependencies: Dict[str, Set[str]] = {}
        self.categories: Dict[str, Set[str]] = {}
        self.tags: Dict[str, Set[str]] = {}
        
        # Create storage directories
        self.storage_path.mkdir(parents=True, exist_ok=True)
        (self.storage_path / "patterns").mkdir(exist_ok=True)
        (self.storage_path / "versions").mkdir(exist_ok=True)
        (self.storage_path / "metadata").mkdir(exist_ok=True)
        
        # Load existing patterns
        self.load_patterns()
        
    def load_patterns(self) -> None:
        """Load patterns from storage"""
        try:
            # Load pattern metadata
            metadata_path = self.storage_path / "metadata" / "patterns.yaml"
            if metadata_path.exists():
                with open(metadata_path, "r") as f:
                    metadata = yaml.safe_load(f)
                    self.patterns = metadata.get("patterns", {})
                    self.versions = metadata.get("versions", {})
                    self.dependencies = metadata.get("dependencies", {})
                    self.categories = metadata.get("categories", {})
                    self.tags = metadata.get("tags", {})
                    
            # Load individual pattern files
            patterns_dir = self.storage_path / "patterns"
            for pattern_file in patterns_dir.glob("*.yaml"):
                pattern_id = pattern_file.stem
                with open(pattern_file, "r") as f:
                    pattern_data = yaml.safe_load(f)
                    self.patterns[pattern_id] = pattern_data
                    
        except Exception as e:
            logger.error(f"Error loading patterns: {str(e)}")
            
    def save_patterns(self) -> None:
        """Save patterns to storage"""
        try:
            # Save pattern metadata
            metadata_path = self.storage_path / "metadata" / "patterns.yaml"
            metadata = {
                "patterns": self.patterns,
                "versions": self.versions,
                "dependencies": self.dependencies,
                "categories": self.categories,
                "tags": self.tags
            }
            with open(metadata_path, "w") as f:
                yaml.dump(metadata, f)
                
            # Save individual pattern files
            patterns_dir = self.storage_path / "patterns"
            for pattern_id, pattern_data in self.patterns.items():
                pattern_file = patterns_dir / f"{pattern_id}.yaml"
                with open(pattern_file, "w") as f:
                    yaml.dump(pattern_data, f)
                    
        except Exception as e:
            logger.error(f"Error saving patterns: {str(e)}")
            
    def add_pattern(
        self,
        pattern_id: str,
        pattern_data: Dict[str, Any],
        author: str,
        version: str = "1.0.0",
        status: PatternStatus = PatternStatus.DRAFT
    ) -> bool:
        """Add a new pattern to the knowledge base"""
        try:
            # Check if pattern already exists
            if pattern_id in self.patterns:
                logger.warning(f"Pattern {pattern_id} already exists")
                return False
                
            # Create pattern version
            pattern_version = PatternVersion(
                version=version,
                timestamp=datetime.now(),
                author=author,
                changes=["Initial version"],
                status=status,
                metadata={
                    "dependencies": pattern_data.get("dependencies", []),
                    "categories": pattern_data.get("categories", []),
                    "tags": pattern_data.get("tags", [])
                }
            )
            
            # Update pattern data
            self.patterns[pattern_id] = pattern_data
            self.versions[pattern_id] = [pattern_version]
            
            # Update dependencies
            self.dependencies[pattern_id] = set(pattern_data.get("dependencies", []))
            
            # Update categories
            for category in pattern_data.get("categories", []):
                if category not in self.categories:
                    self.categories[category] = set()
                self.categories[category].add(pattern_id)
                
            # Update tags
            for tag in pattern_data.get("tags", []):
                if tag not in self.tags:
                    self.tags[tag] = set()
                self.tags[tag].add(pattern_id)
                
            # Save changes
            self.save_patterns()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding pattern: {str(e)}")
            return False
            
    def update_pattern(
        self,
        pattern_id: str,
        pattern_data: Dict[str, Any],
        author: str,
        changes: List[str],
        version: Optional[str] = None
    ) -> bool:
        """Update an existing pattern"""
        try:
            # Check if pattern exists
            if pattern_id not in self.patterns:
                logger.error(f"Pattern {pattern_id} not found")
                return False
                
            # Get current version
            current_version = self.versions[pattern_id][-1]
            
            # Generate new version number if not provided
            if not version:
                major, minor, patch = map(int, current_version.version.split("."))
                version = f"{major}.{minor}.{patch + 1}"
                
            # Create new version
            new_version = PatternVersion(
                version=version,
                timestamp=datetime.now(),
                author=author,
                changes=changes,
                status=current_version.status,
                metadata={
                    "dependencies": pattern_data.get("dependencies", []),
                    "categories": pattern_data.get("categories", []),
                    "tags": pattern_data.get("tags", [])
                }
            )
            
            # Update pattern data
            self.patterns[pattern_id] = pattern_data
            self.versions[pattern_id].append(new_version)
            
            # Update dependencies
            self.dependencies[pattern_id] = set(pattern_data.get("dependencies", []))
            
            # Update categories
            old_categories = set(current_version.metadata["categories"])
            new_categories = set(pattern_data.get("categories", []))
            
            for category in old_categories - new_categories:
                self.categories[category].remove(pattern_id)
            for category in new_categories - old_categories:
                if category not in self.categories:
                    self.categories[category] = set()
                self.categories[category].add(pattern_id)
                
            # Update tags
            old_tags = set(current_version.metadata["tags"])
            new_tags = set(pattern_data.get("tags", []))
            
            for tag in old_tags - new_tags:
                self.tags[tag].remove(pattern_id)
            for tag in new_tags - old_tags:
                if tag not in self.tags:
                    self.tags[tag] = set()
                self.tags[tag].add(pattern_id)
                
            # Save changes
            self.save_patterns()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating pattern: {str(e)}")
            return False
            
    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get pattern data"""
        return self.patterns.get(pattern_id)
        
    def get_pattern_version(
        self,
        pattern_id: str,
        version: Optional[str] = None
    ) -> Optional[PatternVersion]:
        """Get pattern version information"""
        if pattern_id not in self.versions:
            return None
            
        if version:
            for v in self.versions[pattern_id]:
                if v.version == version:
                    return v
            return None
            
        return self.versions[pattern_id][-1]
        
    def get_pattern_dependencies(self, pattern_id: str) -> Set[str]:
        """Get pattern dependencies"""
        return self.dependencies.get(pattern_id, set())
        
    def get_patterns_by_category(self, category: str) -> Set[str]:
        """Get patterns in a category"""
        return self.categories.get(category, set())
        
    def get_patterns_by_tag(self, tag: str) -> Set[str]:
        """Get patterns with a specific tag"""
        return self.tags.get(tag, set())
        
    def get_pattern_diff(
        self,
        pattern_id: str,
        version1: str,
        version2: str
    ) -> List[str]:
        """Get differences between pattern versions"""
        try:
            v1 = self.get_pattern_version(pattern_id, version1)
            v2 = self.get_pattern_version(pattern_id, version2)
            
            if not v1 or not v2:
                return []
                
            # Get pattern data for both versions
            pattern1 = self.patterns.get(pattern_id, {})
            pattern2 = self.patterns.get(pattern_id, {})
            
            # Generate diff
            diff = []
            for key in set(pattern1.keys()) | set(pattern2.keys()):
                if key not in pattern1:
                    diff.append(f"Added {key}: {pattern2[key]}")
                elif key not in pattern2:
                    diff.append(f"Removed {key}: {pattern1[key]}")
                elif pattern1[key] != pattern2[key]:
                    diff.append(f"Changed {key}: {pattern1[key]} -> {pattern2[key]}")
                    
            return diff
            
        except Exception as e:
            logger.error(f"Error getting pattern diff: {str(e)}")
            return []
            
    def update_pattern_status(
        self,
        pattern_id: str,
        status: PatternStatus,
        author: str
    ) -> bool:
        """Update pattern status"""
        try:
            if pattern_id not in self.versions:
                return False
                
            current_version = self.versions[pattern_id][-1]
            current_version.status = status
            
            # Save changes
            self.save_patterns()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating pattern status: {str(e)}")
            return False
            
    def get_pattern_status(self, pattern_id: str) -> Optional[PatternStatus]:
        """Get current pattern status"""
        version = self.get_pattern_version(pattern_id)
        return version.status if version else None 