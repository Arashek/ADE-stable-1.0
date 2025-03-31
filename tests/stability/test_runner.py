import os
import sys
import logging
import unittest
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

from .config import get_config
from .base_test import BaseStabilityTest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'stability_tests_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class TestResult:
    """Class to store test results."""
    def __init__(self, test_name: str, success: bool, duration: float, error: str = None):
        self.test_name = test_name
        self.success = success
        self.duration = duration
        self.error = error

class StabilityTestRunner:
    """Main class to run stability tests."""
    
    def __init__(self):
        self.config = get_config()
        self.results: List[TestResult] = []
        
    def discover_tests(self) -> List[BaseStabilityTest]:
        """Discover all test classes in the current directory."""
        test_classes = []
        current_dir = Path(__file__).parent
        
        for file in current_dir.glob('test_*.py'):
            if file.name == 'test_runner.py':
                continue
                
            module_name = f"tests.stability.{file.stem}"
            try:
                module = __import__(module_name, fromlist=['*'])
                for item in dir(module):
                    obj = getattr(module, item)
                    if (isinstance(obj, type) and 
                        issubclass(obj, BaseStabilityTest) and 
                        obj != BaseStabilityTest):
                        test_classes.append(obj(self.config))
            except Exception as e:
                logger.error(f"Error importing test module {module_name}: {str(e)}")
                
        return test_classes
    
    def run_test(self, test: BaseStabilityTest) -> TestResult:
        """Run a single test case."""
        start_time = datetime.now()
        success = False
        error = None
        
        try:
            logger.info(f"Setting up test: {test.__class__.__name__}")
            test.setup()
            
            logger.info(f"Running test: {test.__class__.__name__}")
            success = test.run()
            
            logger.info(f"Cleaning up test: {test.__class__.__name__}")
            test.teardown()
            
        except Exception as e:
            error = str(e)
            logger.error(f"Test {test.__class__.__name__} failed: {error}")
        finally:
            duration = (datetime.now() - start_time).total_seconds()
            return TestResult(test.__class__.__name__, success, duration, error)
    
    def generate_report(self) -> str:
        """Generate a summary report of test results."""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - successful_tests
        total_duration = sum(r.duration for r in self.results)
        
        report = [
            "\n=== Stability Test Report ===",
            f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"\nTotal Tests: {total_tests}",
            f"Successful: {successful_tests}",
            f"Failed: {failed_tests}",
            f"Total Duration: {total_duration:.2f} seconds",
            "\nDetailed Results:",
            "-" * 50
        ]
        
        for result in self.results:
            status = "✓" if result.success else "✗"
            report.append(f"{status} {result.test_name}")
            report.append(f"  Duration: {result.duration:.2f} seconds")
            if result.error:
                report.append(f"  Error: {result.error}")
            report.append("-" * 50)
            
        return "\n".join(report)
    
    def run(self) -> int:
        """Run all discovered tests and return appropriate exit code."""
        logger.info("Starting stability test suite")
        
        try:
            tests = self.discover_tests()
            if not tests:
                logger.warning("No tests discovered!")
                return 1
                
            logger.info(f"Discovered {len(tests)} test cases")
            
            for test in tests:
                result = self.run_test(test)
                self.results.append(result)
                
            # Generate and log report
            report = self.generate_report()
            logger.info(report)
            
            # Save report to file
            report_file = f'stability_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            with open(report_file, 'w') as f:
                f.write(report)
            logger.info(f"Report saved to {report_file}")
            
            # Return appropriate exit code
            return 0 if all(r.success for r in self.results) else 1
            
        except Exception as e:
            logger.error(f"Test runner failed: {str(e)}")
            return 1

def main():
    """Main entry point for the test runner."""
    runner = StabilityTestRunner()
    sys.exit(runner.run())

if __name__ == '__main__':
    main() 