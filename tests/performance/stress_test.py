import asyncio
import logging
import time
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
import psutil
from .metrics import MetricsCollector, PerformanceReporter

logger = logging.getLogger(__name__)

class StressTest:
    """Stress testing module for peak load simulation and error handling."""
    
    def __init__(
        self,
        base_url: str,
        output_dir: str,
        baseline_file: Optional[str] = None,
        max_concurrent_requests: int = 1000,
        request_timeout: float = 30.0,
        error_threshold: float = 0.1,  # 10%
        recovery_timeout: int = 300  # 5 minutes
    ):
        self.base_url = base_url
        self.output_dir = output_dir
        self.metrics = MetricsCollector(baseline_file)
        self.reporter = PerformanceReporter(self.metrics)
        self.max_concurrent_requests = max_concurrent_requests
        self.request_timeout = request_timeout
        self.error_threshold = error_threshold
        self.recovery_timeout = recovery_timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self.tasks: List[asyncio.Task] = []
        self.process = psutil.Process()
        self.error_count = 0
        self.total_requests = 0
        
    async def setup(self) -> None:
        """Setup test environment."""
        timeout = aiohttp.ClientTimeout(total=self.request_timeout)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
    async def teardown(self) -> None:
        """Cleanup test environment."""
        if self.session:
            await self.session.close()
            
    async def monitor_system_state(self) -> None:
        """Monitor system state during stress test."""
        while True:
            # Record CPU usage
            cpu_percent = self.process.cpu_percent()
            await self.metrics.record_metric(
                metric_type='cpu_usage',
                value=cpu_percent,
                unit='%'
            )
            
            # Record memory usage
            memory_info = self.process.memory_info()
            await self.metrics.record_metric(
                metric_type='memory_usage',
                value=memory_info.rss / (1024 * 1024),  # MB
                unit='MB'
            )
            
            # Record error rate
            if self.total_requests > 0:
                error_rate = self.error_count / self.total_requests
                await self.metrics.record_metric(
                    metric_type='error_rate',
                    value=error_rate * 100,  # Convert to percentage
                    unit='%'
                )
                
            await asyncio.sleep(1)
            
    async def generate_stress_load(self) -> None:
        """Generate stress load with increasing intensity."""
        # Start with a moderate load
        initial_load = self.max_concurrent_requests // 4
        current_load = initial_load
        
        while current_load <= self.max_concurrent_requests:
            logger.info(f"Generating load with {current_load} concurrent requests")
            
            # Create tasks for current load level
            tasks = []
            for _ in range(current_load):
                task = asyncio.create_task(self._make_stress_request())
                tasks.append(task)
                
            # Wait for all tasks to complete
            await asyncio.gather(*tasks)
            
            # Check error rate
            if self.total_requests > 0:
                error_rate = self.error_count / self.total_requests
                if error_rate > self.error_threshold:
                    logger.warning(f"Error rate {error_rate:.2%} exceeds threshold")
                    break
                    
            # Increase load
            current_load *= 2
            
            # Small delay between load levels
            await asyncio.sleep(5)
            
    async def _make_stress_request(self) -> None:
        """Make a stress test request."""
        if not self.session:
            return
            
        self.total_requests += 1
        start_time = time.time()
        
        try:
            # Randomly select an operation
            operations = [
                self._create_complex_plan,
                self._generate_large_code,
                self._run_heavy_tests,
                self._simulate_error_condition
            ]
            
            operation = random.choice(operations)
            await operation()
            
            # Record response time
            response_time = (time.time() - start_time) * 1000  # ms
            await self.metrics.record_metric(
                metric_type='response_time',
                value=response_time,
                unit='ms'
            )
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Stress request failed: {str(e)}")
            await self.metrics.record_metric(
                metric_type='error',
                value=1,
                unit='count',
                metadata={'error': str(e)}
            )
            
    async def _create_complex_plan(self) -> None:
        """Create a complex development plan."""
        if not self.session:
            return
            
        data = {
            "goal": "Complex stress test plan",
            "complexity": "high",
            "priority": "high",
            "tasks": [
                {
                    "name": f"Task {i}",
                    "type": "development",
                    "priority": "high",
                    "estimated_duration": random.randint(1, 10)
                }
                for i in range(10)
            ]
        }
        
        async with self.session.post(
            f"{self.base_url}/api/orchestrator/plan",
            json=data
        ) as response:
            if response.status != 201:
                raise Exception(f"Failed to create plan: {response.status}")
                
    async def _generate_large_code(self) -> None:
        """Generate a large amount of code."""
        if not self.session:
            return
            
        data = {
            "prompt": "Generate a complex system with multiple components",
            "language": "python",
            "size": "large",
            "complexity": "high"
        }
        
        async with self.session.post(
            f"{self.base_url}/api/providers/execute",
            json=data
        ) as response:
            if response.status != 200:
                raise Exception(f"Failed to generate code: {response.status}")
                
    async def _run_heavy_tests(self) -> None:
        """Run computationally intensive tests."""
        if not self.session:
            return
            
        data = {
            "test_type": "stress",
            "complexity": "high",
            "iterations": 1000
        }
        
        async with self.session.post(
            f"{self.base_url}/api/testing/run",
            json=data
        ) as response:
            if response.status != 200:
                raise Exception(f"Failed to run tests: {response.status}")
                
    async def _simulate_error_condition(self) -> None:
        """Simulate an error condition."""
        if not self.session:
            return
            
        # Randomly trigger error conditions
        if random.random() < 0.1:  # 10% chance
            data = {
                "operation": "error_test",
                "error_type": random.choice(["timeout", "validation", "resource"])
            }
            
            async with self.session.post(
                f"{self.base_url}/api/testing/error",
                json=data
            ) as response:
                if response.status != 400:  # Expected error
                    raise Exception(f"Unexpected response: {response.status}")
                    
    async def test_recovery(self) -> None:
        """Test system recovery after stress."""
        logger.info("Testing system recovery")
        
        # Wait for system to stabilize
        await asyncio.sleep(self.recovery_timeout)
        
        # Make a series of normal requests
        for _ in range(10):
            try:
                await self._create_complex_plan()
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Recovery test failed: {str(e)}")
                raise
                
    async def run(self) -> None:
        """Run the stress test."""
        try:
            await self.setup()
            
            # Start system monitoring
            monitor_task = asyncio.create_task(self.monitor_system_state())
            
            # Generate stress load
            await self.generate_stress_load()
            
            # Test recovery
            await self.test_recovery()
            
            # Cancel monitoring
            monitor_task.cancel()
            
            # Generate report
            await self.reporter.generate_report(self.output_dir)
            
        except Exception as e:
            logger.error(f"Stress test failed: {str(e)}")
            raise
        finally:
            await self.teardown()
            
    @classmethod
    async def run_test(
        cls,
        base_url: str,
        output_dir: str,
        baseline_file: Optional[str] = None,
        **kwargs
    ) -> None:
        """Run a stress test with the specified parameters."""
        test = cls(
            base_url=base_url,
            output_dir=output_dir,
            baseline_file=baseline_file,
            **kwargs
        )
        await test.run() 