import asyncio
import logging
import random
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
import psutil
from .metrics import MetricsCollector, PerformanceReporter

logger = logging.getLogger(__name__)

class LoadTest:
    """Load testing module for simulating concurrent users and monitoring performance."""
    
    def __init__(
        self,
        base_url: str,
        output_dir: str,
        baseline_file: Optional[str] = None,
        max_concurrent_users: int = 100,
        ramp_up_time: int = 300,  # 5 minutes
        steady_state_time: int = 600,  # 10 minutes
        ramp_down_time: int = 300  # 5 minutes
    ):
        self.base_url = base_url
        self.output_dir = output_dir
        self.metrics = MetricsCollector(baseline_file)
        self.reporter = PerformanceReporter(self.metrics)
        self.max_concurrent_users = max_concurrent_users
        self.ramp_up_time = ramp_up_time
        self.steady_state_time = steady_state_time
        self.ramp_down_time = ramp_down_time
        self.session: Optional[aiohttp.ClientSession] = None
        self.tasks: List[asyncio.Task] = []
        self.process = psutil.Process()
        
    async def setup(self) -> None:
        """Setup test environment."""
        self.session = aiohttp.ClientSession()
        
    async def teardown(self) -> None:
        """Cleanup test environment."""
        if self.session:
            await self.session.close()
            
    async def monitor_resources(self) -> None:
        """Monitor system resource usage."""
        while True:
            # Record memory usage
            memory_info = self.process.memory_info()
            await self.metrics.record_metric(
                metric_type='memory_usage',
                value=memory_info.rss / (1024 * 1024),  # Convert to MB
                unit='MB'
            )
            
            # Record CPU usage
            cpu_percent = self.process.cpu_percent()
            await self.metrics.record_metric(
                metric_type='cpu_usage',
                value=cpu_percent,
                unit='%'
            )
            
            await asyncio.sleep(1)
            
    async def simulate_user(self, user_id: int) -> None:
        """Simulate a single user's behavior."""
        if not self.session:
            return
            
        while True:
            try:
                # Simulate user actions
                actions = [
                    self._create_development_plan,
                    self._execute_code_generation,
                    self._run_tests,
                    self._check_project_status
                ]
                
                action = random.choice(actions)
                start_time = time.time()
                
                await action()
                
                # Record response time
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                await self.metrics.record_metric(
                    metric_type='response_time',
                    value=response_time,
                    unit='ms',
                    metadata={'user_id': user_id}
                )
                
                # Random delay between actions
                await asyncio.sleep(random.uniform(1, 5))
                
            except Exception as e:
                logger.error(f"Error in user simulation: {str(e)}")
                await self.metrics.record_metric(
                    metric_type='error_rate',
                    value=1,
                    unit='count',
                    metadata={'user_id': user_id, 'error': str(e)}
                )
                
    async def _create_development_plan(self) -> None:
        """Simulate creating a development plan."""
        if not self.session:
            return
            
        data = {
            "goal": "Implement new feature",
            "complexity": "medium",
            "priority": "high"
        }
        
        async with self.session.post(
            f"{self.base_url}/api/orchestrator/plan",
            json=data
        ) as response:
            if response.status != 201:
                raise Exception(f"Failed to create plan: {response.status}")
                
    async def _execute_code_generation(self) -> None:
        """Simulate code generation request."""
        if not self.session:
            return
            
        data = {
            "prompt": "Generate a simple function",
            "language": "python"
        }
        
        async with self.session.post(
            f"{self.base_url}/api/providers/execute",
            json=data
        ) as response:
            if response.status != 200:
                raise Exception(f"Failed to generate code: {response.status}")
                
    async def _run_tests(self) -> None:
        """Simulate running tests."""
        if not self.session:
            return
            
        async with self.session.post(
            f"{self.base_url}/api/testing/run"
        ) as response:
            if response.status != 200:
                raise Exception(f"Failed to run tests: {response.status}")
                
    async def _check_project_status(self) -> None:
        """Simulate checking project status."""
        if not self.session:
            return
            
        async with self.session.get(
            f"{self.base_url}/api/project/status"
        ) as response:
            if response.status != 200:
                raise Exception(f"Failed to check status: {response.status}")
                
    async def ramp_up_users(self) -> None:
        """Gradually increase the number of concurrent users."""
        step_size = self.max_concurrent_users // (self.ramp_up_time // 10)
        current_users = 0
        
        while current_users < self.max_concurrent_users:
            # Add new users
            for _ in range(step_size):
                if current_users >= self.max_concurrent_users:
                    break
                    
                user_id = current_users + 1
                task = asyncio.create_task(self.simulate_user(user_id))
                self.tasks.append(task)
                
                # Record current number of users
                await self.metrics.record_metric(
                    metric_type='concurrent_users',
                    value=user_id,
                    unit='count'
                )
                
                current_users += 1
                
            await asyncio.sleep(10)
            
    async def ramp_down_users(self) -> None:
        """Gradually decrease the number of concurrent users."""
        step_size = len(self.tasks) // (self.ramp_down_time // 10)
        
        while self.tasks:
            # Remove users
            for _ in range(step_size):
                if not self.tasks:
                    break
                    
                task = self.tasks.pop()
                task.cancel()
                
                # Record current number of users
                await self.metrics.record_metric(
                    metric_type='concurrent_users',
                    value=len(self.tasks),
                    unit='count'
                )
                
            await asyncio.sleep(10)
            
    async def run(self) -> None:
        """Run the load test."""
        try:
            await self.setup()
            
            # Start resource monitoring
            monitor_task = asyncio.create_task(self.monitor_resources())
            
            # Ramp up users
            logger.info("Starting user ramp-up")
            await self.ramp_up_users()
            
            # Steady state
            logger.info("Starting steady state")
            await asyncio.sleep(self.steady_state_time)
            
            # Ramp down users
            logger.info("Starting user ramp-down")
            await self.ramp_down_users()
            
            # Cancel monitoring
            monitor_task.cancel()
            
            # Generate report
            logger.info("Generating performance report")
            await self.reporter.generate_report(self.output_dir)
            
        except Exception as e:
            logger.error(f"Load test failed: {str(e)}")
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
        """Run a load test with the specified parameters."""
        test = cls(
            base_url=base_url,
            output_dir=output_dir,
            baseline_file=baseline_file,
            **kwargs
        )
        await test.run() 