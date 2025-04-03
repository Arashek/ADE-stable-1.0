#!/usr/bin/env python
"""
End-to-End Tests for ADE Platform

This script runs comprehensive end-to-end tests for the ADE platform,
focusing on the prompt-to-application generation workflow.
"""

import os
import sys
import json
import time
import logging
import requests
import unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import ADE modules
from scripts.basic_error_logging import log_error, ErrorCategory, ErrorSeverity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# API configuration
API_URL = "http://localhost:8000"
HEALTH_CHECK_ENDPOINT = f"{API_URL}/health"
PROMPT_ENDPOINT = f"{API_URL}/api/prompt"
ERROR_LOG_ENDPOINT = f"{API_URL}/api/errors"

# Test data
TEST_PROMPTS = [
    {
        "name": "simple_calculator",
        "prompt": "Create a simple calculator app that can add, subtract, multiply and divide numbers.",
        "expected_components": ["input", "buttons", "display", "operations"]
    },
    {
        "name": "todo_list",
        "prompt": "Create a todo list application with the ability to add, remove, and mark tasks as complete.",
        "expected_components": ["task_list", "add_form", "task_item", "toggle_completion"]
    },
    {
        "name": "weather_app",
        "prompt": "Create a weather application that shows current weather and forecast.",
        "expected_components": ["current_weather", "forecast", "location_search"]
    }
]

class ADEEndToEndTests(unittest.TestCase):
    """End-to-end tests for the ADE platform"""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment"""
        logger.info("Setting up end-to-end tests")
        
        # Check if the API is running
        cls._check_api_availability()
        
        # Initialize test results
        cls.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": [],
            "prompt_results": []
        }
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after tests"""
        logger.info("Cleaning up after end-to-end tests")
        
        # Log summary
        logger.info(f"Tests passed: {cls.test_results['passed']}")
        logger.info(f"Tests failed: {cls.test_results['failed']}")
        
        # Save results to file
        results_dir = Path(__file__).resolve().parent / "results"
        results_dir.mkdir(exist_ok=True)
        
        results_file = results_dir / f"e2e_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(cls.test_results, f, indent=2)
        
        logger.info(f"Test results saved to {results_file}")
    
    @classmethod
    def _check_api_availability(cls):
        """Check if the API is available"""
        try:
            response = requests.get(HEALTH_CHECK_ENDPOINT, timeout=5)
            response.raise_for_status()
            logger.info("API is available")
        except Exception as e:
            logger.error(f"API is not available: {str(e)}")
            raise unittest.SkipTest("API is not available")
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = requests.get(HEALTH_CHECK_ENDPOINT)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        
        logger.info("Health check test passed")
    
    def test_error_logging(self):
        """Test the error logging system"""
        test_error = {
            "message": "Test error from E2E tests",
            "category": ErrorCategory.SYSTEM,
            "severity": ErrorSeverity.INFO,
            "component": "e2e_tests.py",
            "context": {"test_name": "test_error_logging"},
            "stack_trace": None
        }
        
        # Log via API
        response = requests.post(ERROR_LOG_ENDPOINT, json=test_error)
        self.assertEqual(response.status_code, 200)
        
        # Log via module
        log_error(
            test_error["message"],
            test_error["category"],
            test_error["severity"],
            test_error["component"],
            test_error["context"]
        )
        
        logger.info("Error logging test passed")
    
    def test_prompt_submission(self):
        """Test submitting a prompt"""
        prompt_data = {
            "prompt": "Create a hello world application",
            "context": {"test": True}
        }
        
        response = requests.post(PROMPT_ENDPOINT, json=prompt_data)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("task_id", data)
        self.assertIn("status", data)
        
        logger.info(f"Prompt submission test passed. Task ID: {data['task_id']}")
        
        # Check status
        status_response = requests.get(f"{PROMPT_ENDPOINT}/{data['task_id']}")
        self.assertEqual(status_response.status_code, 200)
        
        logger.info("Prompt status check test passed")
    
    def test_multiple_prompt_processing(self):
        """Test processing multiple prompts in parallel"""
        results = []
        
        with ThreadPoolExecutor(max_workers=len(TEST_PROMPTS)) as executor:
            # Submit all prompts in parallel
            futures = {
                executor.submit(self._process_prompt, prompt): prompt["name"]
                for prompt in TEST_PROMPTS
            }
            
            # Collect results as they complete
            for future in futures:
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"Completed processing prompt: {futures[future]}")
                except Exception as e:
                    prompt_name = futures[future]
                    error_msg = f"Error processing prompt {prompt_name}: {str(e)}"
                    logger.error(error_msg)
                    
                    # Log error
                    log_error(
                        error_msg,
                        ErrorCategory.SYSTEM,
                        ErrorSeverity.ERROR,
                        "e2e_tests.py",
                        {"prompt_name": prompt_name}
                    )
                    
                    # Add to results
                    results.append({
                        "name": prompt_name,
                        "success": False,
                        "error": str(e)
                    })
        
        # Add results to test_results
        self.test_results["prompt_results"].extend(results)
        
        # Count successes and failures
        successes = sum(1 for r in results if r.get("success", False))
        failures = len(results) - successes
        
        self.test_results["passed"] += successes
        self.test_results["failed"] += failures
        
        logger.info(f"Multiple prompt test completed: {successes} succeeded, {failures} failed")
        
        # Assert that at least half of the prompts were successful
        self.assertGreaterEqual(successes, len(TEST_PROMPTS) / 2)
    
    def _process_prompt(self, prompt_data):
        """Process a single prompt and validate the result"""
        result = {
            "name": prompt_data["name"],
            "prompt": prompt_data["prompt"],
            "success": False,
            "task_id": None,
            "processing_time": 0
        }
        
        start_time = time.time()
        
        try:
            # Submit prompt
            submission_response = requests.post(PROMPT_ENDPOINT, json={
                "prompt": prompt_data["prompt"],
                "context": {"test": True, "expected_components": prompt_data["expected_components"]}
            })
            
            submission_response.raise_for_status()
            data = submission_response.json()
            task_id = data["task_id"]
            result["task_id"] = task_id
            
            # Poll for completion
            max_attempts = 30
            for attempt in range(max_attempts):
                status_response = requests.get(f"{PROMPT_ENDPOINT}/{task_id}")
                status_response.raise_for_status()
                status_data = status_response.json()
                
                if status_data["status"] in ["completed", "failed"]:
                    break
                
                time.sleep(2)  # Wait 2 seconds between polls
            
            # Check final status
            final_status_response = requests.get(f"{PROMPT_ENDPOINT}/{task_id}")
            final_status_response.raise_for_status()
            final_status = final_status_response.json()
            
            # Validate result
            result["status"] = final_status["status"]
            result["processing_time"] = time.time() - start_time
            
            if final_status["status"] == "completed":
                result["success"] = True
                result["result"] = final_status.get("result", {})
            else:
                result["error"] = final_status.get("message", "Unknown error")
        
        except Exception as e:
            result["error"] = str(e)
            result["processing_time"] = time.time() - start_time
        
        return result

def run_tests():
    """Run the end-to-end tests"""
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

if __name__ == "__main__":
    run_tests()
