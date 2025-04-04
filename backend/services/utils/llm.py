import logging
import asyncio
import json
from typing import Dict, List, Any, Optional
import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class LLMRequest(BaseModel):
    """Request model for LLM API calls"""
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 1000
    model: str = "default"
    stop_sequences: Optional[List[str]] = None
    system_message: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class LLMResponse(BaseModel):
    """Response model from LLM API calls"""
    text: str
    usage: Dict[str, int]
    model: str
    finish_reason: str
    request_id: str

class LLMClient:
    """Client for interacting with Language Model APIs"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url or "https://api.cloudev.ai/llm"
        self.logger = logging.getLogger(__name__)
        
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate text from the LLM based on the provided request"""
        try:
            # This is a mock implementation - in production, this would make an actual API call
            self.logger.info(f"Generating text with model: {request.model}")
            
            # Simulate API latency
            await asyncio.sleep(0.5)
            
            # Mock response
            response = LLMResponse(
                text="This is a mock response from the LLM API. In a production environment, this would contain actual model output based on your prompt.",
                usage={
                    "prompt_tokens": len(request.prompt) // 4,
                    "completion_tokens": 20,
                    "total_tokens": len(request.prompt) // 4 + 20
                },
                model=request.model,
                finish_reason="stop",
                request_id="mock-request-123"
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating text from LLM: {str(e)}")
            raise
            
    async def classify(self, text: str, categories: List[str], model: str = "default") -> Dict[str, float]:
        """Classify text into provided categories with confidence scores"""
        try:
            # This is a mock implementation
            self.logger.info(f"Classifying text with model: {model}")
            
            # Simulate API latency
            await asyncio.sleep(0.3)
            
            # Mock classification results
            import random
            results = {}
            total = 0
            for category in categories:
                score = random.random()
                total += score
                results[category] = score
                
            # Normalize scores
            for category in categories:
                results[category] /= total
                
            return results
            
        except Exception as e:
            self.logger.error(f"Error classifying text: {str(e)}")
            raise
            
    async def embed(self, texts: List[str], model: str = "embedding-default") -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        try:
            # This is a mock implementation
            self.logger.info(f"Generating embeddings for {len(texts)} texts with model: {model}")
            
            # Simulate API latency
            await asyncio.sleep(0.4)
            
            # Mock embeddings (128-dimensional vectors)
            import random
            embeddings = []
            for _ in texts:
                embedding = [random.random() * 2 - 1 for _ in range(128)]
                # Normalize
                magnitude = sum(x**2 for x in embedding) ** 0.5
                normalized = [x / magnitude for x in embedding]
                embeddings.append(normalized)
                
            return embeddings
            
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {str(e)}")
            raise
            
    async def generate_text(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000, model: str = "default") -> str:
        """
        Generate text from the LLM based on the provided prompt
        
        Args:
            prompt: The prompt to generate text from
            temperature: Controls randomness of output (0-1)
            max_tokens: Maximum number of tokens to generate
            model: The model to use for generation
            
        Returns:
            Generated text as a string
        """
        request = LLMRequest(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model
        )
        
        response = await self.generate(request)
        return response.text
        
    async def generate_structured_output(self, prompt: str, output_key: str = None, model: str = "default") -> Dict[str, Any]:
        """
        Generate structured output (JSON) from the LLM
        
        Args:
            prompt: The prompt to generate structured output from
            output_key: Optional key to extract from the JSON response
            model: The model to use for generation
            
        Returns:
            Generated output as a dictionary
        """
        # Add instructions to return JSON
        json_prompt = f"{prompt}\n\nReturn the result as a valid JSON object."
        
        request = LLMRequest(
            prompt=json_prompt,
            temperature=0.2,  # Lower temperature for more deterministic JSON
            max_tokens=2000,
            model=model,
            system_message="You are a helpful assistant that always responds with valid JSON."
        )
        
        try:
            response = await self.generate(request)
            text = response.text.strip()
            
            # Extract JSON if the response has JSON formatting markers
            if text.startswith("```json"):
                text = text.split("```json", 1)[1]
                if "```" in text:
                    text = text.split("```", 1)[0]
            elif text.startswith("```"):
                text = text.split("```", 1)[1]
                if "```" in text:
                    text = text.split("```", 1)[0]
                
            # Clean up any remaining formatting
            text = text.strip()
            
            # Parse JSON
            result = json.loads(text)
            
            # Extract specific key if requested
            if output_key and output_key in result:
                return result[output_key]
                
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON from LLM response: {e}")
            # Return a basic structure to avoid breaking the application
            if output_key:
                return {output_key: []}
            return {"error": "Failed to generate valid JSON", "text": response.text if 'response' in locals() else "No response"}
            
        except Exception as e:
            self.logger.error(f"Error generating structured output: {str(e)}")
            if output_key:
                return {output_key: []}
            return {"error": str(e)}
