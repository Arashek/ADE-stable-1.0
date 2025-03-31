from typing import Optional, Dict, Any, List
from langchain_community.chat_models import ChatPaLM
from langchain.schema import HumanMessage, SystemMessage
from ..base import BaseModelProvider
from ...config import config

class PaLMProvider(BaseModelProvider):
    """Provider implementation for Google's PaLM 2 model"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the PaLM provider"""
        super().__init__()
        self.api_key = api_key or config.models.palm_api_key
        if not self.api_key:
            raise ValueError("PaLM API key is required")
            
        self.model = ChatPaLM(
            model="palm-2",
            temperature=0.2,
            api_key=self.api_key
        )
        
        # Initialize model capabilities
        self.capabilities = {
            "code_generation": True,
            "code_understanding": True,
            "code_explanation": True,
            "planning": True,
            "reasoning": True,
            "debugging": True,
            "documentation": True,
            "tool_use": True,
            "code_review": True
        }
        
        # Initialize performance tracking
        self.performance_metrics = {
            "success_rate": 0.0,
            "latency": 0.0,
            "error_rate": 0.0,
            "cost_per_token": 0.0
        }
    
    async def generate_code(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate code using PaLM 2"""
        messages = self._prepare_messages(prompt, context)
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    async def understand_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Understand code using PaLM 2"""
        prompt = f"Please analyze and explain the following code:\n\n{code}"
        messages = self._prepare_messages(prompt, context)
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    async def explain_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Explain code using PaLM 2"""
        prompt = f"Please provide a detailed explanation of the following code:\n\n{code}"
        messages = self._prepare_messages(prompt, context)
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    async def plan_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Plan a task using PaLM 2"""
        prompt = f"Please create a detailed plan for the following task:\n\n{task}"
        messages = self._prepare_messages(prompt, context)
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    async def reason_about_code(self, code: str, question: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Reason about code using PaLM 2"""
        prompt = f"Given the following code:\n\n{code}\n\nPlease answer this question: {question}"
        messages = self._prepare_messages(prompt, context)
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    async def debug_code(self, code: str, error: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Debug code using PaLM 2"""
        prompt = f"Please help debug the following code that has this error:\n\n{code}\n\nError: {error}"
        messages = self._prepare_messages(prompt, context)
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    async def generate_documentation(self, code: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate documentation using PaLM 2"""
        prompt = f"Please generate comprehensive documentation for the following code:\n\n{code}"
        messages = self._prepare_messages(prompt, context)
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    async def use_tools(self, task: str, available_tools: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> str:
        """Use tools with PaLM 2"""
        tools_desc = "\n".join([f"- {tool['name']}: {tool['description']}" for tool in available_tools])
        prompt = f"Given these available tools:\n\n{tools_desc}\n\nPlease complete this task: {task}"
        messages = self._prepare_messages(prompt, context)
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    async def review_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Review code using PaLM 2"""
        prompt = f"Please review the following code and provide feedback:\n\n{code}"
        messages = self._prepare_messages(prompt, context)
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    def _prepare_messages(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> List[Any]:
        """Prepare messages for the model"""
        messages = []
        
        # Add system message if context provided
        if context and "system_prompt" in context:
            messages.append(SystemMessage(content=context["system_prompt"]))
            
        # Add human message
        messages.append(HumanMessage(content=prompt))
        
        return messages
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this provider"""
        return self.capabilities
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get the performance metrics of this provider"""
        return self.performance_metrics
    
    def update_performance_metrics(self, metrics: Dict[str, float]):
        """Update the performance metrics of this provider"""
        for key, value in metrics.items():
            if key in self.performance_metrics:
                self.performance_metrics[key] = (
                    0.9 * self.performance_metrics[key] + 0.1 * value
                ) 