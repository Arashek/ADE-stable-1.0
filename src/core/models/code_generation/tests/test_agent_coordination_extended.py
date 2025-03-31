"""
Tests for extended agent coordination patterns and capabilities.
"""

import unittest
import ast
from typing import Dict, Any
from ..agent_coordination_extended import (
    consensus_protocol_pattern, leader_election_pattern,
    ExtendedAgentCoordinationAnalyzer, deployment_guide_template,
    monitoring_guide_template
)

class TestConsensusProtocolPattern(unittest.TestCase):
    """Test cases for the Consensus Protocol pattern implementation."""
    
    def setUp(self):
        self.consensus_code = consensus_protocol_pattern.generate({
            "consensus_manager": "ConsensusManager"
        })
        
    def test_consensus_manager_structure(self):
        """Test the structure of the generated consensus manager class."""
        tree = ast.parse(self.consensus_code)
        self.assertTrue(any(
            isinstance(node, ast.ClassDef) and node.name == "ConsensusManager"
            for node in ast.walk(tree)
        ))
        
    def test_proposal_handling(self):
        """Test the proposal handling functionality."""
        tree = ast.parse(self.consensus_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "propose_value"
            for node in ast.walk(tree)
        ))
        
    def test_consensus_checking(self):
        """Test the consensus checking functionality."""
        tree = ast.parse(self.consensus_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "_check_consensus"
            for node in ast.walk(tree)
        ))

class TestLeaderElectionPattern(unittest.TestCase):
    """Test cases for the Leader Election pattern implementation."""
    
    def setUp(self):
        self.election_code = leader_election_pattern.generate({
            "leader_election_manager": "LeaderElectionManager"
        })
        
    def test_leader_election_manager_structure(self):
        """Test the structure of the generated leader election manager class."""
        tree = ast.parse(self.election_code)
        self.assertTrue(any(
            isinstance(node, ast.ClassDef) and node.name == "LeaderElectionManager"
            for node in ast.walk(tree)
        ))
        
    def test_election_process(self):
        """Test the election process functionality."""
        tree = ast.parse(self.election_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "start_election"
            for node in ast.walk(tree)
        ))
        
    def test_heartbeat_handling(self):
        """Test the heartbeat handling functionality."""
        tree = ast.parse(self.election_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "handle_heartbeat"
            for node in ast.walk(tree)
        ))

class TestExtendedAgentCoordinationAnalyzer(unittest.TestCase):
    """Test cases for the ExtendedAgentCoordinationAnalyzer."""
    
    def setUp(self):
        self.analyzer = ExtendedAgentCoordinationAnalyzer()
        
    def test_performance_analysis(self):
        """Test performance pattern analysis."""
        code = """
def optimize_operation():
    return profile_performance()
"""
        tree = ast.parse(code)
        self.analyzer.analyze_performance(code)
        patterns = self.analyzer.analysis['performance']['patterns']
        self.assertTrue(any(
            pattern['type'] == 'optimization'
            for pattern in patterns
        ))
        
    def test_resource_usage_analysis(self):
        """Test resource usage pattern analysis."""
        code = """
def allocate_memory():
    return free_memory()
"""
        tree = ast.parse(code)
        self.analyzer.analyze_resource_usage(code)
        patterns = self.analyzer.analysis['resource_usage']['patterns']
        self.assertTrue(any(
            pattern['type'] == 'memory'
            for pattern in patterns
        ))
        
    def test_consensus_analysis(self):
        """Test consensus pattern analysis."""
        code = """
def propose_value():
    return handle_proposal()
"""
        tree = ast.parse(code)
        self.analyzer.analyze_consensus(code)
        patterns = self.analyzer.analysis['consensus']['patterns']
        self.assertTrue(any(
            pattern['type'] == 'proposal'
            for pattern in patterns
        ))
        
    def test_optimization_report_generation(self):
        """Test comprehensive optimization report generation."""
        report = self.analyzer.generate_optimization_report()
        self.assertIn('performance', report)
        self.assertIn('resource_usage', report)
        self.assertIn('consensus', report)
        
        # Check performance optimizations
        performance_optimizations = report['performance']
        self.assertIn('concurrency_optimizations', performance_optimizations)
        self.assertIn('caching_optimizations', performance_optimizations)
        self.assertIn('general_optimizations', performance_optimizations)
        
        # Check resource usage optimizations
        resource_optimizations = report['resource_usage']
        self.assertIn('memory_optimizations', resource_optimizations)
        self.assertIn('cpu_optimizations', resource_optimizations)
        self.assertIn('io_optimizations', resource_optimizations)
        
        # Check consensus optimizations
        consensus_optimizations = report['consensus']
        self.assertIn('proposal_optimizations', consensus_optimizations)
        self.assertIn('election_optimizations', consensus_optimizations)
        self.assertIn('replication_optimizations', consensus_optimizations)

class TestDocumentationTemplates(unittest.TestCase):
    """Test cases for the documentation templates."""
    
    def test_deployment_guide_generation(self):
        """Test deployment guide template generation."""
        doc_data = {
            "system_name": "Test System",
            "prerequisites": "System prerequisites",
            "system_requirements": "System requirements",
            "installation_steps": "Installation steps",
            "configuration": "Configuration details",
            "deployment_process": "Deployment process",
            "monitoring_setup": "Monitoring setup",
            "scaling_guidelines": "Scaling guidelines",
            "backup_recovery": "Backup and recovery procedures",
            "troubleshooting": "Troubleshooting guide"
        }
        
        doc = deployment_guide_template.generate(doc_data)
        self.assertIn("Test System", doc)
        self.assertIn("Prerequisites", doc)
        self.assertIn("Installation Steps", doc)
        self.assertIn("Deployment Process", doc)
        
    def test_monitoring_guide_generation(self):
        """Test monitoring guide template generation."""
        doc_data = {
            "system_name": "Test System",
            "overview": "System overview",
            "metrics_collection": "Metrics collection process",
            "alert_configuration": "Alert configuration",
            "dashboard_setup": "Dashboard setup",
            "performance_monitoring": "Performance monitoring",
            "resource_monitoring": "Resource monitoring",
            "log_management": "Log management",
            "incident_response": "Incident response procedures"
        }
        
        doc = monitoring_guide_template.generate(doc_data)
        self.assertIn("Test System", doc)
        self.assertIn("Metrics Collection", doc)
        self.assertIn("Alert Configuration", doc)
        self.assertIn("Performance Monitoring", doc)

if __name__ == '__main__':
    unittest.main() 