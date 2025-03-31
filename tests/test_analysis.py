import unittest
from datetime import datetime
from typing import Dict, List, Any
import tempfile
import os

from src.core.analysis.pattern_detector import PatternDetector, PatternMatch
from src.core.analysis.root_cause_analyzer import RootCauseAnalyzer, RootCause
from src.core.analysis.error_classifier import ErrorClassifier
from src.core.analysis.code_structure_analyzer import CodeStructureAnalyzer

class TestAnalysis(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.pattern_detector = PatternDetector()
        self.root_cause_analyzer = RootCauseAnalyzer()
    
    def test_pattern_detection(self):
        """Test pattern detection functionality."""
        # Test error message
        error_message = "TypeError: 'NoneType' object is not subscriptable"
        stack_trace = [
            "File 'test.py', line 10, in process_data",
            "result = data['key']",
            "TypeError: 'NoneType' object is not subscriptable"
        ]
        context = {
            "file": "test.py",
            "function": "process_data",
            "line": 10
        }
        
        # Detect patterns
        patterns = self.pattern_detector.detect_patterns(
            error_message,
            stack_trace,
            context
        )
        
        # Verify pattern detection
        self.assertIsInstance(patterns, list)
        self.assertTrue(len(patterns) > 0)
        
        # Check for null pointer pattern
        null_patterns = [
            p for p in patterns
            if p.pattern_type == "null_pointer"
        ]
        self.assertTrue(len(null_patterns) > 0)
        
        # Verify pattern match structure
        pattern = null_patterns[0]
        self.assertIsInstance(pattern, PatternMatch)
        self.assertEqual(pattern.pattern_type, "null_pointer")
        self.assertTrue(len(pattern.description) > 0)
        self.assertTrue(0 <= pattern.confidence <= 1)
        self.assertEqual(pattern.context, context)
    
    def test_stack_trace_analysis(self):
        """Test stack trace pattern analysis."""
        stack_trace = [
            "File 'test.py', line 5, in recursive_function",
            "return recursive_function(n - 1)",
            "RecursionError: maximum recursion depth exceeded"
        ]
        
        # Detect patterns
        patterns = self.pattern_detector.detect_patterns(
            "RecursionError",
            stack_trace
        )
        
        # Verify recursion pattern
        recursion_patterns = [
            p for p in patterns
            if p.pattern_type == "recursion"
        ]
        self.assertTrue(len(recursion_patterns) > 0)
        
        # Verify pattern details
        pattern = recursion_patterns[0]
        self.assertEqual(pattern.pattern_type, "recursion")
        self.assertTrue("recursive" in pattern.description.lower())
        self.assertIsNotNone(pattern.location)
    
    def test_context_analysis(self):
        """Test context-based pattern analysis."""
        context = {
            "memory_usage": 0.95,
            "cpu_usage": 0.85,
            "thread_count": 150
        }
        
        # Detect patterns
        patterns = self.pattern_detector.detect_patterns(
            "System error",
            context=context
        )
        
        # Verify resource patterns
        resource_patterns = [
            p for p in patterns
            if p.pattern_type in ["high_memory", "high_cpu", "thread_explosion"]
        ]
        self.assertTrue(len(resource_patterns) > 0)
        
        # Verify pattern details
        for pattern in resource_patterns:
            self.assertTrue(0 <= pattern.confidence <= 1)
            self.assertEqual(pattern.context, context)
    
    def test_root_cause_analysis(self):
        """Test root cause analysis functionality."""
        # Test error data
        error_message = "ImportError: No module named 'missing_package'"
        stack_trace = [
            "File 'test.py', line 1, in <module>",
            "import missing_package",
            "ImportError: No module named 'missing_package'"
        ]
        patterns = [
            {
                "type": "import_error",
                "description": "Failed to import required package",
                "confidence": 0.9
            }
        ]
        context = {
            "python_version": "3.8.0",
            "environment": "development"
        }
        
        # Analyze root cause
        analysis = self.root_cause_analyzer.analyze_root_cause(
            error_message,
            stack_trace,
            patterns,
            context
        )
        
        # Verify analysis structure
        self.assertIsInstance(analysis, RootCause)
        self.assertEqual(analysis.cause, "dependency_issue")
        self.assertTrue(len(analysis.description) > 0)
        self.assertTrue(0 <= analysis.confidence <= 1)
        self.assertIsInstance(analysis.contributing_factors, list)
        self.assertIsInstance(analysis.evidence, list)
        self.assertIsInstance(analysis.suggested_fixes, list)
        self.assertIsInstance(analysis.timestamp, datetime)
    
    def test_root_cause_confidence(self):
        """Test root cause confidence calculation."""
        # Test with strong evidence
        error_message = "MemoryError: Out of memory"
        context = {
            "memory_usage": 0.98,
            "available_memory": "100MB"
        }
        
        analysis = self.root_cause_analyzer.analyze_root_cause(
            error_message,
            context=context
        )
        
        # Verify high confidence for resource exhaustion
        self.assertEqual(analysis.cause, "resource_exhaustion")
        self.assertTrue(analysis.confidence > 0.7)
        
        # Test with weak evidence
        weak_error = "Unknown error"
        weak_analysis = self.root_cause_analyzer.analyze_root_cause(weak_error)
        
        # Verify lower confidence for unknown cause
        self.assertEqual(weak_analysis.cause, "unknown")
        self.assertTrue(weak_analysis.confidence < 0.5)
    
    def test_root_cause_history(self):
        """Test root cause analysis history."""
        # Add multiple analyses
        errors = [
            ("ImportError: No module named 'package'", "dependency_issue"),
            ("MemoryError: Out of memory", "resource_exhaustion"),
            ("TimeoutError: Operation timed out", "network_issue")
        ]
        
        for error_message, expected_cause in errors:
            analysis = self.root_cause_analyzer.analyze_root_cause(error_message)
            self.assertEqual(analysis.cause, expected_cause)
        
        # Get statistics
        stats = self.root_cause_analyzer.get_cause_statistics()
        
        # Verify statistics
        self.assertIn("total_analyses", stats)
        self.assertIn("cause_distribution", stats)
        self.assertIn("average_confidence", stats)
        self.assertEqual(stats["total_analyses"], 3)
        
        # Get history
        history = self.root_cause_analyzer.get_cause_history()
        self.assertEqual(len(history), 3)
        
        # Get filtered history
        filtered_history = self.root_cause_analyzer.get_cause_history(
            cause_type="dependency_issue"
        )
        self.assertEqual(len(filtered_history), 1)
        self.assertEqual(filtered_history[0].cause, "dependency_issue")
    
    def test_custom_patterns(self):
        """Test custom pattern addition and detection."""
        # Add custom pattern
        self.pattern_detector.add_custom_pattern(
            pattern_type="custom_error",
            regex=r"CustomError:.*",
            description="Custom error pattern",
            severity="medium",
            category="custom"
        )
        
        # Test pattern detection
        error_message = "CustomError: Test error"
        patterns = self.pattern_detector.detect_patterns(error_message)
        
        # Verify custom pattern detection
        custom_patterns = [
            p for p in patterns
            if p.pattern_type == "custom_error"
        ]
        self.assertTrue(len(custom_patterns) > 0)
        
        # Verify pattern info
        pattern_info = self.pattern_detector.get_pattern_info("custom_error")
        self.assertIsNotNone(pattern_info)
        self.assertEqual(pattern_info["description"], "Custom error pattern")
        self.assertEqual(pattern_info["severity"], "medium")
        self.assertEqual(pattern_info["category"], "custom")

    def test_new_pattern_detection(self):
        """Test detection of newly added patterns."""
        # Test database error pattern
        db_error = "DatabaseError: Connection refused"
        db_patterns = self.pattern_detector.detect_patterns(db_error)
        self.assertTrue(any(p.pattern_type == "database_error" for p in db_patterns))
        
        # Test API error pattern
        api_error = "APIError: Rate limit exceeded"
        api_patterns = self.pattern_detector.detect_patterns(api_error)
        self.assertTrue(any(p.pattern_type == "api_error" for p in api_patterns))
        
        # Test validation error pattern
        validation_error = "ValidationError: Invalid input format"
        validation_patterns = self.pattern_detector.detect_patterns(validation_error)
        self.assertTrue(any(p.pattern_type == "validation_error" for p in validation_patterns))
        
        # Test authentication error pattern
        auth_error = "AuthenticationError: Invalid credentials"
        auth_patterns = self.pattern_detector.detect_patterns(auth_error)
        self.assertTrue(any(p.pattern_type == "authentication_error" for p in auth_patterns))
    
    def test_enhanced_confidence_calculation(self):
        """Test enhanced confidence calculation."""
        # Test with strong evidence and context
        error_message = "DatabaseError: Connection refused"
        context = {
            "db_connection": False,
            "query_time": 3.5,
            "db_errors": 2
        }
        
        analysis = self.root_cause_analyzer.analyze_root_cause(
            error_message,
            context=context
        )
        
        # Verify high confidence for database error
        self.assertEqual(analysis.cause, "database_error")
        self.assertTrue(analysis.confidence > 0.8)
        
        # Test with multiple patterns
        patterns = [
            {
                "type": "database_error",
                "description": "Database connection issue",
                "confidence": 0.9
            },
            {
                "type": "network_issue",
                "description": "Network connectivity problem",
                "confidence": 0.7
            }
        ]
        
        analysis = self.root_cause_analyzer.analyze_root_cause(
            error_message,
            patterns=patterns,
            context=context
        )
        
        # Verify confidence considers multiple patterns
        self.assertTrue(analysis.confidence > 0.7)
    
    def test_historical_confidence(self):
        """Test confidence calculation with historical data."""
        # Add historical analyses
        errors = [
            ("DatabaseError: Connection refused", "database_error"),
            ("DatabaseError: Query timeout", "database_error"),
            ("DatabaseError: Deadlock detected", "database_error")
        ]
        
        for error_message, expected_cause in errors:
            analysis = self.root_cause_analyzer.analyze_root_cause(error_message)
            self.assertEqual(analysis.cause, expected_cause)
        
        # Test new analysis with historical data
        new_error = "DatabaseError: New error"
        new_analysis = self.root_cause_analyzer.analyze_root_cause(new_error)
        
        # Verify confidence considers historical data
        self.assertTrue(new_analysis.confidence > 0.6)
    
    def test_context_based_confidence(self):
        """Test confidence calculation based on context."""
        # Test resource exhaustion
        resource_error = "MemoryError: Out of memory"
        resource_context = {
            "memory_usage": 0.95,
            "cpu_usage": 0.85,
            "disk_usage": 0.9
        }
        
        analysis = self.root_cause_analyzer.analyze_root_cause(
            resource_error,
            context=resource_context
        )
        
        # Verify high confidence for resource exhaustion
        self.assertEqual(analysis.cause, "resource_exhaustion")
        self.assertTrue(analysis.confidence > 0.8)
        
        # Test network issue
        network_error = "ConnectionError: Failed to connect"
        network_context = {
            "network_status": False,
            "response_time": 6.5,
            "connection_errors": 3
        }
        
        analysis = self.root_cause_analyzer.analyze_root_cause(
            network_error,
            context=network_context
        )
        
        # Verify high confidence for network issue
        self.assertEqual(analysis.cause, "network_issue")
        self.assertTrue(analysis.confidence > 0.8)
    
    def test_confidence_adjustments(self):
        """Test confidence score adjustments."""
        # Test with multiple evidence points
        error_message = "SecurityError: Unauthorized access"
        evidence = [
            "Error: Security violation detected",
            "Warning: Multiple failed login attempts",
            "Info: Access denied for user",
            "Debug: Security check failed",
            "Trace: Authentication failed"
        ]
        
        analysis = self.root_cause_analyzer.analyze_root_cause(
            error_message,
            context={"auth_status": False}
        )
        
        # Verify confidence adjustment for multiple evidence points
        self.assertTrue(analysis.confidence > 0.7)
        
        # Test with quantitative context
        context = {
            "memory_usage": 0.95,
            "cpu_usage": 0.85,
            "error_count": 5
        }
        
        analysis = self.root_cause_analyzer.analyze_root_cause(
            "SystemError: Resource limit reached",
            context=context
        )
        
        # Verify confidence adjustment for quantitative data
        self.assertTrue(analysis.confidence > 0.7)
    
    def test_pattern_categories(self):
        """Test pattern categorization and statistics."""
        # Get pattern statistics
        stats = self.pattern_detector.get_pattern_statistics()
        
        # Verify statistics structure
        self.assertIn("total_patterns", stats)
        self.assertIn("categories", stats)
        self.assertIn("severity_levels", stats)
        
        # Verify category counts
        categories = stats["categories"]
        self.assertTrue(len(categories) > 0)
        self.assertTrue(any(cat in categories for cat in [
            "runtime", "syntax", "import", "system",
            "database", "network", "data", "security",
            "performance", "messaging", "dependency",
            "testing"
        ]))
        
        # Verify severity levels
        severities = stats["severity_levels"]
        self.assertTrue(len(severities) > 0)
        self.assertTrue(any(sev in severities for sev in ["high", "medium", "low"]))

    def test_error_classification(self):
        """Test error classification functionality."""
        classifier = ErrorClassifier()
        
        # Test runtime error classification
        runtime_error = "TypeError: 'NoneType' object is not subscriptable"
        classification = classifier.classify_error(runtime_error)
        self.assertEqual(classification.category, "runtime")
        self.assertEqual(classification.subcategory, "type_error")
        self.assertEqual(classification.severity, "medium")
        self.assertEqual(classification.impact_level, "component_level")
        
        # Test system error classification
        system_error = "OSError: [Errno 2] No such file or directory"
        classification = classifier.classify_error(system_error)
        self.assertEqual(classification.category, "system")
        self.assertEqual(classification.subcategory, "os_error")
        self.assertEqual(classification.severity, "medium")
        
        # Test database error classification
        db_error = "DatabaseError: Connection refused"
        classification = classifier.classify_error(
            db_error,
            context={"affects_all_users": True, "data_loss": True}
        )
        self.assertEqual(classification.category, "database")
        self.assertEqual(classification.subcategory, "connection_error")
        self.assertEqual(classification.severity, "critical")
        self.assertEqual(classification.impact_level, "system_wide")
        
        # Test security error classification
        security_error = "SecurityError: Unauthorized access attempt"
        classification = classifier.classify_error(security_error)
        self.assertEqual(classification.category, "security")
        self.assertEqual(classification.severity, "high")
    
    def test_error_classification_with_context(self):
        """Test error classification with additional context."""
        classifier = ErrorClassifier()
        
        # Test with stack trace
        error = "ValueError: Invalid input"
        stack_trace = [
            "File 'test.py', line 10, in process_data",
            "File 'main.py', line 5, in main",
            "result = process_data(input_data)"
        ]
        classification = classifier.classify_error(error, stack_trace=stack_trace)
        self.assertTrue(classification.confidence > 0.5)
        
        # Test with user impact context
        context = {
            "user_count": 1000,
            "revenue_impact": True,
            "affects_all_users": True
        }
        classification = classifier.classify_error(error, context=context)
        self.assertEqual(classification.impact_level, "system_wide")
        self.assertEqual(classification.severity, "high")
    
    def test_code_structure_analysis(self):
        """Test code structure analysis functionality."""
        analyzer = CodeStructureAnalyzer()
        
        # Create a temporary test directory with Python files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_files = {
                "module1.py": """
                import os
                import sys
                
                def complex_function():
                    if True:
                        for i in range(10):
                            if i % 2 == 0:
                                print(i)
                            else:
                                print(i * 2)
                
                class TestClass:
                    def method1(self):
                        pass
                """,
                "module2.py": """
                from module1 import complex_function
                
                def unused_import():
                    return "test"
                """,
                "module3.py": """
                from module2 import unused_import
                from module1 import TestClass
                
                def circular_dep():
                    return unused_import()
                """
            }
            
            for filename, content in test_files.items():
                with open(os.path.join(temp_dir, filename), 'w') as f:
                    f.write(content)
            
            # Analyze the directory
            analysis = analyzer.analyze_directory(temp_dir)
            
            # Verify results
            self.assertEqual(analysis.metrics['total_modules'], 3)
            self.assertTrue(len(analysis.modules) > 0)
            
            # Check for complex functions
            self.assertTrue(any(
                "complex_function" in funcs
                for funcs in analysis.complex_functions.values()
            ))
            
            # Check for unused imports
            self.assertTrue(any(
                "unused_import" in imports
                for imports in analysis.unused_imports.values()
            ))
            
            # Check for circular dependencies
            self.assertTrue(len(analysis.circular_dependencies) > 0)
    
    def test_code_structure_metrics(self):
        """Test code structure metrics calculation."""
        analyzer = CodeStructureAnalyzer()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file with known metrics
            test_file = """
            import os
            
            def simple_function():
                return True
            
            class TestClass:
                def method1(self):
                    if True:
                        return 1
                    return 0
                
                def method2(self):
                    for i in range(5):
                        if i % 2 == 0:
                            print(i)
            """
            
            with open(os.path.join(temp_dir, "test.py"), 'w') as f:
                f.write(test_file)
            
            # Analyze the directory
            analysis = analyzer.analyze_directory(temp_dir)
            
            # Verify metrics
            self.assertEqual(analysis.metrics['total_modules'], 1)
            self.assertEqual(analysis.metrics['total_classes'], 1)
            self.assertEqual(analysis.metrics['total_functions'], 3)
            self.assertTrue(analysis.metrics['average_complexity'] > 0)
    
    def test_analysis_report(self):
        """Test analysis report generation."""
        analyzer = CodeStructureAnalyzer()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files with various issues
            test_files = {
                "module1.py": """
                import unused_module
                
                def complex_function():
                    if True:
                        for i in range(10):
                            if i % 2 == 0:
                                print(i)
                            else:
                                print(i * 2)
                """,
                "module2.py": """
                from module1 import complex_function
                
                def unused_import():
                    return "test"
                """
            }
            
            for filename, content in test_files.items():
                with open(os.path.join(temp_dir, filename), 'w') as f:
                    f.write(content)
            
            # Generate analysis
            analysis = analyzer.analyze_directory(temp_dir)
            
            # Generate report
            report = analyzer.get_analysis_report(analysis)
            
            # Verify report content
            self.assertIn("Code Structure Analysis Report", report)
            self.assertIn("Total Modules", report)
            self.assertIn("Circular Dependencies", report)
            self.assertIn("Unused Imports", report)
            self.assertIn("Complex Functions", report)

    def test_error_classification_edge_cases(self):
        """Test error classification with edge cases."""
        classifier = ErrorClassifier()
        
        # Test empty error message
        classification = classifier.classify_error("")
        self.assertEqual(classification.category, "unknown")
        self.assertEqual(classification.subcategory, "unknown")
        self.assertEqual(classification.severity, "low")
        self.assertEqual(classification.impact_level, "component_level")
        
        # Test very long error message
        long_error = "Error: " + "x" * 1000
        classification = classifier.classify_error(long_error)
        self.assertEqual(classification.category, "unknown")
        
        # Test error with special characters
        special_error = "Error: @#$%^&*()_+"
        classification = classifier.classify_error(special_error)
        self.assertEqual(classification.category, "unknown")
        
        # Test error with multiple patterns
        multi_pattern_error = "TypeError: 'NoneType' object is not subscriptable\nValueError: Invalid input"
        classification = classifier.classify_error(multi_pattern_error)
        self.assertEqual(classification.category, "runtime")
        self.assertTrue(len(classification.patterns) > 1)
        
        # Test error with malformed stack trace
        malformed_stack = ["Invalid stack trace format"]
        classification = classifier.classify_error("Error", stack_trace=malformed_stack)
        self.assertTrue(classification.confidence < 0.5)
        
        # Test error with invalid context
        invalid_context = {"invalid_key": object()}
        classification = classifier.classify_error("Error", context=invalid_context)
        self.assertEqual(classification.impact_level, "component_level")
    
    def test_code_structure_analysis_edge_cases(self):
        """Test code structure analysis with edge cases."""
        analyzer = CodeStructureAnalyzer()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test empty file
            with open(os.path.join(temp_dir, "empty.py"), 'w') as f:
                f.write("")
            analysis = analyzer.analyze_directory(temp_dir)
            self.assertEqual(analysis.metrics['total_lines_of_code'], 0)
            self.assertEqual(analysis.metrics['total_functions'], 0)
            self.assertEqual(analysis.metrics['total_classes'], 0)
            
            # Test file with only comments
            with open(os.path.join(temp_dir, "comments.py"), 'w') as f:
                f.write("# This is a comment\n# Another comment")
            analysis = analyzer.analyze_directory(temp_dir)
            self.assertEqual(analysis.metrics['total_lines_of_code'], 2)
            
            # Test file with invalid Python syntax
            with open(os.path.join(temp_dir, "invalid.py"), 'w') as f:
                f.write("def invalid_syntax(")
            analysis = analyzer.analyze_directory(temp_dir)
            self.assertEqual(analysis.metrics['total_functions'], 0)
            
            # Test file with very long lines
            with open(os.path.join(temp_dir, "long_lines.py"), 'w') as f:
                f.write("x = " + "1 + " * 1000 + "1")
            analysis = analyzer.analyze_directory(temp_dir)
            self.assertEqual(analysis.metrics['total_lines_of_code'], 1)
            
            # Test file with circular imports
            with open(os.path.join(temp_dir, "circular1.py"), 'w') as f:
                f.write("from circular2 import func")
            with open(os.path.join(temp_dir, "circular2.py"), 'w') as f:
                f.write("from circular1 import func")
            analysis = analyzer.analyze_directory(temp_dir)
            self.assertTrue(len(analysis.circular_dependencies) > 0)
            
            # Test file with deeply nested structures
            with open(os.path.join(temp_dir, "nested.py"), 'w') as f:
                f.write("""
                def outer():
                    def inner1():
                        def inner2():
                            def inner3():
                                def inner4():
                                    def inner5():
                                        return True
                                    return inner5()
                                return inner4()
                            return inner3()
                        return inner2()
                    return inner1()
                """)
            analysis = analyzer.analyze_directory(temp_dir)
            self.assertTrue(analysis.metrics['complexity_distribution']['high'] > 0)
            
            # Test file with mixed encoding
            with open(os.path.join(temp_dir, "mixed_encoding.py"), 'w', encoding='utf-8') as f:
                f.write("def func(): return 'Hello, 世界!'")
            analysis = analyzer.analyze_directory(temp_dir)
            self.assertEqual(analysis.metrics['total_functions'], 1)
            
            # Test file with very large docstring
            with open(os.path.join(temp_dir, "large_doc.py"), 'w') as f:
                f.write('"""' + "x" * 1000 + '"""\ndef func(): pass')
            analysis = analyzer.analyze_directory(temp_dir)
            self.assertTrue(analysis.metrics['code_quality']['docstring_coverage'] > 0)
            
            # Test file with many imports
            with open(os.path.join(temp_dir, "many_imports.py"), 'w') as f:
                f.write("\n".join(f"import module{i}" for i in range(100)))
            analysis = analyzer.analyze_directory(temp_dir)
            self.assertTrue(analysis.metrics['dependency_metrics']['average_dependencies'] > 0)
            
            # Test file with complex inheritance
            with open(os.path.join(temp_dir, "inheritance.py"), 'w') as f:
                f.write("""
                class A: pass
                class B(A): pass
                class C(B): pass
                class D(C): pass
                class E(D): pass
                """)
            analysis = analyzer.analyze_directory(temp_dir)
            self.assertEqual(analysis.metrics['total_classes'], 5)
            
            # Test file with decorators
            with open(os.path.join(temp_dir, "decorators.py"), 'w') as f:
                f.write("""
                def decorator(func):
                    def wrapper(*args, **kwargs):
                        return func(*args, **kwargs)
                    return wrapper
                
                @decorator
                def decorated():
                    pass
                """)
            analysis = analyzer.analyze_directory(temp_dir)
            self.assertEqual(analysis.metrics['total_functions'], 2)

if __name__ == '__main__':
    unittest.main() 