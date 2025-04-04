from typing import Dict, List, Optional, Any
import logging
import os
import time
import statistics
import json

logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    """Utility class for analyzing code performance"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.results_cache = {}
        
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file for performance concerns
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Dictionary with performance analysis results
        """
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return {"error": "File does not exist"}
            
        result = {
            "file": file_path,
            "issues": [],
            "complexity_score": 0,
            "estimated_performance": "unknown"
        }
        
        try:
            # Determine file type
            _, ext = os.path.splitext(file_path)
            file_type = ext.lstrip('.').lower()
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Analyze complexity and performance
            if file_type == 'py':
                self._analyze_python_file(content, result)
            elif file_type in ['js', 'ts', 'jsx', 'tsx']:
                self._analyze_js_file(content, result)
            else:
                result["estimated_performance"] = "unknown"
                
        except Exception as e:
            self.logger.error(f"Error analyzing file {file_path}: {str(e)}")
            result["error"] = str(e)
            
        return result
        
    def _analyze_python_file(self, content: str, result: Dict[str, Any]) -> None:
        """Analyze Python file for performance issues"""
        # Check for common performance issues
        issues = []
        
        # Check for nested loops
        nested_loops = content.count("for") > 0 and "for" in content.split("for", 1)[1]
        if nested_loops:
            issues.append({
                "type": "nested_loops",
                "severity": "MEDIUM",
                "description": "Nested loops detected, which may lead to quadratic time complexity",
                "recommendation": "Consider restructuring to avoid nested iterations or use vectorized operations if applicable"
            })
            
        # Check for large list comprehensions
        if "[" in content and "]" in content and "for" in content:
            list_comp = content.split("[", 1)[1].split("]", 1)[0]
            if list_comp.count("for") > 1:
                issues.append({
                    "type": "complex_comprehension",
                    "severity": "LOW",
                    "description": "Complex list comprehension detected",
                    "recommendation": "Consider breaking down complex comprehensions for better readability and maintainability"
                })
                
        # Check for inefficient string concatenation
        if "+=" in content and "str" in content:
            issues.append({
                "type": "string_concatenation",
                "severity": "LOW",
                "description": "Potential inefficient string concatenation",
                "recommendation": "Use join() for string concatenation in loops or consider string formatting"
            })
            
        # Calculate complexity score (simplified)
        complexity = 0
        complexity += content.count("for") * 2
        complexity += content.count("while") * 3
        complexity += content.count("if") + content.count("elif") + content.count("else")
        complexity += content.count("try") + content.count("except") * 2
        complexity += content.count("class") * 3
        complexity += content.count("def") * 1.5
        
        result["complexity_score"] = round(complexity, 2)
        result["issues"] = issues
        
        # Estimate performance
        if complexity > 50:
            result["estimated_performance"] = "poor"
        elif complexity > 25:
            result["estimated_performance"] = "moderate"
        else:
            result["estimated_performance"] = "good"
            
    def _analyze_js_file(self, content: str, result: Dict[str, Any]) -> None:
        """Analyze JavaScript/TypeScript file for performance issues"""
        # Check for common performance issues
        issues = []
        
        # Check for nested loops
        nested_loops = content.count("for") > 0 and "for" in content.split("for", 1)[1]
        if nested_loops:
            issues.append({
                "type": "nested_loops",
                "severity": "MEDIUM",
                "description": "Nested loops detected, which may lead to quadratic time complexity",
                "recommendation": "Consider restructuring or using higher-order functions like map/reduce"
            })
            
        # Check for inefficient DOM operations
        if ".querySelector" in content or ".getElementById" in content:
            dom_access_count = content.count(".querySelector") + content.count(".getElementById")
            if dom_access_count > 5:
                issues.append({
                    "type": "frequent_dom_access",
                    "severity": "MEDIUM",
                    "description": "Frequent DOM access detected",
                    "recommendation": "Cache DOM elements in variables instead of querying repeatedly"
                })
                
        # Check for memory leaks in event listeners
        if ".addEventListener" in content and ".removeEventListener" not in content:
            issues.append({
                "type": "event_listener_leak",
                "severity": "LOW",
                "description": "Event listeners added without corresponding removal",
                "recommendation": "Remove event listeners when components unmount to prevent memory leaks"
            })
            
        # Calculate complexity score (simplified)
        complexity = 0
        complexity += content.count("for") * 2
        complexity += content.count("while") * 3
        complexity += content.count("if") + content.count("else")
        complexity += content.count("try") + content.count("catch") * 2
        complexity += content.count("class") * 3
        complexity += content.count("function") * 1.5
        
        result["complexity_score"] = round(complexity, 2)
        result["issues"] = issues
        
        # Estimate performance
        if complexity > 50:
            result["estimated_performance"] = "poor"
        elif complexity > 25:
            result["estimated_performance"] = "moderate"
        else:
            result["estimated_performance"] = "good"
            
    def benchmark_function(self, func, args=None, kwargs=None, iterations=100) -> Dict[str, Any]:
        """Benchmark a function's performance
        
        Args:
            func: Function to benchmark
            args: Positional arguments to pass to the function
            kwargs: Keyword arguments to pass to the function
            iterations: Number of iterations to run
            
        Returns:
            Dictionary with benchmark results
        """
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
            
        result = {
            "function_name": func.__name__,
            "iterations": iterations,
            "avg_time_ms": 0,
            "min_time_ms": 0,
            "max_time_ms": 0,
            "median_time_ms": 0,
            "std_dev_ms": 0
        }
        
        try:
            # Run warm-up iteration
            func(*args, **kwargs)
            
            # Run benchmark
            times = []
            for _ in range(iterations):
                start_time = time.time()
                func(*args, **kwargs)
                end_time = time.time()
                elapsed_ms = (end_time - start_time) * 1000
                times.append(elapsed_ms)
                
            # Calculate statistics
            result["avg_time_ms"] = round(sum(times) / len(times), 3)
            result["min_time_ms"] = round(min(times), 3)
            result["max_time_ms"] = round(max(times), 3)
            result["median_time_ms"] = round(statistics.median(times), 3)
            result["std_dev_ms"] = round(statistics.stdev(times), 3) if len(times) > 1 else 0
            
        except Exception as e:
            self.logger.error(f"Error benchmarking function {func.__name__}: {str(e)}")
            result["error"] = str(e)
            
        return result
        
    def analyze_memory_usage(self, func, args=None, kwargs=None) -> Dict[str, Any]:
        """Analyze memory usage of a function (requires memory_profiler)
        
        Args:
            func: Function to analyze
            args: Positional arguments to pass to the function
            kwargs: Keyword arguments to pass to the function
            
        Returns:
            Dictionary with memory usage results
        """
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
            
        result = {
            "function_name": func.__name__,
            "memory_usage_mb": 0,
            "peak_memory_mb": 0
        }
        
        try:
            # Check if memory_profiler is available
            try:
                import memory_profiler
            except ImportError:
                return {"error": "memory_profiler module not available"}
                
            # Profile memory usage
            memory_usage = memory_profiler.memory_usage((func, args, kwargs), interval=0.1, timeout=None)
            
            # Calculate statistics
            if memory_usage:
                baseline = memory_usage[0]
                max_usage = max(memory_usage)
                result["memory_usage_mb"] = round(max_usage - baseline, 2)
                result["peak_memory_mb"] = round(max_usage, 2)
                
        except Exception as e:
            self.logger.error(f"Error analyzing memory usage for {func.__name__}: {str(e)}")
            result["error"] = str(e)
            
        return result
