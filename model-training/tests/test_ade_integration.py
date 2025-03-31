import pytest
import requests
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ade_integration_test.log'),
        logging.StreamHandler()
    ]
)

class ADEIntegrationTester:
    """Test integration with ADE system."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """Initialize the tester with ADE API base URL."""
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
        # Define expected operations for each prompt
        self.expected_operations = {
            "code_refactoring": [
                "code_analysis",
                "smell_detection",
                "refactoring_suggestion",
                "code_transformation",
                "quality_verification"
            ],
            "bug_fixing": [
                "error_analysis",
                "root_cause_identification",
                "fix_generation",
                "fix_verification",
                "test_generation"
            ],
            "code_optimization": [
                "performance_analysis",
                "bottleneck_identification",
                "optimization_suggestion",
                "code_transformation",
                "performance_verification"
            ],
            "documentation": [
                "code_analysis",
                "documentation_generation",
                "example_generation",
                "api_documentation",
                "documentation_verification"
            ]
        }
    
    def check_ade_health(self) -> bool:
        """Check if ADE is running and healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to connect to ADE: {e}")
            return False
    
    def send_prompt(self, prompt_type: str, code: str) -> Optional[str]:
        """Send a prompt to ADE and return the task ID."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/tasks",
                json={
                    "type": prompt_type,
                    "code": code,
                    "parameters": self._get_prompt_parameters(prompt_type)
                }
            )
            if response.status_code == 201:
                return response.json()["task_id"]
            else:
                logging.error(f"Failed to create task: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to send prompt: {e}")
            return None
    
    def monitor_task(self, task_id: str, timeout: int = 300) -> Optional[Dict]:
        """Monitor a task until completion or timeout."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.session.get(f"{self.base_url}/api/v1/tasks/{task_id}")
                if response.status_code == 200:
                    task_data = response.json()
                    if task_data["status"] in ["completed", "failed"]:
                        return task_data
                time.sleep(5)  # Wait before next check
            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to check task status: {e}")
                return None
        return None
    
    def analyze_results(self, prompt_type: str, task_data: Dict) -> Dict:
        """Analyze task results against expected operations."""
        expected_ops = self.expected_operations[prompt_type]
        actual_ops = self._extract_actual_operations(task_data)
        
        # Compare expected vs actual operations
        missing_ops = set(expected_ops) - set(actual_ops)
        extra_ops = set(actual_ops) - set(expected_ops)
        
        # Analyze operation sequence
        sequence_match = self._analyze_operation_sequence(expected_ops, actual_ops)
        
        # Check for error handling
        error_handling = self._analyze_error_handling(task_data)
        
        return {
            "prompt_type": prompt_type,
            "expected_operations": expected_ops,
            "actual_operations": actual_ops,
            "missing_operations": list(missing_ops),
            "extra_operations": list(extra_ops),
            "sequence_match": sequence_match,
            "error_handling": error_handling,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_prompt_parameters(self, prompt_type: str) -> Dict:
        """Get parameters for different prompt types."""
        return {
            "code_refactoring": {
                "quality_threshold": 0.8,
                "max_changes": 10,
                "preserve_tests": True
            },
            "bug_fixing": {
                "error_type": "all",
                "generate_tests": True,
                "fix_verification": True
            },
            "code_optimization": {
                "performance_threshold": 0.7,
                "optimization_level": "high",
                "profile_code": True
            },
            "documentation": {
                "doc_style": "google",
                "include_examples": True,
                "generate_tests": True
            }
        }
    
    def _extract_actual_operations(self, task_data: Dict) -> List[str]:
        """Extract actual operations from task data."""
        operations = []
        if "steps" in task_data:
            for step in task_data["steps"]:
                if "operation" in step:
                    operations.append(step["operation"])
        return operations
    
    def _analyze_operation_sequence(self, expected: List[str], actual: List[str]) -> Dict:
        """Analyze if operations were performed in the expected sequence."""
        sequence_match = True
        for i, op in enumerate(expected):
            if i < len(actual) and actual[i] != op:
                sequence_match = False
                break
        
        return {
            "matches": sequence_match,
            "expected_sequence": expected,
            "actual_sequence": actual
        }
    
    def _analyze_error_handling(self, task_data: Dict) -> Dict:
        """Analyze error handling in the task execution."""
        errors = []
        if "errors" in task_data:
            errors = task_data["errors"]
        
        return {
            "has_errors": len(errors) > 0,
            "error_count": len(errors),
            "error_types": [e.get("type", "unknown") for e in errors],
            "error_messages": [e.get("message", "") for e in errors]
        }
    
    def generate_report(self, results: List[Dict]) -> str:
        """Generate a detailed test report."""
        report = []
        report.append("# ADE Integration Test Report")
        report.append(f"Generated at: {datetime.now().isoformat()}\n")
        
        for result in results:
            report.append(f"## {result['prompt_type'].title()} Test")
            report.append(f"Timestamp: {result['timestamp']}\n")
            
            # Operation Analysis
            report.append("### Operation Analysis")
            report.append(f"- Expected Operations: {', '.join(result['expected_operations'])}")
            report.append(f"- Actual Operations: {', '.join(result['actual_operations'])}")
            
            if result['missing_operations']:
                report.append(f"- Missing Operations: {', '.join(result['missing_operations'])}")
            if result['extra_operations']:
                report.append(f"- Extra Operations: {', '.join(result['extra_operations'])}")
            
            # Sequence Analysis
            report.append("\n### Sequence Analysis")
            report.append(f"- Sequence Match: {'Yes' if result['sequence_match']['matches'] else 'No'}")
            if not result['sequence_match']['matches']:
                report.append("#### Expected Sequence:")
                for i, op in enumerate(result['sequence_match']['expected_sequence']):
                    report.append(f"{i+1}. {op}")
                report.append("\n#### Actual Sequence:")
                for i, op in enumerate(result['sequence_match']['actual_sequence']):
                    report.append(f"{i+1}. {op}")
            
            # Error Analysis
            report.append("\n### Error Analysis")
            report.append(f"- Has Errors: {'Yes' if result['error_handling']['has_errors'] else 'No'}")
            if result['error_handling']['has_errors']:
                report.append(f"- Error Count: {result['error_handling']['error_count']}")
                report.append("#### Error Types:")
                for error_type in result['error_handling']['error_types']:
                    report.append(f"- {error_type}")
                report.append("\n#### Error Messages:")
                for message in result['error_handling']['error_messages']:
                    report.append(f"- {message}")
            
            report.append("\n---\n")
        
        return "\n".join(report)

def test_ade_integration():
    """Run integration tests with ADE."""
    tester = ADEIntegrationTester()
    
    # Check ADE health
    assert tester.check_ade_health(), "ADE is not running or not healthy"
    
    # Test prompts
    test_cases = [
        {
            "type": "code_refactoring",
            "code": """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total
            """
        },
        {
            "type": "bug_fixing",
            "code": """
def divide(a, b):
    return a / b
            """
        },
        {
            "type": "code_optimization",
            "code": """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
            """
        },
        {
            "type": "documentation",
            "code": """
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
            """
        }
    ]
    
    results = []
    for case in test_cases:
        logging.info(f"Testing {case['type']} prompt")
        
        # Send prompt
        task_id = tester.send_prompt(case["type"], case["code"])
        assert task_id is not None, f"Failed to send {case['type']} prompt"
        
        # Monitor task
        task_data = tester.monitor_task(task_id)
        assert task_data is not None, f"Task monitoring failed for {case['type']}"
        assert task_data["status"] == "completed", f"Task failed for {case['type']}"
        
        # Analyze results
        result = tester.analyze_results(case["type"], task_data)
        results.append(result)
        
        # Log results
        logging.info(f"Completed {case['type']} test")
        logging.info(f"Missing operations: {result['missing_operations']}")
        logging.info(f"Extra operations: {result['extra_operations']}")
        logging.info(f"Sequence match: {result['sequence_match']['matches']}")
        logging.info(f"Error count: {result['error_handling']['error_count']}")
    
    # Generate report
    report = tester.generate_report(results)
    
    # Save report
    report_path = Path("ade_integration_report.md")
    report_path.write_text(report)
    logging.info(f"Report saved to {report_path}")
    
    # Assert test conditions
    for result in results:
        assert not result['missing_operations'], f"Missing operations in {result['prompt_type']}"
        assert result['sequence_match']['matches'], f"Operation sequence mismatch in {result['prompt_type']}"
        assert not result['error_handling']['has_errors'], f"Errors found in {result['prompt_type']}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 