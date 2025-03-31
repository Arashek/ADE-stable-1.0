import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class TestResult:
    """Represents a single test result"""
    test_name: str
    category: str
    status: str  # "passed", "failed", "skipped"
    duration: float
    timestamp: datetime
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    metadata: Dict[str, Any] = None

class ResultsCollector:
    """Collects and processes test results"""
    
    def __init__(self, results_dir: str = "test_results"):
        """
        Initialize the results collector
        
        Args:
            results_dir: Directory to store test results
        """
        self.results_dir = results_dir
        self.results: List[TestResult] = []
        self._ensure_results_dir()
    
    def _ensure_results_dir(self):
        """Ensure the results directory exists"""
        os.makedirs(self.results_dir, exist_ok=True)
    
    def add_result(self, result: TestResult):
        """
        Add a test result
        
        Args:
            result: TestResult object to add
        """
        self.results.append(result)
        self._save_result(result)
    
    def _save_result(self, result: TestResult):
        """Save a result to disk"""
        filename = f"{result.timestamp.strftime('%Y%m%d_%H%M%S')}_{result.test_name}.json"
        filepath = os.path.join(self.results_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump({
                "test_name": result.test_name,
                "category": result.category,
                "status": result.status,
                "duration": result.duration,
                "timestamp": result.timestamp.isoformat(),
                "error_message": result.error_message,
                "stack_trace": result.stack_trace,
                "metadata": result.metadata
            }, f)
    
    def load_results(self):
        """Load all results from disk"""
        self.results = []
        for filename in os.listdir(self.results_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.results_dir, filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    self.results.append(TestResult(
                        test_name=data["test_name"],
                        category=data["category"],
                        status=data["status"],
                        duration=data["duration"],
                        timestamp=datetime.fromisoformat(data["timestamp"]),
                        error_message=data.get("error_message"),
                        stack_trace=data.get("stack_trace"),
                        metadata=data.get("metadata")
                    ))
    
    def get_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get summary statistics for the last N days
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary containing summary statistics
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_results = [r for r in self.results if r.timestamp >= cutoff_date]
        
        if not recent_results:
            return {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "success_rate": 0,
                "avg_duration": 0,
                "categories": {}
            }
        
        # Calculate basic statistics
        total_tests = len(recent_results)
        passed = sum(1 for r in recent_results if r.status == "passed")
        failed = sum(1 for r in recent_results if r.status == "failed")
        skipped = sum(1 for r in recent_results if r.status == "skipped")
        
        # Calculate success rate
        success_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
        
        # Calculate average duration
        avg_duration = sum(r.duration for r in recent_results) / total_tests
        
        # Calculate statistics by category
        categories = defaultdict(lambda: {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "success_rate": 0,
            "avg_duration": 0
        })
        
        for result in recent_results:
            cat = categories[result.category]
            cat["total"] += 1
            cat[result.status] += 1
            cat["avg_duration"] += result.duration
        
        # Calculate category-specific rates
        for cat in categories.values():
            cat["success_rate"] = (cat["passed"] / cat["total"]) * 100
            cat["avg_duration"] /= cat["total"]
        
        return {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "success_rate": success_rate,
            "avg_duration": avg_duration,
            "categories": dict(categories)
        }
    
    def get_trends(self, days: int = 7) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get test result trends over time
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary containing trend data
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_results = [r for r in self.results if r.timestamp >= cutoff_date]
        
        # Group results by date
        daily_results = defaultdict(list)
        for result in recent_results:
            date = result.timestamp.date()
            daily_results[date].append(result)
        
        # Calculate daily statistics
        trends = []
        for date in sorted(daily_results.keys()):
            day_results = daily_results[date]
            total = len(day_results)
            passed = sum(1 for r in day_results if r.status == "passed")
            failed = sum(1 for r in day_results if r.status == "failed")
            skipped = sum(1 for r in day_results if r.status == "skipped")
            
            trends.append({
                "date": date.isoformat(),
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "success_rate": (passed / total) * 100 if total > 0 else 0,
                "avg_duration": sum(r.duration for r in day_results) / total if total > 0 else 0
            })
        
        return {"daily": trends}
    
    def get_failures(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get detailed information about test failures
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of failure details
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_failures = [
            r for r in self.results
            if r.timestamp >= cutoff_date and r.status == "failed"
        ]
        
        # Group failures by test name
        failure_groups = defaultdict(list)
        for failure in recent_failures:
            failure_groups[failure.test_name].append(failure)
        
        # Calculate failure statistics
        failures = []
        for test_name, test_failures in failure_groups.items():
            failures.append({
                "test_name": test_name,
                "category": test_failures[0].category,
                "total_failures": len(test_failures),
                "latest_failure": max(f.timestamp for f in test_failures).isoformat(),
                "error_message": test_failures[-1].error_message,
                "stack_trace": test_failures[-1].stack_trace
            })
        
        return sorted(failures, key=lambda x: x["total_failures"], reverse=True)
    
    def get_performance_metrics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get performance metrics for tests
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary containing performance metrics
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_results = [r for r in self.results if r.timestamp >= cutoff_date]
        
        # Calculate duration statistics
        durations = [r.duration for r in recent_results]
        if not durations:
            return {
                "min_duration": 0,
                "max_duration": 0,
                "avg_duration": 0,
                "p95_duration": 0,
                "slow_tests": []
            }
        
        durations.sort()
        p95_index = int(len(durations) * 0.95)
        
        # Find slow tests (top 5%)
        slow_tests = []
        for result in recent_results:
            if result.duration >= durations[p95_index]:
                slow_tests.append({
                    "test_name": result.test_name,
                    "category": result.category,
                    "duration": result.duration,
                    "timestamp": result.timestamp.isoformat()
                })
        
        return {
            "min_duration": min(durations),
            "max_duration": max(durations),
            "avg_duration": sum(durations) / len(durations),
            "p95_duration": durations[p95_index],
            "slow_tests": sorted(slow_tests, key=lambda x: x["duration"], reverse=True)
        } 