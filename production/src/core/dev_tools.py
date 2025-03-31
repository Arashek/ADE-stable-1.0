from typing import Dict, Any, List
import asyncio
from .tool_management import (
    ToolManager, ToolSpec, ToolType, ToolStatus, ToolMetrics
)

class DevelopmentTools:
    def __init__(self):
        self.tool_manager = ToolManager()
        self._register_tools()
    
    async def _register_tools(self):
        """Register all development tools."""
        # Code Analysis Tool
        code_analyzer_spec = ToolSpec(
            name="Code Analyzer",
            description="Analyzes code for potential issues and metrics",
            type=ToolType.CODE_ANALYSIS,
            capabilities={"code_analysis", "static_analysis", "security_scan"},
            required_inputs={
                "code": {"type": "str", "format": "python"},
                "analysis_level": {"type": "str", "format": "enum"}
            },
            output_schema={
                "issues": {"type": "list"},
                "metrics": {"type": "dict"}
            }
        )
        await self.tool_manager.register_tool(
            code_analyzer_spec,
            self._code_analyzer_implementation
        )
        
        # Documentation Generator
        doc_generator_spec = ToolSpec(
            name="Documentation Generator",
            description="Generates documentation from code",
            type=ToolType.DOCUMENTATION,
            capabilities={"doc_generation", "api_docs", "code_docs"},
            required_inputs={
                "code": {"type": "str", "format": "python"},
                "doc_type": {"type": "str", "format": "enum"}
            },
            output_schema={
                "documentation": {"type": "str"},
                "coverage": {"type": "float"}
            }
        )
        await self.tool_manager.register_tool(
            doc_generator_spec,
            self._doc_generator_implementation
        )
        
        # Test Runner
        test_runner_spec = ToolSpec(
            name="Test Runner",
            description="Runs tests and reports results",
            type=ToolType.TESTING,
            capabilities={"test_execution", "coverage_report", "performance_test"},
            required_inputs={
                "test_files": {"type": "list", "format": "python"},
                "test_type": {"type": "str", "format": "enum"}
            },
            output_schema={
                "results": {"type": "dict"},
                "coverage": {"type": "float"},
                "performance": {"type": "dict"}
            }
        )
        await self.tool_manager.register_tool(
            test_runner_spec,
            self._test_runner_implementation
        )
        
        # Deployment Tool
        deployment_spec = ToolSpec(
            name="Deployment Manager",
            description="Manages code deployment",
            type=ToolType.DEPLOYMENT,
            capabilities={"deployment", "rollback", "health_check"},
            required_inputs={
                "environment": {"type": "str", "format": "enum"},
                "version": {"type": "str", "format": "semver"}
            },
            output_schema={
                "status": {"type": "str"},
                "health": {"type": "dict"},
                "metrics": {"type": "dict"}
            }
        )
        await self.tool_manager.register_tool(
            deployment_spec,
            self._deployment_implementation
        )
    
    async def analyze_and_test_code(self, code: str) -> Dict[str, Any]:
        """Analyze code and run tests in parallel."""
        # Get tool recommendations
        recommendations = await self.tool_manager.recommend_tools(
            task_description="Analyze code and run tests"
        )
        
        # Execute tools in parallel
        tools = [
            {
                "tool_id": rec["tool_id"],
                "inputs": {
                    "code": code,
                    "analysis_level": "basic"
                }
            }
            for rec in recommendations
            if rec["tool_id"] in ["code_analyzer", "test_runner"]
        ]
        
        results = await self.tool_manager.execute_parallel_tools(tools)
        return self._aggregate_results(results)
    
    async def generate_docs_and_deploy(self, code: str, version: str) -> Dict[str, Any]:
        """Generate documentation and deploy code in a pipeline."""
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
                    "previous_step": 0
                }
            }
        ]
        
        results = await self.tool_manager.execute_tool_pipeline(pipeline)
        return self._aggregate_results(results)
    
    async def _code_analyzer_implementation(self, inputs: Dict[str, Any],
                                         context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Implementation of code analysis tool."""
        # Simulate code analysis
        await asyncio.sleep(1)
        return {
            "issues": [
                {
                    "type": "style",
                    "message": "Line too long",
                    "line": 10
                }
            ],
            "metrics": {
                "complexity": 15,
                "maintainability": 0.7,
                "security_score": 0.9
            }
        }
    
    async def _doc_generator_implementation(self, inputs: Dict[str, Any],
                                         context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Implementation of documentation generator."""
        # Simulate documentation generation
        await asyncio.sleep(1)
        return {
            "documentation": "# API Documentation\n\n## Endpoints\n...",
            "coverage": 0.85
        }
    
    async def _test_runner_implementation(self, inputs: Dict[str, Any],
                                       context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Implementation of test runner."""
        # Simulate test execution
        await asyncio.sleep(2)
        return {
            "results": {
                "passed": 10,
                "failed": 0,
                "skipped": 2
            },
            "coverage": 0.92,
            "performance": {
                "execution_time": 1.5,
                "memory_usage": "150MB"
            }
        }
    
    async def _deployment_implementation(self, inputs: Dict[str, Any],
                                      context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Implementation of deployment manager."""
        # Simulate deployment
        await asyncio.sleep(3)
        return {
            "status": "success",
            "health": {
                "status": "healthy",
                "response_time": 150,
                "error_rate": 0.01
            },
            "metrics": {
                "deployment_time": 3.0,
                "rollback_ready": True
            }
        }
    
    def _aggregate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from multiple tool executions."""
        aggregated = {
            "success": all(r["success"] for r in results),
            "results": [],
            "total_time": sum(r["execution_time"] for r in results),
            "total_cost": sum(r["cost"] for r in results)
        }
        
        for result in results:
            aggregated["results"].append({
                "tool_id": result["tool_id"],
                "output": result["output"],
                "execution_time": result["execution_time"],
                "cost": result["cost"]
            })
        
        return aggregated
    
    async def get_tool_performance_report(self) -> Dict[str, Any]:
        """Get performance report for all development tools."""
        return await self.tool_manager.get_tool_performance_report() 