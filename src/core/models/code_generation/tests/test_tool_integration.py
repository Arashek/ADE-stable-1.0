"""
Tests for advanced tool integration capabilities combining discovery, dependency management,
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
from ..tool_integration import (
    ToolIntegrationManager,
    IntegrationConfig,
    IntegrationMetrics,
    IntegrationSecurity
)

class TestToolIntegrationManager(unittest.TestCase):
    """Test cases for tool integration capabilities."""
    
    def setUp(self):
        self.integration_manager = ToolIntegrationManager()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        # Clean up temporary files
        for file in os.listdir(self.temp_dir):
            try:
                os.remove(os.path.join(self.temp_dir, file))
            except:
                pass
        os.rmdir(self.temp_dir)
        
    def test_tool_integration_workflow(self):
        """Test complete tool integration workflow."""
        # Create integration configuration
        config = IntegrationConfig(
            discovery_path=self.temp_dir,
            security_policy=SecurityPolicy(
                allowed_operations=["read", "write", "execute"],
                required_permissions=["admin"],
                max_execution_time=60,
                allowed_resources=["file_system", "network", "database"]
            ),
            performance_thresholds={
                "max_execution_time": 5.0,
                "max_memory_usage": 1000,
                "max_cpu_usage": 80
            }
        )
        
        # Run integration workflow
        result = self.integration_manager.integrate_tools(config)
        
        # Verify integration results
        self.assertTrue(result["success"])
        self.assertIn("discovered_tools", result)
        self.assertIn("dependency_graph", result)
        self.assertIn("performance_metrics", result)
        self.assertIn("security_status", result)
        
    def test_tool_discovery_and_dependency_integration(self):
        """Test integration of tool discovery and dependency management."""
        # Create sample tools with dependencies
        self._create_tools_with_dependencies()
        
        # Run discovery and dependency analysis
        result = self.integration_manager.discover_and_analyze_dependencies(self.temp_dir)
        
        # Verify results
        self.assertIn("tools", result)
        self.assertIn("dependencies", result)
        self.assertIn("conflicts", result)
        
        # Verify dependency resolution
        resolved = result["dependencies"]["resolved"]
        self.assertEqual(len(resolved), 4)  # All tools should be resolved
        self.assertIn("tool_d", resolved[0])  # Base dependency should be first
        
    def test_performance_and_security_integration(self):
        """Test integration of performance optimization and security framework."""
        # Create performance and security configuration
        config = {
            "performance": {
                "metrics": ["execution_time", "memory_usage", "cpu_usage"],
                "thresholds": {
                    "execution_time": 5.0,
                    "memory_usage": 1000,
                    "cpu_usage": 80
                }
            },
            "security": {
                "policy": SecurityPolicy(
                    allowed_operations=["read", "write"],
                    required_permissions=["admin"],
                    max_execution_time=30,
                    allowed_resources=["file_system"]
                ),
                "monitoring": {
                    "enabled": True,
                    "alert_thresholds": {
                        "failed_attempts": 3,
                        "concurrent_sessions": 5
                    }
                }
            }
        }
        
        # Run integrated analysis
        result = self.integration_manager.analyze_performance_and_security(config)
        
        # Verify results
        self.assertIn("performance_metrics", result)
        self.assertIn("security_status", result)
        self.assertIn("optimization_suggestions", result)
        self.assertIn("security_recommendations", result)
        
    def test_tool_chain_optimization(self):
        """Test optimization of tool chains and workflows."""
        # Create tool chain configuration
        chain_config = {
            "tools": [
                {"name": "code_analyzer", "version": "1.0.0"},
                {"name": "test_runner", "version": "1.0.0"},
                {"name": "deployer", "version": "1.0.0"}
            ],
            "workflow": [
                {"tool": "code_analyzer", "input": "source_code", "output": "analysis"},
                {"tool": "test_runner", "input": "analysis", "output": "test_results"},
                {"tool": "deployer", "input": "test_results", "output": "deployment"}
            ]
        }
        
        # Optimize tool chain
        result = self.integration_manager.optimize_tool_chain(chain_config)
        
        # Verify optimization results
        self.assertIn("optimized_workflow", result)
        self.assertIn("performance_improvements", result)
        self.assertIn("resource_optimization", result)
        
    def test_integration_metrics_and_monitoring(self):
        """Test metrics collection and monitoring for integrated tools."""
        # Create monitoring configuration
        monitoring_config = {
            "metrics": {
                "performance": ["execution_time", "memory_usage", "cpu_usage"],
                "security": ["access_attempts", "policy_violations", "resource_usage"],
                "integration": ["tool_communication", "workflow_efficiency"]
            },
            "monitoring": {
                "interval": 1.0,
                "alert_thresholds": {
                    "performance": {
                        "execution_time": 5.0,
                        "memory_usage": 1000
                    },
                    "security": {
                        "failed_attempts": 3,
                        "policy_violations": 1
                    }
                }
            }
        }
        
        # Start monitoring
        monitoring_result = self.integration_manager.start_monitoring(monitoring_config)
        
        # Verify monitoring setup
        self.assertTrue(monitoring_result["monitoring_active"])
        self.assertIn("metrics_collector", monitoring_result)
        self.assertIn("alert_manager", monitoring_result)
        
        # Simulate some tool activity
        time.sleep(2.0)  # Wait for some metrics to be collected
        
        # Get current metrics
        current_metrics = self.integration_manager.get_current_metrics()
        
        # Verify metrics
        self.assertIn("performance_metrics", current_metrics)
        self.assertIn("security_metrics", current_metrics)
        self.assertIn("integration_metrics", current_metrics)
        
    def _create_tools_with_dependencies(self):
        """Create sample tools with dependencies for testing."""
        tools = [
            ("tool_a.py", """
from tool_b import ToolB
from tool_c import ToolC

class ToolA:
    def __init__(self):
        self.name = "tool_a"
        self.version = "1.0.0"
        self.dependencies = ["tool_b", "tool_c"]
"""),
            ("tool_b.py", """
from tool_d import ToolD

class ToolB:
    def __init__(self):
        self.name = "tool_b"
        self.version = "1.0.0"
        self.dependencies = ["tool_d"]
"""),
            ("tool_c.py", """
from tool_d import ToolD

class ToolC:
    def __init__(self):
        self.name = "tool_c"
        self.version = "1.0.0"
        self.dependencies = ["tool_d"]
"""),
            ("tool_d.py", """
class ToolD:
    def __init__(self):
        self.name = "tool_d"
        self.version = "1.0.0"
        self.dependencies = []
""")
        ]
        
        for filename, content in tools:
            with open(os.path.join(self.temp_dir, filename), 'w') as f:
                f.write(content)

class TestIntegrationSecurity(unittest.TestCase):
    """Test cases for integrated security framework."""
    
    def setUp(self):
        self.security = IntegrationSecurity()
        
    def test_integrated_security_policy(self):
        """Test integrated security policy management."""
        # Create integrated security policy
        policy = {
            "access_control": {
                "allowed_operations": ["read", "write", "execute"],
                "required_permissions": ["admin", "developer"],
                "resource_limits": {
                    "file_system": ["read", "write"],
                    "network": ["read"],
                    "database": ["read", "write"]
                }
            },
            "performance_limits": {
                "max_execution_time": 60,
                "max_memory_usage": 1000,
                "max_cpu_usage": 80
            },
            "monitoring": {
                "enabled": True,
                "alert_thresholds": {
                    "failed_attempts": 3,
                    "policy_violations": 1
                }
            }
        }
        
        # Apply security policy
        result = self.security.apply_policy(policy)
        
        # Verify policy application
        self.assertTrue(result["success"])
        self.assertIn("active_policies", result)
        self.assertIn("monitoring_status", result)
        
    def test_security_monitoring_integration(self):
        """Test integration of security monitoring with tool execution."""
        # Create monitoring configuration
        config = {
            "monitoring": {
                "enabled": True,
                "metrics": [
                    "access_attempts",
                    "policy_violations",
                    "resource_usage",
                    "execution_time"
                ],
                "alert_thresholds": {
                    "failed_attempts": 3,
                    "policy_violations": 1,
                    "resource_usage": 80
                }
            }
        }
        
        # Start security monitoring
        monitoring = self.security.start_monitoring(config)
        
        # Simulate some security events
        events = [
            {"type": "access", "user": "admin", "resource": "file_system", "success": True},
            {"type": "access", "user": "user1", "resource": "database", "success": False},
            {"type": "policy_violation", "user": "admin", "violation": "resource_limit"}
        ]
        
        for event in events:
            self.security.record_event(event)
            
        # Get security status
        status = self.security.get_security_status()
        
        # Verify security status
        self.assertIn("security_score", status)
        self.assertIn("active_violations", status)
        self.assertIn("recommendations", status)
        
    def test_security_audit_integration(self):
        """Test integration of security auditing with tool execution."""
        # Create audit configuration
        config = {
            "audit": {
                "enabled": True,
                "metrics": [
                    "access_patterns",
                    "resource_usage",
                    "policy_compliance",
                    "security_incidents"
                ],
                "reporting": {
                    "format": "detailed",
                    "include_recommendations": True
                }
            }
        }
        
        # Run security audit
        audit_result = self.security.run_audit(config)
        
        # Verify audit results
        self.assertIn("security_score", audit_result)
        self.assertIn("vulnerabilities", audit_result)
        self.assertIn("recommendations", audit_result)
        self.assertIn("compliance_status", audit_result)

class TestIntegrationMetrics(unittest.TestCase):
    """Test cases for integrated metrics collection and analysis."""
    
    def setUp(self):
        self.metrics = IntegrationMetrics()
        
    def test_integrated_metrics_collection(self):
        """Test collection of integrated metrics across tools."""
        # Create metrics configuration
        config = {
            "metrics": {
                "performance": {
                    "execution_time": True,
                    "memory_usage": True,
                    "cpu_usage": True
                },
                "security": {
                    "access_attempts": True,
                    "policy_violations": True,
                    "resource_usage": True
                },
                "integration": {
                    "tool_communication": True,
                    "workflow_efficiency": True,
                    "dependency_health": True
                }
            },
            "collection": {
                "interval": 1.0,
                "aggregation": "average",
                "retention": "1h"
            }
        }
        
        # Start metrics collection
        collection = self.metrics.start_collection(config)
        
        # Simulate some tool activity
        time.sleep(2.0)  # Wait for some metrics to be collected
        
        # Get collected metrics
        metrics = self.metrics.get_metrics()
        
        # Verify metrics collection
        self.assertIn("performance_metrics", metrics)
        self.assertIn("security_metrics", metrics)
        self.assertIn("integration_metrics", metrics)
        
    def test_metrics_analysis_and_optimization(self):
        """Test analysis and optimization based on collected metrics."""
        # Create analysis configuration
        config = {
            "analysis": {
                "metrics": [
                    "execution_time",
                    "memory_usage",
                    "cpu_usage",
                    "workflow_efficiency"
                ],
                "thresholds": {
                    "execution_time": 5.0,
                    "memory_usage": 1000,
                    "cpu_usage": 80,
                    "workflow_efficiency": 0.8
                }
            },
            "optimization": {
                "enabled": True,
                "strategies": [
                    "resource_optimization",
                    "workflow_optimization",
                    "caching_optimization"
                ]
            }
        }
        
        # Run metrics analysis
        analysis_result = self.metrics.analyze_and_optimize(config)
        
        # Verify analysis results
        self.assertIn("performance_analysis", analysis_result)
        self.assertIn("optimization_suggestions", analysis_result)
        self.assertIn("expected_improvements", analysis_result)
        
    def test_metrics_visualization(self):
        """Test visualization of collected metrics."""
        # Create visualization configuration
        config = {
            "visualization": {
                "metrics": [
                    "execution_time",
                    "memory_usage",
                    "cpu_usage",
                    "workflow_efficiency"
                ],
                "time_range": "1h",
                "chart_types": [
                    "line",
                    "bar",
                    "heatmap"
                ]
            }
        }
        
        # Generate visualizations
        visualizations = self.metrics.generate_visualizations(config)
        
        # Verify visualizations
        self.assertIn("performance_charts", visualizations)
        self.assertIn("resource_usage_charts", visualizations)
        self.assertIn("workflow_charts", visualizations)

if __name__ == '__main__':
    unittest.main() 