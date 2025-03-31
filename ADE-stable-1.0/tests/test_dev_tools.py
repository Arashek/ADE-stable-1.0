import pytest
import asyncio
from production.src.core.dev_tools import DevelopmentTools

@pytest.fixture
async def dev_tools():
    tools = DevelopmentTools()
    yield tools

@pytest.mark.asyncio
async def test_code_analysis_and_testing(dev_tools):
    """Test parallel code analysis and testing."""
    code = """
def example_function():
    # This is a test function
    return "Hello, World!"
    """
    
    results = await dev_tools.analyze_and_test_code(code)
    
    assert results["success"] is True
    assert results["total_time"] > 0
    assert results["total_cost"] >= 0
    assert len(results["results"]) > 0
    
    # Check code analysis results
    analysis_result = next(
        r for r in results["results"]
        if r["tool_id"] == "code_analyzer"
    )
    assert "issues" in analysis_result["output"]
    assert "metrics" in analysis_result["output"]
    
    # Check test results
    test_result = next(
        r for r in results["results"]
        if r["tool_id"] == "test_runner"
    )
    assert "results" in test_result["output"]
    assert "coverage" in test_result["output"]
    assert "performance" in test_result["output"]

@pytest.mark.asyncio
async def test_documentation_and_deployment(dev_tools):
    """Test documentation generation and deployment pipeline."""
    code = """
class ExampleAPI:
    def get_data(self):
        return {"message": "Hello, World!"}
    """
    version = "1.0.0"
    
    results = await dev_tools.generate_docs_and_deploy(code, version)
    
    assert results["success"] is True
    assert results["total_time"] > 0
    assert results["total_cost"] >= 0
    assert len(results["results"]) == 2
    
    # Check documentation results
    doc_result = results["results"][0]
    assert doc_result["tool_id"] == "doc_generator"
    assert "documentation" in doc_result["output"]
    assert "coverage" in doc_result["output"]
    
    # Check deployment results
    deploy_result = results["results"][1]
    assert deploy_result["tool_id"] == "deployment_manager"
    assert "status" in deploy_result["output"]
    assert "health" in deploy_result["output"]
    assert "metrics" in deploy_result["output"]

@pytest.mark.asyncio
async def test_tool_performance_report(dev_tools):
    """Test tool performance reporting."""
    # Execute some tools first
    code = "def test(): pass"
    await dev_tools.analyze_and_test_code(code)
    await dev_tools.generate_docs_and_deploy(code, "1.0.0")
    
    # Get performance report
    report = await dev_tools.get_tool_performance_report()
    
    assert "timestamp" in report
    assert "tools" in report
    assert len(report["tools"]) > 0
    
    # Check metrics for each tool
    for tool_id, tool_data in report["tools"].items():
        assert "name" in tool_data
        assert "type" in tool_data
        assert "status" in tool_data
        assert "metrics" in tool_data
        assert "usage_history" in tool_data
        
        metrics = tool_data["metrics"]
        assert "success_rate" in metrics
        assert "average_execution_time" in metrics
        assert "total_cost" in metrics
        assert "error_patterns" in metrics

@pytest.mark.asyncio
async def test_tool_recommendations(dev_tools):
    """Test tool recommendation system."""
    # Test code analysis recommendation
    code_analysis_recs = await dev_tools.tool_manager.recommend_tools(
        task_description="Analyze code for security issues"
    )
    assert len(code_analysis_recs) > 0
    assert any(
        rec["tool_id"] == "code_analyzer" and
        "security_scan" in rec["capabilities"]
        for rec in code_analysis_recs
    )
    
    # Test documentation recommendation
    doc_recs = await dev_tools.tool_manager.recommend_tools(
        task_description="Generate API documentation"
    )
    assert len(doc_recs) > 0
    assert any(
        rec["tool_id"] == "doc_generator" and
        "api_docs" in rec["capabilities"]
        for rec in doc_recs
    )

@pytest.mark.asyncio
async def test_tool_error_handling(dev_tools):
    """Test tool error handling and retries."""
    # Test with invalid input
    invalid_code = "invalid python code"
    results = await dev_tools.analyze_and_test_code(invalid_code)
    
    # Even with invalid input, the system should handle it gracefully
    assert results["success"] is False
    assert len(results["results"]) > 0
    
    # Check error details
    for result in results["results"]:
        if not result["success"]:
            assert "error" in result
            assert result["execution_time"] > 0
            assert result["cost"] >= 0

@pytest.mark.asyncio
async def test_tool_pipeline_conditions(dev_tools):
    """Test conditional tool pipeline execution."""
    code = "def test(): pass"
    version = "1.0.0"
    
    # Create a pipeline with a condition that should fail
    pipeline = [
        {
            "tool_id": "doc_generator",
            "inputs": {
                "code": code,
                "doc_type": "api"
            }
        },
        {
            "tool_id": "deployment_manager",
            "inputs": {
                "environment": "staging",
                "version": version
            },
            "condition": {
                "type": "success",
                "previous_step": 0,
                "threshold": 0.95  # Unrealistic threshold
            }
        }
    ]
    
    results = await dev_tools.tool_manager.execute_tool_pipeline(pipeline)
    
    # Second step should be skipped due to condition
    assert len(results) == 1
    assert results[0]["tool_id"] == "doc_generator" 