from typing import Dict, List, Optional
import yaml
import logging
from dataclasses import dataclass
from .gpu_manager import GPUManager
from .fallback_manager import FallbackManager
from .language_manager import LanguageManager

logger = logging.getLogger(__name__)

@dataclass
class Task:
    type: str
    complexity: float
    security_critical: bool
    requires_reasoning: bool
    requires_planning: bool
    requires_creativity: bool
    requires_speed: bool
    language: Optional[str] = None
    framework: Optional[str] = None

class ModelSelector:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.gpu_manager = GPUManager(self.config)
        self.fallback_manager = FallbackManager(self.config)
        self.language_manager = LanguageManager(self.config)
        
        self.model_costs = {
            'claude-3-opus-20240229': 15.0,  # $ per 1M tokens
            'gpt-4': 10.0,
            'gemini-pro': 1.0,
            'mixtral-8x7b': 0.27,  # Via Groq
            'deepseek-coder-6.7b': 0.0,  # Open source
            'codellama-13b': 0.0,  # Open source
            'wizardcoder-python-7b': 0.0,
            'wizardcoder-js-7b': 0.0,
            'neural-chat-7b': 0.0,
            'sqlcoder-7b': 0.0
        }
        
    async def select_model(self, task: Task, agent_type: str) -> Dict:
        """
        Select the most appropriate model for a given task and agent
        """
        # First, check if we have a language-specific model
        if task.language:
            lang_model = self.language_manager.get_language_model(
                task.language, task.framework
            )
            if lang_model and not self._requires_premium_model(task):
                return await self._prepare_model_config(lang_model['model'], task)
                
        # Check if task requires premium model
        if self._requires_premium_model(task):
            return await self._prepare_model_config(
                self._select_premium_model(task, agent_type)['model'],
                task
            )
            
        # Try to use specialized agent if available
        if agent_type in self.config.get('specialized_agents', {}):
            agent_config = self.config['specialized_agents'][agent_type]
            return await self._prepare_model_config(agent_config['model'], task)
            
        # Use open source model if possible
        open_source_model = self._select_open_source_model(task, agent_type)
        if open_source_model:
            return await self._prepare_model_config(open_source_model['model'], task)
            
        # Fallback to balanced selection
        balanced_model = self._select_balanced_model(task, agent_type)
        return await self._prepare_model_config(balanced_model['model'], task)
        
    async def _prepare_model_config(self, model_name: str, task: Task) -> Dict:
        """Prepare complete model configuration with GPU and fallback settings"""
        gpu_config = self.gpu_manager.prepare_model_for_gpu(model_name)
        
        # Get fallback models
        fallback_models = self._get_fallback_models(model_name, task)
        
        # Get language-specific prompts if applicable
        prompts = {}
        if task.language:
            prompts = self.language_manager.get_language_specific_prompts(
                task.language, task.framework
            )
            
        return {
            'model': model_name,
            'provider': self._get_provider(model_name),
            'gpu_config': gpu_config,
            'fallback_models': fallback_models,
            'prompts': prompts,
            'batch_size': gpu_config.get('batch_size', 1)
        }
        
    def _requires_premium_model(self, task: Task) -> bool:
        """Check if task characteristics require a premium model"""
        triggers = self.config['cost_optimization']['premium_model_triggers']
        
        if task.security_critical:
            return True
            
        if task.complexity >= 0.9:
            return True
            
        if task.requires_reasoning:
            return True
            
        return False
        
    def _get_provider(self, model_name: str) -> str:
        """Get provider for model"""
        if model_name == 'claude-3-opus-20240229':
            return 'anthropic'
        elif model_name in ['gpt-4']:
            return 'openai'
        elif model_name == 'gemini-pro':
            return 'google'
        elif model_name == 'mixtral-8x7b':
            return 'groq'
        else:
            return 'ollama'
            
    def _get_fallback_models(self, model_name: str, task: Task) -> List[str]:
        """Get appropriate fallback models"""
        fallbacks = []
        
        # Add language-specific fallback if available
        if task.language:
            lang_model = self.language_manager.get_language_model(task.language)
            if lang_model.get('fallback'):
                fallbacks.append(lang_model['fallback'])
                
        # Add general fallbacks
        if model_name in self.config.get('specialized_agents', {}):
            agent_config = self.config['specialized_agents'][model_name]
            if 'fallback' in agent_config:
                fallbacks.append(agent_config['fallback'])
            if 'expert_fallback' in agent_config:
                fallbacks.append(agent_config['expert_fallback'])
                
        # Add default fallbacks
        fallbacks.extend(['deepseek-coder-6.7b', 'neural-chat-7b'])
        
        return list(dict.fromkeys(fallbacks))  # Remove duplicates while preserving order
        
    def estimate_cost(self, model: str, token_count: int) -> float:
        """Estimate cost for using a model"""
        if model not in self.model_costs:
            return 0.0
            
        cost_per_million = self.model_costs[model]
        return (token_count / 1_000_000) * cost_per_million
