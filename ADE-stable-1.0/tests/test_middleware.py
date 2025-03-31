import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, Request, Response, HTTPException
from redis import Redis
from pydantic import BaseModel, Field
import json
import time

from src.core.middleware.validation import ValidationMiddleware, ValidationErrorResponse
from src.core.middleware.rate_limit import RateLimitMiddleware, RateLimitConfig
from src.core.logging.structured_logger import StructuredLogger
from src.core.cache.manager import CacheManager, CacheConfig

# Test models
class TestRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    value: int = Field(..., ge=0, le=100)
    optional_field: str = Field(None, min_length=1)

class TestResponse(BaseModel):
    result: str
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

@pytest.fixture
def redis_client():
    """Create a test Redis client"""
    return Redis(host='localhost', port=6379, db=0)

@pytest.fixture
def app():
    """Create a test FastAPI application"""
    return FastAPI()

@pytest.fixture
def validation_middleware():
    """Create a test validation middleware"""
    request_schemas = {
        "/test": TestRequest
    }
    response_schemas = {
        "/test": TestResponse
    }
    return ValidationMiddleware(request_schemas, response_schemas)

@pytest.fixture
def rate_limit_middleware(redis_client):
    """Create a test rate limit middleware"""
    config = RateLimitConfig(
        requests_per_minute=10,
        burst_size=2,
        block_duration=60
    )
    return RateLimitMiddleware(redis_client, config)

@pytest.fixture
def structured_logger():
    """Create a test structured logger"""
    return StructuredLogger(
        name="test_logger",
        log_level="DEBUG",
        console_output=True
    )

@pytest.fixture
def cache_manager(redis_client):
    """Create a test cache manager"""
    config = CacheConfig(
        default_ttl=60,
        max_ttl=300,
        prefix="test:"
    )
    return CacheManager(redis_client, config)

async def test_validation_middleware(validation_middleware, app):
    """Test validation middleware"""
    @app.post("/test")
    async def test_endpoint(request: Request):
        return Response(
            content=TestResponse(
                result="success",
                timestamp=datetime.now()
            ).json(),
            media_type="application/json"
        )
    
    # Test valid request
    valid_request = Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/test"
        }
    )
    valid_request._body = TestRequest(name="test", value=42).json().encode()
    
    response = await validation_middleware(valid_request, app)
    assert response.status_code == 200
    
    # Test invalid request
    invalid_request = Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/test"
        }
    )
    invalid_request._body = b'{"invalid": "data"}'
    
    response = await validation_middleware(invalid_request, app)
    assert response.status_code == 400
    error_data = ValidationErrorResponse.parse_raw(response.body)
    assert "error" in error_data.dict()

async def test_rate_limit_middleware(rate_limit_middleware, app):
    """Test rate limit middleware"""
    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}
    
    # Create test request
    request = Request(
        scope={
            "type": "http",
            "method": "GET",
            "path": "/test",
            "client": ("127.0.0.1", 12345)
        }
    )
    
    # Test within rate limit
    for _ in range(5):
        response = await rate_limit_middleware(request, app)
        assert response.status_code == 200
        assert "X-RateLimit-Remaining" in response.headers
    
    # Test rate limit exceeded
    for _ in range(10):
        response = await rate_limit_middleware(request, app)
        if response.status_code == 429:
            break
    else:
        pytest.fail("Rate limit not enforced")

def test_structured_logger(structured_logger):
    """Test structured logger"""
    # Test basic logging
    structured_logger.info("Test message")
    
    # Test request logging
    structured_logger.request(
        method="GET",
        path="/test",
        status_code=200,
        duration_ms=100.0,
        client_ip="127.0.0.1"
    )
    
    # Test performance logging
    structured_logger.performance(
        metric_name="response_time",
        value=150.0,
        tags={"endpoint": "/test"}
    )
    
    # Test security logging
    structured_logger.security(
        event_type="login_attempt",
        details={"user": "test", "success": True},
        severity="info"
    )

async def test_cache_manager(cache_manager):
    """Test cache manager"""
    # Test basic operations
    test_key = "test_key"
    test_value = {"data": "test"}
    
    # Test set
    success = await cache_manager.set(test_key, test_value)
    assert success
    
    # Test get
    value = await cache_manager.get(test_key)
    assert value == test_value
    
    # Test exists
    exists = await cache_manager.exists(test_key)
    assert exists
    
    # Test delete
    success = await cache_manager.delete(test_key)
    assert success
    
    # Test get after delete
    value = await cache_manager.get(test_key)
    assert value is None
    
    # Test multiple operations
    items = {
        "key1": "value1",
        "key2": "value2"
    }
    
    # Test set_many
    success = await cache_manager.set_many(items)
    assert success
    
    # Test get_many
    values = await cache_manager.get_many(list(items.keys()))
    assert values == items
    
    # Test cache decorator
    @cache_manager.cached(ttl=60)
    async def test_function(param: str):
        return f"result_{param}"
    
    # First call should cache
    result1 = await test_function("test")
    assert result1 == "result_test"
    
    # Second call should use cache
    result2 = await test_function("test")
    assert result2 == "result_test"
    
    # Test health check
    health = await cache_manager.health_check()
    assert health["status"] in ["healthy", "degraded"]
    assert "stats" in health

async def test_integration(
    validation_middleware,
    rate_limit_middleware,
    structured_logger,
    cache_manager,
    app
):
    """Test integration of all components"""
    @app.post("/test")
    async def test_endpoint(request: Request):
        # Log request
        structured_logger.request(
            method=request.method,
            path=request.url.path,
            status_code=200,
            duration_ms=100.0,
            client_ip=request.client.host
        )
        
        # Cache result
        cache_key = "test_result"
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            return Response(
                content=TestResponse(**cached_result).json(),
                media_type="application/json"
            )
        
        # Generate result
        result = TestResponse(
            result="success",
            timestamp=datetime.now()
        )
        
        # Cache result
        await cache_manager.set(cache_key, result.dict())
        
        return Response(
            content=result.json(),
            media_type="application/json"
        )
    
    # Create test request
    request = Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/test",
            "client": ("127.0.0.1", 12345)
        }
    )
    request._body = TestRequest(name="test", value=42).json().encode()
    
    # Apply middleware chain
    response = await validation_middleware(request, app)
    response = await rate_limit_middleware(request, lambda: response)
    
    # Verify response
    assert response.status_code == 200
    assert "X-RateLimit-Remaining" in response.headers 

async def test_validation_middleware_edge_cases(validation_middleware, app):
    """Test validation middleware edge cases"""
    @app.post("/test")
    async def test_endpoint(request: Request):
        return Response(
            content=TestResponse(
                result="success",
                timestamp=datetime.now(),
                metadata={"test": "data"}
            ).json(),
            media_type="application/json"
        )
    
    # Test empty request body
    empty_request = Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/test"
        }
    )
    empty_request._body = b"{}"
    
    response = await validation_middleware(empty_request, app)
    assert response.status_code == 400
    
    # Test invalid JSON
    invalid_json_request = Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/test"
        }
    )
    invalid_json_request._body = b"{invalid json}"
    
    response = await validation_middleware(invalid_json_request, app)
    assert response.status_code == 400
    
    # Test field validation
    invalid_field_request = Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/test"
        }
    )
    invalid_field_request._body = TestRequest(
        name="a",  # Too short
        value=150,  # Too large
        optional_field=""  # Empty string
    ).json().encode()
    
    response = await validation_middleware(invalid_field_request, app)
    assert response.status_code == 400
    error_data = ValidationErrorResponse.parse_raw(response.body)
    assert "error" in error_data.dict()
    assert "details" in error_data.dict()

async def test_rate_limit_middleware_edge_cases(rate_limit_middleware, app):
    """Test rate limit middleware edge cases"""
    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}
    
    # Test different client IDs
    client1_request = Request(
        scope={
            "type": "http",
            "method": "GET",
            "path": "/test",
            "client": ("127.0.0.1", 12345)
        }
    )
    
    client2_request = Request(
        scope={
            "type": "http",
            "method": "GET",
            "path": "/test",
            "client": ("127.0.0.2", 12345)
        }
    )
    
    # Test rate limits for different clients
    for _ in range(5):
        response1 = await rate_limit_middleware(client1_request, app)
        response2 = await rate_limit_middleware(client2_request, app)
        assert response1.status_code == 200
        assert response2.status_code == 200
    
    # Test API key based rate limiting
    api_key_request = Request(
        scope={
            "type": "http",
            "method": "GET",
            "path": "/test",
            "client": ("127.0.0.1", 12345),
            "headers": [("X-API-Key", "test-key")]
        }
    )
    
    for _ in range(5):
        response = await rate_limit_middleware(api_key_request, app)
        assert response.status_code == 200
    
    # Test burst handling
    burst_request = Request(
        scope={
            "type": "http",
            "method": "GET",
            "path": "/test",
            "client": ("127.0.0.3", 12345)
        }
    )
    
    # Allow burst
    for _ in range(rate_limit_middleware.config.burst_size):
        response = await rate_limit_middleware(burst_request, app)
        assert response.status_code == 200
    
    # Should block after burst
    response = await rate_limit_middleware(burst_request, app)
    assert response.status_code == 429

def test_structured_logger_edge_cases(structured_logger):
    """Test structured logger edge cases"""
    # Test logging with large data
    large_data = {
        "large_field": "x" * 1000,
        "nested": {
            "array": [{"id": i, "data": "x" * 100} for i in range(100)],
            "dict": {str(i): "x" * 50 for i in range(100)}
        }
    }
    
    structured_logger.info("Large data test", extra=large_data)
    
    # Test logging with special characters
    special_chars = {
        "unicode": "测试日志",
        "special": "!@#$%^&*()_+",
        "newlines": "line1\nline2\r\nline3"
    }
    
    structured_logger.info("Special characters test", extra=special_chars)
    
    # Test logging with circular references
    circular_data = {"self": None}
    circular_data["self"] = circular_data
    
    structured_logger.info("Circular reference test", extra={"data": circular_data})
    
    # Test logging with datetime objects
    datetime_data = {
        "now": datetime.now(),
        "utc": datetime.utcnow(),
        "custom": datetime(2024, 1, 1, 12, 0, 0)
    }
    
    structured_logger.info("Datetime test", extra=datetime_data)
    
    # Test logging with exceptions
    try:
        raise ValueError("Test exception")
    except ValueError as e:
        structured_logger.error("Exception test", exc_info=e)

async def test_cache_manager_edge_cases(cache_manager):
    """Test cache manager edge cases"""
    # Test large values
    large_value = {
        "data": "x" * 1000,
        "array": [{"id": i, "value": "x" * 100} for i in range(100)]
    }
    
    success = await cache_manager.set("large_key", large_value)
    assert success
    
    value = await cache_manager.get("large_key")
    assert value == large_value
    
    # Test special characters in keys
    special_key = "test!@#$%^&*()_+"
    special_value = {"special": "value"}
    
    success = await cache_manager.set(special_key, special_value)
    assert success
    
    value = await cache_manager.get(special_key)
    assert value == special_value
    
    # Test concurrent access
    async def concurrent_set(key: str, value: Any):
        return await cache_manager.set(key, value)
    
    tasks = [
        concurrent_set(f"concurrent_key_{i}", f"value_{i}")
        for i in range(10)
    ]
    
    results = await asyncio.gather(*tasks)
    assert all(results)
    
    # Test cache invalidation patterns
    await cache_manager.set("pattern:test1", "value1")
    await cache_manager.set("pattern:test2", "value2")
    await cache_manager.set("other:test3", "value3")
    
    success = await cache_manager.invalidate_pattern("pattern:*")
    assert success
    
    assert await cache_manager.get("pattern:test1") is None
    assert await cache_manager.get("pattern:test2") is None
    assert await cache_manager.get("other:test3") == "value3"
    
    # Test TTL handling
    short_ttl_key = "short_ttl"
    await cache_manager.set(short_ttl_key, "value", ttl=1)
    
    assert await cache_manager.get(short_ttl_key) == "value"
    await asyncio.sleep(2)
    assert await cache_manager.get(short_ttl_key) is None
    
    # Test cache decorator with different parameters
    @cache_manager.cached(ttl=60, key_prefix="test", key_builder=lambda x: f"custom_key_{x}")
    async def custom_key_function(param: str):
        return f"result_{param}"
    
    result1 = await custom_key_function("test")
    result2 = await custom_key_function("test")
    assert result1 == result2
    
    # Test cache decorator with exceptions
    @cache_manager.cached(ttl=60)
    async def failing_function():
        raise ValueError("Test error")
    
    with pytest.raises(ValueError):
        await failing_function()
    
    # Test cache decorator with None values
    @cache_manager.cached(ttl=60)
    async def null_function():
        return None
    
    result1 = await null_function()
    result2 = await null_function()
    assert result1 is None
    assert result2 is None

async def test_integration_edge_cases(
    validation_middleware,
    rate_limit_middleware,
    structured_logger,
    cache_manager,
    app
):
    """Test integration edge cases"""
    @app.post("/test")
    async def test_endpoint(request: Request):
        # Simulate slow processing
        await asyncio.sleep(0.1)
        
        # Log request with extra data
        structured_logger.request(
            method=request.method,
            path=request.url.path,
            status_code=200,
            duration_ms=100.0,
            client_ip=request.client.host,
            extra={
                "request_id": "test-id",
                "user_agent": "test-agent"
            }
        )
        
        # Cache result with short TTL
        cache_key = "test_result"
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            return Response(
                content=TestResponse(**cached_result).json(),
                media_type="application/json"
            )
        
        # Generate result with metadata
        result = TestResponse(
            result="success",
            timestamp=datetime.now(),
            metadata={
                "processing_time": 0.1,
                "cache_hit": False
            }
        )
        
        # Cache result
        await cache_manager.set(cache_key, result.dict(), ttl=1)
        
        return Response(
            content=result.json(),
            media_type="application/json"
        )
    
    # Test concurrent requests
    async def make_request():
        request = Request(
            scope={
                "type": "http",
                "method": "POST",
                "path": "/test",
                "client": ("127.0.0.1", 12345)
            }
        )
        request._body = TestRequest(
            name="test",
            value=42,
            optional_field="optional"
        ).json().encode()
        
        response = await validation_middleware(request, app)
        return await rate_limit_middleware(request, lambda: response)
    
    # Make concurrent requests
    tasks = [make_request() for _ in range(5)]
    responses = await asyncio.gather(*tasks)
    
    # Verify responses
    for response in responses:
        assert response.status_code == 200
        assert "X-RateLimit-Remaining" in response.headers
    
    # Test cache expiration
    await asyncio.sleep(2)
    
    # Make another request (should not use cache)
    request = Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/test",
            "client": ("127.0.0.1", 12345)
        }
    )
    request._body = TestRequest(
        name="test",
        value=42,
        optional_field="optional"
    ).json().encode()
    
    response = await validation_middleware(request, app)
    response = await rate_limit_middleware(request, lambda: response)
    
    assert response.status_code == 200
    response_data = json.loads(response.body)
    assert response_data["metadata"]["cache_hit"] is False 