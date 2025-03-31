"""Stress tests for project context management."""

import unittest
import time
import tempfile
import os
import random
import string
import concurrent.futures
from pathlib import Path
from typing import Dict, Any, List, Set
import psutil
import gc
from ..project_context import ProjectContext, ProjectFile, SemanticContext
from ..enhanced_code_understanding import CodeEntity, LanguageConfig

class TestProjectContextStress(unittest.TestCase):
    """Stress tests for project context management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent / "test_data"
        self.temp_dir = tempfile.mkdtemp()
        self.context = ProjectContext(str(self.temp_dir))
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def test_massive_project_analysis(self):
        """Test analysis of a massive project with many files and dependencies."""
        # Create a large number of files with complex dependencies
        self._create_massive_project()
        
        # Measure initial memory
        initial_memory = self._get_memory_usage()
        
        # Perform analysis with memory tracking
        start_time = time.time()
        analysis = self.context.analyze_project()
        end_time = time.time()
        
        # Calculate metrics
        analysis_time = end_time - start_time
        final_memory = self._get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Verify performance
        self.assertLess(analysis_time, 30.0)  # Should complete within 30 seconds
        self.assertLess(memory_increase, 1000)  # Should use less than 1GB additional memory
        
        # Verify analysis results
        self._verify_massive_project_analysis(analysis)
        
    def _create_massive_project(self):
        """Create a massive project with complex structure."""
        # Create directories
        dirs = ['src', 'src/core', 'src/utils', 'src/models', 'tests']
        for dir_name in dirs:
            (self.temp_dir / dir_name).mkdir(parents=True, exist_ok=True)
            
        # Create files with complex dependencies
        for i in range(1000):
            # Randomly select directory
            dir_path = self.temp_dir / random.choice(dirs)
            
            # Create file with random name
            file_name = f"file_{i}_{self._random_string(8)}.py"
            file_path = dir_path / file_name
            
            # Generate complex code with dependencies
            code = self._generate_complex_code(i, dirs)
            file_path.write_text(code)
            
    def _generate_complex_code(self, file_id: int, dirs: List[str]) -> str:
        """Generate complex code with dependencies."""
        imports = []
        classes = []
        functions = []
        
        # Generate random imports
        num_imports = random.randint(1, 5)
        for _ in range(num_imports):
            import_dir = random.choice(dirs)
            import_file = f"file_{random.randint(0, file_id-1)}_{self._random_string(8)}"
            imports.append(f"from {import_dir}.{import_file} import *")
            
        # Generate random classes
        num_classes = random.randint(1, 3)
        for i in range(num_classes):
            class_name = f"Class_{file_id}_{i}"
            classes.append(f"""
class {class_name}:
    def __init__(self, data):
        self.data = data
        
    def process(self):
        return self.data
""")
            
        # Generate random functions
        num_functions = random.randint(2, 5)
        for i in range(num_functions):
            func_name = f"func_{file_id}_{i}"
            functions.append(f"""
def {func_name}(data):
    result = []
    for item in data:
        if isinstance(item, dict):
            result.append(item)
    return result
""")
            
        # Combine all parts
        return "\n".join(imports + classes + functions)
        
    def _random_string(self, length: int) -> str:
        """Generate random string."""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
        
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
        
    def _verify_massive_project_analysis(self, analysis: Dict[str, Any]):
        """Verify analysis results for massive project."""
        # Check file count
        self.assertGreater(len(analysis['files']), 1000)
        
        # Check dependency graph
        graph = analysis['dependencies']['graph']
        self.assertGreater(len(graph), 1000)
        
        # Check for cycles
        cycles = analysis['dependencies']['cycles']
        self.assertIsInstance(cycles, list)
        
        # Check semantic contexts
        contexts = analysis['semantic_contexts']['contexts']
        self.assertGreater(len(contexts), 3000)  # At least 3 entities per file
        
    def test_concurrent_analysis_stress(self):
        """Test concurrent analysis under stress."""
        # Create test files
        self._create_concurrent_test_files()
        
        # Test with different thread counts
        thread_counts = [2, 4, 8, 16]
        results = []
        
        for num_threads in thread_counts:
            start_time = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = []
                for file_path in self.context._get_project_files():
                    futures.append(executor.submit(self.context.analyzer.analyze_file, str(file_path)))
                concurrent.futures.wait(futures)
            end_time = time.time()
            
            results.append({
                'threads': num_threads,
                'time': end_time - start_time,
                'memory': self._get_memory_usage()
            })
            
        # Verify scaling
        self._verify_concurrent_scaling(results)
        
    def _create_concurrent_test_files(self):
        """Create files for concurrent testing."""
        # Create many small files
        for i in range(500):
            file = self.temp_dir / f"concurrent_{i}.py"
            file.write_text(f"""
def func_{i}():
    return {i}
""")
            
    def _verify_concurrent_scaling(self, results: List[Dict[str, Any]]):
        """Verify concurrent analysis scaling."""
        # Check that more threads generally means faster processing
        for i in range(1, len(results)):
            self.assertLess(results[i]['time'], results[i-1]['time'])
            
        # Check memory usage doesn't explode
        for result in results:
            self.assertLess(result['memory'], 1000)  # Less than 1GB
            
    def test_memory_management(self):
        """Test memory management under stress."""
        # Create files that will stress memory
        self._create_memory_stress_files()
        
        # Track memory usage
        initial_memory = self._get_memory_usage()
        memory_usage = []
        
        # Perform analysis in stages
        for i in range(10):
            # Force garbage collection
            gc.collect()
            
            # Record memory
            memory_usage.append(self._get_memory_usage())
            
            # Analyze a subset of files
            files = list(self.context._get_project_files())[i*100:(i+1)*100]
            for file_path in files:
                self.context.analyzer.analyze_file(str(file_path))
                
        # Verify memory management
        self._verify_memory_management(memory_usage, initial_memory)
        
    def _create_memory_stress_files(self):
        """Create files that stress memory."""
        # Create files with large data structures
        for i in range(1000):
            file = self.temp_dir / f"memory_{i}.py"
            
            # Generate large data structures
            large_dict = {f"key_{j}": self._generate_large_value() for j in range(100)}
            large_list = [self._generate_large_value() for _ in range(100)]
            
            file.write_text(f"""
LARGE_DICT = {large_dict}
LARGE_LIST = {large_list}

def process_data():
    result = []
    for item in LARGE_LIST:
        if isinstance(item, dict):
            result.append(item)
    return result
""")
            
    def _generate_large_value(self) -> Any:
        """Generate large value for testing."""
        if random.random() < 0.5:
            return {f"key_{i}": self._generate_large_value() for i in range(10)}
        else:
            return [self._generate_large_value() for _ in range(10)]
            
    def _verify_memory_management(self, memory_usage: List[float], initial_memory: float):
        """Verify memory management."""
        # Check memory growth
        max_memory = max(memory_usage)
        self.assertLess(max_memory - initial_memory, 500)  # Less than 500MB growth
        
        # Check memory stability
        for i in range(1, len(memory_usage)):
            growth = memory_usage[i] - memory_usage[i-1]
            self.assertLess(growth, 100)  # Less than 100MB growth per stage
            
    def test_error_recovery(self):
        """Test error recovery under stress."""
        # Create files with potential errors
        self._create_error_test_files()
        
        # Attempt analysis
        try:
            analysis = self.context.analyze_project()
        except Exception as e:
            self.fail(f"Analysis failed with error: {str(e)}")
            
        # Verify partial results
        self._verify_error_recovery(analysis)
        
    def _create_error_test_files(self):
        """Create files with potential errors."""
        # Create files with syntax errors
        for i in range(100):
            file = self.temp_dir / f"error_{i}.py"
            if random.random() < 0.1:  # 10% chance of syntax error
                file.write_text("def invalid_syntax(")
            else:
                file.write_text(f"""
def valid_func_{i}():
    return {i}
""")
                
        # Create files with circular imports
        for i in range(50):
            file1 = self.temp_dir / f"circular1_{i}.py"
            file2 = self.temp_dir / f"circular2_{i}.py"
            
            file1.write_text(f"from circular2_{i} import func2")
            file2.write_text(f"from circular1_{i} import func1")
            
    def _verify_error_recovery(self, analysis: Dict[str, Any]):
        """Verify error recovery results."""
        # Check that valid files were analyzed
        valid_files = [f for f in analysis['files'].keys() if 'error_' not in f]
        self.assertGreater(len(valid_files), 0)
        
        # Check that error files were handled gracefully
        error_files = [f for f in analysis['files'].keys() if 'error_' in f]
        self.assertGreater(len(error_files), 0)
        
        # Check dependency graph is still valid
        graph = analysis['dependencies']['graph']
        self.assertIsInstance(graph, dict)
        
    def test_long_running_analysis(self):
        """Test long-running analysis stability."""
        # Create files for long-running test
        self._create_long_running_files()
        
        # Run analysis for extended period
        start_time = time.time()
        analysis = self.context.analyze_project()
        end_time = time.time()
        
        # Verify long-running stability
        self._verify_long_running_stability(analysis, end_time - start_time)
        
    def _create_long_running_files(self):
        """Create files for long-running test."""
        # Create many files with complex dependencies
        for i in range(2000):
            file = self.temp_dir / f"long_{i}.py"
            
            # Generate complex code with many dependencies
            imports = [f"from long_{j} import func_{j}" for j in range(max(0, i-10), i)]
            code = "\n".join(imports + [f"def func_{i}(): return {i}"])
            
            file.write_text(code)
            
    def _verify_long_running_stability(self, analysis: Dict[str, Any], duration: float):
        """Verify long-running analysis stability."""
        # Check analysis completed successfully
        self.assertGreater(len(analysis['files']), 2000)
        
        # Check reasonable duration
        self.assertLess(duration, 60.0)  # Should complete within 60 seconds
        
        # Check memory stability
        final_memory = self._get_memory_usage()
        self.assertLess(final_memory, 2000)  # Less than 2GB memory usage
        
        # Check dependency graph integrity
        graph = analysis['dependencies']['graph']
        self.assertEqual(len(graph), len(analysis['files']))
        
        # Check semantic contexts
        contexts = analysis['semantic_contexts']['contexts']
        self.assertGreater(len(contexts), 2000)

if __name__ == '__main__':
    unittest.main() 