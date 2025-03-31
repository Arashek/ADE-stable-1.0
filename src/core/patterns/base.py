from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import logging
import asyncio
from enum import Enum

logger = logging.getLogger(__name__)

class PatternType(Enum):
    """Types of patterns that can be recognized"""
    DESIGN_PATTERN = "design_pattern"
    CODE_PATTERN = "code_pattern"
    ERROR_PATTERN = "error_pattern"
    PERFORMANCE_PATTERN = "performance_pattern"
    SECURITY_PATTERN = "security_pattern"
    ARCHITECTURE_PATTERN = "architecture_pattern"

class PatternCategory(Enum):
    """Categories of patterns"""
    CREATIONAL = "creational"
    STRUCTURAL = "structural"
    BEHAVIORAL = "behavioral"
    ARCHITECTURAL = "architectural"
    CONCURRENCY = "concurrency"
    ERROR_HANDLING = "error_handling"
    PERFORMANCE = "performance"
    SECURITY = "security"

@dataclass
class PatternMetadata:
    """Metadata for a pattern"""
    name: str
    type: PatternType
    category: PatternCategory
    description: str
    author: str
    version: str
    dependencies: List[str]
    requirements: List[str]
    examples: List[str]
    references: List[str]
    last_updated: datetime

@dataclass
class PatternMetrics:
    """Metrics for tracking pattern recognition performance"""
    recognition_rate: float
    false_positive_rate: float
    average_latency: float
    confidence_threshold: float
    last_update: datetime

@dataclass
class PatternContext:
    """Context information for pattern recognition"""
    current_code: str
    file_path: str
    language: str
    recent_matches: List[Dict[str, Any]]
    error_history: List[Dict[str, Any]]
    learning_data: Dict[str, Any]

class BasePatternRecognizer(ABC):
    """Base class for pattern recognizers"""
    
    def __init__(
        self,
        name: str,
        pattern_type: PatternType,
        category: PatternCategory,
        description: str,
        author: str,
        version: str,
        dependencies: List[str] = None,
        requirements: List[str] = None,
        examples: List[str] = None,
        references: List[str] = None
    ):
        self.name = name
        self.pattern_type = pattern_type
        self.category = category
        self.description = description
        self.author = author
        self.version = version
        self.dependencies = dependencies or []
        self.requirements = requirements or []
        self.examples = examples or []
        self.references = references or []
        
        self.metadata = PatternMetadata(
            name=name,
            type=pattern_type,
            category=category,
            description=description,
            author=author,
            version=version,
            dependencies=self.dependencies,
            requirements=self.requirements,
            examples=self.examples,
            references=self.references,
            last_updated=datetime.now()
        )
        
        self.metrics = PatternMetrics(
            recognition_rate=1.0,
            false_positive_rate=0.0,
            average_latency=0.0,
            confidence_threshold=0.8,
            last_update=datetime.now()
        )
        
        self.context = PatternContext(
            current_code="",
            file_path="",
            language="",
            recent_matches=[],
            error_history=[],
            learning_data={}
        )
        
        self._lock = asyncio.Lock()
        
    @abstractmethod
    async def recognize_pattern(self, code: str, **kwargs) -> Dict[str, Any]:
        """Recognize patterns in the given code"""
        pass
        
    async def validate_pattern(self, pattern_data: Dict[str, Any]) -> bool:
        """Validate recognized pattern data"""
        try:
            # Check required fields
            required_fields = ["pattern_type", "confidence", "location"]
            for field in required_fields:
                if field not in pattern_data:
                    logger.error(f"Missing required field: {field}")
                    return False
                    
            # Validate confidence
            confidence = pattern_data.get("confidence", 0)
            if not 0 <= confidence <= 1:
                logger.error("Invalid confidence value")
                return False
                
            # Validate location
            location = pattern_data.get("location", {})
            if not isinstance(location, dict):
                logger.error("Invalid location format")
                return False
                
            # Validate pattern type
            pattern_type = pattern_data.get("pattern_type")
            if not isinstance(pattern_type, PatternType):
                logger.error("Invalid pattern type")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error validating pattern: {str(e)}")
            return False
            
    async def update_metrics(self, recognition_result: Dict[str, Any]) -> None:
        """Update pattern recognition metrics"""
        try:
            # Update recognition rate
            if recognition_result.get("success", False):
                self.metrics.recognition_rate = (
                    self.metrics.recognition_rate * 0.9 +
                    0.1
                )
            else:
                self.metrics.false_positive_rate = (
                    self.metrics.false_positive_rate * 0.9 +
                    0.1
                )
                
            # Update latency
            if "latency" in recognition_result:
                self.metrics.average_latency = (
                    self.metrics.average_latency * 0.9 +
                    recognition_result["latency"] * 0.1
                )
                
            # Update confidence threshold
            if "confidence" in recognition_result:
                confidence = recognition_result["confidence"]
                if confidence > self.metrics.confidence_threshold:
                    self.metrics.confidence_threshold = (
                        self.metrics.confidence_threshold * 0.9 +
                        confidence * 0.1
                    )
                    
            self.metrics.last_update = datetime.now()
            
        except Exception as e:
            logger.error(f"Error updating metrics: {str(e)}")
            
    def get_metadata(self) -> PatternMetadata:
        """Get pattern metadata"""
        return self.metadata
        
    def get_metrics(self) -> PatternMetrics:
        """Get pattern metrics"""
        return self.metrics
        
    def get_context(self) -> PatternContext:
        """Get pattern context"""
        return self.context 