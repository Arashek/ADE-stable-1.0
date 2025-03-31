from typing import Dict, List, Optional, Any
import openai
from dataclasses import dataclass
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    """Configuration for LLM client."""
    model: str = "gpt-4"
    temperature: float = 0.2
    max_tokens: int = 1000
    top_p: float = 0.95
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None

@dataclass
class ErrorAnalysis:
    """Results from LLM error analysis."""
    primary_cause: str
    contributing_factors: List[str]
    suggested_fixes: List[str]
    confidence_score: float
    reasoning: str
    code_snippets: Optional[List[str]] = None  # New field for code examples
    prevention_strategies: Optional[List[str]] = None  # New field for prevention tips

class LLMClient:
    """Client for interacting with LLM services."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the LLM client.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self._setup_openai()
        
    def _load_config(self, config_path: Optional[str]) -> LLMConfig:
        """Load configuration from file or use defaults."""
        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                config_dict = json.load(f)
                return LLMConfig(**config_dict)
        return LLMConfig()
    
    def _setup_openai(self) -> None:
        """Set up OpenAI client with API key."""
        try:
            api_key = self._get_api_key()
            openai.api_key = api_key
        except Exception as e:
            logger.error(f"Failed to setup OpenAI client: {e}")
            raise
    
    def _get_api_key(self) -> str:
        """Get OpenAI API key from environment or config."""
        # Implementation would depend on your key management system
        # For now, we'll raise an error if not found
        api_key = "your-api-key-here"  # Replace with actual key management
        if not api_key:
            raise ValueError("OpenAI API key not found")
        return api_key
    
    def analyze_error(
        self,
        error_message: str,
        stack_trace: Optional[List[str]] = None,
        patterns: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ErrorAnalysis:
        """
        Analyze an error using LLM.
        
        Args:
            error_message: The error message
            stack_trace: Optional stack trace
            patterns: Optional list of detected patterns
            context: Optional error context
            
        Returns:
            ErrorAnalysis: Analysis results
        """
        try:
            # Prepare prompt
            prompt = self._create_analysis_prompt(
                error_message,
                stack_trace,
                patterns,
                context
            )
            
            # Get LLM response
            response = self._get_llm_response(prompt)
            
            # Parse and validate response
            analysis = self._parse_analysis_response(response)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error during LLM analysis: {e}")
            raise
    
    def _create_analysis_prompt(
        self,
        error_message: str,
        stack_trace: Optional[List[str]],
        patterns: Optional[List[Dict[str, Any]]],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Create prompt for error analysis."""
        prompt_parts = [
            "Analyze the following error and provide a detailed analysis:",
            f"\nError Message: {error_message}",
        ]
        
        if stack_trace:
            prompt_parts.append("\nStack Trace:")
            prompt_parts.extend(stack_trace)
            
        if patterns:
            prompt_parts.append("\nDetected Patterns:")
            for pattern in patterns:
                prompt_parts.append(f"- {pattern['type']}: {pattern['description']}")
                
        if context:
            prompt_parts.append("\nContext:")
            for key, value in context.items():
                prompt_parts.append(f"- {key}: {value}")
                
        prompt_parts.extend([
            "\nPlease provide:",
            "1. Primary cause of the error",
            "2. Contributing factors",
            "3. Suggested fixes",
            "4. Confidence score (0-1)",
            "5. Reasoning for the analysis"
        ])
        
        return "\n".join(prompt_parts)
    
    def _get_llm_response(self, prompt: str) -> str:
        """Get response from LLM."""
        try:
            response = openai.ChatCompletion.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are an expert error analysis assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p,
                frequency_penalty=self.config.frequency_penalty,
                presence_penalty=self.config.presence_penalty,
                stop=self.config.stop
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Failed to get LLM response: {e}")
            raise
    
    def _parse_analysis_response(self, response: str) -> ErrorAnalysis:
        """Parse and validate LLM response."""
        try:
            # Split response into sections
            sections = response.split("\n\n")
            
            # Extract information from sections
            primary_cause = self._extract_section(sections, "Primary cause")
            contributing_factors = self._extract_list(sections, "Contributing factors")
            suggested_fixes = self._extract_list(sections, "Suggested fixes")
            confidence_score = float(self._extract_section(sections, "Confidence score"))
            reasoning = self._extract_section(sections, "Reasoning")
            
            return ErrorAnalysis(
                primary_cause=primary_cause,
                contributing_factors=contributing_factors,
                suggested_fixes=suggested_fixes,
                confidence_score=confidence_score,
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            raise
    
    def _extract_section(self, sections: List[str], section_name: str) -> str:
        """Extract content from a named section."""
        for section in sections:
            if section.lower().startswith(section_name.lower()):
                return section.split(":", 1)[1].strip()
        return ""
    
    def _extract_list(self, sections: List[str], section_name: str) -> List[str]:
        """Extract list items from a named section."""
        section = self._extract_section(sections, section_name)
        if not section:
            return []
        return [item.strip("- ") for item in section.split("\n") if item.strip()]

    def analyze_errors_batch(
        self,
        errors: List[Dict[str, Any]],
        batch_size: int = 5
    ) -> List[ErrorAnalysis]:
        """
        Analyze multiple errors in batches.
        
        Args:
            errors: List of error dictionaries
            batch_size: Number of errors to analyze in each batch
            
        Returns:
            List[ErrorAnalysis]: List of analysis results
        """
        results = []
        for i in range(0, len(errors), batch_size):
            batch = errors[i:i + batch_size]
            batch_prompt = self._create_batch_analysis_prompt(batch)
            response = self._get_llm_response(batch_prompt)
            batch_results = self._parse_batch_response(response)
            results.extend(batch_results)
        return results

    def generate_error_fix(
        self,
        error: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate code fix for an error.
        
        Args:
            error: Error information
            context: Additional context
            
        Returns:
            Dict containing fix code and explanation
        """
        prompt = self._create_fix_generation_prompt(error, context)
        response = self._get_llm_response(prompt)
        return self._parse_fix_response(response)

    def suggest_error_prevention(
        self,
        error_patterns: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Suggest strategies to prevent similar errors.
        
        Args:
            error_patterns: List of error patterns
            context: Additional context
            
        Returns:
            Dict containing prevention strategies and recommendations
        """
        prompt = self._create_prevention_prompt(error_patterns, context)
        response = self._get_llm_response(prompt)
        return self._parse_prevention_response(response)

    def _create_batch_analysis_prompt(self, errors: List[Dict[str, Any]]) -> str:
        """Create prompt for batch error analysis."""
        prompt_parts = [
            "Analyze the following errors and provide detailed analysis for each:",
        ]
        
        for i, error in enumerate(errors, 1):
            prompt_parts.extend([
                f"\nError {i}:",
                f"Message: {error.get('message', '')}",
                f"Type: {error.get('type', 'unknown')}",
                f"Context: {error.get('context', {})}"
            ])
            
        prompt_parts.extend([
            "\nFor each error, provide:",
            "1. Primary cause",
            "2. Contributing factors",
            "3. Suggested fixes",
            "4. Confidence score (0-1)",
            "5. Reasoning",
            "6. Code snippets (if applicable)",
            "7. Prevention strategies"
        ])
        
        return "\n".join(prompt_parts)

    def _create_fix_generation_prompt(
        self,
        error: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Create prompt for code fix generation."""
        prompt_parts = [
            "Generate a code fix for the following error:",
            f"\nError Message: {error.get('message', '')}",
            f"Type: {error.get('type', 'unknown')}",
            f"Location: {error.get('location', 'unknown')}",
        ]
        
        if context:
            prompt_parts.append("\nContext:")
            for key, value in context.items():
                prompt_parts.append(f"- {key}: {value}")
                
        prompt_parts.extend([
            "\nPlease provide:",
            "1. Fixed code snippet",
            "2. Explanation of the fix",
            "3. Any additional considerations",
            "4. Alternative approaches (if applicable)"
        ])
        
        return "\n".join(prompt_parts)

    def _create_prevention_prompt(
        self,
        patterns: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Create prompt for error prevention suggestions."""
        prompt_parts = [
            "Based on the following error patterns, suggest prevention strategies:",
        ]
        
        for pattern in patterns:
            prompt_parts.extend([
                f"\nPattern: {pattern.get('type', 'unknown')}",
                f"Frequency: {pattern.get('frequency', 0)}",
                f"Description: {pattern.get('description', '')}"
            ])
            
        if context:
            prompt_parts.append("\nContext:")
            for key, value in context.items():
                prompt_parts.append(f"- {key}: {value}")
                
        prompt_parts.extend([
            "\nPlease provide:",
            "1. Prevention strategies",
            "2. Best practices",
            "3. Code examples",
            "4. Monitoring suggestions"
        ])
        
        return "\n".join(prompt_parts)

    def _parse_batch_response(self, response: str) -> List[ErrorAnalysis]:
        """Parse response from batch analysis."""
        results = []
        sections = response.split("\n\nError")
        
        for section in sections[1:]:  # Skip the first empty section
            try:
                analysis = self._parse_analysis_response(section)
                results.append(analysis)
            except Exception as e:
                logger.error(f"Failed to parse batch section: {e}")
                continue
                
        return results

    def _parse_fix_response(self, response: str) -> Dict[str, Any]:
        """Parse response from fix generation."""
        try:
            sections = response.split("\n\n")
            return {
                "code": self._extract_section(sections, "Fixed code snippet"),
                "explanation": self._extract_section(sections, "Explanation"),
                "considerations": self._extract_list(sections, "Additional considerations"),
                "alternatives": self._extract_list(sections, "Alternative approaches")
            }
        except Exception as e:
            logger.error(f"Failed to parse fix response: {e}")
            raise

    def _parse_prevention_response(self, response: str) -> Dict[str, Any]:
        """Parse response from prevention suggestions."""
        try:
            sections = response.split("\n\n")
            return {
                "strategies": self._extract_list(sections, "Prevention strategies"),
                "best_practices": self._extract_list(sections, "Best practices"),
                "code_examples": self._extract_list(sections, "Code examples"),
                "monitoring": self._extract_list(sections, "Monitoring suggestions")
            }
        except Exception as e:
            logger.error(f"Failed to parse prevention response: {e}")
            raise 