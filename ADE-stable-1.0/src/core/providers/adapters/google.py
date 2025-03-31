import logging
import json
import re
from typing import Dict, Any, Optional
import base64
from .base import BaseProviderAdapter, AuthenticationError
from ..config import Capability, ProviderConfig

logger = logging.getLogger(__name__)

class GoogleAdapter(BaseProviderAdapter):
    """Google AI implementation of provider adapter"""
    
    def __init__(self, config: ProviderConfig):
        self.name = "google"
        super().__init__(config)
    
    def _initialize(self) -> None:
        """Initialize the Google AI client"""
        try:
            import google.generativeai as genai
            
            # Get API key from credentials
            api_key = self.config.credentials.api_key
            if not api_key:
                raise AuthenticationError("Google AI API key not provided")
            
            # Initialize client
            genai.configure(api_key=api_key)
            
            # Test connection by listing models
            self.models = genai.list_models()
            self.genai = genai
            
            # Find suitable models for different capabilities
            self.text_model = "gemini-pro"
            self.vision_model = "gemini-pro-vision"
            
            for model in self.models:
                if "vision" in model.name.lower():
                    self.vision_model = model.name
                elif "pro" in model.name.lower():
                    self.text_model = model.name
            
            logger.info(f"Successfully initialized Google AI adapter with text model: {self.text_model}, vision model: {self.vision_model}")
            
        except ImportError:
            logger.error("Google GenerativeAI Python package not installed")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Google AI adapter: {str(e)}")
            raise
    
    def get_capabilities(self) -> Dict[Capability, float]:
        """Return capabilities supported by Google AI with confidence scores"""
        return {
            Capability.TEXT_GENERATION: 0.85,
            Capability.CODE_GENERATION: 0.8,
            Capability.PLANNING: 0.75,
            Capability.REASONING: 0.8,
            Capability.CODE_EXPLANATION: 0.8,
            Capability.DEBUGGING: 0.75,
            Capability.DOCUMENTATION: 0.8,
            Capability.IMAGE_UNDERSTANDING: 0.9  # Gemini has good vision capabilities
        }
    
    def _generate_text_impl(self, prompt: str, **kwargs) -> str:
        """Generate text using Google AI"""
        try:
            model_name = kwargs.get("model", self.text_model)
            temperature = kwargs.get("temperature", 0.7)
            
            model = self.genai.GenerativeModel(model_name=model_name)
            response = model.generate_content(
                prompt,
                generation_config={"temperature": temperature}
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Google AI text generation error: {str(e)}")
            raise
    
    def _generate_code_impl(self, spec: str, **kwargs) -> str:
        """Generate code using Google AI"""
        try:
            # Prepare system message for code generation
            system_message = """You are an expert programmer. Generate clean, efficient, and well-documented code based on the specification provided."""
            
            # Add language context if provided
            if 'language' in kwargs:
                system_message += f"\nGenerate code in {kwargs['language']}."
            
            # Add framework context if provided
            if 'framework' in kwargs:
                system_message += f"\nUse the {kwargs['framework']} framework."
            
            # Combine system message and spec
            full_prompt = f"{system_message}\n\nSpecification:\n{spec}"
            
            # Generate code using text generation with code-specific parameters
            return self._generate_text_impl(
                full_prompt,
                temperature=kwargs.get('temperature', 0.2),  # Lower temperature for more deterministic code
                **kwargs
            )
            
        except Exception as e:
            logger.error(f"Google AI code generation error: {str(e)}")
            raise
    
    def _analyze_image_impl(self, image_data: bytes, prompt: str, **kwargs) -> str:
        """Analyze image using Google AI's Gemini Pro Vision"""
        try:
            # Convert image data to PIL Image
            from PIL import Image
            import io
            
            image = Image.open(io.BytesIO(image_data))
            
            # Initialize vision model
            model = self.genai.GenerativeModel(self.vision_model)
            
            # Generate content with image
            response = model.generate_content(
                [prompt, image],
                generation_config={"temperature": kwargs.get('temperature', 0.7)}
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Google AI image analysis error: {str(e)}")
            raise
    
    def _create_plan_impl(self, goal: str, **kwargs) -> Dict[str, Any]:
        """Create a structured plan using Google AI"""
        try:
            # Prepare system message for plan creation
            system_message = """You are an expert project planner. Create a detailed, structured plan to achieve the given goal. 
            The plan should include:
            1. Main objectives
            2. Key tasks and subtasks
            3. Dependencies between tasks
            4. Estimated timeframes
            5. Required resources
            
            Format the response as a JSON object with these sections."""
            
            # Generate plan using text generation
            plan_text = self._generate_text_impl(
                f"{system_message}\n\nGoal:\n{goal}",
                temperature=kwargs.get('temperature', 0.3),  # Lower temperature for more structured output
                **kwargs
            )
            
            # Parse the JSON response
            try:
                plan = json.loads(plan_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON-like structure using regex
                json_match = re.search(r'\{.*\}', plan_text, re.DOTALL)
                if json_match:
                    plan = json.loads(json_match.group())
                else:
                    # If no JSON structure found, create a basic plan
                    plan = {
                        "objectives": [goal],
                        "tasks": [],
                        "dependencies": {},
                        "timeframes": {},
                        "resources": []
                    }
            
            return plan
            
        except Exception as e:
            logger.error(f"Google AI plan creation error: {str(e)}")
            raise


