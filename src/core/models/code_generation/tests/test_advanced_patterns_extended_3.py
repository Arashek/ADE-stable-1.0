"""
Tests for extended advanced patterns, security checks, performance metrics, and documentation templates.
"""

import unittest
import ast
from typing import Dict, Any
from ..advanced_patterns_extended_3 import (
    visitor_pattern, bridge_pattern, flyweight_pattern,
    ExtendedSecurityAnalyzer3, ExtendedPerformanceAnalyzer3,
    api_reference_template, user_guide_template,
    troubleshooting_guide_template
)

class TestVisitorPattern(unittest.TestCase):
    """Test cases for the Visitor pattern implementation."""
    
    def setUp(self):
        self.visitor_code = visitor_pattern.generate({
            "visitor_base": "Visitor"
        })
        
    def test_visitor_structure(self):
        """Test the structure of the generated visitor class."""
        tree = ast.parse(self.visitor_code)
        self.assertTrue(any(
            isinstance(node, ast.ClassDef) and node.name == "Visitor"
            for node in ast.walk(tree)
        ))
        
    def test_visit_method(self):
        """Test the visit method functionality."""
        tree = ast.parse(self.visitor_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "visit"
            for node in ast.walk(tree)
        ))
        
    def test_visit_tracking(self):
        """Test the visit tracking functionality."""
        tree = ast.parse(self.visitor_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "__init__"
            and "self._visited" in ast.unparse(node)
            for node in ast.walk(tree)
        ))

class TestBridgePattern(unittest.TestCase):
    """Test cases for the Bridge pattern implementation."""
    
    def setUp(self):
        self.bridge_code = bridge_pattern.generate({
            "abstraction_base": "Abstraction",
            "implementation_type": "Implementation"
        })
        
    def test_bridge_structure(self):
        """Test the structure of the generated bridge class."""
        tree = ast.parse(self.bridge_code)
        self.assertTrue(any(
            isinstance(node, ast.ClassDef) and node.name == "Abstraction"
            for node in ast.walk(tree)
        ))
        
    def test_implementation_assignment(self):
        """Test implementation assignment functionality."""
        tree = ast.parse(self.bridge_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "__init__"
            and "self._implementation" in ast.unparse(node)
            for node in ast.walk(tree)
        ))
        
    def test_operation_delegation(self):
        """Test operation delegation functionality."""
        tree = ast.parse(self.bridge_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "operation"
            and "self._implementation.operation_impl()" in ast.unparse(node)
            for node in ast.walk(tree)
        ))

class TestFlyweightPattern(unittest.TestCase):
    """Test cases for the Flyweight pattern implementation."""
    
    def setUp(self):
        self.flyweight_code = flyweight_pattern.generate({
            "flyweight_base": "Flyweight",
            "factory_type": "FlyweightFactory"
        })
        
    def test_flyweight_structure(self):
        """Test the structure of the generated flyweight class."""
        tree = ast.parse(self.flyweight_code)
        self.assertTrue(any(
            isinstance(node, ast.ClassDef) and node.name == "Flyweight"
            for node in ast.walk(tree)
        ))
        
    def test_state_management(self):
        """Test state management functionality."""
        tree = ast.parse(self.flyweight_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "__init__"
            and "self._intrinsic_state" in ast.unparse(node)
            for node in ast.walk(tree)
        ))
        
    def test_operation_handling(self):
        """Test operation handling functionality."""
        tree = ast.parse(self.flyweight_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "operation"
            and "self._get_extrinsic_state()" in ast.unparse(node)
            for node in ast.walk(tree)
        ))

class TestExtendedSecurityAnalyzer3(unittest.TestCase):
    """Test cases for the ExtendedSecurityAnalyzer3."""
    
    def setUp(self):
        self.analyzer = ExtendedSecurityAnalyzer3()
        
    def test_cryptography_check(self):
        """Test cryptography vulnerability detection."""
        code = """
def encrypt_data(data):
    return encrypt(data)
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        vulnerabilities = self.analyzer.analysis['security']['vulnerabilities']
        self.assertTrue(any(
            vuln['type'].startswith('weak_crypto_')
            for vuln in vulnerabilities
        ))
        
    def test_session_management_check(self):
        """Test session management vulnerability detection."""
        code = """
def create_session(user):
    return start_session(user)
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        vulnerabilities = self.analyzer.analysis['security']['vulnerabilities']
        self.assertTrue(any(
            vuln['type'].startswith('weak_session_')
            for vuln in vulnerabilities
        ))
        
    def test_access_control_check(self):
        """Test access control vulnerability detection."""
        code = """
def authenticate_user(user):
    return login(user)
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        vulnerabilities = self.analyzer.analysis['security']['vulnerabilities']
        self.assertTrue(any(
            vuln['type'].startswith('weak_access_')
            for vuln in vulnerabilities
        ))

class TestExtendedPerformanceAnalyzer3(unittest.TestCase):
    """Test cases for the ExtendedPerformanceAnalyzer3."""
    
    def setUp(self):
        self.analyzer = ExtendedPerformanceAnalyzer3()
        
    def test_database_performance_analysis(self):
        """Test database performance pattern analysis."""
        code = """
def query_data():
    return execute_query("SELECT * FROM data")
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        metrics = self.analyzer.analysis['performance']['metrics']
        self.assertGreater(metrics.get('db_query_execution', 0), 0)
        
    def test_network_performance_analysis(self):
        """Test network performance pattern analysis."""
        code = """
def transfer_data():
    return stream_data(data)
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        metrics = self.analyzer.analysis['performance']['metrics']
        self.assertGreater(metrics.get('network_bandwidth', 0), 0)
        
    def test_cache_performance_analysis(self):
        """Test cache performance pattern analysis."""
        code = """
def get_data():
    return fetch_from_cache(key)
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        metrics = self.analyzer.analysis['performance']['metrics']
        self.assertGreater(metrics.get('cache_hit_rate', 0), 0)

class TestDocumentationTemplates(unittest.TestCase):
    """Test cases for the documentation templates."""
    
    def test_api_reference_generation(self):
        """Test API reference template generation."""
        doc_data = {
            "api_name": "Test API",
            "overview": "Test API Overview",
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
                    ],
                    "language": "python",
                    "example": "response = api.get_users(page=1)"
                }
            ],
            "data_models": [
                {
                    "name": "User",
                    "description": "User model",
                    "properties": [
                        {"name": "id", "type": "string", "description": "User ID"}
                    ],
                    "example": '{"id": "123", "name": "John"}'
                }
            ],
            "rate_limiting": "100 requests per minute",
            "version_history": "v1.0.0",
            "sdk_examples": "Example SDK usage"
        }
        
        doc = api_reference_template.generate(doc_data)
        self.assertIn("Test API", doc)
        self.assertIn("GET /users", doc)
        self.assertIn("Bearer token", doc)
        
    def test_user_guide_generation(self):
        """Test user guide template generation."""
        doc_data = {
            "product_name": "Test Product",
            "introduction": "Product introduction",
            "getting_started": [
                {
                    "title": "Setup",
                    "description": "Setup description",
                    "prerequisites": ["Python 3.8"],
                    "steps": ["Step 1", "Step 2"],
                    "examples": "Example setup"
                }
            ],
            "features": [
                {
                    "name": "Feature 1",
                    "description": "Feature description",
                    "usage": "Usage instructions",
                    "examples": "Example usage",
                    "tips": ["Tip 1", "Tip 2"]
                }
            ],
            "configurations": [
                {
                    "name": "Config 1",
                    "description": "Config description",
                    "options": [
                        {"name": "option1", "description": "Option description"}
                    ],
                    "language": "python",
                    "example": "config.option1 = 'value'"
                }
            ],
            "troubleshooting": [
                {
                    "title": "Issue 1",
                    "description": "Issue description",
                    "symptoms": ["Symptom 1"],
                    "solution": "Solution steps",
                    "prevention": "Prevention tips"
                }
            ],
            "support": "Support information"
        }
        
        doc = user_guide_template.generate(doc_data)
        self.assertIn("Test Product", doc)
        self.assertIn("Setup", doc)
        self.assertIn("Feature 1", doc)
        
    def test_troubleshooting_guide_generation(self):
        """Test troubleshooting guide template generation."""
        doc_data = {
            "system_name": "Test System",
            "common_issues": [
                {
                    "title": "Issue 1",
                    "description": "Issue description",
                    "symptoms": ["Symptom 1"],
                    "causes": ["Cause 1"],
                    "solutions": ["Solution 1"],
                    "prevention": "Prevention tips"
                }
            ],
            "error_messages": [
                {
                    "code": "ERR001",
                    "message": "Error message",
                    "description": "Error description",
                    "causes": ["Cause 1"],
                    "solutions": ["Solution 1"]
                }
            ],
            "performance_issues": [
                {
                    "title": "Performance Issue 1",
                    "description": "Issue description",
                    "symptoms": ["Symptom 1"],
                    "causes": ["Cause 1"],
                    "solutions": ["Solution 1"],
                    "monitoring": "Monitoring tips"
                }
            ],
            "network_issues": [
                {
                    "title": "Network Issue 1",
                    "description": "Issue description",
                    "symptoms": ["Symptom 1"],
                    "causes": ["Cause 1"],
                    "solutions": ["Solution 1"],
                    "prevention": "Prevention tips"
                }
            ],
            "support_resources": "Support resources"
        }
        
        doc = troubleshooting_guide_template.generate(doc_data)
        self.assertIn("Test System", doc)
        self.assertIn("Issue 1", doc)
        self.assertIn("ERR001", doc)

if __name__ == '__main__':
    unittest.main() 