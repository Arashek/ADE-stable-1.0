from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta
import json
from pathlib import Path

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class Provider(ABC):
    """Base class for all providers"""
    
    def __init__(self, name: str, tier: str = "standard"):
        self.name = name
        self.tier = tier
        self.last_used = None
        self.total_tokens = 0
        self.total_cost = 0.0
        self.error_count = 0
        self.success_count = 0
        self.response_times = []
        self.is_enabled = True
        
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from the provider"""
        pass
    
    @abstractmethod
    async def get_models(self) -> List[str]:
        """Get available models from the provider"""
        pass
    
    def update_metrics(self, tokens: int, cost: float, response_time: float, success: bool):
        """Update provider metrics"""
        self.last_used = datetime.now()
        self.total_tokens += tokens
        self.total_cost += cost
        self.response_times.append(response_time)
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
            
    def get_performance_score(self) -> float:
        """Calculate performance score based on multiple factors"""
        if not self.response_times:
            return 0.0
            
        avg_response_time = sum(self.response_times) / len(self.response_times)
        success_rate = self.success_count / (self.success_count + self.error_count) if (self.success_count + self.error_count) > 0 else 0
        cost_efficiency = 1.0 / (self.total_cost + 1)  # Avoid division by zero
        
        # Weighted scoring
        weights = {
            'response_time': 0.4,
            'success_rate': 0.4,
            'cost_efficiency': 0.2
        }
        
        # Normalize response time (lower is better)
        max_response_time = max(self.response_times)
        normalized_response_time = 1 - (avg_response_time / max_response_time)
        
        score = (
            weights['response_time'] * normalized_response_time +
            weights['success_rate'] * success_rate +
            weights['cost_efficiency'] * cost_efficiency
        )
        
        return score

class ProviderRegistry:
    """Registry for managing different providers"""
    
    def __init__(self):
        self.providers: Dict[str, Provider] = {}
        self.default_provider = None
        self.metrics_file = Path("data/provider_metrics.json")
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.load_metrics()
        
    def load_metrics(self):
        """Load provider metrics from file"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    metrics = json.load(f)
                    for provider_name, provider_metrics in metrics.items():
                        if provider_name in self.providers:
                            provider = self.providers[provider_name]
                            provider.total_tokens = provider_metrics['total_tokens']
                            provider.total_cost = provider_metrics['total_cost']
                            provider.error_count = provider_metrics['error_count']
                            provider.success_count = provider_metrics['success_count']
                            provider.response_times = provider_metrics['response_times']
                            provider.last_used = datetime.fromisoformat(provider_metrics['last_used']) if provider_metrics['last_used'] else None
            except Exception as e:
                logger.error(f"Error loading provider metrics: {e}")
                
    def save_metrics(self):
        """Save provider metrics to file"""
        try:
            metrics = {}
            for provider_name, provider in self.providers.items():
                metrics[provider_name] = {
                    'total_tokens': provider.total_tokens,
                    'total_cost': provider.total_cost,
                    'error_count': provider.error_count,
                    'success_count': provider.success_count,
                    'response_times': provider.response_times,
                    'last_used': provider.last_used.isoformat() if provider.last_used else None
                }
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics, f)
        except Exception as e:
            logger.error(f"Error saving provider metrics: {e}")
            
    def register_provider(self, provider: Provider):
        """Register a new provider"""
        self.providers[provider.name] = provider
        if not self.default_provider:
            self.default_provider = provider
            
    def get_provider(self, name: Optional[str] = None) -> Provider:
        """Get a provider by name or the best performing provider"""
        if name and name in self.providers:
            return self.providers[name]
            
        # Get enabled providers sorted by performance score
        enabled_providers = [p for p in self.providers.values() if p.is_enabled]
        if not enabled_providers:
            raise ValueError("No enabled providers available")
            
        # Sort by performance score
        sorted_providers = sorted(enabled_providers, key=lambda p: p.get_performance_score(), reverse=True)
        return sorted_providers[0]
        
    def get_best_provider(self, **kwargs) -> Provider:
        """Get the best performing provider based on current metrics"""
        return self.get_provider()
        
    def get_provider_stats(self) -> Dict[str, Any]:
        """Get statistics for all providers"""
        stats = {}
        for name, provider in self.providers.items():
            stats[name] = {
                'total_tokens': provider.total_tokens,
                'total_cost': provider.total_cost,
                'error_count': provider.error_count,
                'success_count': provider.success_count,
                'avg_response_time': sum(provider.response_times) / len(provider.response_times) if provider.response_times else 0,
                'performance_score': provider.get_performance_score(),
                'last_used': provider.last_used.isoformat() if provider.last_used else None,
                'is_enabled': provider.is_enabled
            }
        return stats

# Create global registry instance
registry = ProviderRegistry() 