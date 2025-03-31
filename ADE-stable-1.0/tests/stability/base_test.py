import time
import logging
import requests
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from requests.exceptions import RequestException
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class BaseStabilityTest(ABC):
    """Base class for all stability tests with common utilities."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = requests.Session()
        self.auth_token = None
        self.base_url = config['server_url']
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def authenticate(self) -> None:
        """Authenticate with the server and store the token."""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={
                    "username": self.config['test_user']['username'],
                    "password": self.config['test_user']['password']
                },
                timeout=self.config['timeouts']['request']
            )
            response.raise_for_status()
            self.auth_token = response.json()['access_token']
            self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
            logger.info("Successfully authenticated")
        except RequestException as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise

    def make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """Make an authenticated API request with retry logic."""
        url = f"{self.base_url}{endpoint}"
        timeout = timeout or self.config['timeouts']['request']
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=timeout
            )
            response.raise_for_status()
            return response
        except RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    def assert_response_time(self, response: requests.Response, max_time: float) -> None:
        """Assert that the response time is within acceptable limits."""
        elapsed = response.elapsed.total_seconds()
        assert elapsed <= max_time, f"Response time {elapsed}s exceeds maximum {max_time}s"

    def assert_status_code(self, response: requests.Response, expected_code: int) -> None:
        """Assert that the response status code matches the expected code."""
        assert response.status_code == expected_code, \
            f"Status code {response.status_code} does not match expected {expected_code}"

    def wait_for_condition(self, condition_func, timeout: int, interval: float = 1.0) -> bool:
        """Wait for a condition to be met with timeout."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(interval)
        return False

    @abstractmethod
    def setup(self) -> None:
        """Setup test environment."""
        pass

    @abstractmethod
    def teardown(self) -> None:
        """Cleanup test environment."""
        pass

    @abstractmethod
    def run(self) -> bool:
        """Run the test case."""
        pass 