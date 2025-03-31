from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging
from datetime import datetime

from src.core.providers import ProviderRegistry, Capability
from src.core.providers.response import TextResponse, PlanResponse

logger = logging.getLogger(__name__)

@dataclass
class TaskResult:
    """Result of a processed task"""
    success: bool
    output: Any
    provider: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()

class AITaskProcessor:
    """Processes development tasks using AI models through the Provider Registry"""
    
    def __init__(self, provider_registry: ProviderRegistry):
        self.provider_registry = provider_registry
        self.task_history: List[TaskResult] = []
        
    async def process_task(
        self,
        task_description: str,
        required_capabilities: List[Capability],
        context: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        **kwargs
    ) -> TaskResult:
        """Process a development task using appropriate AI models
        
        Args:
            task_description: Description of the task to process
            required_capabilities: List of capabilities needed for the task
            context: Additional context for the task
            max_retries: Maximum number of retry attempts
            **kwargs: Additional parameters for the task
            
        Returns:
            TaskResult containing the processed task output
        """
        context = context or {}
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Get best provider for the task
                provider = self.provider_registry.get_provider_for_capability(
                    required_capabilities[0],  # Use primary capability for provider selection
                    context
                )
                
                if not provider:
                    raise ValueError("No suitable provider found for task capabilities")
                
                # Formulate prompt based on task and context
                prompt = self._formulate_prompt(task_description, context)
                
                # Process task based on primary capability
                if Capability.TEXT_GENERATION in required_capabilities:
                    response = await provider.generate_text(prompt, **kwargs)
                elif Capability.PLAN_CREATION in required_capabilities:
                    response = await provider.create_plan(prompt, **kwargs)
                else:
                    raise ValueError(f"Unsupported capability: {required_capabilities[0]}")
                
                # Validate response
                if not response.success:
                    raise ValueError(f"Provider error: {response.error}")
                
                # Create task result
                result = TaskResult(
                    success=True,
                    output=response.text if isinstance(response, TextResponse) else response.plan,
                    provider=provider.name,
                    metadata={
                        "capabilities_used": required_capabilities,
                        "context": context,
                        "retry_count": retry_count
                    }
                )
                
                # Add to history
                self.task_history.append(result)
                
                return result
                
            except Exception as e:
                retry_count += 1
                logger.error(f"Task processing error (attempt {retry_count}/{max_retries}): {str(e)}")
                
                if retry_count == max_retries:
                    return TaskResult(
                        success=False,
                        output=None,
                        provider="none",
                        error=f"Task processing failed after {max_retries} attempts: {str(e)}",
                        metadata={
                            "capabilities_attempted": required_capabilities,
                            "context": context,
                            "retry_count": retry_count
                        }
                    )
                
                # Wait before retry
                await asyncio.sleep(1 * retry_count)
    
    def _formulate_prompt(self, task_description: str, context: Dict[str, Any]) -> str:
        """Formulate an appropriate prompt for the AI model
        
        Args:
            task_description: Description of the task
            context: Additional context for the task
            
        Returns:
            Formatted prompt string
        """
        # Build prompt from task description and context
        prompt_parts = [task_description]
        
        if context:
            prompt_parts.append("\nContext:")
            for key, value in context.items():
                prompt_parts.append(f"{key}: {value}")
        
        return "\n".join(prompt_parts)
    
    def get_task_history(self) -> List[TaskResult]:
        """Get history of processed tasks"""
        return self.task_history
    
    def clear_history(self) -> None:
        """Clear the task history"""
        self.task_history = [] 