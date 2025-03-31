"""DeepSeek API provider implementation."""
from typing import Dict, List, Optional, Any
import logging
import aiohttp
import json
from datetime import datetime
from langchain_community.chat_models import ChatDeepSeek
from langchain.schema import HumanMessage, SystemMessage
from ..base import BaseModelProvider
from ...config import config

from src.core.models.providers.base import ModelProvider
from src.core.models.types import ModelCapability, ProviderResponse
from src.utils.encryption import encrypt_value, decrypt_value

# Configure logging
logger = logging.getLogger("ade-deepseek-provider")

class DeepSeekProvider(BaseModelProvider):
    """Provider implementation for DeepSeek Coder model"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the DeepSeek provider"""
        super().__init__()
        self.api_key = api_key or config.models.deepseek_api_key
        if not self.api_key:
            raise ValueError("DeepSeek API key is required")
            
        self.model = ChatDeepSeek(
            model="deepseek-coder-33b-instruct",
            temperature=0.2,
            api_key=self.api_key
        )
        
        # Initialize model capabilities with enhanced support
        self.capabilities = {
            "code_generation": True,
            "code_understanding": True,
            "code_explanation": True,
            "planning": True,
            "reasoning": True,
            "debugging": True,
            "documentation": True,
            "tool_use": True,
            "code_review": True,
            "code_optimization": True,
            "test_generation": True,
            "security_analysis": True
        }
        
        # Initialize performance tracking with enhanced metrics
        self.performance_metrics = {
            "success_rate": 0.0,
            "latency": 0.0,
            "error_rate": 0.0,
            "cost_per_token": 0.0,
            "code_quality_score": 0.0,
            "response_consistency": 0.0
        }
        
        # Initialize specialized prompts for different tasks
        self.task_prompts = {
            "code_generation": """You are an expert code generator. Generate high-quality, efficient, and well-documented code that follows best practices.
            Consider edge cases, error handling, and performance optimization.""",
            
            "code_understanding": """You are an expert code analyzer. Provide detailed analysis of the code structure, algorithms, and design patterns used.
            Identify potential improvements and areas of concern.""",
            
            "code_explanation": """You are an expert code explainer. Provide clear, concise, and comprehensive explanations of the code.
            Use examples and analogies where appropriate to improve understanding.""",
            
            "planning": """You are an expert task planner. Create detailed, actionable plans that consider dependencies, resources, and potential risks.
            Break down complex tasks into manageable steps.""",
            
            "reasoning": """You are an expert code reasoner. Analyze code logic and provide sound reasoning about its behavior and implications.
            Consider edge cases and potential issues.""",
            
            "debugging": """You are an expert debugger. Analyze code and errors to identify root causes and provide effective solutions.
            Consider common pitfalls and best practices for debugging.""",
            
            "documentation": """You are an expert technical writer. Generate comprehensive documentation that is clear, accurate, and useful.
            Include examples, API references, and usage guidelines.""",
            
            "tool_use": """You are an expert tool user. Select and use appropriate tools to complete tasks efficiently and effectively.
            Consider tool capabilities, limitations, and best practices.""",
            
            "code_review": """You are an expert code reviewer. Provide thorough, constructive feedback on code quality, style, and best practices.
            Consider maintainability, readability, and performance.""",
            
            "code_optimization": """You are an expert code optimizer. Analyze code for performance bottlenecks and suggest optimizations.
            Consider algorithmic complexity, memory usage, and execution time.""",
            
            "test_generation": """You are an expert test generator. Create comprehensive test suites that cover edge cases and error conditions.
            Consider unit tests, integration tests, and performance tests.""",
            
            "security_analysis": """You are an expert security analyst. Identify potential security vulnerabilities and suggest improvements.
            Consider common attack vectors and security best practices."""
        }
    
    async def generate_code(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate code using DeepSeek Coder"""
        messages = self._prepare_messages(prompt, context, "code_generation")
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    async def understand_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Understand code using DeepSeek Coder"""
        prompt = f"Please analyze and explain the following code:\n\n{code}"
        messages = self._prepare_messages(prompt, context, "code_understanding")
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    async def explain_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Explain code using DeepSeek Coder"""
        prompt = f"Please provide a detailed explanation of the following code:\n\n{code}"
        messages = self._prepare_messages(prompt, context, "code_explanation")
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    async def plan_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Plan a task using DeepSeek Coder"""
        prompt = f"Please create a detailed plan for the following task:\n\n{task}"
        messages = self._prepare_messages(prompt, context, "planning")
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    async def reason_about_code(self, code: str, question: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Reason about code using DeepSeek Coder"""
        prompt = f"Given the following code:\n\n{code}\n\nPlease answer this question: {question}"
        messages = self._prepare_messages(prompt, context, "reasoning")
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    async def debug_code(self, code: str, error: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Debug code using DeepSeek Coder"""
        prompt = f"Please help debug the following code that has this error:\n\n{code}\n\nError: {error}"
        messages = self._prepare_messages(prompt, context, "debugging")
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    async def generate_documentation(self, code: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate documentation using DeepSeek Coder"""
        prompt = f"Please generate comprehensive documentation for the following code:\n\n{code}"
        messages = self._prepare_messages(prompt, context, "documentation")
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    async def use_tools(self, task: str, available_tools: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> str:
        """Use tools with DeepSeek Coder"""
        tools_desc = "\n".join([f"- {tool['name']}: {tool['description']}" for tool in available_tools])
        prompt = f"Given these available tools:\n\n{tools_desc}\n\nPlease complete this task: {task}"
        messages = self._prepare_messages(prompt, context, "tool_use")
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    async def review_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Review code using DeepSeek Coder"""
        prompt = f"Please review the following code and provide feedback:\n\n{code}"
        messages = self._prepare_messages(prompt, context, "code_review")
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    async def optimize_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Optimize code using DeepSeek Coder"""
        prompt = f"Please optimize the following code for better performance:\n\n{code}"
        messages = self._prepare_messages(prompt, context, "code_optimization")
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    async def generate_tests(self, code: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate tests using DeepSeek Coder"""
        prompt = f"Please generate comprehensive tests for the following code:\n\n{code}"
        messages = self._prepare_messages(prompt, context, "test_generation")
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    async def analyze_security(self, code: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Analyze code security using DeepSeek Coder"""
        prompt = f"Please analyze the security of the following code:\n\n{code}"
        messages = self._prepare_messages(prompt, context, "security_analysis")
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    def _prepare_messages(self, prompt: str, context: Optional[Dict[str, Any]] = None, task_type: str = "general") -> List[Any]:
        """Prepare messages for the model with specialized prompts"""
        messages = []
        
        # Add system message with specialized prompt
        system_prompt = self.task_prompts.get(task_type, "")
        if context and "system_prompt" in context:
            system_prompt = f"{system_prompt}\n\n{context['system_prompt']}"
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
            
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

    @property
    def provider_type(self) -> str:
        return "deepseek"
    
    def initialize(self) -> bool:
        """Initialize the DeepSeek client"""
        try:
            # No specific client to initialize
            self.is_initialized = True
            logger.info(f"DeepSeek provider initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek provider: {str(e)}")
            self.is_initialized = False
            return False
    
    def list_available_models(self) -> List[str]:
        """List all available models from DeepSeek"""
        # DeepSeek doesn't have a model listing API, return hardcoded values
        return [
            "deepseek-coder-33b-instruct",
            "deepseek-coder-6.7b-instruct",
            "deepseek-llm-67b-chat",
            "deepseek-llm-7b-chat"
        ]
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        images: Optional[List[bytes]] = None
    ) -> ProviderResponse:
        """Generate text from a prompt using DeepSeek"""
        if not self.is_initialized:
            raise Exception("DeepSeek provider not initialized")
        
        # Use default model if not specified
        if not model:
            model = self.model_map.get(ModelCapability.CHAT, "deepseek-llm-67b-chat")
        
        # Merge default parameters with provided parameters
        params = {**self.default_parameters}
        if parameters:
            params.update(parameters)
        
        try:
            # DeepSeek API endpoint
            endpoint = f"{self.base_url}/chat/completions"
            
            # Prepare request data
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                **params
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                start_time = datetime.now()
                async with session.post(endpoint, json=data, headers=headers) as response:
                    response_time = (datetime.now() - start_time).total_seconds() * 1000  # in ms
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"DeepSeek API error: {response.status} - {error_text}")
                        
                        # Record failure
                        self.performance.record_failure(response_time)
                        
                        raise Exception(f"DeepSeek API error: {response.status} - {error_text}")
                    
                    # Parse response
                    response_json = await response.json()
                    
                    # Extract content
                    content = response_json["choices"][0]["message"]["content"]
                    
                    # Calculate token usage
                    tokens = 0
                    if "usage" in response_json:
                        tokens = response_json["usage"].get("total_tokens", 0)
                    
                    # Record success
                    self.performance.record_success(response_time, tokens)
                    
                    return ProviderResponse(
                        content=content,
                        raw_response=response_json,
                        metadata={
                            "model": model,
                            "response_time_ms": response_time,
                            "tokens": tokens
                        }
                    )
                    
        except Exception as e:
            logger.error(f"DeepSeek generation error: {str(e)}")
            self.performance.record_failure()
            raise 