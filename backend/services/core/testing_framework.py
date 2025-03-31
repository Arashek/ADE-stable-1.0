from typing import Dict, List, Any, Optional, Callable
import logging
import asyncio
from datetime import datetime, timedelta
import pytest
import coverage
from pathlib import Path
import json

from .monitoring import MonitoringService

logger = logging.getLogger(__name__)

class TestCase:
    """Represents a single test case"""
    def __init__(
        self,
        name: str,
        test_type: str,
        test_code: str,
        expected_result: Any,
        setup: Optional[str] = None,
        teardown: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.name = name
        self.type = test_type
        self.test_code = test_code
        self.expected_result = expected_result
        self.setup = setup
        self.teardown = teardown
        self.metadata = metadata or {}
        self.results: List[Dict[str, Any]] = []
        
class TestSuite:
    """Collection of related test cases"""
    def __init__(
        self,
        name: str,
        description: str,
        test_types: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = f"suite_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.name = name
        self.description = description
        self.test_types = test_types
        self.metadata = metadata or {}
        self.test_cases: List[TestCase] = []
        self.results: List[Dict[str, Any]] = []
        
class TestingFramework:
    """Framework for managing and executing tests"""
    
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.monitoring = MonitoringService()
        self.test_suites: Dict[str, TestSuite] = {}
        self.coverage = coverage.Coverage()
        
    async def create_test_suite(
        self,
        name: str,
        description: str,
        test_types: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> TestSuite:
        """Create a new test suite"""
        suite = TestSuite(name, description, test_types, metadata)
        self.test_suites[suite.id] = suite
        return suite
        
    async def add_test_case(
        self,
        suite_id: str,
        name: str,
        test_type: str,
        test_code: str,
        expected_result: Any,
        setup: Optional[str] = None,
        teardown: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TestCase:
        """Add a test case to a suite"""
        suite = self.test_suites.get(suite_id)
        if not suite:
            raise ValueError(f"Test suite {suite_id} not found")
            
        test_case = TestCase(
            name=name,
            test_type=test_type,
            test_code=test_code,
            expected_result=expected_result,
            setup=setup,
            teardown=teardown,
            metadata=metadata
        )
        
        suite.test_cases.append(test_case)
        return test_case
        
    async def run_test_suite(
        self,
        suite_id: str,
        parallel: bool = True
    ) -> Dict[str, Any]:
        """Run all tests in a suite"""
        suite = self.test_suites.get(suite_id)
        if not suite:
            raise ValueError(f"Test suite {suite_id} not found")
            
        start_time = datetime.now()
        
        try:
            # Start coverage
            self.coverage.start()
            
            # Run tests
            if parallel:
                results = await self._run_parallel(suite.test_cases)
            else:
                results = await self._run_sequential(suite.test_cases)
                
            # Stop coverage
            self.coverage.stop()
            self.coverage.save()
            
            # Calculate coverage
            coverage_data = self.coverage.get_data()
            coverage_report = self.coverage.report(show_missing=True)
            
            # Record results
            duration = (datetime.now() - start_time).total_seconds()
            suite_result = {
                'suite_id': suite_id,
                'timestamp': datetime.now().isoformat(),
                'duration': duration,
                'total_tests': len(suite.test_cases),
                'passed': len([r for r in results if r['status'] == 'passed']),
                'failed': len([r for r in results if r['status'] == 'failed']),
                'skipped': len([r for r in results if r['status'] == 'skipped']),
                'coverage': coverage_report,
                'results': results
            }
            
            suite.results.append(suite_result)
            
            # Record metrics
            self.monitoring.record_performance_metric(
                category='testing',
                name='suite_duration',
                value=duration,
                tags={'suite_id': suite_id}
            )
            
            return suite_result
            
        except Exception as e:
            logger.error(f"Error running test suite {suite_id}: {str(e)}")
            self.monitoring.record_error(
                error_id=f'test_suite_{suite_id}',
                error=str(e),
                context={'suite': suite.name}
            )
            raise
            
    async def _run_parallel(self, test_cases: List[TestCase]) -> List[Dict[str, Any]]:
        """Run test cases in parallel"""
        tasks = []
        for test in test_cases:
            task = asyncio.create_task(self._run_test_case(test))
            tasks.append(task)
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]
        
    async def _run_sequential(self, test_cases: List[TestCase]) -> List[Dict[str, Any]]:
        """Run test cases sequentially"""
        results = []
        for test in test_cases:
            try:
                result = await self._run_test_case(test)
                results.append(result)
            except Exception as e:
                logger.error(f"Error running test {test.name}: {str(e)}")
                results.append({
                    'test_id': test.id,
                    'status': 'failed',
                    'error': str(e)
                })
        return results
        
    async def _run_test_case(self, test: TestCase) -> Dict[str, Any]:
        """Run a single test case"""
        start_time = datetime.now()
        
        try:
            # Run setup if provided
            if test.setup:
                exec(test.setup)
                
            # Run test
            actual_result = await self._execute_test(test.test_code)
            
            # Compare results
            passed = self._compare_results(actual_result, test.expected_result)
            
            # Run teardown if provided
            if test.teardown:
                exec(test.teardown)
                
            # Record result
            duration = (datetime.now() - start_time).total_seconds()
            result = {
                'test_id': test.id,
                'name': test.name,
                'status': 'passed' if passed else 'failed',
                'duration': duration,
                'expected': test.expected_result,
                'actual': actual_result
            }
            
            test.results.append(result)
            
            # Record metrics
            self.monitoring.record_performance_metric(
                category='testing',
                name='test_duration',
                value=duration,
                tags={'test_id': test.id}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in test {test.name}: {str(e)}")
            return {
                'test_id': test.id,
                'name': test.name,
                'status': 'failed',
                'error': str(e)
            }
            
    async def _execute_test(self, test_code: str) -> Any:
        """Execute test code and return result"""
        try:
            # Create test environment
            test_globals = {}
            test_locals = {}
            
            # Execute test code
            exec(test_code, test_globals, test_locals)
            
            # Return result if specified
            return test_locals.get('result')
            
        except Exception as e:
            logger.error(f"Error executing test: {str(e)}")
            raise
            
    def _compare_results(self, actual: Any, expected: Any) -> bool:
        """Compare test results"""
        try:
            if isinstance(expected, dict):
                return all(
                    actual.get(k) == v
                    for k, v in expected.items()
                )
            return actual == expected
        except Exception:
            return False
            
    def get_test_report(
        self,
        suite_id: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """Generate test report"""
        cutoff = datetime.now() - timedelta(days=days)
        
        if suite_id:
            suite = self.test_suites.get(suite_id)
            if not suite:
                raise ValueError(f"Test suite {suite_id} not found")
            suites = [suite]
        else:
            suites = list(self.test_suites.values())
            
        report = {
            'timestamp': datetime.now().isoformat(),
            'period_days': days,
            'suites': []
        }
        
        for suite in suites:
            recent_results = [
                r for r in suite.results
                if datetime.fromisoformat(r['timestamp']) >= cutoff
            ]
            
            if recent_results:
                suite_report = {
                    'suite_id': suite.id,
                    'name': suite.name,
                    'total_runs': len(recent_results),
                    'avg_duration': sum(r['duration'] for r in recent_results) / len(recent_results),
                    'pass_rate': sum(1 for r in recent_results if r['passed'] == r['total_tests']) / len(recent_results),
                    'last_run': max(recent_results, key=lambda r: r['timestamp'])
                }
                report['suites'].append(suite_report)
                
        return report
