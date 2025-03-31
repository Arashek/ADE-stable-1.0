from typing import Dict, List, Optional, Set, Any, Tuple
from datetime import datetime
import logging
from collections import defaultdict
from pathlib import Path
import json
import threading
from queue import Queue

from ...utils.logging import get_logger
from ...config import Config
from ..models.pattern import BasePattern, PatternType
from ..models.privacy_settings import PrivacySettings
from .pattern_extractor import PatternExtractor
from ..anonymization.anonymizer import Anonymizer, AnonymizationContext

logger = get_logger(__name__)

class PatternCollector:
    """Component for orchestrating pattern extraction and anonymization"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the pattern collector.
        
        Args:
            config: Optional configuration object
        """
        self.config = config or Config()
        self.pattern_extractor = PatternExtractor(config)
        self.anonymizer = Anonymizer(config)
        self._initialize_collector()
        
    def _initialize_collector(self) -> None:
        """Initialize collector state and resources"""
        # Pattern storage
        self.patterns: Dict[str, BasePattern] = {}
        self.pattern_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Collection statistics
        self.collection_stats = {
            "total_patterns": 0,
            "patterns_by_type": defaultdict(int),
            "last_collection": None,
            "collection_errors": 0,
            "anonymization_errors": 0
        }
        
        # Privacy settings
        self.privacy_settings = PrivacySettings()
        
        # Threading support
        self._lock = threading.Lock()
        self._collection_queue = Queue()
        self._is_collecting = False
        
        # Load existing patterns if available
        self._load_existing_patterns()
        
    def _load_existing_patterns(self) -> None:
        """Load existing patterns from storage"""
        try:
            pattern_dir = Path(self.config.storage_path) / "patterns"
            if not pattern_dir.exists():
                pattern_dir.mkdir(parents=True)
                return
                
            for pattern_file in pattern_dir.glob("*.json"):
                try:
                    with open(pattern_file, "r") as f:
                        pattern_data = json.load(f)
                        pattern = BasePattern.parse_obj(pattern_data)
                        self.patterns[pattern.pattern_id] = pattern
                        self.pattern_metadata[pattern.pattern_id] = {
                            "created_at": pattern_data.get("created_at"),
                            "last_updated": pattern_data.get("last_updated"),
                            "usage_count": pattern_data.get("usage_count", 0)
                        }
                        self.collection_stats["patterns_by_type"][pattern.pattern_type] += 1
                except Exception as e:
                    logger.error(f"Error loading pattern from {pattern_file}: {str(e)}")
                    continue
                    
            self.collection_stats["total_patterns"] = len(self.patterns)
            logger.info(f"Loaded {len(self.patterns)} existing patterns")
            
        except Exception as e:
            logger.error(f"Error loading existing patterns: {str(e)}")
    
    def collect_patterns(
        self,
        activities: List[Dict[str, Any]],
        privacy_settings: Optional[PrivacySettings] = None
    ) -> List[BasePattern]:
        """
        Collect patterns from development activities.
        
        Args:
            activities: List of development activities
            privacy_settings: Optional privacy settings override
            
        Returns:
            List[BasePattern]: List of collected patterns
        """
        try:
            # Update privacy settings if provided
            if privacy_settings:
                self._update_privacy_settings(privacy_settings)
            
            # Extract patterns
            patterns = self.pattern_extractor.extract_patterns(
                activities,
                self.privacy_settings
            )
            
            # Filter patterns based on privacy settings
            filtered_patterns = self._filter_patterns(patterns)
            
            # Anonymize patterns
            context = AnonymizationContext(
                privacy_settings=self.privacy_settings,
                timestamp=datetime.utcnow(),
                instance_id=self.config.instance_id
            )
            anonymized_patterns = self.anonymizer.anonymize_patterns(
                filtered_patterns,
                context
            )
            
            # Store patterns
            self._store_patterns(anonymized_patterns)
            
            # Update statistics
            self._update_collection_stats(anonymized_patterns)
            
            logger.info(f"Collected {len(anonymized_patterns)} patterns from {len(activities)} activities")
            return anonymized_patterns
            
        except Exception as e:
            logger.error(f"Error collecting patterns: {str(e)}")
            self.collection_stats["collection_errors"] += 1
            raise
    
    def _update_privacy_settings(
        self,
        new_settings: PrivacySettings
    ) -> None:
        """
        Update privacy settings with thread safety.
        
        Args:
            new_settings: New privacy settings
        """
        with self._lock:
            self.privacy_settings = new_settings
            logger.info("Updated privacy settings")
    
    def _filter_patterns(
        self,
        patterns: List[BasePattern]
    ) -> List[BasePattern]:
        """
        Filter patterns based on privacy settings.
        
        Args:
            patterns: List of patterns to filter
            
        Returns:
            List[BasePattern]: Filtered patterns
        """
        filtered_patterns = []
        
        for pattern in patterns:
            # Check if pattern type is allowed
            if pattern.pattern_type not in self.privacy_settings.shared_pattern_types:
                continue
                
            # Check if pattern matches privacy level
            if pattern.privacy.level > self.privacy_settings.privacy_level:
                continue
                
            # Check if pattern is from excluded project
            if pattern.context.get("project", {}).get("id") in self.privacy_settings.excluded_projects:
                continue
                
            # Check if pattern is from excluded language
            if pattern.context.get("code_context", {}).get("language") in self.privacy_settings.excluded_languages:
                continue
                
            filtered_patterns.append(pattern)
        
        return filtered_patterns
    
    def _store_patterns(
        self,
        patterns: List[BasePattern]
    ) -> None:
        """
        Store patterns with thread safety.
        
        Args:
            patterns: List of patterns to store
        """
        with self._lock:
            for pattern in patterns:
                # Update pattern metadata
                if pattern.pattern_id in self.pattern_metadata:
                    metadata = self.pattern_metadata[pattern.pattern_id]
                    metadata["last_updated"] = datetime.utcnow()
                    metadata["usage_count"] += 1
                else:
                    self.pattern_metadata[pattern.pattern_id] = {
                        "created_at": datetime.utcnow(),
                        "last_updated": datetime.utcnow(),
                        "usage_count": 1
                    }
                
                # Store pattern
                self.patterns[pattern.pattern_id] = pattern
                
                # Save to file
                self._save_pattern_to_file(pattern)
    
    def _save_pattern_to_file(self, pattern: BasePattern) -> None:
        """
        Save pattern to file.
        
        Args:
            pattern: Pattern to save
        """
        try:
            pattern_dir = Path(self.config.storage_path) / "patterns"
            pattern_file = pattern_dir / f"{pattern.pattern_id}.json"
            
            # Prepare pattern data
            pattern_data = pattern.dict()
            pattern_data.update(self.pattern_metadata[pattern.pattern_id])
            
            # Save to file
            with open(pattern_file, "w") as f:
                json.dump(pattern_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error saving pattern {pattern.pattern_id}: {str(e)}")
    
    def _update_collection_stats(
        self,
        patterns: List[BasePattern]
    ) -> None:
        """
        Update collection statistics.
        
        Args:
            patterns: List of collected patterns
        """
        with self._lock:
            self.collection_stats["total_patterns"] = len(self.patterns)
            self.collection_stats["last_collection"] = datetime.utcnow()
            
            # Update pattern type counts
            for pattern in patterns:
                self.collection_stats["patterns_by_type"][pattern.pattern_type] += 1
    
    def get_patterns(
        self,
        pattern_type: Optional[PatternType] = None,
        limit: Optional[int] = None
    ) -> List[BasePattern]:
        """
        Get collected patterns with optional filtering.
        
        Args:
            pattern_type: Optional pattern type filter
            limit: Optional limit on number of patterns
            
        Returns:
            List[BasePattern]: List of patterns
        """
        with self._lock:
            patterns = list(self.patterns.values())
            
            # Apply type filter
            if pattern_type:
                patterns = [p for p in patterns if p.pattern_type == pattern_type]
            
            # Apply limit
            if limit:
                patterns = patterns[:limit]
            
            return patterns
    
    def get_pattern_metadata(
        self,
        pattern_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific pattern.
        
        Args:
            pattern_id: Pattern ID
            
        Returns:
            Optional[Dict[str, Any]]: Pattern metadata
        """
        with self._lock:
            return self.pattern_metadata.get(pattern_id)
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics.
        
        Returns:
            Dict[str, Any]: Collection statistics
        """
        with self._lock:
            return {
                "total_patterns": self.collection_stats["total_patterns"],
                "patterns_by_type": dict(self.collection_stats["patterns_by_type"]),
                "last_collection": self.collection_stats["last_collection"],
                "collection_errors": self.collection_stats["collection_errors"],
                "anonymization_errors": self.collection_stats["anonymization_errors"]
            }
    
    def delete_pattern(self, pattern_id: str) -> bool:
        """
        Delete a pattern and its metadata.
        
        Args:
            pattern_id: Pattern ID to delete
            
        Returns:
            bool: True if pattern was deleted, False otherwise
        """
        with self._lock:
            if pattern_id not in self.patterns:
                return False
                
            try:
                # Delete pattern file
                pattern_file = Path(self.config.storage_path) / "patterns" / f"{pattern_id}.json"
                if pattern_file.exists():
                    pattern_file.unlink()
                
                # Remove from memory
                pattern_type = self.patterns[pattern_id].pattern_type
                del self.patterns[pattern_id]
                del self.pattern_metadata[pattern_id]
                
                # Update statistics
                self.collection_stats["total_patterns"] -= 1
                self.collection_stats["patterns_by_type"][pattern_type] -= 1
                
                logger.info(f"Deleted pattern {pattern_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error deleting pattern {pattern_id}: {str(e)}")
                return False
    
    def clear_patterns(self) -> bool:
        """
        Clear all collected patterns.
        
        Returns:
            bool: True if patterns were cleared, False otherwise
        """
        with self._lock:
            try:
                # Delete pattern files
                pattern_dir = Path(self.config.storage_path) / "patterns"
                if pattern_dir.exists():
                    for pattern_file in pattern_dir.glob("*.json"):
                        pattern_file.unlink()
                
                # Clear memory
                self.patterns.clear()
                self.pattern_metadata.clear()
                
                # Reset statistics
                self.collection_stats = {
                    "total_patterns": 0,
                    "patterns_by_type": defaultdict(int),
                    "last_collection": None,
                    "collection_errors": 0,
                    "anonymization_errors": 0
                }
                
                logger.info("Cleared all patterns")
                return True
                
            except Exception as e:
                logger.error(f"Error clearing patterns: {str(e)}")
                return False 