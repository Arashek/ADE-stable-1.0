"""
Tests for agent coordination patterns and capabilities.
"""

import unittest
import ast
from typing import Dict, Any
from ..agent_coordination import (
    task_allocation_pattern, agent_specialization_pattern,
    collaboration_optimization_pattern, AgentCoordinationAnalyzer,
    agent_coordination_template
)

class TestTaskAllocationPattern(unittest.TestCase):
    """Test cases for the Task Allocation pattern implementation."""
    
    def setUp(self):
        self.task_allocation_code = task_allocation_pattern.generate({
            "task_manager": "TaskManager",
            "load_balancer_type": "LoadBalancer"
        })
        
    def test_task_manager_structure(self):
        """Test the structure of the generated task manager class."""
        tree = ast.parse(self.task_allocation_code)
        self.assertTrue(any(
            isinstance(node, ast.ClassDef) and node.name == "TaskManager"
            for node in ast.walk(tree)
        ))
        
    def test_task_allocation_method(self):
        """Test the task allocation functionality."""
        tree = ast.parse(self.task_allocation_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "allocate_task"
            for node in ast.walk(tree)
        ))
        
    def test_priority_calculation(self):
        """Test the priority calculation functionality."""
        tree = ast.parse(self.task_allocation_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "_calculate_priority"
            for node in ast.walk(tree)
        ))

class TestAgentSpecializationPattern(unittest.TestCase):
    """Test cases for the Agent Specialization pattern implementation."""
    
    def setUp(self):
        self.specialization_code = agent_specialization_pattern.generate({
            "specialized_agent": "SpecializedAgent"
        })
        
    def test_specialized_agent_structure(self):
        """Test the structure of the generated specialized agent class."""
        tree = ast.parse(self.specialization_code)
        self.assertTrue(any(
            isinstance(node, ast.ClassDef) and node.name == "SpecializedAgent"
            for node in ast.walk(tree)
        ))
        
    def test_skill_management(self):
        """Test the skill management functionality."""
        tree = ast.parse(self.specialization_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "update_specialization"
            for node in ast.walk(tree)
        ))
        
    def test_capability_matching(self):
        """Test the capability matching functionality."""
        tree = ast.parse(self.specialization_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "can_handle_task"
            for node in ast.walk(tree)
        ))

class TestCollaborationOptimizationPattern(unittest.TestCase):
    """Test cases for the Collaboration Optimization pattern implementation."""
    
    def setUp(self):
        self.collaboration_code = collaboration_optimization_pattern.generate({
            "collaboration_manager": "CollaborationManager"
        })
        
    def test_collaboration_manager_structure(self):
        """Test the structure of the generated collaboration manager class."""
        tree = ast.parse(self.collaboration_code)
        self.assertTrue(any(
            isinstance(node, ast.ClassDef) and node.name == "CollaborationManager"
            for node in ast.walk(tree)
        ))
        
    def test_collaboration_optimization(self):
        """Test the collaboration optimization functionality."""
        tree = ast.parse(self.collaboration_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "optimize_collaboration"
            for node in ast.walk(tree)
        ))
        
    def test_resource_sharing(self):
        """Test the resource sharing functionality."""
        tree = ast.parse(self.collaboration_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "share_resource"
            for node in ast.walk(tree)
        ))

class TestAgentCoordinationAnalyzer(unittest.TestCase):
    """Test cases for the AgentCoordinationAnalyzer."""
    
    def setUp(self):
        self.analyzer = AgentCoordinationAnalyzer()
        
    def test_task_allocation_analysis(self):
        """Test task allocation pattern analysis."""
        code = """
def allocate_task(task):
    return select_agent(task)
"""
        tree = ast.parse(code)
        self.analyzer.analyze_task_allocation(code)
        patterns = self.analyzer.analysis['task_allocation']['patterns']
        self.assertTrue(any(
            pattern['type'] == 'load_balancing'
            for pattern in patterns
        ))
        
    def test_specialization_analysis(self):
        """Test specialization pattern analysis."""
        code = """
def update_skills(agent):
    return evaluate_skills(agent)
"""
        tree = ast.parse(code)
        self.analyzer.analyze_specialization(code)
        patterns = self.analyzer.analysis['specialization']['patterns']
        self.assertTrue(any(
            pattern['type'] == 'skill_management'
            for pattern in patterns
        ))
        
    def test_collaboration_analysis(self):
        """Test collaboration pattern analysis."""
        code = """
def coordinate_agents():
    return manage_workflow()
"""
        tree = ast.parse(code)
        self.analyzer.analyze_collaboration(code)
        patterns = self.analyzer.analysis['collaboration']['patterns']
        self.assertTrue(any(
            pattern['type'] == 'coordination'
            for pattern in patterns
        ))
        
    def test_optimization_report_generation(self):
        """Test optimization report generation."""
        report = self.analyzer.generate_optimization_report()
        self.assertIn('task_allocation', report)
        self.assertIn('specialization', report)
        self.assertIn('collaboration', report)
        
        # Check task allocation optimizations
        task_optimizations = report['task_allocation']
        self.assertIn('load_balancing_opportunities', task_optimizations)
        self.assertIn('priority_optimizations', task_optimizations)
        self.assertIn('resource_utilization_improvements', task_optimizations)
        
        # Check specialization optimizations
        specialization_optimizations = report['specialization']
        self.assertIn('skill_development_opportunities', specialization_optimizations)
        self.assertIn('capability_optimizations', specialization_optimizations)
        self.assertIn('performance_improvements', specialization_optimizations)
        
        # Check collaboration optimizations
        collaboration_optimizations = report['collaboration']
        self.assertIn('communication_optimizations', collaboration_optimizations)
        self.assertIn('resource_sharing_improvements', collaboration_optimizations)
        self.assertIn('coordination_enhancements', collaboration_optimizations)

class TestAgentCoordinationTemplate(unittest.TestCase):
    """Test cases for the agent coordination documentation template."""
    
    def test_documentation_generation(self):
        """Test documentation template generation."""
        doc_data = {
            "system_name": "Test System",
            "overview": "System overview",
            "load_balancing": "Load balancing strategy",
            "priority_management": "Priority management approach",
            "resource_utilization": "Resource utilization guidelines",
            "skill_management": "Skill management process",
            "capability_matching": "Capability matching algorithm",
            "performance_tracking": "Performance tracking methodology",
            "communication_patterns": "Communication patterns",
            "resource_sharing": "Resource sharing strategy",
            "coordination_mechanisms": "Coordination mechanisms",
            "task_allocation_metrics": [
                {
                    "name": "Task Completion Rate",
                    "description": "Rate of task completion"
                }
            ],
            "specialization_metrics": [
                {
                    "name": "Skill Development Rate",
                    "description": "Rate of skill development"
                }
            ],
            "collaboration_metrics": [
                {
                    "name": "Collaboration Efficiency",
                    "description": "Efficiency of agent collaboration"
                }
            ],
            "task_allocation_optimizations": [
                {
                    "title": "Load Balancing Optimization",
                    "description": "Optimize load balancing",
                    "impact": "High",
                    "implementation": "Implementation steps"
                }
            ],
            "specialization_optimizations": [
                {
                    "title": "Skill Development Optimization",
                    "description": "Optimize skill development",
                    "impact": "High",
                    "implementation": "Implementation steps"
                }
            ],
            "collaboration_optimizations": [
                {
                    "title": "Communication Optimization",
                    "description": "Optimize communication",
                    "impact": "High",
                    "implementation": "Implementation steps"
                }
            ],
            "best_practices": "Best practices for agent coordination",
            "troubleshooting": "Troubleshooting guide"
        }
        
        doc = agent_coordination_template.generate(doc_data)
        self.assertIn("Test System", doc)
        self.assertIn("Load Balancing", doc)
        self.assertIn("Task Completion Rate", doc)
        self.assertIn("Load Balancing Optimization", doc)

if __name__ == '__main__':
    unittest.main() 