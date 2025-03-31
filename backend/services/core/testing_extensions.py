from typing import Dict, List, Any, Optional, Callable
import logging
import asyncio
from datetime import datetime
import pytest
import coverage
from pathlib import Path
import json
import aiohttp
import docker
from unittest.mock import MagicMock, patch

from .monitoring import MonitoringService
from .testing_framework import TestCase, TestSuite

logger = logging.getLogger(__name__)

class IntegrationTest(TestCase):
    """Extended test case for integration testing"""
    
    def __init__(
        self,
        name: str,
        components: List[str],
        setup_steps: List[str],
        test_steps: List[str],
        cleanup_steps: List[str],
        expected_result: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            name=name,
            test_type='integration',
            test_code='\n'.join(test_steps),
            expected_result=expected_result,
            setup='\n'.join(setup_steps),
            teardown='\n'.join(cleanup_steps),
            metadata=metadata
        )
        self.components = components

class LoadTest(TestCase):
    """Test case for load testing"""
    
    def __init__(
        self,
        name: str,
        endpoint: str,
        method: str,
        payload: Optional[Dict[str, Any]],
        concurrent_users: int,
        duration_seconds: int,
        expected_result: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            name=name,
            test_type='load',
            test_code=self._generate_load_test(
                endpoint, method, payload,
                concurrent_users, duration_seconds
            ),
            expected_result=expected_result,
            metadata=metadata
        )
        
    def _generate_load_test(
        self,
        endpoint: str,
        method: str,
        payload: Optional[Dict[str, Any]],
        concurrent_users: int,
        duration_seconds: int
    ) -> str:
        """Generate load test code"""
        return f"""
async def run_load_test():
    async with aiohttp.ClientSession() as session:
        tasks = []
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < {duration_seconds}:
            for _ in range({concurrent_users}):
                tasks.append(
                    session.{method.lower()}(
                        '{endpoint}',
                        json={json.dumps(payload) if payload else None}
                    )
                )
            
            responses = await asyncio.gather(*tasks)
            tasks.clear()
            
            # Record metrics
            for resp in responses:
                result['requests'] += 1
                result['latencies'].append(resp.elapsed.total_seconds())
                if resp.status == 200:
                    result['successes'] += 1
                else:
                    result['failures'] += 1
                    
result = {{
    'requests': 0,
    'successes': 0,
    'failures': 0,
    'latencies': []
}}

asyncio.run(run_load_test())
"""

class SecurityTest(TestCase):
    """Test case for security testing"""
    
    def __init__(
        self,
        name: str,
        target: str,
        test_type: str,
        payload: Any,
        expected_result: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            name=name,
            test_type='security',
            test_code=self._generate_security_test(
                target, test_type, payload
            ),
            expected_result=expected_result,
            metadata=metadata
        )
        
    def _generate_security_test(
        self,
        target: str,
        test_type: str,
        payload: Any
    ) -> str:
        """Generate security test code"""
        if test_type == 'sql_injection':
            return self._generate_sql_injection_test(target, payload)
        elif test_type == 'xss':
            return self._generate_xss_test(target, payload)
        elif test_type == 'csrf':
            return self._generate_csrf_test(target, payload)
        else:
            raise ValueError(f"Unknown security test type: {test_type}")
            
    def _generate_sql_injection_test(self, target: str, payload: str) -> str:
        return f"""
async def test_sql_injection():
    async with aiohttp.ClientSession() as session:
        response = await session.post(
            '{target}',
            json={{'query': '{payload}'}}
        )
        
        result['status'] = response.status
        result['body'] = await response.text()
        
result = {{}}
asyncio.run(test_sql_injection())
"""
    
    def _generate_xss_test(self, target: str, payload: str) -> str:
        return f"""
async def test_xss():
    async with aiohttp.ClientSession() as session:
        response = await session.post(
            '{target}',
            json={{'content': '{payload}'}}
        )
        
        result['status'] = response.status
        result['body'] = await response.text()
        
result = {{}}
asyncio.run(test_xss())
"""
    
    def _generate_csrf_test(self, target: str, payload: Dict[str, Any]) -> str:
        return f"""
async def test_csrf():
    async with aiohttp.ClientSession() as session:
        # First request to get CSRF token
        response = await session.get('{target}')
        csrf_token = response.cookies.get('csrf_token')
        
        # Second request without CSRF token
        response = await session.post(
            '{target}',
            json={json.dumps(payload)},
            headers={{'X-CSRF-Token': 'invalid'}}
        )
        
        result['status'] = response.status
        result['body'] = await response.text()
        
result = {{}}
asyncio.run(test_csrf())
"""

class TestingExtensions:
    """Extensions for the testing framework"""
    
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.monitoring = MonitoringService()
        self.docker_client = docker.from_env()
        
    async def create_integration_suite(
        self,
        name: str,
        components: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> TestSuite:
        """Create an integration test suite"""
        suite = TestSuite(
            name=name,
            description=f"Integration tests for {', '.join(components)}",
            test_types=['integration'],
            metadata=metadata
        )
        
        # Generate test cases based on component interactions
        for i, comp1 in enumerate(components):
            for comp2 in components[i+1:]:
                test = IntegrationTest(
                    name=f"test_{comp1}_{comp2}_integration",
                    components=[comp1, comp2],
                    setup_steps=[
                        f"# Set up {comp1}",
                        f"comp1 = setup_{comp1}()",
                        f"# Set up {comp2}",
                        f"comp2 = setup_{comp2}()"
                    ],
                    test_steps=[
                        f"# Test interaction between {comp1} and {comp2}",
                        f"result = test_{comp1}_{comp2}_interaction(comp1, comp2)"
                    ],
                    cleanup_steps=[
                        f"# Clean up {comp2}",
                        f"cleanup_{comp2}(comp2)",
                        f"# Clean up {comp1}",
                        f"cleanup_{comp1}(comp1)"
                    ],
                    expected_result={'status': 'success'},
                    metadata={'components': [comp1, comp2]}
                )
                suite.test_cases.append(test)
                
        return suite
        
    async def create_load_suite(
        self,
        name: str,
        endpoints: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> TestSuite:
        """Create a load test suite"""
        suite = TestSuite(
            name=name,
            description="Load tests for API endpoints",
            test_types=['load'],
            metadata=metadata
        )
        
        for endpoint in endpoints:
            test = LoadTest(
                name=f"load_test_{endpoint['path']}",
                endpoint=endpoint['path'],
                method=endpoint['method'],
                payload=endpoint.get('payload'),
                concurrent_users=endpoint.get('users', 10),
                duration_seconds=endpoint.get('duration', 60),
                expected_result={
                    'min_rps': endpoint.get('min_rps', 1),
                    'max_latency': endpoint.get('max_latency', 1.0),
                    'success_rate': endpoint.get('success_rate', 0.95)
                },
                metadata={'endpoint': endpoint['path']}
            )
            suite.test_cases.append(test)
            
        return suite
        
    async def create_security_suite(
        self,
        name: str,
        targets: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> TestSuite:
        """Create a security test suite"""
        suite = TestSuite(
            name=name,
            description="Security tests for application",
            test_types=['security'],
            metadata=metadata
        )
        
        for target in targets:
            # SQL Injection tests
            if target.get('sql_injection'):
                test = SecurityTest(
                    name=f"sql_injection_{target['path']}",
                    target=target['path'],
                    test_type='sql_injection',
                    payload="' OR '1'='1",
                    expected_result={'status': 400},
                    metadata={'type': 'sql_injection'}
                )
                suite.test_cases.append(test)
                
            # XSS tests
            if target.get('xss'):
                test = SecurityTest(
                    name=f"xss_{target['path']}",
                    target=target['path'],
                    test_type='xss',
                    payload="<script>alert('xss')</script>",
                    expected_result={'status': 400},
                    metadata={'type': 'xss'}
                )
                suite.test_cases.append(test)
                
            # CSRF tests
            if target.get('csrf'):
                test = SecurityTest(
                    name=f"csrf_{target['path']}",
                    target=target['path'],
                    test_type='csrf',
                    payload={'action': 'update'},
                    expected_result={'status': 403},
                    metadata={'type': 'csrf'}
                )
                suite.test_cases.append(test)
                
        return suite
        
    async def mock_dependencies(
        self,
        dependencies: List[Dict[str, Any]]
    ) -> List[MagicMock]:
        """Create mocks for external dependencies"""
        mocks = []
        
        for dep in dependencies:
            mock = MagicMock()
            
            # Configure mock behavior
            if 'return_value' in dep:
                mock.return_value = dep['return_value']
            if 'side_effect' in dep:
                mock.side_effect = dep['side_effect']
                
            # Apply mock
            with patch(dep['target'], mock):
                mocks.append(mock)
                
        return mocks
        
    async def setup_test_environment(
        self,
        services: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Set up test environment with required services"""
        containers = {}
        
        try:
            for service in services:
                # Start Docker container
                container = self.docker_client.containers.run(
                    image=service['image'],
                    name=service['name'],
                    ports=service.get('ports', {}),
                    environment=service.get('environment', {}),
                    detach=True
                )
                
                containers[service['name']] = container
                
                # Wait for service to be ready
                if 'healthcheck' in service:
                    await self._wait_for_service(
                        service['healthcheck']['url'],
                        service['healthcheck'].get('timeout', 30)
                    )
                    
            return containers
            
        except Exception as e:
            # Clean up on failure
            for container in containers.values():
                container.remove(force=True)
            raise
            
    async def _wait_for_service(
        self,
        url: str,
        timeout: int
    ) -> None:
        """Wait for a service to be ready"""
        start_time = datetime.now()
        
        async with aiohttp.ClientSession() as session:
            while (datetime.now() - start_time).total_seconds() < timeout:
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            return
                except aiohttp.ClientError:
                    pass
                    
                await asyncio.sleep(1)
                
        raise TimeoutError(f"Service at {url} not ready after {timeout} seconds")
