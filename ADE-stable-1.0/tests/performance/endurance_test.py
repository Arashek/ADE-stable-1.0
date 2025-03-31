import asyncio
import logging
import time
import gc
import tracemalloc
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
import psutil
from .metrics import MetricsCollector, PerformanceReporter

logger = logging.getLogger(__name__)

class EnduranceTest:
    """Endurance testing module for long-running tests and memory leak detection."""
    
    def __init__(
        self,
        base_url: str,
        output_dir: str,
        baseline_file: Optional[str] = None,
        duration: int = 3600,  # 1 hour
        check_interval: int = 300,  # 5 minutes
        memory_threshold: float = 1000  # 1GB
    ):
        self.base_url = base_url
        self.output_dir = output_dir
        self.metrics = MetricsCollector(baseline_file)
        self.reporter = PerformanceReporter(self.metrics)
        self.duration = duration
        self.check_interval = check_interval
        self.memory_threshold = memory_threshold
        self.session: Optional[aiohttp.ClientSession] = None
        self.tasks: List[asyncio.Task] = []
        self.process = psutil.Process()
        self.start_time = None
        self.initial_memory = None
        
    async def setup(self) -> None:
        """Setup test environment."""
        self.session = aiohttp.ClientSession()
        self.start_time = time.time()
        self.initial_memory = self.process.memory_info().rss
        
        # Start memory tracking
        tracemalloc.start()
        
    async def teardown(self) -> None:
        """Cleanup test environment."""
        if self.session:
            await self.session.close()
        tracemalloc.stop()
        
    async def monitor_memory(self) -> None:
        """Monitor memory usage and detect leaks."""
        while True:
            # Get current memory usage
            current_memory = self.process.memory_info().rss / (1024 * 1024)  # MB
            memory_increase = current_memory - (self.initial_memory / (1024 * 1024))
            
            # Record memory metrics
            await self.metrics.record_metric(
                metric_type='memory_usage',
                value=current_memory,
                unit='MB'
            )
            
            await self.metrics.record_metric(
                metric_type='memory_increase',
                value=memory_increase,
                unit='MB'
            )
            
            # Check for memory leaks
            if memory_increase > self.memory_threshold:
                logger.warning(f"Potential memory leak detected: {memory_increase:.2f}MB increase")
                
                # Take memory snapshot
                snapshot = tracemalloc.take_snapshot()
                top_stats = snapshot.statistics('lineno')
                
                # Record leak information
                await self.metrics.record_metric(
                    metric_type='memory_leak',
                    value=memory_increase,
                    unit='MB',
                    metadata={
                        'top_stats': [str(stat) for stat in top_stats[:5]]
                    }
                )
                
            await asyncio.sleep(60)  # Check every minute
            
    async def monitor_system_health(self) -> None:
        """Monitor overall system health."""
        while True:
            # Record CPU usage
            cpu_percent = self.process.cpu_percent()
            await self.metrics.record_metric(
                metric_type='cpu_usage',
                value=cpu_percent,
                unit='%'
            )
            
            # Record thread count
            thread_count = self.process.num_threads()
            await self.metrics.record_metric(
                metric_type='thread_count',
                value=thread_count,
                unit='count'
            )
            
            # Record file descriptor count
            fd_count = self.process.num_fds()
            await self.metrics.record_metric(
                metric_type='fd_count',
                value=fd_count,
                unit='count'
            )
            
            await asyncio.sleep(60)
            
    async def run_continuous_operations(self) -> None:
        """Run continuous operations to test system stability."""
        while True:
            try:
                # Create and execute development plan
                plan_id = await self._create_plan()
                
                # Generate and execute tasks
                tasks = await self._get_tasks(plan_id)
                for task in tasks:
                    await self._execute_task(task['id'])
                    
                # Run tests
                await self._run_tests()
                
                # Check project status
                await self._check_status()
                
                # Clean up
                await self._cleanup_plan(plan_id)
                
                # Force garbage collection
                gc.collect()
                
            except Exception as e:
                logger.error(f"Error in continuous operations: {str(e)}")
                await self.metrics.record_metric(
                    metric_type='operation_error',
                    value=1,
                    unit='count',
                    metadata={'error': str(e)}
                )
                
    async def _create_plan(self) -> str:
        """Create a development plan."""
        if not self.session:
            raise Exception("Session not initialized")
            
        data = {
            "goal": "Endurance test plan",
            "complexity": "medium",
            "priority": "normal"
        }
        
        async with self.session.post(
            f"{self.base_url}/api/orchestrator/plan",
            json=data
        ) as response:
            if response.status != 201:
                raise Exception(f"Failed to create plan: {response.status}")
            return (await response.json())['id']
            
    async def _get_tasks(self, plan_id: str) -> List[Dict[str, Any]]:
        """Get tasks for a plan."""
        if not self.session:
            raise Exception("Session not initialized")
            
        async with self.session.get(
            f"{self.base_url}/api/orchestrator/plan/{plan_id}/tasks"
        ) as response:
            if response.status != 200:
                raise Exception(f"Failed to get tasks: {response.status}")
            return await response.json()
            
    async def _execute_task(self, task_id: str) -> None:
        """Execute a task."""
        if not self.session:
            raise Exception("Session not initialized")
            
        async with self.session.post(
            f"{self.base_url}/api/orchestrator/tasks/{task_id}/start"
        ) as response:
            if response.status != 200:
                raise Exception(f"Failed to execute task: {response.status}")
                
    async def _run_tests(self) -> None:
        """Run tests."""
        if not self.session:
            raise Exception("Session not initialized")
            
        async with self.session.post(
            f"{self.base_url}/api/testing/run"
        ) as response:
            if response.status != 200:
                raise Exception(f"Failed to run tests: {response.status}")
                
    async def _check_status(self) -> None:
        """Check project status."""
        if not self.session:
            raise Exception("Session not initialized")
            
        async with self.session.get(
            f"{self.base_url}/api/project/status"
        ) as response:
            if response.status != 200:
                raise Exception(f"Failed to check status: {response.status}")
                
    async def _cleanup_plan(self, plan_id: str) -> None:
        """Clean up a development plan."""
        if not self.session:
            raise Exception("Session not initialized")
            
        async with self.session.delete(
            f"{self.base_url}/api/orchestrator/plans/{plan_id}"
        ) as response:
            if response.status != 204:
                raise Exception(f"Failed to cleanup plan: {response.status}")
                
    async def run(self) -> None:
        """Run the endurance test."""
        try:
            await self.setup()
            
            # Start monitoring tasks
            monitor_tasks = [
                asyncio.create_task(self.monitor_memory()),
                asyncio.create_task(self.monitor_system_health())
            ]
            
            # Start continuous operations
            operations_task = asyncio.create_task(self.run_continuous_operations())
            
            # Run for specified duration
            await asyncio.sleep(self.duration)
            
            # Cancel all tasks
            for task in monitor_tasks + [operations_task]:
                task.cancel()
                
            # Generate report
            await self.reporter.generate_report(self.output_dir)
            
        except Exception as e:
            logger.error(f"Endurance test failed: {str(e)}")
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
        """Run an endurance test with the specified parameters."""
        test = cls(
            base_url=base_url,
            output_dir=output_dir,
            baseline_file=baseline_file,
            **kwargs
        )
        await test.run() 