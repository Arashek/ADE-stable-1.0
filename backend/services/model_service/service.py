from typing import Dict, List, Optional
import asyncio
import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .config import ModelConfig
from .types import ModelRequest, ModelResponse
from ..utils.llm import LLMClient
from ..utils.cache import ModelCache
from ..utils.telemetry import track_event

logger = logging.getLogger(__name__)

class ModelService:
    def __init__(self, config: ModelConfig):
        self.config = config
        self.llm_client = LLMClient()
        self.cache = ModelCache()
        self.app = FastAPI(title="ADE Model Service")
        self._setup_routes()
        
    def _setup_routes(self):
        @self.app.post("/generate", response_model=ModelResponse)
        async def generate(request: ModelRequest):
            try:
                # Check cache first
                cache_key = self._generate_cache_key(request)
                cached_response = await self.cache.get(cache_key)
                if cached_response:
                    return ModelResponse(
                        id=str(uuid4()),
                        result=cached_response,
                        cached=True
                    )
                    
                # Generate response
                response = await self._generate_response(request)
                
                # Cache response
                await self.cache.set(cache_key, response)
                
                return ModelResponse(
                    id=str(uuid4()),
                    result=response,
                    cached=False
                )
                
            except Exception as e:
                logger.error(f"Generation failed: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.post("/analyze", response_model=Dict)
        async def analyze(request: Dict):
            try:
                analysis = await self._analyze_request(request)
                return analysis
            except Exception as e:
                logger.error(f"Analysis failed: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
    async def _generate_response(self, request: ModelRequest) -> str:
        """
        Generate response using appropriate model
        """
        # Select model based on request type
        model = self._select_model(request)
        
        # Prepare prompt
        prompt = self._prepare_prompt(request)
        
        # Generate response
        response = await self.llm_client.generate(
            prompt=prompt,
            model=model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return response
        
    async def _analyze_request(self, request: Dict) -> Dict:
        """
        Analyze request for insights
        """
        analysis = {}
        
        # Analyze content
        content_analysis = await self._analyze_content(request)
        analysis['content'] = content_analysis
        
        # Analyze complexity
        complexity = await self._analyze_complexity(request)
        analysis['complexity'] = complexity
        
        # Generate suggestions
        suggestions = await self._generate_suggestions(
            content_analysis,
            complexity
        )
        analysis['suggestions'] = suggestions
        
        return analysis
        
    def _select_model(self, request: ModelRequest) -> str:
        """
        Select appropriate model based on request
        """
        if request.model:
            return request.model
            
        # Select based on task type
        if request.task_type == 'code_generation':
            return self.config.code_generation_model
        elif request.task_type == 'analysis':
            return self.config.analysis_model
        elif request.task_type == 'explanation':
            return self.config.explanation_model
        else:
            return self.config.default_model
            
    def _prepare_prompt(self, request: ModelRequest) -> str:
        """
        Prepare prompt based on request type
        """
        if request.task_type == 'code_generation':
            return self._prepare_code_prompt(request)
        elif request.task_type == 'analysis':
            return self._prepare_analysis_prompt(request)
        elif request.task_type == 'explanation':
            return self._prepare_explanation_prompt(request)
        else:
            return request.prompt
            
    def _prepare_code_prompt(self, request: ModelRequest) -> str:
        """
        Prepare prompt for code generation
        """
        return f"""
        Generate code based on the following requirements:
        
        Requirements:
        {request.prompt}
        
        Additional Context:
        {request.context or ''}
        
        Please ensure the code:
        1. Follows best practices and patterns
        2. Includes proper error handling
        3. Is well-documented
        4. Is optimized for performance
        5. Follows the specified style guide
        """
        
    def _prepare_analysis_prompt(self, request: ModelRequest) -> str:
        """
        Prepare prompt for code analysis
        """
        return f"""
        Analyze the following code:
        
        {request.prompt}
        
        Please provide:
        1. Code quality assessment
        2. Potential issues and risks
        3. Performance considerations
        4. Security concerns
        5. Improvement suggestions
        """
        
    def _prepare_explanation_prompt(self, request: ModelRequest) -> str:
        """
        Prepare prompt for code explanation
        """
        return f"""
        Explain the following code:
        
        {request.prompt}
        
        Please include:
        1. High-level overview
        2. Key components and their purpose
        3. Important algorithms or patterns
        4. Potential edge cases
        5. Usage examples
        """
        
    def _generate_cache_key(self, request: ModelRequest) -> str:
        """
        Generate cache key for request
        """
        return f"{request.task_type}:{request.model}:{hash(request.prompt)}"
        
    async def start(self):
        """
        Start the model service
        """
        import uvicorn
        uvicorn.run(
            self.app,
            host=self.config.host,
            port=self.config.port,
            reload=self.config.debug
        )
