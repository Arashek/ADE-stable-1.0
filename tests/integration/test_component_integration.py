import pytest
from typing import Dict, Any
from unittest.mock import MagicMock

from interfaces.base import (
    ComponentInterface,
    DataCollector,
    Monitor,
    Coordinator,
    ErrorHandler,
    StateManager,
    ResourceManager,
)

class MockComponent(ComponentInterface):
    def __init__(self, name: str):
        self.name = name
        self.initialized = False
        self.config = {}
        
    def initialize(self, config: Dict[str, Any]) -> None:
        self.initialized = True
        self.config = config
        
    def health_check(self) -> Dict[str, Any]:
        return {"status": "healthy", "name": self.name}
        
    def shutdown(self) -> None:
        self.initialized = False

class TestComponentIntegration:
    @pytest.fixture
    def coordinator(self):
        return MagicMock(spec=Coordinator)
        
    @pytest.fixture
    def error_handler(self):
        return MagicMock(spec=ErrorHandler)
        
    @pytest.fixture
    def state_manager(self):
        return MagicMock(spec=StateManager)
        
    @pytest.fixture
    def resource_manager(self):
        return MagicMock(spec=ResourceManager)
        
    def test_component_lifecycle(self, coordinator, error_handler):
        # Create test component
        component = MockComponent("test_component")
        
        # Test initialization
        config = {"setting": "value"}
        component.initialize(config)
        assert component.initialized
        assert component.config == config
        
        # Test registration
        coordinator.register_component.return_value = "comp_id_1"
        component_id = coordinator.register_component(component)
        assert component_id == "comp_id_1"
        coordinator.register_component.assert_called_once_with(component)
        
        # Test error handling
        error = Exception("Test error")
        context = {"component": component.name}
        error_handler.handle_error(error, context)
        error_handler.handle_error.assert_called_once_with(error, context)
        
        # Test shutdown
        component.shutdown()
        assert not component.initialized
        coordinator.unregister_component.assert_not_called()
        
    def test_component_state_management(self, state_manager):
        # Create test component
        component = MockComponent("test_component")
        
        # Test state saving
        state = {"key": "value"}
        state_manager.save_state.return_value = "state_1"
        state_id = state_manager.save_state(state)
        assert state_id == "state_1"
        state_manager.save_state.assert_called_once_with(state)
        
        # Test state loading
        state_manager.load_state.return_value = state
        loaded_state = state_manager.load_state(state_id)
        assert loaded_state == state
        state_manager.load_state.assert_called_once_with(state_id)
        
    def test_resource_management(self, resource_manager):
        # Test resource allocation
        resource_manager.allocate.return_value = "alloc_1"
        allocation_id = resource_manager.allocate("cpu", 2)
        assert allocation_id == "alloc_1"
        resource_manager.allocate.assert_called_once_with("cpu", 2)
        
        # Test resource usage
        resource_manager.get_usage.return_value = {"cpu": 2}
        usage = resource_manager.get_usage()
        assert usage == {"cpu": 2}
        resource_manager.get_usage.assert_called_once()
        
        # Test resource deallocation
        resource_manager.deallocate(allocation_id)
        resource_manager.deallocate.assert_called_once_with(allocation_id)
        
    def test_component_monitoring(self, coordinator):
        # Create test components
        component1 = MockComponent("component1")
        component2 = MockComponent("component2")
        
        # Register components
        coordinator.register_component.side_effect = ["comp_1", "comp_2"]
        id1 = coordinator.register_component(component1)
        id2 = coordinator.register_component(component2)
        
        # Verify health checks
        assert component1.health_check() == {"status": "healthy", "name": "component1"}
        assert component2.health_check() == {"status": "healthy", "name": "component2"}
        
        # Test component coordination
        task = {"action": "test", "components": [id1, id2]}
        coordinator.coordinate_task(task)
        coordinator.coordinate_task.assert_called_once_with(task)
        
    def test_error_pattern_detection(self, error_handler):
        # Test error pattern registration
        def recovery_strategy(error: Exception) -> None:
            pass
            
        error_handler.register_recovery_strategy("test_pattern", recovery_strategy)
        error_handler.register_recovery_strategy.assert_called_once_with(
            "test_pattern", recovery_strategy
        )
        
        # Test error pattern retrieval
        error_handler.get_error_pattern.return_value = {
            "pattern": "test_pattern",
            "strategy": recovery_strategy,
        }
        pattern = error_handler.get_error_pattern("error_1")
        assert pattern["pattern"] == "test_pattern"
        error_handler.get_error_pattern.assert_called_once_with("error_1") 