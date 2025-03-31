from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass
import logging
import re
import json
from datetime import datetime

from src.core.providers import ProviderRegistry, Capability
from .task_processor import AITaskProcessor, TaskResult

logger = logging.getLogger(__name__)

@dataclass
class ParsedResponse:
    """Parsed and validated AI response"""
    content_type: str  # 'text', 'code', 'json', 'list', 'table'
    content: Any
    metadata: Dict[str, Any]
    confidence: float
    timestamp: datetime = datetime.now()

class ResponseInterpreter:
    """Interprets and validates AI model responses"""
    
    def __init__(self, provider_registry: ProviderRegistry):
        self.provider_registry = provider_registry
        self.task_processor = AITaskProcessor(provider_registry)
        self.interpretation_history: List[ParsedResponse] = []
        
    async def interpret_response(
        self,
        response: str,
        expected_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ParsedResponse:
        """Interpret an AI model response
        
        Args:
            response: Raw response from AI model
            expected_type: Expected type of response (optional)
            context: Additional context for interpretation
            **kwargs: Additional parameters for interpretation
            
        Returns:
            ParsedResponse containing interpreted content
        """
        try:
            # First, try to detect the response type
            content_type = self._detect_content_type(response)
            
            # If expected type is specified, validate against it
            if expected_type and content_type != expected_type:
                logger.warning(f"Response type mismatch: expected {expected_type}, got {content_type}")
            
            # Parse content based on type
            content = self._parse_content(response, content_type)
            
            # Validate content
            validation_result = self._validate_content(content, content_type)
            if not validation_result[0]:
                raise ValueError(f"Content validation failed: {validation_result[1]}")
            
            # Extract metadata
            metadata = self._extract_metadata(response, content_type)
            
            # Calculate confidence
            confidence = self._calculate_confidence(content, content_type, context)
            
            # Create parsed response
            parsed = ParsedResponse(
                content_type=content_type,
                content=content,
                metadata=metadata,
                confidence=confidence
            )
            
            # Add to history
            self.interpretation_history.append(parsed)
            
            return parsed
            
        except Exception as e:
            logger.error(f"Response interpretation failed: {str(e)}")
            raise
    
    def _detect_content_type(self, response: str) -> str:
        """Detect the type of content in the response
        
        Args:
            response: Raw response text
            
        Returns:
            Detected content type
        """
        # Check for code blocks
        if re.search(r"```[\s\S]*?```", response):
            return "code"
            
        # Check for JSON
        try:
            json.loads(response)
            return "json"
        except:
            pass
            
        # Check for table format
        if re.search(r"\|.*\|", response):
            return "table"
            
        # Check for list format
        if re.search(r"^\s*[-*]\s+", response, re.MULTILINE):
            return "list"
            
        # Default to text
        return "text"
    
    def _parse_content(self, response: str, content_type: str) -> Any:
        """Parse content based on type
        
        Args:
            response: Raw response text
            content_type: Type of content to parse
            
        Returns:
            Parsed content
        """
        if content_type == "code":
            # Extract code from code blocks
            code_blocks = re.findall(r"```(?:.*\n)?(.*?)```", response, re.DOTALL)
            return "\n\n".join(block.strip() for block in code_blocks)
            
        elif content_type == "json":
            # Parse JSON
            return json.loads(response)
            
        elif content_type == "table":
            # Parse table format
            lines = response.strip().split("\n")
            if len(lines) < 3:  # Need header, separator, and at least one row
                raise ValueError("Invalid table format")
                
            # Parse header
            header = [cell.strip() for cell in lines[0].split("|")[1:-1]]
            
            # Skip separator line
            # Parse data rows
            data = []
            for line in lines[2:]:
                cells = [cell.strip() for cell in line.split("|")[1:-1]]
                if len(cells) == len(header):
                    data.append(dict(zip(header, cells)))
                    
            return data
            
        elif content_type == "list":
            # Parse list format
            items = []
            for line in response.split("\n"):
                if re.match(r"^\s*[-*]\s+", line):
                    items.append(line.lstrip("-* ").strip())
            return items
            
        else:  # text
            return response.strip()
    
    def _validate_content(self, content: Any, content_type: str) -> Tuple[bool, Optional[str]]:
        """Validate parsed content
        
        Args:
            content: Parsed content to validate
            content_type: Type of content
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if content_type == "code":
                # Basic code validation
                if not content.strip():
                    return False, "Empty code"
                return True, None
                
            elif content_type == "json":
                # JSON validation
                if not isinstance(content, (dict, list)):
                    return False, "Invalid JSON structure"
                return True, None
                
            elif content_type == "table":
                # Table validation
                if not isinstance(content, list):
                    return False, "Invalid table format"
                if not content:
                    return False, "Empty table"
                return True, None
                
            elif content_type == "list":
                # List validation
                if not isinstance(content, list):
                    return False, "Invalid list format"
                if not content:
                    return False, "Empty list"
                return True, None
                
            else:  # text
                if not isinstance(content, str):
                    return False, "Invalid text format"
                if not content.strip():
                    return False, "Empty text"
                return True, None
                
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _extract_metadata(self, response: str, content_type: str) -> Dict[str, Any]:
        """Extract metadata from response
        
        Args:
            response: Raw response text
            content_type: Type of content
            
        Returns:
            Dictionary of metadata
        """
        metadata = {
            "content_type": content_type,
            "raw_length": len(response),
            "timestamp": datetime.now().isoformat()
        }
        
        if content_type == "code":
            # Extract language from code block
            lang_match = re.search(r"```(\w+)", response)
            if lang_match:
                metadata["language"] = lang_match.group(1)
                
        elif content_type == "table":
            # Count rows and columns
            lines = response.strip().split("\n")
            if len(lines) >= 3:
                header = [cell.strip() for cell in lines[0].split("|")[1:-1]]
                metadata["columns"] = len(header)
                metadata["rows"] = len(lines) - 2  # Subtract header and separator
                
        elif content_type == "list":
            # Count items
            items = [line for line in response.split("\n") if re.match(r"^\s*[-*]\s+", line)]
            metadata["item_count"] = len(items)
            
        return metadata
    
    def _calculate_confidence(
        self,
        content: Any,
        content_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate confidence score for parsed content
        
        Args:
            content: Parsed content
            content_type: Type of content
            context: Additional context
            
        Returns:
            Confidence score between 0 and 1
        """
        confidence = 1.0
        
        # Adjust confidence based on content type
        if content_type == "code":
            # Check for common code issues
            if re.search(r"TODO|FIXME|XXX", str(content)):
                confidence *= 0.8
            if re.search(r"pass|raise NotImplementedError", str(content)):
                confidence *= 0.7
                
        elif content_type == "json":
            # Check for required fields if specified in context
            if context and "required_fields" in context:
                required = set(context["required_fields"])
                if isinstance(content, dict):
                    present = set(content.keys())
                    confidence *= len(present.intersection(required)) / len(required)
                    
        elif content_type == "table":
            # Check for data consistency
            if isinstance(content, list) and content:
                row_lengths = set(len(row) for row in content)
                if len(row_lengths) > 1:
                    confidence *= 0.8
                    
        elif content_type == "list":
            # Check for list completeness
            if isinstance(content, list) and context and "expected_items" in context:
                expected = set(context["expected_items"])
                present = set(content)
                confidence *= len(present.intersection(expected)) / len(expected)
                
        return min(max(confidence, 0.0), 1.0)
    
    def get_interpretation_history(self) -> List[ParsedResponse]:
        """Get history of interpreted responses"""
        return self.interpretation_history
    
    def clear_history(self) -> None:
        """Clear the interpretation history"""
        self.interpretation_history = [] 