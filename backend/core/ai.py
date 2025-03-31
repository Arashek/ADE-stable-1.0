from typing import Dict, Any, List, Optional
import os
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
import requests
from .models import (
    DynamicModelOrchestrator,
    ModelQuality,
    ModelCapability,
    ModelConfig
)

class AIService:
    def __init__(self):
        self.orchestrator = DynamicModelOrchestrator()
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize API clients for different providers"""
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.google_client = genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    
    async def generate_code(
        self,
        language: str,
        framework: Optional[str],
        requirements: str,
        constraints: Optional[Dict[str, Any]] = None,
        style_guide: Optional[Dict[str, Any]] = None,
        existing_code: Optional[str] = None,
        quality_requirement: ModelQuality = ModelQuality.MAXIMUM,
        max_response_time: Optional[float] = None
    ) -> str:
        """Generate code using the appropriate model"""
        model_config = self.orchestrator.get_model_for_task(
            task_type=ModelCapability.CODE,
            quality_requirement=quality_requirement,
            max_response_time=max_response_time
        )
        
        try:
            result = await self._generate_with_model(
                model_config=model_config,
                prompt=self._create_code_prompt(
                    language=language,
                    framework=framework,
                    requirements=requirements,
                    constraints=constraints,
                    style_guide=style_guide,
                    existing_code=existing_code
                )
            )
            self.orchestrator.update_model_metrics(model_config.name, True)
            return result
        except Exception as e:
            self.orchestrator.update_model_metrics(model_config.name, False)
            # Try fallback model
            fallback_model = self.orchestrator.get_model_for_task(
                task_type=ModelCapability.CODE,
                quality_requirement=ModelQuality.HIGH,
                max_response_time=max_response_time
            )
            return await self._generate_with_model(
                model_config=fallback_model,
                prompt=self._create_code_prompt(
                    language=language,
                    framework=framework,
                    requirements=requirements,
                    constraints=constraints,
                    style_guide=style_guide,
                    existing_code=existing_code
                )
            )
    
    async def generate_review_comments(
        self,
        code: str,
        review_types: List[str],
        context: Optional[Dict[str, Any]] = None,
        focus_areas: Optional[List[str]] = None,
        analysis_result: Optional[Dict[str, Any]] = None,
        quality_requirement: ModelQuality = ModelQuality.MAXIMUM,
        max_response_time: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Generate code review comments using the appropriate model"""
        model_config = self.orchestrator.get_model_for_task(
            task_type=ModelCapability.REASONING,
            quality_requirement=quality_requirement,
            max_response_time=max_response_time
        )
        
        try:
            result = await self._generate_with_model(
                model_config=model_config,
                prompt=self._create_review_prompt(
                    code=code,
                    review_types=review_types,
                    context=context,
                    focus_areas=focus_areas,
                    analysis_result=analysis_result
                )
            )
            self.orchestrator.update_model_metrics(model_config.name, True)
            return result
        except Exception as e:
            self.orchestrator.update_model_metrics(model_config.name, False)
            # Try fallback model
            fallback_model = self.orchestrator.get_model_for_task(
                task_type=ModelCapability.REASONING,
                quality_requirement=ModelQuality.HIGH,
                max_response_time=max_response_time
            )
            return await self._generate_with_model(
                model_config=fallback_model,
                prompt=self._create_review_prompt(
                    code=code,
                    review_types=review_types,
                    context=context,
                    focus_areas=focus_areas,
                    analysis_result=analysis_result
                )
            )
    
    async def generate_test_cases(
        self,
        code: str,
        test_types: List[str],
        coverage_target: float,
        framework: Optional[str] = None,
        analysis_result: Optional[Dict[str, Any]] = None,
        user_tier: ModelTier = ModelTier.FREE
    ) -> List[Dict[str, Any]]:
        """Generate test cases using the appropriate model"""
        model_config = self.orchestrator.get_model_for_task("code", user_tier)
        return await self._generate_with_model(
            model_config=model_config,
            prompt=self._create_test_prompt(
                code=code,
                test_types=test_types,
                coverage_target=coverage_target,
                framework=framework,
                analysis_result=analysis_result
            )
        )
    
    async def _generate_with_model(
        self,
        model_config: ModelConfig,
        prompt: str
    ) -> Any:
        """Generate content using the specified model"""
        if model_config.is_local:
            return await self._generate_with_local_model(model_config, prompt)
        
        if model_config.provider == "openai":
            return await self._generate_with_openai(model_config, prompt)
        elif model_config.provider == "anthropic":
            return await self._generate_with_anthropic(model_config, prompt)
        elif model_config.provider == "google":
            return await self._generate_with_google(model_config, prompt)
        elif model_config.provider == "deepseek":
            return await self._generate_with_deepseek(model_config, prompt)
        
        raise ValueError(f"Unsupported model provider: {model_config.provider}")
    
    async def _generate_with_local_model(self, model_config: ModelConfig, prompt: str) -> Any:
        """Generate content using a local model via Ollama"""
        response = requests.post(
            f"{model_config.local_endpoint}/api/generate",
            json={
                "model": model_config.name,
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()["response"]
    
    async def _generate_with_openai(self, model_config: ModelConfig, prompt: str) -> Any:
        """Generate content using OpenAI models"""
        response = await self.openai_client.chat.completions.create(
            model=model_config.name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    async def _generate_with_anthropic(self, model_config: ModelConfig, prompt: str) -> Any:
        """Generate content using Anthropic models"""
        response = await self.anthropic_client.messages.create(
            model=model_config.name,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    async def _generate_with_google(self, model_config: ModelConfig, prompt: str) -> Any:
        """Generate content using Google models"""
        model = genai.GenerativeModel(model_config.name)
        response = await model.generate_content(prompt)
        return response.text
    
    async def _generate_with_deepseek(self, model_config: ModelConfig, prompt: str) -> Any:
        """Generate content using DeepSeek models"""
        # Implement DeepSeek API integration
        # This is a placeholder - actual implementation will depend on DeepSeek's API
        raise NotImplementedError("DeepSeek API integration not implemented yet")
    
    def _create_code_prompt(
        self,
        language: str,
        framework: Optional[str],
        requirements: str,
        constraints: Optional[Dict[str, Any]] = None,
        style_guide: Optional[Dict[str, Any]] = None,
        existing_code: Optional[str] = None
    ) -> str:
        """Create a prompt for code generation"""
        prompt = f"Generate code in {language}"
        if framework:
            prompt += f" using {framework}"
        prompt += f" with the following requirements:\n{requirements}"
        
        if constraints:
            prompt += "\nConstraints:\n" + "\n".join(f"- {k}: {v}" for k, v in constraints.items())
        
        if style_guide:
            prompt += "\nStyle Guide:\n" + "\n".join(f"- {k}: {v}" for k, v in style_guide.items())
        
        if existing_code:
            prompt += f"\nExisting code:\n{existing_code}"
        
        return prompt
    
    def _create_review_prompt(
        self,
        code: str,
        review_types: List[str],
        context: Optional[Dict[str, Any]] = None,
        focus_areas: Optional[List[str]] = None,
        analysis_result: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a prompt for code review"""
        prompt = f"Review the following code for {', '.join(review_types)}:\n\n{code}"
        
        if context:
            prompt += "\nContext:\n" + "\n".join(f"- {k}: {v}" for k, v in context.items())
        
        if focus_areas:
            prompt += f"\nFocus areas: {', '.join(focus_areas)}"
        
        if analysis_result:
            prompt += f"\nAnalysis results:\n{analysis_result}"
        
        return prompt
    
    def _create_test_prompt(
        self,
        code: str,
        test_types: List[str],
        coverage_target: float,
        framework: Optional[str] = None,
        analysis_result: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a prompt for test generation"""
        prompt = f"Generate {', '.join(test_types)} tests for the following code"
        if framework:
            prompt += f" using {framework}"
        prompt += f" with a target coverage of {coverage_target}%:\n\n{code}"
        
        if analysis_result:
            prompt += f"\nAnalysis results:\n{analysis_result}"
        
        return prompt 