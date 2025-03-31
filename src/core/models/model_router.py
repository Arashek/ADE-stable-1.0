from langchain_community.chat_models import ChatOpenAI, ChatAnthropic, ChatPaLM
import google.generativeai as genai
from typing import Optional, Dict, List, Any, Union
from pydantic import BaseModel
import os
from src.core.config import config
from .types import ModelCapability, ProviderType, ProviderResponse

class TaskRequest(BaseModel):
    """A request for a model to perform a task"""
    task_type: str
    content: str
    image_data: Optional[bytes] = None
    temperature: float = 0.2
    options: Dict[str, Any] = {}
    budget: Optional[float] = None

class ModelResponse(BaseModel):
    """Response from a model"""
    content: str
    model_used: str
    metadata: Dict[str, Any] = {}

class ModelRouter:
    """Routes tasks to appropriate AI models based on capabilities and availability"""
    
    def __init__(self):
        self._initialize_models()
        self._setup_capabilities()
        self._initialize_metrics()
        
    def _initialize_metrics(self):
        """Initialize performance and cost tracking metrics"""
        self.performance_metrics = {
            "success_rate": {},
            "latency": {},
            "error_rate": {},
            "cost_per_token": {}
        }
        self.model_health = {}
        
    def _initialize_models(self):
        """Initialize connections to various models"""
        self.models = {}
        
        # Initialize OpenAI models if API key is available
        if config.models.openai_api_key:
            self.models["gpt4"] = ChatOpenAI(
                model="gpt-4-turbo-preview",
                temperature=0.2,
                api_key=config.models.openai_api_key
            )
            
        # Initialize Anthropic models if API key is available
        if config.models.anthropic_api_key:
            self.models["claude"] = ChatAnthropic(
                model="claude-3-opus-20240229",
                temperature=0.1,
                api_key=config.models.anthropic_api_key
            )
            
        # Initialize DeepSeek models if API key is available
        if config.models.deepseek_api_key:
            self.models["deepseek"] = ChatDeepSeek(
                model="deepseek-coder-33b-instruct",
                temperature=0.2,
                api_key=config.models.deepseek_api_key
            )
            
        # Initialize Groq models if API key is available
        if config.models.groq_api_key:
            self.models["groq"] = ChatGroq(
                model="mixtral-8x7b-32768",
                temperature=0.2,
                api_key=config.models.groq_api_key
            )
            
        # Initialize PaLM 2 if API key is available
        if config.models.palm_api_key:
            self.models["palm"] = ChatPaLM(
                model="palm-2",
                temperature=0.2,
                api_key=config.models.palm_api_key
            )
    
    def _setup_capabilities(self):
        """Define which models are best for which tasks"""
        self.capabilities = {
            "code_generation": ["deepseek", "claude", "gpt4", "groq", "palm"],
            "code_understanding": ["deepseek", "claude", "gpt4", "palm"],
            "code_explanation": ["claude", "gpt4", "deepseek", "palm"],
            "planning": ["claude", "gpt4", "groq", "palm"],
            "reasoning": ["claude", "gpt4", "deepseek", "groq", "palm"],
            "debugging": ["gpt4", "claude", "deepseek", "palm"],
            "documentation": ["claude", "gpt4", "deepseek", "palm"],
            "tool_use": ["claude", "gpt4", "deepseek", "palm"],
            "code_review": ["claude", "gpt4", "deepseek", "palm"]
        }
        
        # Track which models are actually available
        self.available_capabilities = {}
        for capability, model_list in self.capabilities.items():
            self.available_capabilities[capability] = [
                model for model in model_list if model in self.models
            ]
            
        # Define model tiers for cost optimization
        self.model_tiers = {
            "premium": ["gpt4", "claude"],
            "standard": ["deepseek", "palm"],
            "economy": ["groq"]
        }
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Returns mapping of capabilities to available models"""
        return self.available_capabilities
    
    def get_model_for_capability(self, capability: str, budget: Optional[float] = None) -> Optional[str]:
        """Get the best available model for a specific capability based on performance and cost"""
        if capability not in self.available_capabilities:
            return None
            
        available_models = self.available_capabilities[capability]
        if not available_models:
            return None
            
        # Get performance metrics for available models
        model_scores = {}
        for model in available_models:
            score = self._calculate_model_score(model, capability)
            if budget and not self._is_within_budget(model, budget):
                continue
            model_scores[model] = score
            
        if not model_scores:
            return None
            
        # Return model with highest score
        return max(model_scores.items(), key=lambda x: x[1])[0]
    
    def _calculate_model_score(self, model: str, capability: str) -> float:
        """Calculate a score for a model based on performance metrics"""
        metrics = self.performance_metrics
        if model not in metrics["success_rate"]:
            return 0.5  # Default score for new models
            
        success_rate = metrics["success_rate"][model]
        latency = metrics["latency"][model]
        error_rate = metrics["error_rate"][model]
        cost = metrics["cost_per_token"][model]
        
        # Weighted scoring
        score = (
            0.4 * success_rate +
            0.3 * (1 - min(latency / 1000, 1)) +  # Normalize latency
            0.2 * (1 - error_rate) +
            0.1 * (1 - min(cost / 0.01, 1))  # Normalize cost
        )
        
        return score
    
    def _is_within_budget(self, model: str, budget: float) -> bool:
        """Check if model usage is within budget"""
        if model not in self.performance_metrics["cost_per_token"]:
            return True  # Allow new models
            
        cost_per_token = self.performance_metrics["cost_per_token"][model]
        estimated_tokens = 1000  # Conservative estimate
        estimated_cost = cost_per_token * estimated_tokens
        
        return estimated_cost <= budget
    
    async def route_task(self, request: TaskRequest) -> ModelResponse:
        """Route a task to the appropriate model"""
        task_type = request.task_type
        budget = request.budget if hasattr(request, 'budget') else None
        
        # Get the best available model for this task
        model_name = self.get_model_for_capability(task_type, budget)
        if not model_name:
            # Try fallback to reasoning capability
            model_name = self.get_model_for_capability("reasoning", budget)
            if not model_name:
                raise ValueError("No models available for task")
                
        model = self.models[model_name]
        
        try:
            # Process the request based on model type and task
            if request.image_data and "vision" in model_name:
                result = await self._process_with_vision(model, model_name, request)
            else:
                result = await self._process_text_only(model, model_name, request)
                
            # Update performance metrics
            self._update_metrics(model_name, result)
            
            return result
            
        except Exception as e:
            # Update error metrics
            self._update_error_metrics(model_name)
            
            # Try fallback model if available
            fallback_model = self._get_fallback_model(model_name, task_type)
            if fallback_model:
                return await self.route_task(request)
                
            raise e
    
    def _update_metrics(self, model: str, result: ModelResponse):
        """Update performance metrics for a model"""
        if model not in self.performance_metrics["success_rate"]:
            self.performance_metrics["success_rate"][model] = 0.0
            self.performance_metrics["latency"][model] = 0.0
            self.performance_metrics["error_rate"][model] = 0.0
            self.performance_metrics["cost_per_token"][model] = 0.0
            
        # Update success rate
        self.performance_metrics["success_rate"][model] = (
            0.9 * self.performance_metrics["success_rate"][model] + 0.1
        )
        
        # Update latency
        if hasattr(result, 'latency'):
            self.performance_metrics["latency"][model] = (
                0.9 * self.performance_metrics["latency"][model] + 0.1 * result.latency
            )
            
        # Update cost
        if hasattr(result, 'cost_per_token'):
            self.performance_metrics["cost_per_token"][model] = (
                0.9 * self.performance_metrics["cost_per_token"][model] + 0.1 * result.cost_per_token
            )
    
    def _update_error_metrics(self, model: str):
        """Update error metrics for a model"""
        if model not in self.performance_metrics["error_rate"]:
            self.performance_metrics["error_rate"][model] = 0.0
            
        self.performance_metrics["error_rate"][model] = (
            0.9 * self.performance_metrics["error_rate"][model] + 0.1
        )
    
    def _get_fallback_model(self, current_model: str, capability: str) -> Optional[str]:
        """Get a fallback model for a capability"""
        available_models = self.available_capabilities[capability]
        if not available_models:
            return None
            
        # Try models in the same tier first
        current_tier = None
        for tier, models in self.model_tiers.items():
            if current_model in models:
                current_tier = tier
                break
                
        if current_tier:
            tier_models = self.model_tiers[current_tier]
            for model in tier_models:
                if model != current_model and model in available_models:
                    return model
                    
        # Try models in other tiers
        for tier, models in self.model_tiers.items():
            if tier != current_tier:
                for model in models:
                    if model in available_models:
                        return model
                        
        return None
    
    async def _process_with_vision(self, model, model_name: str, request: TaskRequest) -> ModelResponse:
        """Process requests that include images"""
        try:
            if "gemini" in model_name:
                response = model.generate_content([request.content, request.image_data])
                return ModelResponse(
                    content=response.text,
                    model_used=model_name,
                    metadata={"provider": "google"}
                )
            # Add other vision models here as needed
            else:
                raise ValueError(f"Vision processing not implemented for model: {model_name}")
        except Exception as e:
            # Fallback to text-only if vision processing fails
            return ModelResponse(
                content=f"Error processing image with {model_name}: {str(e)}",
                model_used=model_name,
                metadata={"error": str(e), "fallback": "text_only"}
            )
    
    async def _process_text_only(self, model, model_name: str, request: TaskRequest) -> ModelResponse:
        """Process text-only requests"""
        try:
            if "gpt" in model_name:
                response = model.invoke(request.content)
                return ModelResponse(
                    content=response.content,
                    model_used=model_name,
                    metadata={"provider": "openai"}
                )
            elif "claude" in model_name:
                response = model.invoke(request.content)
                return ModelResponse(
                    content=response.content,
                    model_used=model_name,
                    metadata={"provider": "anthropic"}
                )
            elif "gemini" in model_name:
                response = model.generate_content(request.content)
                return ModelResponse(
                    content=response.text,
                    model_used=model_name,
                    metadata={"provider": "google"}
                )
            else:
                raise ValueError(f"Text processing not implemented for model: {model_name}")
        except Exception as e:
            return ModelResponse(
                content=f"Error with {model_name}: {str(e)}",
                model_used=model_name,
                metadata={"error": str(e)}
            )