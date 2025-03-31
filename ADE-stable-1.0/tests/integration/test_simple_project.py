import pytest
import asyncio
from datetime import datetime, timedelta
import os
from typing import Dict, Any

from src.core.orchestrator import Orchestrator
from src.project_management.task_scheduler import TaskScheduler
from src.project_management.timeline_tracker import TimelineTracker
from tests.integration.workflow_runner import WorkflowRunner

# Test configuration
TEST_PROJECT_DIR = "test_projects/hello_world"
TEST_TIMEOUT = timedelta(minutes=5)

@pytest.fixture
async def workflow_runner():
    """Create a workflow runner instance"""
    orchestrator = Orchestrator()
    task_scheduler = TaskScheduler()
    timeline_tracker = TimelineTracker()
    
    runner = WorkflowRunner(
        orchestrator=orchestrator,
        task_scheduler=task_scheduler,
        timeline_tracker=timeline_tracker,
        timeout=TEST_TIMEOUT
    )
    
    yield runner
    await runner.cleanup()

@pytest.fixture
def project_config() -> Dict[str, Any]:
    """Create project configuration"""
    return {
        "name": "hello_world",
        "description": "Simple Hello World project",
        "language": "python",
        "dependencies": [],
        "tasks": [
            {
                "name": "create_project",
                "description": "Create project structure",
                "type": "setup"
            },
            {
                "name": "write_code",
                "description": "Write Hello World code",
                "type": "development"
            },
            {
                "name": "test_code",
                "description": "Test the code",
                "type": "testing"
            }
        ]
    }

class TestSimpleProject:
    """Test simple Hello World project workflow"""
    
    async def test_project_creation(self, workflow_runner, project_config):
        """Test project creation step"""
        async def create_project():
            # Create project directory
            os.makedirs(TEST_PROJECT_DIR, exist_ok=True)
            
            # Create project files
            with open(os.path.join(TEST_PROJECT_DIR, "main.py"), "w") as f:
                f.write('print("Hello, World!")')
            
            with open(os.path.join(TEST_PROJECT_DIR, "requirements.txt"), "w") as f:
                f.write("pytest==7.4.0")
            
            return {
                "project_dir": TEST_PROJECT_DIR,
                "files": ["main.py", "requirements.txt"]
            }
        
        async def validate_project(result: Dict[str, Any]) -> bool:
            # Verify project structure
            project_dir = result["project_dir"]
            files = result["files"]
            
            for file in files:
                if not os.path.exists(os.path.join(project_dir, file)):
                    return False
            
            return True
        
        workflow_runner.add_step(
            name="create_project",
            action=create_project,
            timeout=timedelta(seconds=10),
            validation=validate_project
        )
        
        result = await workflow_runner.execute_step(workflow_runner.steps["create_project"])
        assert result["project_dir"] == TEST_PROJECT_DIR
        assert len(result["files"]) == 2
    
    async def test_code_execution(self, workflow_runner):
        """Test code execution step"""
        async def run_code():
            import subprocess
            result = subprocess.run(
                ["python", os.path.join(TEST_PROJECT_DIR, "main.py")],
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        
        async def validate_output(output: str) -> bool:
            return output == "Hello, World!"
        
        workflow_runner.add_step(
            name="run_code",
            action=run_code,
            timeout=timedelta(seconds=5),
            validation=validate_output
        )
        
        result = await workflow_runner.execute_step(workflow_runner.steps["run_code"])
        assert result == "Hello, World!"
    
    async def test_complete_workflow(self, workflow_runner, project_config):
        """Test complete project workflow"""
        # Add project creation step
        async def create_project():
            os.makedirs(TEST_PROJECT_DIR, exist_ok=True)
            with open(os.path.join(TEST_PROJECT_DIR, "main.py"), "w") as f:
                f.write('print("Hello, World!")')
            with open(os.path.join(TEST_PROJECT_DIR, "requirements.txt"), "w") as f:
                f.write("pytest==7.4.0")
            return {"project_dir": TEST_PROJECT_DIR}
        
        # Add code execution step
        async def run_code():
            import subprocess
            result = subprocess.run(
                ["python", os.path.join(TEST_PROJECT_DIR, "main.py")],
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        
        # Add test step
        async def run_tests():
            import subprocess
            result = subprocess.run(
                ["pytest", TEST_PROJECT_DIR],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        
        # Configure workflow steps
        workflow_runner.add_step(
            name="create_project",
            action=create_project,
            timeout=timedelta(seconds=10)
        )
        
        workflow_runner.add_step(
            name="run_code",
            action=run_code,
            timeout=timedelta(seconds=5),
            dependencies=["create_project"]
        )
        
        workflow_runner.add_step(
            name="run_tests",
            action=run_tests,
            timeout=timedelta(seconds=10),
            dependencies=["run_code"]
        )
        
        # Execute workflow
        results = await workflow_runner.execute()
        
        # Verify results
        assert results["create_project"]["project_dir"] == TEST_PROJECT_DIR
        assert results["run_code"] == "Hello, World!"
        assert results["run_tests"] is True
        
        # Verify workflow status
        summary = workflow_runner.get_execution_summary()
        assert summary["status"] == "completed"
        assert all(step["status"] == "completed" for step in summary["steps"].values())
    
    async def test_workflow_timeout(self, workflow_runner):
        """Test workflow timeout handling"""
        async def long_running_task():
            await asyncio.sleep(10)  # Simulate long-running task
            return "result"
        
        workflow_runner.add_step(
            name="long_task",
            action=long_running_task,
            timeout=timedelta(seconds=1)  # Set short timeout
        )
        
        with pytest.raises(asyncio.TimeoutError):
            await workflow_runner.execute_step(workflow_runner.steps["long_task"])
        
        summary = workflow_runner.get_execution_summary()
        assert summary["status"] == "failed"
    
    async def test_workflow_retry(self, workflow_runner):
        """Test workflow retry mechanism"""
        attempt_count = 0
        
        async def failing_task():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError("Simulated error")
            return "success"
        
        workflow_runner.add_step(
            name="retry_task",
            action=failing_task,
            timeout=timedelta(seconds=5),
            retries=3,
            retry_delay=timedelta(seconds=0.1)
        )
        
        result = await workflow_runner.execute_step(workflow_runner.steps["retry_task"])
        assert result == "success"
        assert attempt_count == 3 