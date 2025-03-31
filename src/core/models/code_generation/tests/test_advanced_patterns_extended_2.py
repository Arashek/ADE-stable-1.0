"""
Tests for extended advanced patterns, security checks, performance metrics, and documentation templates.
"""

import unittest
import ast
from typing import Dict, Any
from ..advanced_patterns_extended_2 import (
    chain_of_responsibility_pattern, mediator_pattern, memento_pattern,
    ExtendedSecurityAnalyzer2, ExtendedPerformanceAnalyzer2,
    api_documentation_template, architecture_documentation_template,
    development_guide_template
)

class TestChainOfResponsibilityPattern(unittest.TestCase):
    """Test cases for the Chain of Responsibility pattern implementation."""
    
    def setUp(self):
        self.handler_code = chain_of_responsibility_pattern.generate({
            "handler_base": "Handler",
            "handler_type": "request_handler"
        })
        
    def test_handler_structure(self):
        """Test the structure of the generated handler class."""
        tree = ast.parse(self.handler_code)
        self.assertTrue(any(
            isinstance(node, ast.ClassDef) and node.name == "Handler"
            for node in ast.walk(tree)
        ))
        
    def test_handler_chain(self):
        """Test the handler chain functionality."""
        tree = ast.parse(self.handler_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "set_next"
            for node in ast.walk(tree)
        ))
        
    def test_request_handling(self):
        """Test the request handling functionality."""
        tree = ast.parse(self.handler_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "handle"
            for node in ast.walk(tree)
        ))

class TestMediatorPattern(unittest.TestCase):
    """Test cases for the Mediator pattern implementation."""
    
    def setUp(self):
        self.mediator_code = mediator_pattern.generate({
            "mediator_base": "Mediator",
            "colleague_type": "Colleague"
        })
        
    def test_mediator_structure(self):
        """Test the structure of the generated mediator class."""
        tree = ast.parse(self.mediator_code)
        self.assertTrue(any(
            isinstance(node, ast.ClassDef) and node.name == "Mediator"
            for node in ast.walk(tree)
        ))
        
    def test_colleague_registration(self):
        """Test colleague registration functionality."""
        tree = ast.parse(self.mediator_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "register_colleague"
            for node in ast.walk(tree)
        ))
        
    def test_event_handling(self):
        """Test event handling functionality."""
        tree = ast.parse(self.mediator_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "notify"
            for node in ast.walk(tree)
        ))

class TestMementoPattern(unittest.TestCase):
    """Test cases for the Memento pattern implementation."""
    
    def setUp(self):
        self.originator_code = memento_pattern.generate({
            "originator_base": "Originator",
            "memento_type": "Memento"
        })
        
    def test_originator_structure(self):
        """Test the structure of the generated originator class."""
        tree = ast.parse(self.originator_code)
        self.assertTrue(any(
            isinstance(node, ast.ClassDef) and node.name == "Originator"
            for node in ast.walk(tree)
        ))
        
    def test_memento_creation(self):
        """Test memento creation functionality."""
        tree = ast.parse(self.originator_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "create_memento"
            for node in ast.walk(tree)
        ))
        
    def test_state_restoration(self):
        """Test state restoration functionality."""
        tree = ast.parse(self.originator_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "restore_from_memento"
            for node in ast.walk(tree)
        ))

class TestExtendedSecurityAnalyzer2(unittest.TestCase):
    """Test cases for the ExtendedSecurityAnalyzer2."""
    
    def setUp(self):
        self.analyzer = ExtendedSecurityAnalyzer2()
        
    def test_api_security_check(self):
        """Test API security vulnerability detection."""
        code = """
def process_request(data):
    return handle_request(data)
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        vulnerabilities = self.analyzer.analysis['security']['vulnerabilities']
        self.assertTrue(any(
            vuln['type'].startswith('weak_api_')
            for vuln in vulnerabilities
        ))
        
    def test_file_system_security_check(self):
        """Test file system security vulnerability detection."""
        code = """
def read_file(path):
    return open(path).read()
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        vulnerabilities = self.analyzer.analysis['security']['vulnerabilities']
        self.assertTrue(any(
            vuln['type'].startswith('weak_file_system_')
            for vuln in vulnerabilities
        ))
        
    def test_network_security_check(self):
        """Test network security vulnerability detection."""
        code = """
def send_data(data):
    return connect().send(data)
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        vulnerabilities = self.analyzer.analysis['security']['vulnerabilities']
        self.assertTrue(any(
            vuln['type'].startswith('weak_network_')
            for vuln in vulnerabilities
        ))

class TestExtendedPerformanceAnalyzer2(unittest.TestCase):
    """Test cases for the ExtendedPerformanceAnalyzer2."""
    
    def setUp(self):
        self.analyzer = ExtendedPerformanceAnalyzer2()
        
    def test_memory_profiling(self):
        """Test memory usage pattern analysis."""
        code = """
def process_data(data):
    result = allocate_memory(len(data))
    return result
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        metrics = self.analyzer.analysis['performance']['metrics']
        self.assertGreater(metrics.get('memory_allocation', 0), 0)
        
    def test_cpu_profiling(self):
        """Test CPU usage pattern analysis."""
        code = """
def calculate_result(data):
    return process_data(data)
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        metrics = self.analyzer.analysis['performance']['metrics']
        self.assertGreater(metrics.get('cpu_computation', 0), 0)
        
    def test_io_profiling(self):
        """Test I/O operation pattern analysis."""
        code = """
def read_data():
    return read_file('data.txt')
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        metrics = self.analyzer.analysis['performance']['metrics']
        self.assertGreater(metrics.get('io_file_io', 0), 0)

class TestDocumentationTemplates(unittest.TestCase):
    """Test cases for the documentation templates."""
    
    def test_api_documentation_generation(self):
        """Test API documentation template generation."""
        doc_data = {
            "api_name": "Test API",
            "overview": "Test API Overview",
            "base_url": "https://api.test.com",
            "authentication": "Bearer token",
            "endpoints": [
                {
                    "method": "GET",
                    "path": "/users",
                    "description": "Get users",
                    "parameters": [
                        {"name": "page", "type": "integer", "description": "Page number"}
                    ],
                    "request_body": "{}",
                    "response": '{"users": []}',
                    "error_codes": [
                        {"code": "401", "description": "Unauthorized"}
                    ]
                }
            ],
            "rate_limiting": "100 requests per minute",
            "version_history": "v1.0.0",
            "examples": "Example usage"
        }
        
        doc = api_documentation_template.generate(doc_data)
        self.assertIn("Test API", doc)
        self.assertIn("GET /users", doc)
        self.assertIn("Bearer token", doc)
        
    def test_architecture_documentation_generation(self):
        """Test architecture documentation template generation."""
        doc_data = {
            "system_name": "Test System",
            "system_overview": "System overview",
            "architecture_diagram": "diagram.png",
            "components": [
                {
                    "name": "Component 1",
                    "description": "Component description",
                    "responsibilities": ["Responsibility 1"],
                    "dependencies": ["Dependency 1"],
                    "interfaces": ["Interface 1"]
                }
            ],
            "data_flow": "Data flow description",
            "security_architecture": "Security architecture",
            "deployment_architecture": "Deployment architecture",
            "scalability_considerations": "Scalability considerations",
            "monitoring_logging": "Monitoring and logging",
            "disaster_recovery": "Disaster recovery"
        }
        
        doc = architecture_documentation_template.generate(doc_data)
        self.assertIn("Test System", doc)
        self.assertIn("Component 1", doc)
        self.assertIn("Data flow description", doc)
        
    def test_development_guide_generation(self):
        """Test development guide template generation."""
        doc_data = {
            "project_name": "Test Project",
            "setup_steps": [
                {
                    "title": "Setup Step 1",
                    "description": "Setup description",
                    "prerequisites": ["Prerequisite 1"],
                    "installation": "Installation steps",
                    "configuration": "Configuration steps"
                }
            ],
            "code_style_guide": "Code style guide",
            "testing_guidelines": [
                {
                    "title": "Testing Guideline 1",
                    "description": "Testing description",
                    "examples": "Testing examples"
                }
            ],
            "debugging_guide": "Debugging guide",
            "performance_optimization": "Performance optimization",
            "security_guidelines": "Security guidelines",
            "deployment_process": "Deployment process",
            "contributing_guidelines": "Contributing guidelines",
            "troubleshooting": "Troubleshooting guide"
        }
        
        doc = development_guide_template.generate(doc_data)
        self.assertIn("Test Project", doc)
        self.assertIn("Setup Step 1", doc)
        self.assertIn("Code style guide", doc)

if __name__ == '__main__':
    unittest.main() 