import pytest
import asyncio
from datetime import datetime, timedelta
import os
import json
from typing import Dict, Any, List

from src.core.orchestrator import Orchestrator
from src.project_management.task_scheduler import TaskScheduler
from src.project_management.timeline_tracker import TimelineTracker
from tests.integration.workflow_runner import WorkflowRunner

# Test configuration
TEST_PROJECT_DIR = "test_projects/complex_app"
TEST_TIMEOUT = timedelta(minutes=15)

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
    """Create complex project configuration"""
    return {
        "name": "complex_app",
        "description": "Complex multi-stage application",
        "language": "python",
        "dependencies": [
            "fastapi==0.68.0",
            "uvicorn==0.15.0",
            "sqlalchemy==1.4.23",
            "pytest==7.4.0",
            "pytest-asyncio==0.18.3"
        ],
        "tasks": [
            {
                "name": "setup_project",
                "description": "Set up project structure",
                "type": "setup",
                "dependencies": []
            },
            {
                "name": "create_database",
                "description": "Create database schema",
                "type": "database",
                "dependencies": ["setup_project"]
            },
            {
                "name": "implement_api",
                "description": "Implement API endpoints",
                "type": "development",
                "dependencies": ["create_database"]
            },
            {
                "name": "write_tests",
                "description": "Write API tests",
                "type": "testing",
                "dependencies": ["implement_api"]
            },
            {
                "name": "run_tests",
                "description": "Run test suite",
                "type": "testing",
                "dependencies": ["write_tests"]
            }
        ]
    }

class TestComplexProject:
    """Test complex multi-stage project workflow"""
    
    async def test_project_setup(self, workflow_runner, project_config):
        """Test project setup step"""
        async def setup_project():
            # Create project structure
            os.makedirs(TEST_PROJECT_DIR, exist_ok=True)
            
            # Create requirements.txt
            with open(os.path.join(TEST_PROJECT_DIR, "requirements.txt"), "w") as f:
                f.write("\n".join(project_config["dependencies"]))
            
            # Create project structure
            os.makedirs(os.path.join(TEST_PROJECT_DIR, "app"), exist_ok=True)
            os.makedirs(os.path.join(TEST_PROJECT_DIR, "tests"), exist_ok=True)
            
            # Create initial files
            with open(os.path.join(TEST_PROJECT_DIR, "app/__init__.py"), "w") as f:
                f.write("")
            
            return {
                "project_dir": TEST_PROJECT_DIR,
                "structure": [
                    "requirements.txt",
                    "app/__init__.py",
                    "tests/"
                ]
            }
        
        async def validate_setup(result: Dict[str, Any]) -> bool:
            project_dir = result["project_dir"]
            structure = result["structure"]
            
            for item in structure:
                path = os.path.join(project_dir, item)
                if not os.path.exists(path):
                    return False
            
            return True
        
        workflow_runner.add_step(
            name="setup_project",
            action=setup_project,
            timeout=timedelta(seconds=10),
            validation=validate_setup
        )
        
        result = await workflow_runner.execute_step(workflow_runner.steps["setup_project"])
        assert result["project_dir"] == TEST_PROJECT_DIR
        assert len(result["structure"]) == 3
    
    async def test_database_setup(self, workflow_runner):
        """Test database setup step"""
        async def create_database():
            # Create database configuration
            db_config = {
                "database_url": "sqlite:///test.db",
                "models": [
                    {
                        "name": "User",
                        "fields": [
                            {"name": "id", "type": "Integer", "primary_key": True},
                            {"name": "username", "type": "String"},
                            {"name": "email", "type": "String"}
                        ]
                    }
                ]
            }
            
            # Create database models
            with open(os.path.join(TEST_PROJECT_DIR, "app/models.py"), "w") as f:
                f.write("""
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
""")
            
            # Create database initialization script
            with open(os.path.join(TEST_PROJECT_DIR, "app/database.py"), "w") as f:
                f.write("""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

engine = create_engine('sqlite:///test.db')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
""")
            
            return db_config
        
        async def validate_database(result: Dict[str, Any]) -> bool:
            # Check if database files exist
            db_file = os.path.join(TEST_PROJECT_DIR, "test.db")
            return os.path.exists(db_file)
        
        workflow_runner.add_step(
            name="create_database",
            action=create_database,
            timeout=timedelta(seconds=10),
            validation=validate_database
        )
        
        result = await workflow_runner.execute_step(workflow_runner.steps["create_database"])
        assert result["database_url"] == "sqlite:///test.db"
        assert len(result["models"]) == 1
    
    async def test_api_implementation(self, workflow_runner):
        """Test API implementation step"""
        async def implement_api():
            # Create FastAPI application
            with open(os.path.join(TEST_PROJECT_DIR, "app/main.py"), "w") as f:
                f.write("""
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import User

app = FastAPI()

@app.get("/users")
async def get_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return [{"id": user.id, "username": user.username, "email": user.email} for user in users]
    finally:
        db.close()

@app.post("/users")
async def create_user(user: dict):
    db = SessionLocal()
    try:
        db_user = User(username=user["username"], email=user["email"])
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"id": db_user.id, "username": db_user.username, "email": db_user.email}
    finally:
        db.close()
""")
            
            return {"endpoints": ["/users"]}
        
        async def validate_api(result: Dict[str, Any]) -> bool:
            # Check if API file exists
            api_file = os.path.join(TEST_PROJECT_DIR, "app/main.py")
            return os.path.exists(api_file)
        
        workflow_runner.add_step(
            name="implement_api",
            action=implement_api,
            timeout=timedelta(seconds=10),
            validation=validate_api
        )
        
        result = await workflow_runner.execute_step(workflow_runner.steps["implement_api"])
        assert len(result["endpoints"]) == 2
    
    async def test_error_recovery(self, workflow_runner):
        """Test error recovery during workflow execution"""
        async def failing_task():
            raise ValueError("Simulated API error")
        
        async def recovery_task():
            # Implement recovery logic
            with open(os.path.join(TEST_PROJECT_DIR, "app/error_handler.py"), "w") as f:
                f.write("""
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

def handle_database_error(error: SQLAlchemyError):
    raise HTTPException(status_code=500, detail="Database error occurred")

def handle_validation_error(error: ValueError):
    raise HTTPException(status_code=400, detail=str(error))
""")
            return {"recovered": True}
        
        workflow_runner.add_step(
            name="failing_task",
            action=failing_task,
            timeout=timedelta(seconds=5)
        )
        
        workflow_runner.add_step(
            name="recovery_task",
            action=recovery_task,
            timeout=timedelta(seconds=5),
            dependencies=["failing_task"]
        )
        
        # Execute workflow with error recovery
        results = await workflow_runner.execute()
        
        # Verify recovery
        assert results["recovery_task"]["recovered"] is True
        assert os.path.exists(os.path.join(TEST_PROJECT_DIR, "app/error_handler.py"))
    
    async def test_complete_workflow(self, workflow_runner, project_config):
        """Test complete complex project workflow"""
        # Add setup step
        async def setup_project():
            os.makedirs(TEST_PROJECT_DIR, exist_ok=True)
            with open(os.path.join(TEST_PROJECT_DIR, "requirements.txt"), "w") as f:
                f.write("\n".join(project_config["dependencies"]))
            return {"project_dir": TEST_PROJECT_DIR}
        
        # Add database setup step
        async def create_database():
            with open(os.path.join(TEST_PROJECT_DIR, "app/models.py"), "w") as f:
                f.write("""
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
""")
            return {"database": "created"}
        
        # Add API implementation step
        async def implement_api():
            with open(os.path.join(TEST_PROJECT_DIR, "app/main.py"), "w") as f:
                f.write("""
from fastapi import FastAPI
from .models import User

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API is running"}
""")
            return {"api": "implemented"}
        
        # Add test implementation step
        async def write_tests():
            with open(os.path.join(TEST_PROJECT_DIR, "tests/test_api.py"), "w") as f:
                f.write("""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is running"}
""")
            return {"tests": "written"}
        
        # Add test execution step
        async def run_tests():
            import subprocess
            result = subprocess.run(
                ["pytest", os.path.join(TEST_PROJECT_DIR, "tests")],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        
        # Configure workflow steps
        workflow_runner.add_step(
            name="setup_project",
            action=setup_project,
            timeout=timedelta(seconds=10)
        )
        
        workflow_runner.add_step(
            name="create_database",
            action=create_database,
            timeout=timedelta(seconds=10),
            dependencies=["setup_project"]
        )
        
        workflow_runner.add_step(
            name="implement_api",
            action=implement_api,
            timeout=timedelta(seconds=10),
            dependencies=["create_database"]
        )
        
        workflow_runner.add_step(
            name="write_tests",
            action=write_tests,
            timeout=timedelta(seconds=10),
            dependencies=["implement_api"]
        )
        
        workflow_runner.add_step(
            name="run_tests",
            action=run_tests,
            timeout=timedelta(seconds=10),
            dependencies=["write_tests"]
        )
        
        # Execute workflow
        results = await workflow_runner.execute()
        
        # Verify results
        assert results["setup_project"]["project_dir"] == TEST_PROJECT_DIR
        assert results["create_database"]["database"] == "created"
        assert results["implement_api"]["api"] == "implemented"
        assert results["write_tests"]["tests"] == "written"
        assert results["run_tests"] is True
        
        # Verify workflow status
        summary = workflow_runner.get_execution_summary()
        assert summary["status"] == "completed"
        assert all(step["status"] == "completed" for step in summary["steps"].values())
        
        # Verify final artifacts
        assert os.path.exists(os.path.join(TEST_PROJECT_DIR, "requirements.txt"))
        assert os.path.exists(os.path.join(TEST_PROJECT_DIR, "app/models.py"))
        assert os.path.exists(os.path.join(TEST_PROJECT_DIR, "app/main.py"))
        assert os.path.exists(os.path.join(TEST_PROJECT_DIR, "tests/test_api.py")) 