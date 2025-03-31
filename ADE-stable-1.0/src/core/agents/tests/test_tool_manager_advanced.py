import unittest
from datetime import datetime
import time
import threading
import queue
import concurrent.futures
from typing import Dict, Any, List
from ..tool_manager import ToolManager, ToolCall
from ..memory_tracker import MemoryTracker
from ..capabilities import AgentCapabilities

class TestToolManagerAdvanced(unittest.TestCase):
    def setUp(self):
        self.manager = ToolManager()
        self.memory_tracker = MemoryTracker()
        self.agent_capabilities = AgentCapabilities(
            agent_id="test_agent",
            supported_languages=["python", "javascript", "java"]
        )
        
    def test_concurrent_tool_execution(self):
        """Test concurrent tool execution and thread safety."""
        def concurrent_tool(delay: float) -> str:
            time.sleep(delay)
            return f"completed after {delay}s"
            
        self.manager.register_tool("concurrent_tool", concurrent_tool)
        
        # Create multiple threads to execute tools concurrently
        results = queue.Queue()
        threads = []
        
        for i in range(5):
            thread = threading.Thread(
                target=lambda: results.put(
                    self.manager.execute_tool(
                        "concurrent_tool",
                        {"delay": 0.1},
                        "test_agent",
                        {"thread_id": i}
                    )
                )
            )
            threads.append(thread)
            thread.start()
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        # Verify all executions completed successfully
        self.assertEqual(results.qsize(), 5)
        for _ in range(5):
            self.assertIn("completed after 0.1s", results.get())
            
    def test_tool_with_memory_tracking(self):
        """Test tool execution with memory tracking integration."""
        def memory_intensive_tool(size: int) -> List[int]:
            return [0] * size
            
        self.manager.register_tool("memory_tool", memory_intensive_tool)
        
        # Take initial memory snapshot
        initial_snapshot = self.memory_tracker.take_snapshot()
        
        # Execute memory-intensive tool
        result = self.manager.execute_tool(
            "memory_tool",
            {"size": 1000000},
            "test_agent",
            {"context": "memory_test"}
        )
        
        # Take final memory snapshot
        final_snapshot = self.memory_tracker.take_snapshot()
        
        # Verify memory usage increased
        self.assertGreater(
            final_snapshot.used_memory,
            initial_snapshot.used_memory
        )
        
        # Verify memory access was tracked
        access_history = self.memory_tracker.get_access_history(
            agent_id="test_agent"
        )
        self.assertGreater(len(access_history), 0)
        
    def test_tool_with_agent_capabilities(self):
        """Test tool execution with agent capabilities integration."""
        def code_analysis_tool(file_path: str) -> Dict[str, Any]:
            return self.agent_capabilities.analyze_code(file_path, "python")
            
        self.manager.register_tool("code_analyzer", code_analysis_tool)
        
        # Create a test Python file
        test_file = "test_analysis.py"
        with open(test_file, "w") as f:
            f.write("""
def test_function(param: str) -> str:
    return param.upper()

class TestClass:
    def __init__(self, value: int):
        self.value = value
""")
            
        # Execute code analysis tool
        result = self.manager.execute_tool(
            "code_analyzer",
            {"file_path": test_file},
            "test_agent",
            {"context": "code_analysis"}
        )
        
        # Verify analysis results
        self.assertIn("functions", result)
        self.assertIn("classes", result)
        self.assertEqual(len(result["functions"]), 1)
        self.assertEqual(len(result["classes"]), 1)
        
        # Clean up
        import os
        os.remove(test_file)
        
    def test_tool_error_recovery(self):
        """Test tool error recovery and retry mechanisms."""
        class RetryableError(Exception):
            pass
            
        retry_count = 0
        def failing_tool() -> str:
            nonlocal retry_count
            retry_count += 1
            if retry_count < 3:
                raise RetryableError("Temporary failure")
            return "success"
            
        self.manager.register_tool("failing_tool", failing_tool)
        
        # Execute with retry
        result = self.manager.execute_tool(
            "failing_tool",
            {},
            "test_agent",
            {"context": "retry_test"}
        )
        
        # Verify successful recovery
        self.assertEqual(result, "success")
        self.assertEqual(retry_count, 3)
        
    def test_tool_performance(self):
        """Test tool performance under load."""
        def performance_tool(iterations: int) -> List[int]:
            return [i * i for i in range(iterations)]
            
        self.manager.register_tool("performance_tool", performance_tool)
        
        # Test with increasing load
        sizes = [1000, 10000, 100000]
        durations = []
        
        for size in sizes:
            start_time = time.time()
            result = self.manager.execute_tool(
                "performance_tool",
                {"iterations": size},
                "test_agent",
                {"context": "performance_test"}
            )
            duration = time.time() - start_time
            durations.append(duration)
            
        # Verify performance characteristics
        self.assertEqual(len(result), sizes[-1])
        self.assertLess(durations[0], durations[1])  # Should scale with size
        self.assertLess(durations[1], durations[2])
        
    def test_tool_resource_limits(self):
        """Test tool execution with resource limits."""
        def resource_intensive_tool(size: int) -> List[int]:
            return [0] * size
            
        self.manager.register_tool("resource_tool", resource_intensive_tool)
        
        # Set memory limit
        import psutil
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Test with large allocation
        with self.assertRaises(RuntimeError):
            self.manager.execute_tool(
                "resource_tool",
                {"size": 1000000000},  # 1GB allocation
                "test_agent",
                {"context": "resource_test"}
            )
            
        # Verify memory was cleaned up
        final_memory = process.memory_info().rss
        self.assertLess(final_memory - initial_memory, 1024 * 1024 * 100)  # Less than 100MB difference
        
    def test_tool_dependency_chain(self):
        """Test execution of dependent tools."""
        def tool_a() -> int:
            return 42
            
        def tool_b(value: int) -> str:
            return f"value: {value}"
            
        def tool_c(text: str) -> bool:
            return "42" in text
            
        self.manager.register_tool("tool_a", tool_a)
        self.manager.register_tool("tool_b", tool_b)
        self.manager.register_tool("tool_c", tool_c)
        
        # Execute chain of dependent tools
        result_a = self.manager.execute_tool(
            "tool_a",
            {},
            "test_agent",
            {"context": "chain_test"}
        )
        
        result_b = self.manager.execute_tool(
            "tool_b",
            {"value": result_a},
            "test_agent",
            {"context": "chain_test"}
        )
        
        result_c = self.manager.execute_tool(
            "tool_c",
            {"text": result_b},
            "test_agent",
            {"context": "chain_test"}
        )
        
        # Verify chain execution
        self.assertEqual(result_a, 42)
        self.assertEqual(result_b, "value: 42")
        self.assertTrue(result_c)
        
    def test_tool_metrics_aggregation(self):
        """Test aggregation of tool metrics across multiple executions."""
        def metric_tool(delay: float) -> str:
            time.sleep(delay)
            return "done"
            
        self.manager.register_tool("metric_tool", metric_tool)
        
        # Execute tool multiple times with varying delays
        delays = [0.1, 0.2, 0.3, 0.4, 0.5]
        for delay in delays:
            self.manager.execute_tool(
                "metric_tool",
                {"delay": delay},
                "test_agent",
                {"context": "metric_test"}
            )
            
        metrics = self.manager.get_tool_metrics()
        
        # Verify metrics
        self.assertEqual(metrics['total_calls'], len(delays))
        self.assertEqual(metrics['success_rate'], 1.0)
        self.assertGreater(metrics['avg_duration'], 0.3)  # Should be close to average delay
        
        # Verify tool-specific metrics
        tool_metrics = metrics['tool_usage']['metric_tool']
        self.assertEqual(tool_metrics['calls'], len(delays))
        self.assertEqual(tool_metrics['success_rate'], 1.0)
        self.assertGreater(tool_metrics['avg_duration'], 0.3)
        
if __name__ == '__main__':
    unittest.main() 