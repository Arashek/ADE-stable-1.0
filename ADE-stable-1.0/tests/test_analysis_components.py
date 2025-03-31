import unittest
from datetime import datetime
import tempfile
import os
from pathlib import Path

from src.core.analysis.context_analyzer import ContextAnalyzer, ContextInfo
from src.core.analysis.pattern_matcher import PatternMatcher, MatchResult
from src.core.analysis.llm_reasoning import LLMReasoning, ReasoningResult
from src.core.analysis.error_knowledge_base import ErrorPattern, ErrorSolution

class TestContextAnalyzer(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.analyzer = ContextAnalyzer()
    
    def test_analyze_error_message(self):
        """Test error message analysis."""
        # Test runtime error
        runtime_error = "TypeError: 'NoneType' object is not subscriptable"
        context = self.analyzer.analyze_error_message(runtime_error)
        self.assertEqual(context["category"], "runtime")
        self.assertEqual(context["error_type"], "TypeError")
        self.assertEqual(context["severity"], "medium")
        self.assertEqual(context["subcategory"], "type_error")
        
        # Test database error
        db_error = "DatabaseError: Connection refused"
        context = self.analyzer.analyze_error_message(db_error)
        self.assertEqual(context["category"], "database")
        self.assertEqual(context["error_type"], "DatabaseError")
        self.assertEqual(context["severity"], "high")
    
    def test_analyze_stack_trace(self):
        """Test stack trace analysis."""
        stack_trace = [
            'File "test.py", line 10, in process_data',
            '    result = data["key"]',
            'TypeError: \'NoneType\' object is not subscriptable',
            'File "main.py", line 5, in main',
            '    process_data(input_data)'
        ]
        context = self.analyzer.analyze_stack_trace(stack_trace)
        self.assertEqual(len(context["file_paths"]), 2)
        self.assertEqual(len(context["line_numbers"]), 2)
        self.assertEqual(len(context["function_names"]), 2)
        self.assertIn("process_data", context["function_names"])
        self.assertIn("main", context["function_names"])
    
    def test_analyze_code_context(self):
        """Test code context analysis."""
        code_snippet = """
def process_data(data):
    result = data["key"]
    return result

def main():
    input_data = None
    process_data(input_data)
"""
        context = self.analyzer.analyze_code_context(code_snippet, 3)
        self.assertEqual(context["line_number"], 3)
        self.assertEqual(len(context["surrounding_lines"]), 7)
        self.assertIn("result", context["variables"])
        self.assertIn("process_data", context["function_calls"])
    
    def test_analyze_environment(self):
        """Test environment analysis."""
        env_info = {
            "python_version": "3.8.0",
            "os_info": "Linux",
            "dependencies": {"numpy": "1.19.0"},
            "environment_vars": {"DEBUG": "true"},
            "resource_usage": {
                "memory_usage": 0.85,
                "cpu_usage": 0.95
            }
        }
        context = self.analyzer.analyze_environment(env_info)
        self.assertEqual(context["python_version"], "3.8.0")
        self.assertEqual(context["os_info"], "Linux")
        self.assertIn("high_memory_usage", context["resource_issues"])
        self.assertIn("high_cpu_usage", context["resource_issues"])
    
    def test_comprehensive_analysis(self):
        """Test comprehensive context analysis."""
        error_message = "TypeError: 'NoneType' object is not subscriptable"
        stack_trace = [
            'File "test.py", line 10, in process_data',
            '    result = data["key"]',
            'TypeError: \'NoneType\' object is not subscriptable'
        ]
        code_context = {
            "code_snippet": "result = data['key']",
            "line_number": 10
        }
        env_info = {
            "python_version": "3.8.0",
            "os_info": "Linux"
        }
        
        context_info = self.analyzer.analyze(
            error_message,
            stack_trace,
            code_context,
            env_info
        )
        
        self.assertEqual(context_info.error_type, "TypeError")
        self.assertEqual(context_info.category, "runtime")
        self.assertEqual(context_info.severity, "medium")
        self.assertEqual(context_info.subcategory, "type_error")
        self.assertIsNotNone(context_info.timestamp)

class TestPatternMatcher(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.matcher = PatternMatcher()
        
        # Add test patterns
        self.matcher.add_pattern("test_001", ErrorPattern(
            pattern_type="null_pointer",
            regex=r"TypeError: 'NoneType' object is not subscriptable",
            description="Attempting to access a method or attribute of a None object",
            severity="medium",
            category="runtime",
            subcategory="type_error",
            common_causes=["Uninitialized variable"],
            solutions=["sol_001"],
            examples=["data['key']"]
        ))
    
    def test_add_pattern(self):
        """Test pattern addition."""
        pattern = ErrorPattern(
            pattern_type="test_pattern",
            regex="test.*error",
            description="Test error pattern",
            severity="medium",
            category="runtime",
            subcategory="general",
            common_causes=["test cause"],
            solutions=["sol_001"],
            examples=["test error example"]
        )
        self.matcher.add_pattern("test_002", pattern)
        self.assertIn("test_002", self.matcher.patterns)
        self.assertIn("test_002", self.matcher.compiled_patterns)
    
    def test_remove_pattern(self):
        """Test pattern removal."""
        self.matcher.remove_pattern("test_001")
        self.assertNotIn("test_001", self.matcher.patterns)
        self.assertNotIn("test_001", self.matcher.compiled_patterns)
    
    def test_match(self):
        """Test pattern matching."""
        error_message = "TypeError: 'NoneType' object is not subscriptable"
        context = ContextInfo(
            error_type="TypeError",
            error_message=error_message,
            category="runtime",
            severity="medium",
            subcategory="type_error",
            timestamp=datetime.now()
        )
        
        matches = self.matcher.match(error_message, context)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].pattern_id, "test_001")
        self.assertEqual(matches[0].match_score, 1.0)
    
    def test_find_similar_patterns(self):
        """Test finding similar patterns."""
        # Add another similar pattern
        self.matcher.add_pattern("test_002", ErrorPattern(
            pattern_type="null_pointer_2",
            regex=r"TypeError: 'NoneType' object has no attribute",
            description="Attempting to access a method or attribute of a None object",
            severity="medium",
            category="runtime",
            subcategory="type_error",
            common_causes=["Uninitialized variable"],
            solutions=["sol_002"],
            examples=["obj.method()"]
        ))
        
        similar_patterns = self.matcher.find_similar_patterns("test_001")
        self.assertEqual(len(similar_patterns), 1)
        self.assertEqual(similar_patterns[0][0], "test_002")
        self.assertGreater(similar_patterns[0][1], 0.7)

class TestLLMReasoning(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.reasoning = LLMReasoning(model_name="test-model", temperature=0.7)
    
    def test_analyze_error(self):
        """Test error analysis."""
        context = ContextInfo(
            error_type="TypeError",
            error_message="TypeError: 'NoneType' object is not subscriptable",
            category="runtime",
            severity="medium",
            subcategory="type_error",
            timestamp=datetime.now()
        )
        matches = [
            MatchResult(
                pattern_id="test_001",
                pattern=ErrorPattern(
                    pattern_type="null_pointer",
                    regex="test.*error",
                    description="Test error pattern",
                    severity="medium",
                    category="runtime",
                    subcategory="type_error",
                    common_causes=["test cause"],
                    solutions=["sol_001"],
                    examples=["test error example"]
                ),
                match_score=1.0,
                matched_groups={},
                context_similarity=1.0,
                timestamp=datetime.now()
            )
        ]
        
        result = self.reasoning.analyze_error(context, matches)
        self.assertIsInstance(result, ReasoningResult)
        self.assertEqual(result.error_type, "TypeError")
        self.assertGreater(result.confidence_score, 0.0)
        self.assertEqual(len(result.related_patterns), 1)
    
    def test_generate_solution(self):
        """Test solution generation."""
        pattern = ErrorPattern(
            pattern_type="null_pointer",
            regex="test.*error",
            description="Test error pattern",
            severity="medium",
            category="runtime",
            subcategory="type_error",
            common_causes=["test cause"],
            solutions=["sol_001"],
            examples=["test error example"]
        )
        context = ContextInfo(
            error_type="TypeError",
            error_message="TypeError: 'NoneType' object is not subscriptable",
            category="runtime",
            severity="medium",
            subcategory="type_error",
            timestamp=datetime.now()
        )
        
        result = self.reasoning.generate_solution(pattern, context)
        self.assertIsNotNone(result["solution"])
        self.assertGreater(result["confidence_score"], 0.0)
        self.assertEqual(len(result["reasoning_chain"]), 3)
    
    def test_format_contexts(self):
        """Test context formatting."""
        # Test code context formatting
        code_context = {
            "surrounding_lines": ["def test():", "    result = data['key']"],
            "variables": ["result", "data"],
            "function_calls": ["test"]
        }
        formatted = self.reasoning._format_code_context(code_context)
        self.assertIn("Surrounding Code:", formatted)
        self.assertIn("Variables:", formatted)
        self.assertIn("Function Calls:", formatted)
        
        # Test stack trace formatting
        stack_trace = ["File 'test.py', line 1", "    result = data['key']"]
        formatted = self.reasoning._format_stack_trace(stack_trace)
        self.assertEqual(formatted, "\n".join(stack_trace))
        
        # Test environment info formatting
        env_info = {
            "python_version": "3.8.0",
            "dependencies": {"numpy": "1.19.0"}
        }
        formatted = self.reasoning._format_environment_info(env_info)
        self.assertIn("python_version: 3.8.0", formatted)
        self.assertIn("dependencies:", formatted)
        self.assertIn("numpy: 1.19.0", formatted)
    
    def test_statistics(self):
        """Test statistics collection."""
        # Add some test data
        context = ContextInfo(
            error_type="TypeError",
            error_message="Test error",
            timestamp=datetime.now()
        )
        matches = []
        self.reasoning.analyze_error(context, matches)
        
        stats = self.reasoning.get_statistics()
        self.assertEqual(stats["total_analyses"], 1)
        self.assertEqual(stats["model_name"], "test-model")
        self.assertEqual(stats["temperature"], 0.7)

if __name__ == '__main__':
    unittest.main() 