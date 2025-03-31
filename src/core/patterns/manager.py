from typing import Dict, List, Optional, Any, Type
from datetime import datetime
import logging
import asyncio
import importlib
import inspect
from pathlib import Path

from .base import (
    BasePatternRecognizer,
    PatternType,
    PatternCategory,
    PatternMetadata,
    PatternMetrics,
    PatternContext
)

logger = logging.getLogger(__name__)

class PatternManager:
    """Manager class for handling pattern recognition"""
    
    def __init__(self):
        self.patterns: Dict[str, BasePatternRecognizer] = {}
        self.pattern_types: Dict[PatternType, List[str]] = {
            pattern_type: [] for pattern_type in PatternType
        }
        self.pattern_categories: Dict[PatternCategory, List[str]] = {
            category: [] for category in PatternCategory
        }
        self.pattern_metrics: Dict[str, PatternMetrics] = {}
        self.pattern_contexts: Dict[str, PatternContext] = {}
        
        self._lock = asyncio.Lock()
        
    async def register_pattern(self, pattern: BasePatternRecognizer) -> bool:
        """Register a new pattern recognizer"""
        async with self._lock:
            try:
                # Check if pattern already exists
                if pattern.name in self.patterns:
                    logger.warning(f"Pattern {pattern.name} already registered")
                    return False
                    
                # Validate pattern
                if not await self._validate_pattern(pattern):
                    return False
                    
                # Register pattern
                self.patterns[pattern.name] = pattern
                self.pattern_types[pattern.pattern_type].append(pattern.name)
                self.pattern_categories[pattern.category].append(pattern.name)
                self.pattern_metrics[pattern.name] = pattern.metrics
                self.pattern_contexts[pattern.name] = pattern.context
                
                logger.info(f"Successfully registered pattern: {pattern.name}")
                return True
                
            except Exception as e:
                logger.error(f"Error registering pattern {pattern.name}: {str(e)}")
                return False
                
    async def discover_patterns(self, search_paths: List[str]) -> List[str]:
        """Discover pattern recognizers in the given paths"""
        discovered_patterns = []
        
        for path in search_paths:
            try:
                # Convert path to Path object
                path_obj = Path(path)
                
                # Find Python files
                for file_path in path_obj.rglob("*.py"):
                    try:
                        # Import module
                        module_path = str(file_path.relative_to(path_obj))
                        module_name = module_path.replace("/", ".").replace(".py", "")
                        module = importlib.import_module(module_name)
                        
                        # Find pattern recognizer classes
                        for name, obj in inspect.getmembers(module):
                            if (
                                inspect.isclass(obj) and
                                issubclass(obj, BasePatternRecognizer) and
                                obj != BasePatternRecognizer
                            ):
                                # Create pattern instance
                                pattern = obj()
                                if await self.register_pattern(pattern):
                                    discovered_patterns.append(pattern.name)
                                    
                    except Exception as e:
                        logger.error(f"Error processing file {file_path}: {str(e)}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error searching path {path}: {str(e)}")
                continue
                
        return discovered_patterns
        
    async def recognize_patterns(
        self,
        code: str,
        file_path: str,
        language: str,
        pattern_types: Optional[List[PatternType]] = None,
        categories: Optional[List[PatternCategory]] = None
    ) -> List[Dict[str, Any]]:
        """Recognize patterns in the given code"""
        async with self._lock:
            try:
                results = []
                
                # Get relevant patterns
                patterns = await self._get_relevant_patterns(
                    pattern_types,
                    categories
                )
                
                # Recognize patterns
                for pattern_name in patterns:
                    pattern = self.patterns[pattern_name]
                    
                    # Update context
                    pattern.context.current_code = code
                    pattern.context.file_path = file_path
                    pattern.context.language = language
                    
                    # Recognize pattern
                    start_time = datetime.now()
                    
                    try:
                        result = await pattern.recognize_pattern(
                            code,
                            file_path=file_path,
                            language=language
                        )
                        
                        # Validate result
                        if await pattern.validate_pattern(result):
                            # Update metrics
                            execution_time = (
                                datetime.now() - start_time
                            ).total_seconds()
                            
                            await pattern.update_metrics({
                                "success": True,
                                "latency": execution_time,
                                "confidence": result.get("confidence", 0)
                            })
                            
                            # Update context
                            pattern.context.recent_matches.append({
                                "timestamp": datetime.now(),
                                "file_path": file_path,
                                "result": result
                            })
                            
                            results.append(result)
                            
                    except Exception as e:
                        logger.error(
                            f"Error recognizing pattern {pattern_name}: {str(e)}"
                        )
                        pattern.context.error_history.append({
                            "timestamp": datetime.now(),
                            "error": str(e),
                            "file_path": file_path
                        })
                        continue
                        
                return results
                
            except Exception as e:
                logger.error(f"Error in pattern recognition: {str(e)}")
                raise
                
    async def get_pattern_metadata(self, pattern_name: str) -> Optional[PatternMetadata]:
        """Get metadata for a pattern"""
        pattern = self.patterns.get(pattern_name)
        if pattern:
            return pattern.get_metadata()
        return None
        
    async def get_pattern_metrics(self, pattern_name: str) -> Optional[PatternMetrics]:
        """Get metrics for a pattern"""
        return self.pattern_metrics.get(pattern_name)
        
    async def get_pattern_context(self, pattern_name: str) -> Optional[PatternContext]:
        """Get context for a pattern"""
        return self.pattern_contexts.get(pattern_name)
        
    async def get_patterns_by_type(self, pattern_type: PatternType) -> List[str]:
        """Get all patterns of a specific type"""
        return self.pattern_types.get(pattern_type, [])
        
    async def get_patterns_by_category(self, category: PatternCategory) -> List[str]:
        """Get all patterns in a category"""
        return self.pattern_categories.get(category, [])
        
    async def _validate_pattern(self, pattern: BasePatternRecognizer) -> bool:
        """Validate a pattern before registration"""
        try:
            # Check required attributes
            required_attrs = [
                "name", "pattern_type", "category", "description",
                "author", "version", "recognize_pattern"
            ]
            
            for attr in required_attrs:
                if not hasattr(pattern, attr):
                    logger.error(f"Pattern missing required attribute: {attr}")
                    return False
                    
            # Validate pattern type
            if not isinstance(pattern.pattern_type, PatternType):
                logger.error("Invalid pattern type")
                return False
                
            # Validate category
            if not isinstance(pattern.category, PatternCategory):
                logger.error("Invalid pattern category")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error validating pattern: {str(e)}")
            return False
            
    async def _get_relevant_patterns(
        self,
        pattern_types: Optional[List[PatternType]],
        categories: Optional[List[PatternCategory]]
    ) -> List[str]:
        """Get relevant patterns based on type and category filters"""
        relevant_patterns = set()
        
        if pattern_types:
            for pattern_type in pattern_types:
                patterns = await self.get_patterns_by_type(pattern_type)
                relevant_patterns.update(patterns)
                
        if categories:
            for category in categories:
                patterns = await self.get_patterns_by_category(category)
                relevant_patterns.update(patterns)
                
        if not pattern_types and not categories:
            relevant_patterns = set(self.patterns.keys())
            
        return list(relevant_patterns) 