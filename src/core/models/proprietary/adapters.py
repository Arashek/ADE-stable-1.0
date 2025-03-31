from typing import Dict, Any, Optional, List
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from ...providers.adapters.base import BaseProviderAdapter
from ...providers.config import ProviderConfig, Capability
from .inference import CodeCompletionInference

class CodeCompletionAdapter(BaseProviderAdapter):
    """Adapter for proprietary code completion models"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.name = "proprietary"
        self.model = None
        self.tokenizer = None
        self.inference = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the model and tokenizer"""
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.model_path,
                device_map="auto",
                torch_dtype=torch.float16,
                load_in_8bit=self.config.quantization == "8bit",
                load_in_4bit=self.config.quantization == "4bit"
            )
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_path,
                trust_remote_code=True
            )
            
            self.inference = CodeCompletionInference(
                model=self.model,
                tokenizer=self.tokenizer,
                device=self.config.device,
                batch_size=self.config.batch_size
            )
            
            self.initialized = True
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize code completion model: {str(e)}")
    
    async def generate_code_completion(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.95,
        stop_sequences: Optional[List[str]] = None
    ) -> str:
        """Generate code completion for the given prompt"""
        if not self.initialized:
            self._initialize()
            
        try:
            completion = await self.inference.generate(
                prompt=prompt,
                context=context,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop_sequences=stop_sequences
            )
            return completion
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate code completion: {str(e)}")
    
    async def generate_plan(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 0.95
    ) -> str:
        """Generate a plan for the given task"""
        if not self.initialized:
            self._initialize()
            
        try:
            # Format task as a planning prompt
            planning_prompt = f"Task: {task}\n\nPlan:"
            
            plan = await self.inference.generate(
                prompt=planning_prompt,
                context=context,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            )
            return plan
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate plan: {str(e)}")
    
    def get_capabilities(self) -> Dict[Capability, float]:
        """Get all capabilities and their scores"""
        return {
            Capability.CODE_COMPLETION: 0.95,
            Capability.PLANNING: 0.85,
            Capability.CONTEXT_AWARENESS: 0.9,
            Capability.CODE_ANALYSIS: 0.8,
            Capability.REFACTORING: 0.75,
            Capability.TEST_GENERATION: 0.7,
            Capability.DOCUMENTATION: 0.8,
            Capability.DEBUGGING: 0.75
        } 