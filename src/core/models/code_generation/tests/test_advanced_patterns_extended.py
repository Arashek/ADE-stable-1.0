"""
Tests for extended advanced patterns, security checks, performance metrics, and documentation templates.
"""

import unittest
import ast
from typing import Dict, Any
from ..advanced_patterns_extended import (
    command_pattern, state_pattern, template_method_pattern,
    ExtendedSecurityAnalyzer, ExtendedPerformanceAnalyzer,
    deployment_guide_template, user_manual_template, troubleshooting_guide_template
)

class TestCommandPattern(unittest.TestCase):
    """Test cases for the Command pattern implementation."""
    
    def setUp(self):
        self.command_code = command_pattern.generate({
            "command_base": "DocumentCommand",
            "action": "insert",
            "undo_action": "delete"
        })
        
    def test_command_structure(self):
        """Test the structure of the generated command class."""
        tree = ast.parse(self.command_code)
        self.assertTrue(any(
            isinstance(node, ast.ClassDef) and node.name == "DocumentCommand"
            for node in ast.walk(tree)
        ))
        
    def test_command_execution(self):
        """Test the command execution functionality."""
        tree = ast.parse(self.command_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "execute"
            for node in ast.walk(tree)
        ))
        
    def test_command_undo(self):
        """Test the command undo functionality."""
        tree = ast.parse(self.command_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "undo"
            for node in ast.walk(tree)
        ))

class TestStatePattern(unittest.TestCase):
    """Test cases for the State pattern implementation."""
    
    def setUp(self):
        self.state_code = state_pattern.generate({
            "context_name": "Context",
            "state_interface": "State"
        })
        
    def test_state_structure(self):
        """Test the structure of the generated state class."""
        tree = ast.parse(self.state_code)
        self.assertTrue(any(
            isinstance(node, ast.ClassDef) and node.name == "Context"
            for node in ast.walk(tree)
        ))
        
    def test_state_transition(self):
        """Test state transition functionality."""
        tree = ast.parse(self.state_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "set_state"
            for node in ast.walk(tree)
        ))
        
    def test_state_event_handling(self):
        """Test state event handling functionality."""
        tree = ast.parse(self.state_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "handle_event"
            for node in ast.walk(tree)
        ))

class TestTemplateMethodPattern(unittest.TestCase):
    """Test cases for the Template Method pattern implementation."""
    
    def setUp(self):
        self.template_code = template_method_pattern.generate({
            "abstract_class": "AbstractClass"
        })
        
    def test_template_structure(self):
        """Test the structure of the generated template class."""
        tree = ast.parse(self.template_code)
        self.assertTrue(any(
            isinstance(node, ast.ClassDef) and node.name == "AbstractClass"
            for node in ast.walk(tree)
        ))
        
    def test_template_method(self):
        """Test the template method functionality."""
        tree = ast.parse(self.template_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "template_method"
            for node in ast.walk(tree)
        ))
        
    def test_hooks(self):
        """Test the hook methods."""
        tree = ast.parse(self.template_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "_before_hook"
            for node in ast.walk(tree)
        ))
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "_after_hook"
            for node in ast.walk(tree)
        ))

class TestExtendedSecurityAnalyzer(unittest.TestCase):
    """Test cases for the ExtendedSecurityAnalyzer."""
    
    def setUp(self):
        self.analyzer = ExtendedSecurityAnalyzer()
        
    def test_authentication_check(self):
        """Test authentication vulnerability detection."""
        code = """
def login(password):
    hashed = hash(password)
    return verify(hashed)
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        vulnerabilities = self.analyzer.analysis['security']['vulnerabilities']
        self.assertTrue(any(
            vuln['type'] == 'weak_authentication'
            for vuln in vulnerabilities
        ))
        
    def test_authorization_check(self):
        """Test authorization vulnerability detection."""
        code = """
def check_access(user):
    return has_access(user)
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        vulnerabilities = self.analyzer.analysis['security']['vulnerabilities']
        self.assertTrue(any(
            vuln['type'] == 'weak_authorization'
            for vuln in vulnerabilities
        ))
        
    def test_encryption_check(self):
        """Test encryption vulnerability detection."""
        code = """
def encrypt_data(data):
    return encrypt(data)
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        vulnerabilities = self.analyzer.analysis['security']['vulnerabilities']
        self.assertTrue(any(
            vuln['type'] == 'weak_encryption'
            for vuln in vulnerabilities
        ))

class TestExtendedPerformanceAnalyzer(unittest.TestCase):
    """Test cases for the ExtendedPerformanceAnalyzer."""
    
    def setUp(self):
        self.analyzer = ExtendedPerformanceAnalyzer()
        
    def test_concurrency_analysis(self):
        """Test concurrency pattern analysis."""
        code = """
def process_data(data):
    with Thread() as thread:
        thread.start()
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        metrics = self.analyzer.analysis['performance']['metrics']
        self.assertGreater(metrics.get('threading_operations', 0), 0)
        
    def test_caching_analysis(self):
        """Test caching pattern analysis."""
        code = """
@cache
def get_data():
    return fetch_data()
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        metrics = self.analyzer.analysis['performance']['metrics']
        self.assertGreater(metrics.get('caching_operations', 0), 0)
        
    def test_database_analysis(self):
        """Test database operation analysis."""
        code = """
def save_data(data):
    cursor.execute(query)
    connection.commit()
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        metrics = self.analyzer.analysis['performance']['metrics']
        self.assertGreater(metrics.get('database_operations', 0), 0)

class TestDocumentationTemplates(unittest.TestCase):
    """Test cases for the documentation templates."""
    
    def test_deployment_guide_generation(self):
        """Test deployment guide template generation."""
        doc_data = {
            "system_name": "Test System",
            "prerequisites": "Python 3.8+",
            "system_requirements": "2GB RAM",
            "installation_steps": [
                {
                    "title": "Install Dependencies",
                    "description": "Install required packages",
                    "commands": "pip install -r requirements.txt",
                    "verification": "Check installed packages"
                }
            ],
            "configurations": [
                {
                    "name": "Database",
                    "description": "Database configuration",
                    "settings": [
                        {"name": "host", "description": "Database host"}
                    ]
                }
            ],
            "environment_setup": "Set environment variables",
            "security_considerations": "Use HTTPS",
            "monitoring_setup": "Configure logging",
            "backup_recovery": "Regular backups",
            "troubleshooting": "Common issues"
        }
        
        doc = deployment_guide_template.generate(doc_data)
        self.assertIn("Test System", doc)
        self.assertIn("Install Dependencies", doc)
        self.assertIn("Database configuration", doc)
        
    def test_user_manual_generation(self):
        """Test user manual template generation."""
        doc_data = {
            "product_name": "Test Product",
            "introduction": "Welcome to Test Product",
            "getting_started": [
                {
                    "title": "First Steps",
                    "description": "Getting started guide",
                    "screenshot": "screenshot.png"
                }
            ],
            "features": [
                {
                    "name": "Feature 1",
                    "description": "Feature description",
                    "usage": "How to use",
                    "examples": [
                        {
                            "language": "python",
                            "code": "print('Hello')"
                        }
                    ]
                }
            ],
            "configurations": [
                {
                    "name": "Settings",
                    "description": "User settings",
                    "options": [
                        {"name": "theme", "description": "UI theme"}
                    ]
                }
            ],
            "troubleshooting": [
                {
                    "title": "Common Issue",
                    "description": "Issue description",
                    "solution": "Solution steps"
                }
            ],
            "faq": "Frequently asked questions",
            "support": "Contact support"
        }
        
        doc = user_manual_template.generate(doc_data)
        self.assertIn("Test Product", doc)
        self.assertIn("First Steps", doc)
        self.assertIn("Feature 1", doc)
        
    def test_troubleshooting_guide_generation(self):
        """Test troubleshooting guide template generation."""
        doc_data = {
            "system_name": "Test System",
            "common_issues": [
                {
                    "title": "Connection Issue",
                    "description": "Cannot connect",
                    "symptoms": "Connection timeout",
                    "causes": "Network issue",
                    "solutions": ["Check network", "Restart service"],
                    "prevention": "Regular maintenance"
                }
            ],
            "error_messages": [
                {
                    "code": "ERR001",
                    "description": "Connection error",
                    "causes": "Network timeout",
                    "steps": ["Check connection", "Verify settings"]
                }
            ],
            "performance_issues": [
                {
                    "title": "Slow Response",
                    "description": "System is slow",
                    "indicators": "High CPU usage",
                    "diagnosis": "Resource intensive process",
                    "solutions": ["Optimize code", "Add caching"]
                }
            ],
            "network_issues": [
                {
                    "title": "Network Error",
                    "description": "Network connectivity issues",
                    "symptoms": "Connection drops",
                    "diagnosis_steps": ["Check cables", "Test connection"],
                    "solutions": ["Replace cable", "Update drivers"]
                }
            ],
            "support_resources": "Contact support team"
        }
        
        doc = troubleshooting_guide_template.generate(doc_data)
        self.assertIn("Test System", doc)
        self.assertIn("Connection Issue", doc)
        self.assertIn("ERR001", doc)

if __name__ == '__main__':
    unittest.main() 