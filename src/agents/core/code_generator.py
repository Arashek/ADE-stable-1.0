from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import logging
import ast
import re
from datetime import datetime

from src.core.providers import ProviderRegistry, Capability
from src.core.providers.response import TextResponse
from .task_processor import AITaskProcessor, TaskResult

logger = logging.getLogger(__name__)

@dataclass
class CodeGenerationResult:
    """Result of code generation"""
    success: bool
    code: str
    documentation: str
    provider: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()

class CodeGenerationEngine:
    """Engine for generating and validating code using AI models"""
    
    def __init__(self, provider_registry: ProviderRegistry):
        self.provider_registry = provider_registry
        self.task_processor = AITaskProcessor(provider_registry)
        self.generation_history: List[CodeGenerationResult] = []
        
    async def generate_code(
        self,
        requirements: str,
        language: str,
        framework: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        max_iterations: int = 3,
        **kwargs
    ) -> CodeGenerationResult:
        """Generate code from high-level requirements
        
        Args:
            requirements: High-level requirements for the code
            language: Target programming language
            framework: Optional framework to use
            context: Additional context for generation
            max_iterations: Maximum number of refinement iterations
            **kwargs: Additional parameters for generation
            
        Returns:
            CodeGenerationResult containing the generated code
        """
        context = context or {}
        iteration = 0
        
        while iteration < max_iterations:
            try:
                # Prepare generation context
                gen_context = {
                    **context,
                    "language": language,
                    "framework": framework,
                    "iteration": iteration,
                    "previous_code": context.get("previous_code") if iteration > 0 else None
                }
                
                # Generate code using task processor
                result = await self.task_processor.process_task(
                    task_description=self._create_code_prompt(requirements, gen_context),
                    required_capabilities=[Capability.CODE_GENERATION],
                    context=gen_context,
                    **kwargs
                )
                
                if not result.success:
                    raise ValueError(f"Code generation failed: {result.error}")
                
                # Extract code and documentation
                code, documentation = self._extract_code_and_docs(result.output)
                
                # Validate generated code
                validation_result = self._validate_code(code, language)
                if not validation_result[0]:
                    if iteration < max_iterations - 1:
                        # Add validation error to context for next iteration
                        context["validation_error"] = validation_result[1]
                        iteration += 1
                        continue
                    else:
                        raise ValueError(f"Code validation failed: {validation_result[1]}")
                
                # Create generation result
                gen_result = CodeGenerationResult(
                    success=True,
                    code=code,
                    documentation=documentation,
                    provider=result.provider,
                    metadata={
                        "language": language,
                        "framework": framework,
                        "iterations": iteration + 1,
                        "validation_passed": True
                    }
                )
                
                # Add to history
                self.generation_history.append(gen_result)
                
                return gen_result
                
            except Exception as e:
                logger.error(f"Code generation error (iteration {iteration}/{max_iterations}): {str(e)}")
                
                if iteration == max_iterations - 1:
                    return CodeGenerationResult(
                        success=False,
                        code="",
                        documentation="",
                        provider="none",
                        error=f"Code generation failed after {max_iterations} iterations: {str(e)}",
                        metadata={
                            "language": language,
                            "framework": framework,
                            "iterations": iteration + 1,
                            "error": str(e)
                        }
                    )
                
                iteration += 1
    
    def _create_code_prompt(self, requirements: str, context: Dict[str, Any]) -> str:
        """Create a prompt for code generation
        
        Args:
            requirements: High-level requirements
            context: Generation context
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = [
            f"Generate code in {context['language']}",
            f"Requirements: {requirements}"
        ]
        
        if context.get("framework"):
            prompt_parts.append(f"Using framework: {context['framework']}")
            
        if context.get("previous_code"):
            prompt_parts.append("\nPrevious code (needs improvement):")
            prompt_parts.append(context["previous_code"])
            
        if context.get("validation_error"):
            prompt_parts.append("\nPrevious validation error:")
            prompt_parts.append(context["validation_error"])
            
        return "\n".join(prompt_parts)
    
    def _extract_code_and_docs(self, response: str) -> Tuple[str, str]:
        """Extract code and documentation from AI response
        
        Args:
            response: Raw response from AI model
            
        Returns:
            Tuple of (code, documentation)
        """
        # Split response into code and documentation
        parts = response.split("\n\n")
        
        # First part is documentation
        documentation = parts[0].strip()
        
        # Find code blocks
        code_blocks = []
        for part in parts[1:]:
            # Look for code block markers
            if "```" in part:
                # Extract code between markers
                code_match = re.search(r"```(?:.*\n)?(.*?)```", part, re.DOTALL)
                if code_match:
                    code_blocks.append(code_match.group(1).strip())
        
        code = "\n\n".join(code_blocks)
        
        return code, documentation
    
    def _validate_code(self, code: str, language: str) -> Tuple[bool, Optional[str]]:
        """Validate generated code
        
        Args:
            code: Code to validate
            language: Programming language
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if language.lower() == "python":
                # Parse Python code to check syntax
                ast.parse(code)
                return True, None
            else:
                # For other languages, basic validation
                if not code.strip():
                    return False, "Empty code"
                return True, None
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def get_generation_history(self) -> List[CodeGenerationResult]:
        """Get history of code generations"""
        return self.generation_history
    
    def clear_history(self) -> None:
        """Clear the generation history"""
        self.generation_history = [] 