import unittest
from datetime import datetime
import time
from typing import Dict, Any
from ..tool_manager import ToolManager, ToolCall

class TestToolManager(unittest.TestCase):
    def setUp(self):
        self.manager = ToolManager()
        
    def test_tool_registration(self):
        """Test tool registration and parameter validation."""
        def test_tool(param1: str, param2: int = 42) -> str:
            return f"{param1}: {param2}"
            
        self.manager.register_tool("test_tool", test_tool)
        
        # Test valid call
        result = self.manager.execute_tool(
            "test_tool",
            {"param1": "hello"},
            "test_agent",
            {"context": "test"}
        )
        self.assertEqual(result, "hello: 42")
        
        # Test with explicit param2
        result = self.manager.execute_tool(
            "test_tool",
            {"param1": "hello", "param2": 100},
            "test_agent",
            {"context": "test"}
        )
        self.assertEqual(result, "hello: 100")
        
        # Test missing required parameter
        with self.assertRaises(ValueError) as cm:
            self.manager.execute_tool(
                "test_tool",
                {},
                "test_agent",
                {"context": "test"}
            )
        self.assertIn("Missing required parameters", str(cm.exception))
        
        # Test invalid parameter type
        with self.assertRaises(TypeError) as cm:
            self.manager.execute_tool(
                "test_tool",
                {"param1": 123},  # Should be string
                "test_agent",
                {"context": "test"}
            )
        self.assertIn("must be of type str", str(cm.exception))
        
    def test_tool_timeout(self):
        """Test tool execution timeout."""
        def slow_tool() -> str:
            time.sleep(2)  # Sleep for 2 seconds
            return "done"
            
        self.manager.register_tool("slow_tool", slow_tool)
        self.manager._timeout = 1  # Set timeout to 1 second
        
        with self.assertRaises(RuntimeError) as cm:
            self.manager.execute_tool(
                "slow_tool",
                {},
                "test_agent",
                {"context": "test"}
            )
        self.assertIn("Tool execution failed", str(cm.exception))
        
    def test_tool_history(self):
        """Test tool call history tracking."""
        def test_tool(param: str) -> str:
            return param.upper()
            
        self.manager.register_tool("test_tool", test_tool)
        
        # Make some test calls
        for i in range(3):
            self.manager.execute_tool(
                "test_tool",
                {"param": f"test{i}"},
                "test_agent",
                {"context": "test"}
            )
            
        # Check history
        history = self.manager.get_tool_history()
        self.assertEqual(len(history), 3)
        
        # Check filtered history
        filtered = self.manager.get_tool_history(agent_id="test_agent")
        self.assertEqual(len(filtered), 3)
        
        filtered = self.manager.get_tool_history(tool_name="test_tool")
        self.assertEqual(len(filtered), 3)
        
    def test_tool_metrics(self):
        """Test tool usage metrics calculation."""
        def success_tool() -> str:
            return "success"
            
        def error_tool() -> str:
            raise ValueError("Test error")
            
        self.manager.register_tool("success_tool", success_tool)
        self.manager.register_tool("error_tool", error_tool)
        
        # Make some test calls
        for _ in range(3):
            self.manager.execute_tool(
                "success_tool",
                {},
                "test_agent",
                {"context": "test"}
            )
            
        for _ in range(2):
            with self.assertRaises(RuntimeError):
                self.manager.execute_tool(
                    "error_tool",
                    {},
                    "test_agent",
                    {"context": "test"}
                )
                
        metrics = self.manager.get_tool_metrics()
        
        # Check basic metrics
        self.assertEqual(metrics['total_calls'], 5)
        self.assertEqual(metrics['success_rate'], 0.6)
        
        # Check tool-specific metrics
        self.assertEqual(metrics['tool_usage']['success_tool']['calls'], 3)
        self.assertEqual(metrics['tool_usage']['success_tool']['success_rate'], 1.0)
        self.assertEqual(metrics['tool_usage']['error_tool']['calls'], 2)
        self.assertEqual(metrics['tool_usage']['error_tool']['success_rate'], 0.0)
        
        # Check error rates
        self.assertEqual(
            metrics['error_rates']['error_tool']['ValueError'],
            2
        )
        
    def test_data_export_import(self):
        """Test data export and import functionality."""
        def test_tool(param: str) -> str:
            return param.upper()
            
        self.manager.register_tool("test_tool", test_tool)
        
        # Make some test calls
        for i in range(3):
            self.manager.execute_tool(
                "test_tool",
                {"param": f"test{i}"},
                "test_agent",
                {"context": "test"}
            )
            
        # Export data
        export_path = "test_tool_data.json"
        self.manager.export_data(export_path)
        
        # Create new manager and import data
        new_manager = ToolManager()
        new_manager.import_data(export_path)
        
        # Verify imported data
        self.assertEqual(
            len(new_manager.get_tool_history()),
            len(self.manager.get_tool_history())
        )
        
        # Clean up
        import os
        os.remove(export_path)
        
if __name__ == '__main__':
    unittest.main() 