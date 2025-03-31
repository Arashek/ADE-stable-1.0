from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic

T = TypeVar('T')

class ComponentInterface(ABC):
    """Base interface for all ADE platform components."""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the component with configuration."""
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Return component health status."""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Clean shutdown of the component."""
        pass

class DataCollector(ComponentInterface, Generic[T]):
    """Interface for components that collect data."""
    
    @abstractmethod
    def collect(self, source: str) -> List[T]:
        """Collect data from specified source."""
        pass
    
    @abstractmethod
    def process(self, data: List[T]) -> List[T]:
        """Process collected data."""
        pass
    
    @abstractmethod
    def store(self, data: List[T]) -> None:
        """Store processed data."""
        pass

class Monitor(ComponentInterface):
    """Interface for monitoring components."""
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        pass
    
    @abstractmethod
    def set_alert(self, condition: str, threshold: Any) -> None:
        """Set monitoring alert."""
        pass
    
    @abstractmethod
    def clear_alert(self, alert_id: str) -> None:
        """Clear monitoring alert."""
        pass

class Coordinator(ComponentInterface):
    """Interface for coordination components."""
    
    @abstractmethod
    def register_component(self, component: ComponentInterface) -> str:
        """Register a component for coordination."""
        pass
    
    @abstractmethod
    def unregister_component(self, component_id: str) -> None:
        """Unregister a component."""
        pass
    
    @abstractmethod
    def coordinate_task(self, task: Dict[str, Any]) -> None:
        """Coordinate task execution."""
        pass

class ErrorHandler(ComponentInterface):
    """Interface for error handling components."""
    
    @abstractmethod
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Handle an error with context."""
        pass
    
    @abstractmethod
    def get_error_pattern(self, error_id: str) -> Optional[Dict[str, Any]]:
        """Get error pattern by ID."""
        pass
    
    @abstractmethod
    def register_recovery_strategy(self, pattern: str, strategy: callable) -> None:
        """Register error recovery strategy."""
        pass

class StateManager(ComponentInterface):
    """Interface for state management components."""
    
    @abstractmethod
    def save_state(self, state: Dict[str, Any]) -> str:
        """Save component state."""
        pass
    
    @abstractmethod
    def load_state(self, state_id: str) -> Dict[str, Any]:
        """Load component state."""
        pass
    
    @abstractmethod
    def clear_state(self, state_id: str) -> None:
        """Clear component state."""
        pass

class ResourceManager(ComponentInterface):
    """Interface for resource management components."""
    
    @abstractmethod
    def allocate(self, resource_type: str, amount: int) -> str:
        """Allocate resources."""
        pass
    
    @abstractmethod
    def deallocate(self, allocation_id: str) -> None:
        """Deallocate resources."""
        pass
    
    @abstractmethod
    def get_usage(self) -> Dict[str, Any]:
        """Get current resource usage."""
        pass 