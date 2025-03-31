from typing import Dict, List, Optional, Set, Any
from datetime import datetime
import logging
import threading
from dataclasses import dataclass
from pathlib import Path
import json

from ...utils.logging import get_logger
from ...config import Config
from ...orchestrator import Orchestrator
from ..models.pattern import BasePattern, PatternType
from ..models.privacy_settings import PrivacySettings
from .collector.pattern_collector import PatternCollector
from .collector.privacy_manager import PrivacyManager
from .collector.pattern_extractor import PatternExtractor
from .anonymization.anonymizer import Anonymizer

logger = get_logger(__name__)

@dataclass
class LearningStats:
    """Statistics for learning infrastructure"""
    total_patterns: int = 0
    patterns_by_type: Dict[PatternType, int] = None
    last_collection: Optional[datetime] = None
    collection_errors: int = 0
    anonymization_errors: int = 0
    processing_errors: int = 0
    total_activities_processed: int = 0
    total_patterns_shared: int = 0
    total_patterns_filtered: int = 0

class LearningManager:
    """Central component for coordinating ADE learning infrastructure"""
    
    def __init__(
        self,
        orchestrator: Orchestrator,
        config: Optional[Config] = None
    ):
        """
        Initialize the learning manager.
        
        Args:
            orchestrator: ADE orchestrator instance
            config: Optional configuration object
        """
        self.orchestrator = orchestrator
        self.config = config or Config()
        self._initialize_manager()
        
    def _initialize_manager(self) -> None:
        """Initialize manager state and resources"""
        # Component initialization
        self.privacy_manager = PrivacyManager(self.config)
        self.pattern_extractor = PatternExtractor(self.config)
        self.anonymizer = Anonymizer(self.config)
        self.pattern_collector = PatternCollector(self.config)
        
        # State management
        self.is_active = False
        self.is_processing = False
        
        # Threading support
        self._lock = threading.Lock()
        self._processing_queue = []
        self._processing_thread = None
        
        # Statistics
        self.stats = LearningStats(
            patterns_by_type={pt: 0 for pt in PatternType}
        )
        
        # Load existing patterns
        self._load_existing_patterns()
        
    def _load_existing_patterns(self) -> None:
        """Load existing patterns from storage"""
        try:
            patterns = self.pattern_collector.get_patterns()
            self.stats.total_patterns = len(patterns)
            
            # Update pattern type counts
            for pattern in patterns:
                self.stats.patterns_by_type[pattern.pattern_type] += 1
                
            logger.info(f"Loaded {len(patterns)} existing patterns")
            
        except Exception as e:
            logger.error(f"Error loading existing patterns: {str(e)}")
    
    def start(self) -> None:
        """Start the learning manager"""
        with self._lock:
            if self.is_active:
                return
                
            try:
                # Initialize components
                self._initialize_components()
                
                # Start processing thread
                self._start_processing_thread()
                
                self.is_active = True
                logger.info("Started learning manager")
                
            except Exception as e:
                logger.error(f"Error starting learning manager: {str(e)}")
                raise
    
    def stop(self) -> None:
        """Stop the learning manager"""
        with self._lock:
            if not self.is_active:
                return
                
            try:
                # Stop processing thread
                self._stop_processing_thread()
                
                # Cleanup components
                self._cleanup_components()
                
                self.is_active = False
                logger.info("Stopped learning manager")
                
            except Exception as e:
                logger.error(f"Error stopping learning manager: {str(e)}")
                raise
    
    def _initialize_components(self) -> None:
        """Initialize learning components"""
        try:
            # Initialize privacy settings
            self.privacy_manager.get_settings()
            
            # Initialize pattern extractor
            self.pattern_extractor._initialize_pattern_rules()
            
            # Initialize anonymizer
            self.anonymizer._initialize_metric_configs()
            
            logger.info("Initialized learning components")
            
        except Exception as e:
            logger.error(f"Error initializing components: {str(e)}")
            raise
    
    def _cleanup_components(self) -> None:
        """Cleanup learning components"""
        try:
            # Clear processing queue
            self._processing_queue.clear()
            
            # Clear pattern collector
            self.pattern_collector.clear_patterns()
            
            logger.info("Cleaned up learning components")
            
        except Exception as e:
            logger.error(f"Error cleaning up components: {str(e)}")
            raise
    
    def _start_processing_thread(self) -> None:
        """Start pattern processing thread"""
        if self._processing_thread and self._processing_thread.is_alive():
            return
            
        self._processing_thread = threading.Thread(
            target=self._process_patterns,
            daemon=True
        )
        self._processing_thread.start()
    
    def _stop_processing_thread(self) -> None:
        """Stop pattern processing thread"""
        self.is_processing = False
        if self._processing_thread and self._processing_thread.is_alive():
            self._processing_thread.join()
    
    def _process_patterns(self) -> None:
        """Process patterns in the queue"""
        self.is_processing = True
        
        while self.is_processing:
            try:
                with self._lock:
                    if not self._processing_queue:
                        break
                        
                    pattern = self._processing_queue.pop(0)
                
                # Process pattern
                self._process_single_pattern(pattern)
                
            except Exception as e:
                logger.error(f"Error processing pattern: {str(e)}")
                self.stats.processing_errors += 1
                continue
    
    def _process_single_pattern(self, pattern: BasePattern) -> None:
        """
        Process a single pattern.
        
        Args:
            pattern: Pattern to process
        """
        try:
            # Check privacy settings
            if not self._check_pattern_privacy(pattern):
                self.stats.total_patterns_filtered += 1
                return
            
            # Store pattern
            self.pattern_collector._store_patterns([pattern])
            self.stats.total_patterns_shared += 1
            
            # Update statistics
            self.stats.patterns_by_type[pattern.pattern_type] += 1
            self.stats.last_collection = datetime.utcnow()
            
            logger.info(f"Processed pattern {pattern.pattern_id}")
            
        except Exception as e:
            logger.error(f"Error processing pattern {pattern.pattern_id}: {str(e)}")
            self.stats.processing_errors += 1
    
    def _check_pattern_privacy(self, pattern: BasePattern) -> bool:
        """
        Check if pattern meets privacy requirements.
        
        Args:
            pattern: Pattern to check
            
        Returns:
            bool: True if pattern meets privacy requirements
        """
        try:
            # Check pattern type
            if not self.privacy_manager.is_pattern_type_shared(pattern.pattern_type):
                return False
            
            # Check project
            project_id = pattern.context.get("project", {}).get("id")
            if project_id and self.privacy_manager.is_project_excluded(project_id):
                return False
            
            # Check language
            language = pattern.context.get("code_context", {}).get("language")
            if language and self.privacy_manager.is_language_excluded(language):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking pattern privacy: {str(e)}")
            return False
    
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
                self.privacy_manager.update_settings(privacy_settings)
            
            # Extract patterns
            patterns = self.pattern_extractor.extract_patterns(
                activities,
                self.privacy_manager.get_settings()
            )
            
            # Update statistics
            self.stats.total_activities_processed += len(activities)
            
            # Add patterns to processing queue
            with self._lock:
                self._processing_queue.extend(patterns)
            
            # Start processing if needed
            self._start_processing_thread()
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error collecting patterns: {str(e)}")
            self.stats.collection_errors += 1
            raise
    
    def get_patterns(
        self,
        pattern_type: Optional[PatternType] = None,
        limit: Optional[int] = None
    ) -> List[BasePattern]:
        """
        Get collected patterns.
        
        Args:
            pattern_type: Optional pattern type filter
            limit: Optional limit on number of patterns
            
        Returns:
            List[BasePattern]: List of patterns
        """
        return self.pattern_collector.get_patterns(pattern_type, limit)
    
    def get_privacy_settings(self) -> PrivacySettings:
        """
        Get current privacy settings.
        
        Returns:
            PrivacySettings: Current privacy settings
        """
        return self.privacy_manager.get_settings()
    
    def update_privacy_settings(
        self,
        new_settings: PrivacySettings,
        modified_by: str = "user"
    ) -> None:
        """
        Update privacy settings.
        
        Args:
            new_settings: New privacy settings
            modified_by: Identifier of who modified the settings
        """
        self.privacy_manager.update_settings(new_settings, modified_by)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get learning statistics.
        
        Returns:
            Dict[str, Any]: Learning statistics
        """
        return {
            "total_patterns": self.stats.total_patterns,
            "patterns_by_type": self.stats.patterns_by_type,
            "last_collection": self.stats.last_collection,
            "collection_errors": self.stats.collection_errors,
            "anonymization_errors": self.stats.anonymization_errors,
            "processing_errors": self.stats.processing_errors,
            "total_activities_processed": self.stats.total_activities_processed,
            "total_patterns_shared": self.stats.total_patterns_shared,
            "total_patterns_filtered": self.stats.total_patterns_filtered
        }
    
    def clear_patterns(self) -> bool:
        """
        Clear all collected patterns.
        
        Returns:
            bool: True if patterns were cleared
        """
        return self.pattern_collector.clear_patterns()
    
    def delete_pattern(self, pattern_id: str) -> bool:
        """
        Delete a specific pattern.
        
        Args:
            pattern_id: Pattern ID to delete
            
        Returns:
            bool: True if pattern was deleted
        """
        return self.pattern_collector.delete_pattern(pattern_id) 