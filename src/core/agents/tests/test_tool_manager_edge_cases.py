import unittest
from datetime import datetime
import time
import threading
import queue
import concurrent.futures
import random
import string
import gc
import sys
import os
from typing import Dict, Any, List, Optional
from ..tool_manager import ToolManager, ToolCall
from ..memory_tracker import MemoryTracker
from ..capabilities import AgentCapabilities
from ..language_analyzers.python import PythonAnalyzer
from ..language_analyzers.javascript import JavaScriptAnalyzer
from ..language_analyzers.java import JavaAnalyzer

class TestToolManagerEdgeCases(unittest.TestCase):
    def setUp(self):
        self.manager = ToolManager()
        self.memory_tracker = MemoryTracker()
        self.agent_capabilities = AgentCapabilities(
            agent_id="test_agent",
            supported_languages=["python", "javascript", "java"]
        )
        self.python_analyzer = PythonAnalyzer()
        self.javascript_analyzer = JavaScriptAnalyzer()
        self.java_analyzer = JavaAnalyzer()
        
    def test_edge_case_parameters(self):
        """Test edge cases for tool parameters."""
        def edge_case_tool(
            empty_str: str = "",
            none_value: Optional[str] = None,
            zero: int = 0,
            negative: int = -1,
            large_number: int = sys.maxsize,
            empty_list: List = [],
            empty_dict: Dict = {},
            special_chars: str = "!@#$%^&*()",
            unicode_chars: str = "你好世界",
            very_long_str: str = "a" * 10000
        ) -> Dict[str, Any]:
            return {
                "empty_str": empty_str,
                "none_value": none_value,
                "zero": zero,
                "negative": negative,
                "large_number": large_number,
                "empty_list": empty_list,
                "empty_dict": empty_dict,
                "special_chars": special_chars,
                "unicode_chars": unicode_chars,
                "very_long_str": very_long_str
            }
            
        self.manager.register_tool("edge_case_tool", edge_case_tool)
        
        # Test with default values
        result = self.manager.execute_tool(
            "edge_case_tool",
            {},
            "test_agent",
            {"context": "edge_cases"}
        )
        
        # Verify all edge cases are handled correctly
        self.assertEqual(result["empty_str"], "")
        self.assertIsNone(result["none_value"])
        self.assertEqual(result["zero"], 0)
        self.assertEqual(result["negative"], -1)
        self.assertEqual(result["large_number"], sys.maxsize)
        self.assertEqual(result["empty_list"], [])
        self.assertEqual(result["empty_dict"], {})
        self.assertEqual(result["special_chars"], "!@#$%^&*()")
        self.assertEqual(result["unicode_chars"], "你好世界")
        self.assertEqual(len(result["very_long_str"]), 10000)
        
    def test_integration_with_analyzers(self):
        """Test integration with different language analyzers."""
        def multi_language_analyzer(file_path: str, language: str) -> Dict[str, Any]:
            analyzers = {
                "python": self.python_analyzer,
                "javascript": self.javascript_analyzer,
                "java": self.java_analyzer
            }
            
            if language not in analyzers:
                raise ValueError(f"Unsupported language: {language}")
                
            analyzer = analyzers[language]
            return analyzer.analyze_code(file_path)
            
        self.manager.register_tool("multi_language_analyzer", multi_language_analyzer)
        
        # Test with Python code
        python_file = "test_python.py"
        with open(python_file, "w") as f:
            f.write("""
def test_function(param: str) -> str:
    return param.upper()

class TestClass:
    def __init__(self, value: int):
        self.value = value
""")
            
        python_result = self.manager.execute_tool(
            "multi_language_analyzer",
            {"file_path": python_file, "language": "python"},
            "test_agent",
            {"context": "python_analysis"}
        )
        
        # Test with JavaScript code
        js_file = "test_js.js"
        with open(js_file, "w") as f:
            f.write("""
function testFunction(param) {
    return param.toUpperCase();
}

class TestClass {
    constructor(value) {
        this.value = value;
    }
}
""")
            
        js_result = self.manager.execute_tool(
            "multi_language_analyzer",
            {"file_path": js_file, "language": "javascript"},
            "test_agent",
            {"context": "js_analysis"}
        )
        
        # Test with Java code
        java_file = "TestJava.java"
        with open(java_file, "w") as f:
            f.write("""
public class TestJava {
    public static String testFunction(String param) {
        return param.toUpperCase();
    }
    
    public static class TestClass {
        private int value;
        
        public TestClass(int value) {
            this.value = value;
        }
    }
}
""")
            
        java_result = self.manager.execute_tool(
            "multi_language_analyzer",
            {"file_path": java_file, "language": "java"},
            "test_agent",
            {"context": "java_analysis"}
        )
        
        # Verify analysis results
        for result in [python_result, js_result, java_result]:
            self.assertIn("functions", result)
            self.assertIn("classes", result)
            self.assertEqual(len(result["functions"]), 1)
            self.assertEqual(len(result["classes"]), 1)
            
        # Clean up
        for file in [python_file, js_file, java_file]:
            os.remove(file)
            
    def test_performance_benchmarks(self):
        """Test performance benchmarks for different operations."""
        def benchmark_tool(operation: str, size: int) -> Dict[str, float]:
            results = {}
            
            if operation == "list_operations":
                start = time.time()
                lst = [i for i in range(size)]
                results["creation"] = time.time() - start
                
                start = time.time()
                lst.sort()
                results["sorting"] = time.time() - start
                
                start = time.time()
                sum(lst)
                results["summation"] = time.time() - start
                
            elif operation == "string_operations":
                start = time.time()
                s = "a" * size
                results["creation"] = time.time() - start
                
                start = time.time()
                s.upper()
                results["uppercase"] = time.time() - start
                
                start = time.time()
                len(s)
                results["length"] = time.time() - start
                
            elif operation == "dict_operations":
                start = time.time()
                d = {i: str(i) for i in range(size)}
                results["creation"] = time.time() - start
                
                start = time.time()
                d.get(size // 2)
                results["lookup"] = time.time() - start
                
                start = time.time()
                d.update({i: str(i+1) for i in range(size)})
                results["update"] = time.time() - start
                
            return results
            
        self.manager.register_tool("benchmark_tool", benchmark_tool)
        
        # Test with different sizes
        sizes = [1000, 10000, 100000]
        operations = ["list_operations", "string_operations", "dict_operations"]
        
        for size in sizes:
            for operation in operations:
                result = self.manager.execute_tool(
                    "benchmark_tool",
                    {"operation": operation, "size": size},
                    "test_agent",
                    {"context": "benchmark_test"}
                )
                
                # Verify performance characteristics
                for metric, duration in result.items():
                    self.assertGreater(duration, 0)
                    self.assertLess(duration, 10)  # Should complete within 10 seconds
                    
    def test_stress_scenarios(self):
        """Test stress scenarios with high concurrency and resource usage."""
        def stress_tool(operation: str, size: int, delay: float = 0) -> Dict[str, Any]:
            if delay > 0:
                time.sleep(delay)
                
            if operation == "memory_stress":
                return [0] * size
            elif operation == "cpu_stress":
                return [i * i for i in range(size)]
            elif operation == "io_stress":
                temp_file = f"stress_test_{random.randint(0, 1000)}.txt"
                with open(temp_file, "w") as f:
                    f.write("x" * size)
                with open(temp_file, "r") as f:
                    data = f.read()
                os.remove(temp_file)
                return {"size": len(data)}
                
        self.manager.register_tool("stress_tool", stress_tool)
        
        # Test concurrent memory stress
        memory_threads = []
        for _ in range(5):
            thread = threading.Thread(
                target=lambda: self.manager.execute_tool(
                    "stress_tool",
                    {"operation": "memory_stress", "size": 1000000},
                    "test_agent",
                    {"context": "memory_stress"}
                )
            )
            memory_threads.append(thread)
            thread.start()
            
        # Test concurrent CPU stress
        cpu_threads = []
        for _ in range(5):
            thread = threading.Thread(
                target=lambda: self.manager.execute_tool(
                    "stress_tool",
                    {"operation": "cpu_stress", "size": 100000},
                    "test_agent",
                    {"context": "cpu_stress"}
                )
            )
            cpu_threads.append(thread)
            thread.start()
            
        # Test concurrent IO stress
        io_threads = []
        for _ in range(5):
            thread = threading.Thread(
                target=lambda: self.manager.execute_tool(
                    "stress_tool",
                    {"operation": "io_stress", "size": 100000},
                    "test_agent",
                    {"context": "io_stress"}
                )
            )
            io_threads.append(thread)
            thread.start()
            
        # Wait for all threads to complete
        for thread in memory_threads + cpu_threads + io_threads:
            thread.join()
            
        # Verify system state
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        cpu_percent = process.cpu_percent()
        
        # Memory usage should be reasonable
        self.assertLess(memory_info.rss, 1024 * 1024 * 1000)  # Less than 1GB
        
        # CPU usage should be reasonable
        self.assertLess(cpu_percent, 90)  # Less than 90% CPU usage
        
    def test_error_handling_edge_cases(self):
        """Test error handling edge cases."""
        def error_tool(error_type: str) -> None:
            if error_type == "recursion":
                return error_tool(error_type)
            elif error_type == "memory":
                return [0] * (1024 * 1024 * 1024)  # Try to allocate 1GB
            elif error_type == "io":
                with open("/nonexistent/file.txt", "r") as f:
                    f.read()
            elif error_type == "type":
                return "string" + 42
            elif error_type == "import":
                import nonexistent_module
            elif error_type == "keyboard":
                raise KeyboardInterrupt()
                
        self.manager.register_tool("error_tool", error_tool)
        
        # Test various error types
        error_types = [
            "recursion", "memory", "io", "type", "import", "keyboard"
        ]
        
        for error_type in error_types:
            with self.assertRaises(Exception):
                self.manager.execute_tool(
                    "error_tool",
                    {"error_type": error_type},
                    "test_agent",
                    {"context": "error_test"}
                )
                
        # Verify error metrics
        metrics = self.manager.get_tool_metrics()
        self.assertEqual(metrics['total_calls'], len(error_types))
        self.assertEqual(metrics['success_rate'], 0.0)
        
    def test_resource_cleanup(self):
        """Test resource cleanup in various scenarios."""
        def cleanup_tool(operation: str) -> None:
            if operation == "file":
                temp_file = "cleanup_test.txt"
                with open(temp_file, "w") as f:
                    f.write("test")
                # File should be cleaned up by the tool manager
            elif operation == "memory":
                large_list = [0] * 1000000
                # Memory should be cleaned up by garbage collection
            elif operation == "thread":
                thread = threading.Thread(target=time.sleep, args=(1,))
                thread.start()
                # Thread should be cleaned up
                
        self.manager.register_tool("cleanup_tool", cleanup_tool)
        
        # Test file cleanup
        self.manager.execute_tool(
            "cleanup_tool",
            {"operation": "file"},
            "test_agent",
            {"context": "cleanup_test"}
        )
        self.assertFalse(os.path.exists("cleanup_test.txt"))
        
        # Test memory cleanup
        initial_memory = psutil.Process().memory_info().rss
        self.manager.execute_tool(
            "cleanup_tool",
            {"operation": "memory"},
            "test_agent",
            {"context": "cleanup_test"}
        )
        gc.collect()  # Force garbage collection
        final_memory = psutil.Process().memory_info().rss
        self.assertLess(final_memory - initial_memory, 1024 * 1024 * 10)  # Less than 10MB difference
        
        # Test thread cleanup
        initial_threads = threading.active_count()
        self.manager.execute_tool(
            "cleanup_tool",
            {"operation": "thread"},
            "test_agent",
            {"context": "cleanup_test"}
        )
        time.sleep(1.1)  # Wait for thread to complete
        final_threads = threading.active_count()
        self.assertEqual(final_threads, initial_threads)
        
if __name__ == '__main__':
    unittest.main() 