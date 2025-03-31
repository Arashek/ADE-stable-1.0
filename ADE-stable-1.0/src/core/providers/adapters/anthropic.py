import logging
import json
import re
from typing import Dict, Any, Optional
import base64
from .base import BaseProviderAdapter, AuthenticationError
from ..config import Capability, ProviderConfig

logger = logging.getLogger(__name__)

class AnthropicAdapter(BaseProviderAdapter):
    """Anthropic implementation of provider adapter"""
    
    def __init__(self, config: ProviderConfig):
        self.name = "anthropic"
        super().__init__(config)
    
    def _initialize(self) -> None:
        """Initialize the Anthropic client"""
        try:
            from anthropic import Anthropic
            
            # Get API key from credentials
            api_key = self.config.credentials.api_key
            if not api_key:
                raise AuthenticationError("Anthropic API key not provided")
            
            # Initialize client
            self.client = Anthropic(api_key=api_key)
            
            # Get available models to verify connection
            self.models = self.client.models.list()
            
            logger.info("Successfully initialized Anthropic adapter")
            
        except ImportError:
            logger.error("Anthropic Python package not installed")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic adapter: {str(e)}")
            raise
    
    def get_capabilities(self) -> Dict[Capability, float]:
        """Return Anthropic's capabilities with confidence scores"""
        return {
            Capability.TEXT_GENERATION: 1.0,  # Claude excels at text generation
            Capability.CODE_GENERATION: 0.95, # Claude is excellent at code generation
            Capability.IMAGE_ANALYSIS: 0.9,   # Claude 3 is very good at image analysis
            Capability.PLAN_CREATION: 0.98,   # Claude is excellent at planning
        }
    
    def _generate_text_impl(self, prompt: str, **kwargs) -> str:
        """Generate text using Anthropic's API"""
        try:
            # Get model from config or use default
            model = kwargs.get('model', self.config.model or 'claude-3-sonnet-20240229')
            
            # Prepare messages
            messages = [{"role": "user", "content": prompt}]
            
            # Add system message if provided
            if 'system_message' in kwargs:
                messages.insert(0, {"role": "system", "content": kwargs['system_message']})
            
            # Make API call
            response = self.client.messages.create(
                model=model,
                messages=messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 1000),
                top_p=kwargs.get('top_p', 1.0),
            )
            
            # Extract and return the generated text
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic text generation error: {str(e)}")
            raise
    
    def _generate_code_impl(self, spec: str, **kwargs) -> str:
        """Generate code using Anthropic's API"""
        try:
            # Prepare system message for code generation
            system_message = """You are an expert programmer. Generate clean, efficient, and well-documented code based on the specification provided."""
            
            # Add language context if provided
            if 'language' in kwargs:
                system_message += f"\nGenerate code in {kwargs['language']}."
            
            # Add framework context if provided
            if 'framework' in kwargs:
                system_message += f"\nUse the {kwargs['framework']} framework."
            
            # Generate code using text generation with code-specific parameters
            return self._generate_text_impl(
                spec,
                system_message=system_message,
                temperature=kwargs.get('temperature', 0.2),  # Lower temperature for more deterministic code
                **kwargs
            )
            
        except Exception as e:
            logger.error(f"Anthropic code generation error: {str(e)}")
            raise
    
    def _analyze_image_impl(self, image_data: bytes, prompt: str, **kwargs) -> str:
        """Analyze image using Anthropic's Claude 3 API"""
        try:
            # Convert image data to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare messages with image
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ]
            
            # Make API call to Claude 3
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                messages=messages,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7),
            )
            
            # Extract and return the analysis
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic image analysis error: {str(e)}")
            raise
    
    def _create_plan_impl(self, goal: str, **kwargs) -> Dict[str, Any]:
        """Create a structured plan using Anthropic's API"""
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
                goal,
                system_message=system_message,
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
            logger.error(f"Anthropic plan creation error: {str(e)}")
            raise


