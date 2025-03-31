"""
Tests for advanced tool management capabilities including discovery, dependency management,
performance optimization, and security framework.
"""

import unittest
import time
import tempfile
import os
from typing import Dict, List, Any, Optional
from ..tool_management import (
    ToolDiscoveryManager,
    ToolDependencyManager,
    ToolPerformanceOptimizer,
    ToolSecurityFramework,
    ToolMetadata,
    ToolDependency,
    SecurityPolicy,
    PerformanceMetrics
)

class TestToolDiscoveryManager(unittest.TestCase):
    """Test cases for intelligent tool discovery capabilities."""
    
    def setUp(self):
        self.discovery_manager = ToolDiscoveryManager()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        # Clean up temporary files
        for file in os.listdir(self.temp_dir):
            try:
                os.remove(os.path.join(self.temp_dir, file))
            except:
                pass
        os.rmdir(self.temp_dir)
        
    def test_tool_discovery(self):
        """Test basic tool discovery functionality."""
        # Create some sample tool files
        self._create_sample_tools()
        
        # Discover tools
        tools = self.discovery_manager.discover_tools(self.temp_dir)
        
        # Verify discovery results
        self.assertEqual(len(tools), 3)
        self.assertTrue(all(isinstance(tool, ToolMetadata) for tool in tools))
        
        # Verify tool metadata
        for tool in tools:
            self.assertIn("name", tool.__dict__)
            self.assertIn("version", tool.__dict__)
            self.assertIn("description", tool.__dict__)
            
    def test_tool_categorization(self):
        """Test tool categorization based on functionality."""
        # Create categorized tools
        self._create_categorized_tools()
        
        # Discover and categorize tools
        categorized_tools = self.discovery_manager.discover_and_categorize_tools(self.temp_dir)
        
        # Verify categorization
        self.assertIn("code_analysis", categorized_tools)
        self.assertIn("testing", categorized_tools)
        self.assertIn("deployment", categorized_tools)
        
    def test_tool_validation(self):
        """Test tool validation during discovery."""
        # Create valid and invalid tools
        self._create_valid_and_invalid_tools()
        
        # Discover tools with validation
        valid_tools = self.discovery_manager.discover_valid_tools(self.temp_dir)
        
        # Verify validation results
        self.assertEqual(len(valid_tools), 2)
        self.assertTrue(all(tool.is_valid for tool in valid_tools))
        
    def _create_sample_tools(self):
        """Create sample tool files for testing."""
        tools = [
            ("code_analyzer.py", """
class CodeAnalyzer:
    def __init__(self):
        self.name = "code_analyzer"
        self.version = "1.0.0"
        self.description = "Analyzes code quality and complexity"
"""),
            ("test_runner.py", """
class TestRunner:
    def __init__(self):
        self.name = "test_runner"
        self.version = "1.0.0"
        self.description = "Runs test suites"
"""),
            ("deployer.py", """
class Deployer:
    def __init__(self):
        self.name = "deployer"
        self.version = "1.0.0"
        self.description = "Deploys applications"
""")
        ]
        
        for filename, content in tools:
            with open(os.path.join(self.temp_dir, filename), 'w') as f:
                f.write(content)
                
    def _create_categorized_tools(self):
        """Create categorized tool files for testing."""
        categories = {
            "code_analysis": ["analyzer.py", "metrics.py"],
            "testing": ["runner.py", "coverage.py"],
            "deployment": ["deploy.py", "config.py"]
        }
        
        for category, files in categories.items():
            for filename in files:
                with open(os.path.join(self.temp_dir, filename), 'w') as f:
                    f.write(f"""
class {filename.split('.')[0].title()}:
    def __init__(self):
        self.category = "{category}"
        self.name = "{filename.split('.')[0]}"
        self.version = "1.0.0"
""")
                    
    def _create_valid_and_invalid_tools(self):
        """Create valid and invalid tool files for testing."""
        tools = [
            ("valid_tool.py", """
class ValidTool:
    def __init__(self):
        self.name = "valid_tool"
        self.version = "1.0.0"
        self.description = "A valid tool"
        self.is_valid = True
"""),
            ("invalid_tool.py", """
class InvalidTool:
    def __init__(self):
        self.name = "invalid_tool"
        # Missing required fields
        self.is_valid = False
"""),
            ("malformed_tool.py", """
class MalformedTool:
    # Invalid syntax
    def __init__(self
        self.name = "malformed"
""")
        ]
        
        for filename, content in tools:
            with open(os.path.join(self.temp_dir, filename), 'w') as f:
                f.write(content)

class TestToolDependencyManager(unittest.TestCase):
    """Test cases for tool dependency management."""
    
    def setUp(self):
        self.dependency_manager = ToolDependencyManager()
        
    def test_dependency_resolution(self):
        """Test dependency resolution for tools."""
        # Create dependency graph
        dependencies = {
            "tool_a": ["tool_b", "tool_c"],
            "tool_b": ["tool_d"],
            "tool_c": ["tool_d"],
            "tool_d": []
        }
        
        # Resolve dependencies
        resolved = self.dependency_manager.resolve_dependencies(dependencies)
        
        # Verify resolution
        self.assertEqual(len(resolved), 4)
        self.assertIn("tool_d", resolved[0])  # tool_d should be first
        self.assertIn("tool_a", resolved[-1])  # tool_a should be last
        
    def test_dependency_conflict_detection(self):
        """Test detection of dependency conflicts."""
        # Create conflicting dependencies
        dependencies = {
            "tool_a": ["tool_b"],
            "tool_b": ["tool_a"]  # Circular dependency
        }
        
        # Check for conflicts
        conflicts = self.dependency_manager.detect_conflicts(dependencies)
        
        # Verify conflict detection
        self.assertTrue(conflicts["has_conflicts"])
        self.assertIn("circular_dependency", conflicts["conflict_types"])
        
    def test_version_compatibility(self):
        """Test version compatibility checking."""
        # Create version requirements
        requirements = {
            "tool_a": ">=1.0.0",
            "tool_b": ">=2.0.0,<3.0.0",
            "tool_c": "==1.5.0"
        }
        
        # Check compatibility
        compatibility = self.dependency_manager.check_version_compatibility(requirements)
        
        # Verify compatibility check
        self.assertIn("compatible", compatibility)
        self.assertIn("incompatible", compatibility)
        
    def test_dependency_installation(self):
        """Test dependency installation process."""
        # Create installation requirements
        requirements = [
            ToolDependency(name="tool_a", version="1.0.0"),
            ToolDependency(name="tool_b", version="2.0.0")
        ]
        
        # Install dependencies
        result = self.dependency_manager.install_dependencies(requirements)
        
        # Verify installation
        self.assertTrue(result["success"])
        self.assertEqual(len(result["installed"]), 2)
        self.assertEqual(len(result["failed"]), 0)

class TestToolPerformanceOptimizer(unittest.TestCase):
    """Test cases for tool performance optimization."""
    
    def setUp(self):
        self.optimizer = ToolPerformanceOptimizer()
        
    def test_performance_metrics_collection(self):
        """Test collection of performance metrics."""
        # Create sample tool execution
        def sample_tool():
            time.sleep(0.1)  # Simulate work
            return "result"
            
        # Collect metrics
        metrics = self.optimizer.collect_metrics(sample_tool)
        
        # Verify metrics
        self.assertIsInstance(metrics, PerformanceMetrics)
        self.assertGreater(metrics.execution_time, 0)
        self.assertGreater(metrics.memory_usage, 0)
        
    def test_performance_optimization(self):
        """Test performance optimization strategies."""
        # Create performance data
        performance_data = {
            "execution_times": [0.1, 0.2, 0.15, 0.3],
            "memory_usage": [100, 150, 120, 200],
            "cpu_usage": [50, 60, 55, 70]
        }
        
        # Optimize performance
        optimization_result = self.optimizer.optimize_performance(performance_data)
        
        # Verify optimization
        self.assertIn("optimization_strategies", optimization_result)
        self.assertIn("expected_improvement", optimization_result)
        
    def test_resource_usage_optimization(self):
        """Test optimization of resource usage."""
        # Create resource usage data
        resource_data = {
            "memory_usage": [100, 150, 200],
            "cpu_usage": [50, 60, 70],
            "disk_usage": [1000, 1500, 2000]
        }
        
        # Optimize resource usage
        optimization = self.optimizer.optimize_resource_usage(resource_data)
        
        # Verify optimization
        self.assertIn("memory_optimization", optimization)
        self.assertIn("cpu_optimization", optimization)
        self.assertIn("disk_optimization", optimization)
        
    def test_caching_strategy(self):
        """Test caching strategy optimization."""
        # Create caching data
        cache_data = {
            "hit_rate": 0.7,
            "miss_rate": 0.3,
            "cache_size": 1000
        }
        
        # Optimize caching
        cache_optimization = self.optimizer.optimize_caching(cache_data)
        
        # Verify optimization
        self.assertIn("optimal_cache_size", cache_optimization)
        self.assertIn("eviction_policy", cache_optimization)
        self.assertIn("expected_hit_rate", cache_optimization)

class TestToolSecurityFramework(unittest.TestCase):
    """Test cases for tool security framework."""
    
    def setUp(self):
        self.security_framework = ToolSecurityFramework()
        
    def test_security_policy_validation(self):
        """Test validation of security policies."""
        # Create security policy
        policy = SecurityPolicy(
            allowed_operations=["read", "write"],
            required_permissions=["admin"],
            max_execution_time=30,
            allowed_resources=["file_system", "network"]
        )
        
        # Validate policy
        validation_result = self.security_framework.validate_policy(policy)
        
        # Verify validation
        self.assertTrue(validation_result["is_valid"])
        self.assertEqual(len(validation_result["violations"]), 0)
        
    def test_security_audit(self):
        """Test security audit functionality."""
        # Create audit data
        audit_data = {
            "operations": ["read", "write", "execute"],
            "resources": ["file_system", "network", "database"],
            "users": ["admin", "user1", "user2"]
        }
        
        # Perform security audit
        audit_result = self.security_framework.perform_security_audit(audit_data)
        
        # Verify audit
        self.assertIn("security_score", audit_result)
        self.assertIn("vulnerabilities", audit_result)
        self.assertIn("recommendations", audit_result)
        
    def test_access_control(self):
        """Test access control mechanisms."""
        # Create access control data
        access_data = {
            "user": "admin",
            "operation": "write",
            "resource": "file_system"
        }
        
        # Check access
        access_result = self.security_framework.check_access(access_data)
        
        # Verify access control
        self.assertIn("allowed", access_result)
        self.assertIn("reason", access_result)
        self.assertIn("required_permissions", access_result)
        
    def test_security_monitoring(self):
        """Test security monitoring capabilities."""
        # Create monitoring data
        monitoring_data = {
            "events": [
                {"type": "access", "user": "admin", "resource": "file_system"},
                {"type": "operation", "user": "user1", "operation": "read"}
            ],
            "thresholds": {
                "max_failed_attempts": 3,
                "max_concurrent_sessions": 5
            }
        }
        
        # Monitor security
        monitoring_result = self.security_framework.monitor_security(monitoring_data)
        
        # Verify monitoring
        self.assertIn("security_status", monitoring_result)
        self.assertIn("alerts", monitoring_result)
        self.assertIn("metrics", monitoring_result)

if __name__ == '__main__':
    unittest.main() 