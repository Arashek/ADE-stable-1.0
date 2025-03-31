import logging
import json
import re
from typing import Dict, Any, Optional
import base64
from .base import BaseProviderAdapter, AuthenticationError
from ..config import Capability, ProviderConfig

logger = logging.getLogger(__name__)

class OpenAIAdapter(BaseProviderAdapter):
    """OpenAI implementation of provider adapter"""
    
    def __init__(self, config: ProviderConfig):
        self.name = "openai"
        super().__init__(config)
    
    def _initialize(self) -> None:
        """Initialize the OpenAI client"""
        try:
            import openai
            
            # Get API key from credentials
            api_key = self.config.credentials.api_key
            if not api_key:
                raise AuthenticationError("OpenAI API key not provided")
            
            # Set API key
            openai.api_key = api_key
            
            # Set organization if provided
            org_id = self.config.credentials.organization_id
            if org_id:
                openai.organization = org_id
                
            # Test connection by retrieving models list
            self.client = openai.Client(api_key=api_key, organization=org_id)
            self.models = self.client.models.list()
            
            logger.info("Successfully initialized OpenAI adapter")
            
        except ImportError:
            logger.error("OpenAI Python package not installed")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI adapter: {str(e)}")
            raise
    
    def get_capabilities(self) -> Dict[Capability, float]:
        """Return OpenAI's capabilities with confidence scores"""
        return {
            Capability.TEXT_GENERATION: 1.0,  # GPT models excel at text generation
            Capability.CODE_GENERATION: 0.9,  # GPT models are good at code generation
            Capability.IMAGE_ANALYSIS: 0.8,   # GPT-4V is good at image analysis
            Capability.PLAN_CREATION: 0.95,   # GPT models are excellent at planning
        }
    
    def _generate_text_impl(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenAI's API"""
        try:
            # Get model from config or use default
            model = kwargs.get('model', self.config.model or 'gpt-3.5-turbo')
            
            # Prepare messages
            messages = [{"role": "user", "content": prompt}]
            
            # Add system message if provided
            if 'system_message' in kwargs:
                messages.insert(0, {"role": "system", "content": kwargs['system_message']})
            
            # Make API call
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 1000),
                top_p=kwargs.get('top_p', 1.0),
                frequency_penalty=kwargs.get('frequency_penalty', 0.0),
                presence_penalty=kwargs.get('presence_penalty', 0.0),
            )
            
            # Extract and return the generated text
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI text generation error: {str(e)}")
            raise
    
    def _generate_code_impl(self, spec: str, **kwargs) -> str:
        """Generate code using OpenAI's API"""
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
            logger.error(f"OpenAI code generation error: {str(e)}")
            raise
    
    def _analyze_image_impl(self, image_data: bytes, prompt: str, **kwargs) -> str:
        """Analyze image using OpenAI's GPT-4V API"""
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
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # Make API call to GPT-4V
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7),
            )
            
            # Extract and return the analysis
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI image analysis error: {str(e)}")
            raise
    
    def _create_plan_impl(self, goal: str, **kwargs) -> Dict[str, Any]:
        """Create a structured plan using OpenAI's API"""
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
            logger.error(f"OpenAI plan creation error: {str(e)}")
            raise


