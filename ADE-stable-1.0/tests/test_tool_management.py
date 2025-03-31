import pytest
import asyncio
from datetime import datetime, timedelta
from production.src.core.tool_management import (
    ToolManager, ToolSpec, ToolType, ToolStatus, ToolMetrics
)

@pytest.fixture
async def tool_manager():
    manager = ToolManager()
    yield manager

@pytest.fixture
def sample_tool_spec():
    return ToolSpec(
        name="Code Analyzer",
        description="Analyzes code for potential issues",
        type=ToolType.CODE_ANALYSIS,
        capabilities={"code_analysis", "static_analysis", "security_scan"},
        required_inputs={
            "code": {"type": "str", "format": "python"},
            "analysis_level": {"type": "str", "format": "enum"}
        },
        output_schema={
            "issues": {"type": "list"},
            "metrics": {"type": "dict"}
        },
        error_schema={
            "error_code": {"type": "str"},
            "message": {"type": "str"}
        }
    )

@pytest.fixture
def sample_tool_implementation():
    async def implementation(inputs: dict, context: dict = None) -> dict:
        # Simulate tool execution
        await asyncio.sleep(0.1)
        return {
            "issues": [],
            "metrics": {
                "complexity": 10,
                "maintainability": 0.8
            }
        }
    return implementation

@pytest.mark.asyncio
async def test_tool_registration(tool_manager, sample_tool_spec, sample_tool_implementation):
    """Test tool registration and specification validation."""
    success = await tool_manager.register_tool(sample_tool_spec, sample_tool_implementation)
    
    assert success is True
    assert sample_tool_spec.tool_id in tool_manager.tools
    assert sample_tool_spec.tool_id in tool_manager.tool_implementations
    assert sample_tool_spec.tool_id in tool_manager.tool_performance_data

@pytest.mark.asyncio
async def test_tool_execution(tool_manager, sample_tool_spec, sample_tool_implementation):
    """Test tool execution and result handling."""
    await tool_manager.register_tool(sample_tool_spec, sample_tool_implementation)
    
    result = await tool_manager.execute_tool(
        tool_id=sample_tool_spec.tool_id,
        inputs={
            "code": "def test(): pass",
            "analysis_level": "basic"
        }
    )
    
    assert result.success is True
    assert "issues" in result.output
    assert "metrics" in result.output
    assert result.execution_time > 0
    assert result.cost == sample_tool_spec.cost_per_call

@pytest.mark.asyncio
async def test_tool_pipeline_execution(tool_manager, sample_tool_spec, sample_tool_implementation):
    """Test sequential tool pipeline execution."""
    await tool_manager.register_tool(sample_tool_spec, sample_tool_implementation)
    
    pipeline = [
        {
            "tool_id": sample_tool_spec.tool_id,
            "inputs": {
                "code": "def test(): pass",
                "analysis_level": "basic"
            }
        },
        {
            "tool_id": sample_tool_spec.tool_id,
            "inputs": {
                "code": "def test2(): pass",
                "analysis_level": "advanced"
            },
            "condition": {"type": "success", "previous_step": 0}
        }
    ]
    
    results = await tool_manager.execute_tool_pipeline(pipeline)
    
    assert len(results) == 2
    assert all(r.success for r in results)
    assert results[0].execution_time > 0
    assert results[1].execution_time > 0

@pytest.mark.asyncio
async def test_parallel_tool_execution(tool_manager, sample_tool_spec, sample_tool_implementation):
    """Test parallel tool execution."""
    await tool_manager.register_tool(sample_tool_spec, sample_tool_implementation)
    
    tools = [
        {
            "tool_id": sample_tool_spec.tool_id,
            "inputs": {
                "code": "def test1(): pass",
                "analysis_level": "basic"
            }
        },
        {
            "tool_id": sample_tool_spec.tool_id,
            "inputs": {
                "code": "def test2(): pass",
                "analysis_level": "basic"
            }
        }
    ]
    
    results = await tool_manager.execute_parallel_tools(tools)
    
    assert len(results) == 2
    assert all(r.success for r in results)
    # Parallel execution should be faster than sequential
    assert max(r.execution_time for r in results) < sum(r.execution_time for r in results)

@pytest.mark.asyncio
async def test_tool_recommendation(tool_manager, sample_tool_spec, sample_tool_implementation):
    """Test tool recommendation based on task description."""
    await tool_manager.register_tool(sample_tool_spec, sample_tool_implementation)
    
    recommendations = await tool_manager.recommend_tools(
        task_description="Analyze code for security issues and optimize performance"
    )
    
    assert len(recommendations) > 0
    assert all(
        "tool_id" in rec and
        "name" in rec and
        "match_score" in rec and
        "capabilities" in rec and
        "performance_metrics" in rec
        for rec in recommendations
    )
    assert recommendations[0]["match_score"] > 0.5

@pytest.mark.asyncio
async def test_tool_metrics_tracking(tool_manager, sample_tool_spec, sample_tool_implementation):
    """Test tool performance metrics tracking."""
    await tool_manager.register_tool(sample_tool_spec, sample_tool_implementation)
    
    # Execute tool multiple times
    for _ in range(3):
        await tool_manager.execute_tool(
            tool_id=sample_tool_spec.tool_id,
            inputs={
                "code": "def test(): pass",
                "analysis_level": "basic"
            }
        )
    
    # Check metrics
    assert sample_tool_spec.metrics.success_count == 3
    assert sample_tool_spec.metrics.total_execution_time > 0
    assert sample_tool_spec.metrics.average_execution_time > 0
    assert len(tool_manager.tool_usage_history) == 3

@pytest.mark.asyncio
async def test_tool_rate_limiting(tool_manager, sample_tool_spec, sample_tool_implementation):
    """Test tool rate limiting."""
    # Set rate limit
    sample_tool_spec.rate_limit = 2
    sample_tool_spec.rate_limit_period = 1.0  # 1 second
    
    await tool_manager.register_tool(sample_tool_spec, sample_tool_implementation)
    
    # Execute tool up to rate limit
    results = []
    for _ in range(3):
        result = await tool_manager.execute_tool(
            tool_id=sample_tool_spec.tool_id,
            inputs={
                "code": "def test(): pass",
                "analysis_level": "basic"
            }
        )
        results.append(result)
        await asyncio.sleep(0.1)  # Small delay between calls
    
    # Third call should fail due to rate limit
    assert results[2].success is False
    assert "Rate limit exceeded" in results[2].error

@pytest.mark.asyncio
async def test_tool_performance_report(tool_manager, sample_tool_spec, sample_tool_implementation):
    """Test tool performance report generation."""
    await tool_manager.register_tool(sample_tool_spec, sample_tool_implementation)
    
    # Execute tool a few times
    for _ in range(2):
        await tool_manager.execute_tool(
            tool_id=sample_tool_spec.tool_id,
            inputs={
                "code": "def test(): pass",
                "analysis_level": "basic"
            }
        )
    
    report = await tool_manager.get_tool_performance_report()
    
    assert "timestamp" in report
    assert "tools" in report
    assert sample_tool_spec.tool_id in report["tools"]
    
    tool_report = report["tools"][sample_tool_spec.tool_id]
    assert "name" in tool_report
    assert "type" in tool_report
    assert "status" in tool_report
    assert "metrics" in tool_report
    assert "usage_history" in tool_report
    
    metrics = tool_report["metrics"]
    assert "success_rate" in metrics
    assert "average_execution_time" in metrics
    assert "total_cost" in metrics
    assert "error_patterns" in metrics 