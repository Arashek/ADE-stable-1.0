"""Resource Management System

This module provides a comprehensive resource management system for monitoring,
optimizing, and analyzing system resources. It includes components for:

1. Resource Monitoring: Tracks system resource usage and generates predictions
2. Resource Optimization: Optimizes resource allocation and handles dynamic scaling
3. Resource Analytics: Analyzes resource usage patterns and generates insights
4. Resource Management: Coordinates between components and manages resource lifecycle

The system is designed to be:
- Asynchronous: Uses async/await for non-blocking operations
- Configurable: All settings can be customized through YAML configuration
- Extensible: Easy to add new monitoring metrics and optimization strategies
- Efficient: Uses caching and batch processing for better performance
"""

import logging
from pathlib import Path
import yaml

from .factory import ResourceManagerFactory
from .manager import ResourceManager
from .monitor import ResourceMonitor, ResourceMetrics, ResourcePrediction
from .optimizer import ResourceOptimizer, OptimizationAction
from .analytics import ResourceAnalyticsManager, ResourceAnalytics

# Configure logging
def setup_logging():
    """Configure logging for the resource management system"""
    try:
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "resource_manager.log"),
                logging.StreamHandler()
            ]
        )
        
    except Exception as e:
        print(f"Error setting up logging: {str(e)}")
        
# Initialize resource management system
def initialize_resource_manager() -> ResourceManager:
    """Initialize the resource management system"""
    try:
        # Setup logging
        setup_logging()
        
        # Get resource manager instance
        manager = ResourceManagerFactory.get_instance()
        
        return manager
        
    except Exception as e:
        print(f"Error initializing resource manager: {str(e)}")
        raise
        
# Export main components
__all__ = [
    'ResourceManager',
    'ResourceMonitor',
    'ResourceMetrics',
    'ResourcePrediction',
    'ResourceOptimizer',
    'OptimizationAction',
    'ResourceAnalyticsManager',
    'ResourceAnalytics',
    'ResourceManagerFactory',
    'initialize_resource_manager'
] 