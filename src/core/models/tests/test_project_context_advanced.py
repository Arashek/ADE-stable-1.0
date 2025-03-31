"""Advanced tests for project context management."""

import unittest
import time
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List
import concurrent.futures
from ..project_context import ProjectContext, ProjectFile, SemanticContext
from ..enhanced_code_understanding import CodeEntity, LanguageConfig

class TestProjectContextAdvanced(unittest.TestCase):
    """Advanced tests for project context management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent / "test_data"
        self.context = ProjectContext(str(self.test_dir))
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def test_edge_cases(self):
        """Test edge cases in project analysis."""
        # Test with circular dependencies
        self._create_circular_dependencies()
        
        # Test with deeply nested imports
        self._create_deep_imports()
        
        # Test with duplicate entity names
        self._create_duplicate_entities()
        
        # Test with mixed language files
        self._create_mixed_language_files()
        
        # Test with large files
        self._create_large_files()
        
    def _create_circular_dependencies(self):
        """Create and test circular dependencies."""
        # Create files with circular imports
        file1 = self.temp_dir / "circular1.py"
        file2 = self.temp_dir / "circular2.py"
        
        file1.write_text("""
from circular2 import func2

def func1():
    return func2()
""")
        
        file2.write_text("""
from circular1 import func1

def func2():
    return func1()
""")
        
        context = ProjectContext(str(self.temp_dir))
        analysis = context.analyze_project()
        
        # Check for cycles
        cycles = analysis['dependencies']['cycles']
        self.assertGreater(len(cycles), 0)
        
        # Verify cycle detection
        for cycle in cycles:
            self.assertGreater(len(cycle), 1)
            self.assertIn(str(file1), cycle)
            self.assertIn(str(file2), cycle)
            
    def _create_deep_imports(self):
        """Create and test deeply nested imports."""
        # Create a chain of imports
        files = []
        for i in range(10):
            file = self.temp_dir / f"deep{i}.py"
            if i > 0:
                file.write_text(f"from deep{i-1} import func{i-1}\n\ndef func{i}():\n    return func{i-1}()")
            else:
                file.write_text("def func0():\n    return 0")
            files.append(file)
            
        context = ProjectContext(str(self.temp_dir))
        analysis = context.analyze_project()
        
        # Check import chain
        for i in range(1, len(files)):
            deps = context.get_file_dependencies(str(files[i]))
            self.assertIn(str(files[i-1]), deps)
            
    def _create_duplicate_entities(self):
        """Create and test duplicate entity names."""
        # Create files with duplicate entity names
        file1 = self.temp_dir / "duplicate1.py"
        file2 = self.temp_dir / "duplicate2.py"
        
        file1.write_text("""
class User:
    def __init__(self, name):
        self.name = name
""")
        
        file2.write_text("""
class User:
    def __init__(self, id):
        self.id = id
""")
        
        context = ProjectContext(str(self.temp_dir))
        analysis = context.analyze_project()
        
        # Check for multiple definitions
        user_context = context.get_entity_context("User")
        self.assertGreater(len(user_context.definitions), 1)
        
    def _create_mixed_language_files(self):
        """Create and test mixed language files."""
        # Create Python and JavaScript files
        py_file = self.temp_dir / "mixed.py"
        js_file = self.temp_dir / "mixed.js"
        
        py_file.write_text("""
def python_func():
    return "Python"
""")
        
        js_file.write_text("""
function javascriptFunc() {
    return "JavaScript";
}
""")
        
        context = ProjectContext(str(self.temp_dir))
        analysis = context.analyze_project()
        
        # Check language detection
        self.assertEqual(analysis['files'][str(py_file)]['language'], 'Python')
        self.assertEqual(analysis['files'][str(js_file)]['language'], 'JavaScript')
        
    def _create_large_files(self):
        """Create and test large files."""
        # Create a large file with many entities
        large_file = self.temp_dir / "large.py"
        
        with open(large_file, 'w') as f:
            f.write("def func0():\n    return 0\n\n")
            for i in range(1000):
                f.write(f"def func{i+1}():\n    return func{i}()\n\n")
                
        context = ProjectContext(str(self.temp_dir))
        analysis = context.analyze_project()
        
        # Check entity count
        self.assertGreater(len(analysis['files'][str(large_file)]['entities']), 1000)
        
    def test_performance_benchmarks(self):
        """Test performance of project analysis."""
        # Create test files
        self._create_performance_test_files()
        
        # Measure analysis time
        start_time = time.time()
        context = ProjectContext(str(self.temp_dir))
        analysis = context.analyze_project()
        end_time = time.time()
        
        analysis_time = end_time - start_time
        self.assertLess(analysis_time, 5.0)  # Should complete within 5 seconds
        
        # Measure memory usage
        import psutil
        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        self.assertLess(memory_usage, 500)  # Should use less than 500MB
        
        # Measure concurrent analysis
        self._test_concurrent_analysis()
        
    def _create_performance_test_files(self):
        """Create files for performance testing."""
        # Create multiple files with dependencies
        for i in range(100):
            file = self.temp_dir / f"perf{i}.py"
            if i > 0:
                file.write_text(f"from perf{i-1} import func{i-1}\n\ndef func{i}():\n    return func{i-1}()")
            else:
                file.write_text("def func0():\n    return 0")
                
    def _test_concurrent_analysis(self):
        """Test concurrent file analysis."""
        context = ProjectContext(str(self.temp_dir))
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for file_path in context._get_project_files():
                futures.append(executor.submit(context.analyzer.analyze_file, str(file_path)))
            concurrent.futures.wait(futures)
        concurrent_time = time.time() - start_time
        
        # Compare with sequential analysis
        start_time = time.time()
        for file_path in context._get_project_files():
            context.analyzer.analyze_file(str(file_path))
        sequential_time = time.time() - start_time
        
        # Concurrent analysis should be faster
        self.assertLess(concurrent_time, sequential_time)
        
    def test_integration_with_enhanced_code_understanding(self):
        """Test integration with EnhancedCodeUnderstanding."""
        # Create test files with complex code structures
        self._create_integration_test_files()
        
        context = ProjectContext(str(self.temp_dir))
        analysis = context.analyze_project()
        
        # Test AST integration
        self._test_ast_integration(analysis)
        
        # Test semantic analysis integration
        self._test_semantic_integration(analysis)
        
        # Test control flow integration
        self._test_control_flow_integration(analysis)
        
        # Test data flow integration
        self._test_data_flow_integration(analysis)
        
    def _create_integration_test_files(self):
        """Create files for integration testing."""
        # Create a complex Python file
        complex_file = self.temp_dir / "complex.py"
        complex_file.write_text("""
from typing import List, Dict, Any
import json
from datetime import datetime

class ComplexClass:
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.timestamp = datetime.now()
        
    def process_data(self) -> List[Dict[str, Any]]:
        result = []
        for key, value in self.data.items():
            if isinstance(value, dict):
                result.append(self._process_dict(value))
            elif isinstance(value, list):
                result.extend(self._process_list(value))
        return result
        
    def _process_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v.upper() if isinstance(v, str) else v for k, v in d.items()}
        
    def _process_list(self, l: List[Any]) -> List[Dict[str, Any]]:
        return [self._process_dict(item) if isinstance(item, dict) else item for item in l]
        
    def save_to_file(self, filename: str) -> None:
        with open(filename, 'w') as f:
            json.dump(self.data, f)
            
    @classmethod
    def load_from_file(cls, filename: str) -> 'ComplexClass':
        with open(filename, 'r') as f:
            data = json.load(f)
        return cls(data)
""")
        
    def _test_ast_integration(self, analysis: Dict[str, Any]):
        """Test AST analysis integration."""
        complex_file = str(self.temp_dir / "complex.py")
        file_analysis = analysis['files'][complex_file]
        
        # Check AST structure
        self.assertIn('ast', file_analysis)
        ast = file_analysis['ast']
        
        # Verify class definition
        self.assertIn('classes', ast)
        self.assertEqual(len(ast['classes']), 1)
        self.assertEqual(ast['classes'][0]['name'], 'ComplexClass')
        
        # Verify method definitions
        self.assertIn('functions', ast)
        self.assertEqual(len(ast['functions']), 5)
        
    def _test_semantic_integration(self, analysis: Dict[str, Any]):
        """Test semantic analysis integration."""
        complex_file = str(self.temp_dir / "complex.py")
        file_analysis = analysis['files'][complex_file]
        
        # Check semantic information
        self.assertIn('semantics', file_analysis)
        semantics = file_analysis['semantics']
        
        # Verify type information
        self.assertIn('type_info', semantics)
        type_info = semantics['type_info']
        
        # Check class type
        self.assertIn('ComplexClass', type_info)
        self.assertEqual(type_info['ComplexClass']['type'], 'class')
        
        # Check method types
        self.assertIn('process_data', type_info)
        self.assertEqual(type_info['process_data']['return_type'], 'List[Dict[str, Any]]')
        
    def _test_control_flow_integration(self, analysis: Dict[str, Any]):
        """Test control flow analysis integration."""
        complex_file = str(self.temp_dir / "complex.py")
        file_analysis = analysis['files'][complex_file]
        
        # Check control flow information
        self.assertIn('control_flow', file_analysis)
        control_flow = file_analysis['control_flow']
        
        # Verify branches
        self.assertIn('branches', control_flow)
        self.assertGreater(len(control_flow['branches']), 0)
        
        # Verify loops
        self.assertIn('loops', control_flow)
        self.assertGreater(len(control_flow['loops']), 0)
        
    def _test_data_flow_integration(self, analysis: Dict[str, Any]):
        """Test data flow analysis integration."""
        complex_file = str(self.temp_dir / "complex.py")
        file_analysis = analysis['files'][complex_file]
        
        # Check data flow information
        self.assertIn('data_flow', file_analysis)
        data_flow = file_analysis['data_flow']
        
        # Verify variable definitions
        self.assertIn('definitions', data_flow)
        self.assertGreater(len(data_flow['definitions']), 0)
        
        # Verify variable uses
        self.assertIn('uses', data_flow)
        self.assertGreater(len(data_flow['uses']), 0)
        
        # Verify dependencies
        self.assertIn('dependencies', data_flow)
        self.assertGreater(len(data_flow['dependencies']), 0)

if __name__ == '__main__':
    unittest.main() 