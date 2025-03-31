from typing import Dict, Optional
import logging
from pathlib import Path
import yaml

from .manager import ResourceManager
from .monitor import ResourceMonitor
from .optimizer import ResourceOptimizer
from .analytics import ResourceAnalyticsManager

logger = logging.getLogger(__name__)

class ResourceManagerFactory:
    """Factory for creating and configuring resource management components"""
    
    _instance: Optional[ResourceManager] = None
    
    @classmethod
    def get_instance(cls) -> ResourceManager:
        """Get or create the singleton ResourceManager instance"""
        if cls._instance is None:
            cls._instance = cls._create_manager()
        return cls._instance
        
    @classmethod
    def _create_manager(cls) -> ResourceManager:
        """Create and configure a new ResourceManager instance"""
        try:
            # Load configuration
            config = cls._load_config()
            
            # Create components with configuration
            monitor = cls._create_monitor(config)
            optimizer = cls._create_optimizer(config, monitor)
            analytics = cls._create_analytics(config, monitor, optimizer)
            
            # Create and configure manager
            manager = ResourceManager()
            manager.monitor = monitor
            manager.optimizer = optimizer
            manager.analytics = analytics
            
            return manager
            
        except Exception as e:
            logger.error(f"Error creating resource manager: {str(e)}")
            raise
            
    @classmethod
    def _load_config(cls) -> Dict:
        """Load configuration from file"""
        try:
            config_path = Path("src/core/resources/config/monitoring.yaml")
            if config_path.exists():
                with open(config_path, "r") as f:
                    return yaml.safe_load(f)
            else:
                logger.warning("Configuration file not found, using defaults")
                return {}
                
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return {}
            
    @classmethod
    def _create_monitor(cls, config: Dict) -> ResourceMonitor:
        """Create and configure ResourceMonitor"""
        try:
            monitor = ResourceMonitor()
            
            # Configure monitor settings
            if "monitoring" in config:
                monitor.config = config["monitoring"]
                
            return monitor
            
        except Exception as e:
            logger.error(f"Error creating monitor: {str(e)}")
            raise
            
    @classmethod
    def _create_optimizer(cls, config: Dict, monitor: ResourceMonitor) -> ResourceOptimizer:
        """Create and configure ResourceOptimizer"""
        try:
            optimizer = ResourceOptimizer(monitor)
            
            # Configure optimizer settings
            if "optimization" in config:
                optimizer.config = config["optimization"]
                
            return optimizer
            
        except Exception as e:
            logger.error(f"Error creating optimizer: {str(e)}")
            raise
            
    @classmethod
    def _create_analytics(cls, config: Dict, monitor: ResourceMonitor, optimizer: ResourceOptimizer) -> ResourceAnalyticsManager:
        """Create and configure ResourceAnalyticsManager"""
        try:
            analytics = ResourceAnalyticsManager(monitor, optimizer)
            
            # Configure analytics settings
            if "analytics" in config:
                analytics.config = config["analytics"]
                
            return analytics
            
        except Exception as e:
            logger.error(f"Error creating analytics: {str(e)}")
            raise
            
    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance"""
        cls._instance = None 