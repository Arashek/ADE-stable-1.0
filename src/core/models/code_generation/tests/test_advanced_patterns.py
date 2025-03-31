"""
Tests for advanced design patterns, enhanced analysis capabilities, and specialized documentation templates.
"""

import unittest
import ast
from typing import Dict, Any
from ..advanced_patterns import (
    factory_pattern, strategy_pattern,
    SecurityAnalyzer, PerformanceAnalyzer,
    api_documentation_template, architecture_documentation_template
)

class TestFactoryPattern(unittest.TestCase):
    """Test cases for the Factory pattern implementation."""
    
    def setUp(self):
        self.factory_code = factory_pattern.generate({
            "factory_name": "ProductFactory",
            "base_class": "Product"
        })
        
    def test_factory_structure(self):
        """Test the structure of the generated factory class."""
        tree = ast.parse(self.factory_code)
        self.assertTrue(any(
            isinstance(node, ast.ClassDef) and node.name == "ProductFactory"
            for node in ast.walk(tree)
        ))
        
    def test_creator_registration(self):
        """Test the creator registration functionality."""
        tree = ast.parse(self.factory_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "register"
            for node in ast.walk(tree)
        ))
        
    def test_type_safety(self):
        """Test type safety in creator registration."""
        tree = ast.parse(self.factory_code)
        self.assertTrue(any(
            isinstance(node, ast.AnnAssign) and
            isinstance(node.target, ast.Name) and
            node.target.id == "_creators"
            for node in ast.walk(tree)
        ))

class TestStrategyPattern(unittest.TestCase):
    """Test cases for the Strategy pattern implementation."""
    
    def setUp(self):
        self.strategy_code = strategy_pattern.generate({
            "context_name": "Context",
            "strategy_interface": "Strategy"
        })
        
    def test_strategy_structure(self):
        """Test the structure of the generated strategy class."""
        tree = ast.parse(self.strategy_code)
        self.assertTrue(any(
            isinstance(node, ast.ClassDef) and node.name == "Context"
            for node in ast.walk(tree)
        ))
        
    def test_strategy_management(self):
        """Test strategy management functionality."""
        tree = ast.parse(self.strategy_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "set_strategy"
            for node in ast.walk(tree)
        ))
        
    def test_strategy_execution(self):
        """Test strategy execution functionality."""
        tree = ast.parse(self.strategy_code)
        self.assertTrue(any(
            isinstance(node, ast.FunctionDef) and node.name == "execute_strategy"
            for node in ast.walk(tree)
        ))

class TestSecurityAnalyzer(unittest.TestCase):
    """Test cases for the SecurityAnalyzer."""
    
    def setUp(self):
        self.analyzer = SecurityAnalyzer()
        
    def test_sql_injection_detection(self):
        """Test SQL injection vulnerability detection."""
        code = """
def execute_query(query):
    cursor.execute(query.format(user_input))
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        vulnerabilities = self.analyzer.analysis['security']['vulnerabilities']
        self.assertTrue(any(
            vuln['type'] == 'sql_injection'
            for vuln in vulnerabilities
        ))
        
    def test_xss_vulnerability_detection(self):
        """Test XSS vulnerability detection."""
        code = """
def render_page(content):
    return render_template('page.html', content=user_input)
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        vulnerabilities = self.analyzer.analysis['security']['vulnerabilities']
        self.assertTrue(any(
            vuln['type'] == 'xss_vulnerability'
            for vuln in vulnerabilities
        ))
        
    def test_command_injection_detection(self):
        """Test command injection vulnerability detection."""
        code = """
def execute_command(command):
    os.system(command)
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        vulnerabilities = self.analyzer.analysis['security']['vulnerabilities']
        self.assertTrue(any(
            vuln['type'] == 'command_injection'
            for vuln in vulnerabilities
        ))

class TestPerformanceAnalyzer(unittest.TestCase):
    """Test cases for the PerformanceAnalyzer."""
    
    def setUp(self):
        self.analyzer = PerformanceAnalyzer()
        
    def test_memory_usage_analysis(self):
        """Test memory usage pattern analysis."""
        code = """
def process_data(data):
    result = []
    for item in data:
        result.append(item)
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        metrics = self.analyzer.analysis['performance']['metrics']
        self.assertGreater(metrics.get('memory_operations', 0), 0)
        
    def test_cpu_usage_analysis(self):
        """Test CPU usage pattern analysis."""
        code = """
def process_data(data):
    return sorted(data)
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        metrics = self.analyzer.analysis['performance']['metrics']
        self.assertGreater(metrics.get('cpu_operations', 0), 0)
        
    def test_io_operations_analysis(self):
        """Test I/O operations pattern analysis."""
        code = """
def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()
"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        metrics = self.analyzer.analysis['performance']['metrics']
        self.assertGreater(metrics.get('io_operations', 0), 0)

class TestDocumentationTemplates(unittest.TestCase):
    """Test cases for the documentation templates."""
    
    def test_api_documentation_generation(self):
        """Test API documentation template generation."""
        doc_data = {
            "title": "Test API",
            "overview": "Test API overview",
            "base_url": "https://api.example.com",
            "authentication": "Bearer token",
            "endpoints": [
                {
                    "method": "GET",
                    "path": "/users",
                    "description": "Get users",
                    "parameters": [
                        {"name": "page", "type": "int", "description": "Page number"}
                    ],
                    "request_body": "None",
                    "response": "List of users",
                    "example_language": "python",
                    "example": "response = requests.get('/users', params={'page': 1})"
                }
            ],
            "error_codes": [
                {"code": "400", "description": "Bad Request"}
            ],
            "rate_limiting": "100 requests per minute",
            "versions": [
                {"number": "1.0.0", "changes": "Initial release"}
            ]
        }
        
        doc = api_documentation_template.generate(doc_data)
        self.assertIn("Test API", doc)
        self.assertIn("GET /users", doc)
        self.assertIn("Bearer token", doc)
        
    def test_architecture_documentation_generation(self):
        """Test architecture documentation template generation."""
        doc_data = {
            "system_name": "Test System",
            "overview": "Test system overview",
            "diagram": "System diagram",
            "components": [
                {
                    "name": "Component A",
                    "description": "Component A description",
                    "responsibilities": ["Responsibility 1", "Responsibility 2"],
                    "dependencies": ["Dependency 1", "Dependency 2"],
                    "interfaces": ["Interface 1", "Interface 2"]
                }
            ],
            "data_flow": "Data flow description",
            "security_architecture": "Security architecture description",
            "deployment_architecture": "Deployment architecture description",
            "scalability": "Scalability considerations",
            "monitoring": "Monitoring and logging",
            "disaster_recovery": "Disaster recovery plan"
        }
        
        doc = architecture_documentation_template.generate(doc_data)
        self.assertIn("Test System", doc)
        self.assertIn("Component A", doc)
        self.assertIn("Security architecture", doc)

if __name__ == '__main__':
    unittest.main() 