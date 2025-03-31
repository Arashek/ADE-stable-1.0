from typing import Dict, List, Optional
import logging
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ModelResponse:
    content: str
    confidence_score: float
    response_time: float
    error: Optional[str] = None

class FallbackManager:
    def __init__(self, config: Dict):
        self.config = config
        self.fallback_history = {}
        self.load_thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8
        }
        
    async def execute_with_fallback(self, task_id: str, primary_model: str, 
                                  fallback_models: List[str], execute_fn, **kwargs) -> ModelResponse:
        """Execute task with fallback strategy"""
        start_time = time.time()
        
        # Try primary model first
        response = await self._try_model(primary_model, execute_fn, **kwargs)
        
        # Check if we need fallback
        if self._needs_fallback(response):
            logger.info(f"Initiating fallback for task {task_id}")
            response = await self._handle_fallback(fallback_models, execute_fn, **kwargs)
            
        # Record execution history
        self._record_execution(task_id, primary_model, response)
        
        return response
        
    async def _try_model(self, model: str, execute_fn, **kwargs) -> ModelResponse:
        """Try executing with a specific model"""
        try:
            start_time = time.time()
            result = await execute_fn(model=model, **kwargs)
            response_time = time.time() - start_time
            
            return ModelResponse(
                content=result.get('content', ''),
                confidence_score=result.get('confidence', 0.0),
                response_time=response_time
            )
        except Exception as e:
            logger.error(f"Error executing model {model}: {str(e)}")
            return ModelResponse(
                content='',
                confidence_score=0.0,
                response_time=0.0,
                error=str(e)
            )
            
    def _needs_fallback(self, response: ModelResponse) -> bool:
        """Determine if fallback is needed based on response"""
        if response.error:
            return True
            
        strategies = self.config.get('fallback_strategies', {})
        
        # Check performance threshold
        if strategies.get('performance'):
            perf_threshold = strategies['performance'][0].get('condition', '').split(' ')[2]
            if response.response_time > float(perf_threshold[:-1]):  # Remove 's' from '5s'
                return True
                
        # Check quality threshold
        if strategies.get('quality'):
            quality_threshold = float(strategies['quality'][0].get('condition', '').split(' ')[2])
            if response.confidence_score < quality_threshold:
                return True
                
        return False
        
    async def _handle_fallback(self, fallback_models: List[str], execute_fn, **kwargs) -> ModelResponse:
        """Handle fallback execution"""
        best_response = None
        
        for model in fallback_models:
            response = await self._try_model(model, execute_fn, **kwargs)
            
            if not response.error and (not best_response or 
                response.confidence_score > best_response.confidence_score):
                best_response = response
                
            # If we get a good enough response, stop trying
            if response.confidence_score > 0.8:
                break
                
        return best_response or ModelResponse(
            content='All fallback attempts failed',
            confidence_score=0.0,
            response_time=0.0,
            error='Fallback chain exhausted'
        )
        
    def _record_execution(self, task_id: str, model: str, response: ModelResponse):
        """Record execution results for analysis"""
        if task_id not in self.fallback_history:
            self.fallback_history[task_id] = []
            
        self.fallback_history[task_id].append({
            'model': model,
            'response_time': response.response_time,
            'confidence_score': response.confidence_score,
            'error': response.error,
            'timestamp': time.time()
        })
        
    def get_load_balancing_model(self, available_models: List[str]) -> str:
        """Get model based on load balancing strategy"""
        strategies = self.config.get('fallback_strategies', {}).get('load_balancing', [])
        if not strategies:
            return available_models[0]
            
        strategy = strategies[0]
        if strategy['strategy'] == 'round_robin':
            # Simple round-robin selection
            current_time = int(time.time())
            return available_models[current_time % len(available_models)]
            
        return available_models[0]
        
    def analyze_performance(self, window_minutes: int = 60) -> Dict:
        """Analyze model performance over time window"""
        current_time = time.time()
        window_start = current_time - (window_minutes * 60)
        
        model_stats = {}
        
        for executions in self.fallback_history.values():
            for exec in executions:
                if exec['timestamp'] < window_start:
                    continue
                    
                model = exec['model']
                if model not in model_stats:
                    model_stats[model] = {
                        'total_executions': 0,
                        'successful_executions': 0,
                        'avg_response_time': 0,
                        'avg_confidence': 0,
                        'error_rate': 0
                    }
                    
                stats = model_stats[model]
                stats['total_executions'] += 1
                
                if not exec['error']:
                    stats['successful_executions'] += 1
                    stats['avg_response_time'] += exec['response_time']
                    stats['avg_confidence'] += exec['confidence_score']
                    
        # Calculate averages
        for model, stats in model_stats.items():
            if stats['successful_executions'] > 0:
                stats['avg_response_time'] /= stats['successful_executions']
                stats['avg_confidence'] /= stats['successful_executions']
            stats['error_rate'] = 1 - (stats['successful_executions'] / stats['total_executions'])
            
        return model_stats
