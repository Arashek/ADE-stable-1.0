from typing import Dict, List, Any, Optional
import logging
from enum import Enum
from dataclasses import dataclass
import openai
import anthropic
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"

@dataclass
class LLMConfig:
    provider: LLMProvider
    model_name: str
    api_key: Optional[str] = None
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

class LLMIntegration:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.tokenizer = None
        self.model = None
        
        if config.provider == LLMProvider.LOCAL:
            self._initialize_local_model()
            
    def _initialize_local_model(self):
        """Initialize local model for code-specific tasks"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
            self.model = AutoModel.from_pretrained("microsoft/codebert-base")
        except Exception as e:
            logger.error(f"Failed to initialize local model: {e}")
            
    async def generate_code(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate code based on prompt and context"""
        try:
            if self.config.provider == LLMProvider.OPENAI:
                return await self._generate_with_openai(prompt, context)
            elif self.config.provider == LLMProvider.ANTHROPIC:
                return await self._generate_with_anthropic(prompt, context)
            else:
                return await self._generate_with_local(prompt, context)
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return ""
            
    async def analyze_code(self, code: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze code for specific patterns or issues"""
        try:
            if self.config.provider == LLMProvider.OPENAI:
                return await self._analyze_with_openai(code, analysis_type)
            elif self.config.provider == LLMProvider.ANTHROPIC:
                return await self._analyze_with_anthropic(code, analysis_type)
            else:
                return await self._analyze_with_local(code, analysis_type)
        except Exception as e:
            logger.error(f"Error analyzing code: {e}")
            return {}
            
    async def suggest_improvements(self, code: str, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """Generate code improvement suggestions"""
        try:
            if self.config.provider == LLMProvider.OPENAI:
                return await self._suggest_with_openai(code, context)
            elif self.config.provider == LLMProvider.ANTHROPIC:
                return await self._suggest_with_anthropic(code, context)
            else:
                return await self._suggest_with_local(code, context)
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return []
            
    async def _generate_with_openai(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate code using OpenAI's API"""
        if not self.config.api_key:
            raise ValueError("OpenAI API key not configured")
            
        openai.api_key = self.config.api_key
        
        messages = [
            {"role": "system", "content": "You are an expert code generation assistant."}
        ]
        
        if context:
            messages.append({"role": "system", "content": f"Context: {context}"})
            
        messages.append({"role": "user", "content": prompt})
        
        response = await openai.ChatCompletion.acreate(
            model=self.config.model_name,
            messages=messages,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            frequency_penalty=self.config.frequency_penalty,
            presence_penalty=self.config.presence_penalty
        )
        
        return response.choices[0].message.content
        
    async def _generate_with_anthropic(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate code using Anthropic's API"""
        if not self.config.api_key:
            raise ValueError("Anthropic API key not configured")
            
        client = anthropic.Client(api_key=self.config.api_key)
        
        system_prompt = "You are an expert code generation assistant."
        if context:
            system_prompt += f"\nContext: {context}"
            
        response = await client.messages.create(
            model=self.config.model_name,
            max_tokens=self.config.max_tokens,
            messages=[{
                "role": "user",
                "content": f"{system_prompt}\n\n{prompt}"
            }],
            temperature=self.config.temperature
        )
        
        return response.content[0].text
        
    async def _generate_with_local(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate code using local model"""
        if not self.model or not self.tokenizer:
            raise ValueError("Local model not initialized")
            
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        outputs = self.model.generate(**inputs, max_length=self.config.max_tokens)
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
    async def _analyze_with_openai(self, code: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze code using OpenAI's API"""
        if not self.config.api_key:
            raise ValueError("OpenAI API key not configured")
            
        openai.api_key = self.config.api_key
        
        prompt = f"Analyze the following code for {analysis_type}:\n\n{code}"
        
        response = await openai.ChatCompletion.acreate(
            model=self.config.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
        
        return {"analysis": response.choices[0].message.content}
        
    async def _analyze_with_anthropic(self, code: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze code using Anthropic's API"""
        if not self.config.api_key:
            raise ValueError("Anthropic API key not configured")
            
        client = anthropic.Client(api_key=self.config.api_key)
        
        prompt = f"Analyze the following code for {analysis_type}:\n\n{code}"
        
        response = await client.messages.create(
            model=self.config.model_name,
            max_tokens=self.config.max_tokens,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.temperature
        )
        
        return {"analysis": response.content[0].text}
        
    async def _analyze_with_local(self, code: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze code using local model"""
        if not self.model or not self.tokenizer:
            raise ValueError("Local model not initialized")
            
        inputs = self.tokenizer(code, return_tensors="pt", truncation=True, max_length=512)
        outputs = self.model(**inputs)
        
        # Extract relevant features for analysis
        features = outputs.last_hidden_state.mean(dim=1)
        
        return {
            "features": features.tolist(),
            "analysis_type": analysis_type
        }
        
    async def _suggest_with_openai(self, code: str, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """Generate suggestions using OpenAI's API"""
        if not self.config.api_key:
            raise ValueError("OpenAI API key not configured")
            
        openai.api_key = self.config.api_key
        
        prompt = f"Suggest improvements for the following code:\n\n{code}"
        if context:
            prompt += f"\n\nContext: {context}"
            
        response = await openai.ChatCompletion.acreate(
            model=self.config.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
        
        suggestions = response.choices[0].message.content.split("\n")
        return [s.strip() for s in suggestions if s.strip()]
        
    async def _suggest_with_anthropic(self, code: str, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """Generate suggestions using Anthropic's API"""
        if not self.config.api_key:
            raise ValueError("Anthropic API key not configured")
            
        client = anthropic.Client(api_key=self.config.api_key)
        
        prompt = f"Suggest improvements for the following code:\n\n{code}"
        if context:
            prompt += f"\n\nContext: {context}"
            
        response = await client.messages.create(
            model=self.config.model_name,
            max_tokens=self.config.max_tokens,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.temperature
        )
        
        suggestions = response.content[0].text.split("\n")
        return [s.strip() for s in suggestions if s.strip()]
        
    async def _suggest_with_local(self, code: str, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """Generate suggestions using local model"""
        if not self.model or not self.tokenizer:
            raise ValueError("Local model not initialized")
            
        inputs = self.tokenizer(code, return_tensors="pt", truncation=True, max_length=512)
        outputs = self.model(**inputs)
        
        # Generate suggestions based on model output
        suggestions = []
        for i in range(3):  # Generate 3 suggestions
            suggestion = self.tokenizer.decode(
                self.model.generate(**inputs, max_length=100)[0],
                skip_special_tokens=True
            )
            suggestions.append(suggestion)
            
        return suggestions 