import logging
from typing import Dict, Any
from .base_test import BaseStabilityTest
from .test_data import TestDataGenerator

logger = logging.getLogger(__name__)

class TestProviderRegistry(BaseStabilityTest):
    """Test cases for the Provider Registry component."""
    
    def setup(self) -> None:
        """Setup test environment."""
        self.authenticate()
        self.test_data = TestDataGenerator()
        self.providers = self.test_data.generate_provider_configs()
        
    def run(self) -> bool:
        """Run provider registry test cases."""
        try:
            # Test 1: Register multiple providers
            logger.info("Testing multiple provider registration")
            registered_providers = []
            for provider in self.providers:
                response = self.make_request(
                    method="POST",
                    endpoint="/api/providers",
                    data=provider
                )
                self.assert_status_code(response, 201)
                self.assert_response_time(response, self.config['test_params']['max_response_time'])
                registered_providers.append(response.json()['id'])
            
            # Test 2: Test capability routing
            logger.info("Testing capability routing")
            test_capabilities = ["code_generation", "code_review", "documentation"]
            for capability in test_capabilities:
                response = self.make_request(
                    method="GET",
                    endpoint="/api/providers/routing",
                    params={"capability": capability}
                )
                self.assert_status_code(response, 200)
                providers = response.json()['providers']
                assert len(providers) > 0, f"No providers found for capability: {capability}"
            
            # Test 3: Test fallback mechanisms
            logger.info("Testing provider fallback")
            # Simulate primary provider failure
            primary_provider = registered_providers[0]
            self.make_request(
                method="POST",
                endpoint=f"/api/providers/{primary_provider}/simulate_failure"
            )
            
            # Attempt request that should trigger fallback
            response = self.make_request(
                method="POST",
                endpoint="/api/providers/execute",
                data={
                    "capability": "code_generation",
                    "prompt": "Generate a simple function"
                }
            )
            self.assert_status_code(response, 200)
            assert response.json()['provider_id'] != primary_provider, \
                "Request was not routed to fallback provider"
            
            # Test 4: Test response formatting
            logger.info("Testing response formatting")
            test_prompts = [
                "Generate a React component",
                "Write a unit test",
                "Create an API endpoint"
            ]
            
            for prompt in test_prompts:
                response = self.make_request(
                    method="POST",
                    endpoint="/api/providers/execute",
                    data={"prompt": prompt}
                )
                self.assert_status_code(response, 200)
                result = response.json()
                
                # Verify response structure
                assert 'provider_id' in result, "Response missing provider_id"
                assert 'content' in result, "Response missing content"
                assert 'metadata' in result, "Response missing metadata"
                assert 'timestamp' in result, "Response missing timestamp"
                
                # Verify content formatting
                content = result['content']
                assert isinstance(content, str), "Content should be a string"
                assert len(content) > 0, "Content should not be empty"
                
                # Verify metadata
                metadata = result['metadata']
                assert 'model' in metadata, "Metadata missing model information"
                assert 'tokens_used' in metadata, "Metadata missing token usage"
                assert 'processing_time' in metadata, "Metadata missing processing time"
            
            # Test 5: Test provider health monitoring
            logger.info("Testing provider health monitoring")
            for provider_id in registered_providers:
                response = self.make_request(
                    method="GET",
                    endpoint=f"/api/providers/{provider_id}/health"
                )
                self.assert_status_code(response, 200)
                health_data = response.json()
                
                assert 'status' in health_data, "Health data missing status"
                assert 'latency' in health_data, "Health data missing latency"
                assert 'error_rate' in health_data, "Health data missing error rate"
                assert 'last_check' in health_data, "Health data missing last check"
            
            # Test 6: Test concurrent provider usage
            logger.info("Testing concurrent provider usage")
            concurrent_requests = []
            for _ in range(5):
                response = self.make_request(
                    method="POST",
                    endpoint="/api/providers/execute",
                    data={"prompt": "Test concurrent request"}
                )
                self.assert_status_code(response, 200)
                concurrent_requests.append(response.json())
            
            # Verify all requests were handled
            assert len(concurrent_requests) == 5, "Not all concurrent requests were processed"
            
            return True
            
        except Exception as e:
            logger.error(f"Provider registry test failed: {str(e)}")
            return False
            
    def teardown(self) -> None:
        """Cleanup test environment."""
        try:
            # Clean up all registered providers
            response = self.make_request(
                method="GET",
                endpoint="/api/providers"
            )
            self.assert_status_code(response, 200)
            
            for provider in response.json():
                self.make_request(
                    method="DELETE",
                    endpoint=f"/api/providers/{provider['id']}"
                )
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}") 