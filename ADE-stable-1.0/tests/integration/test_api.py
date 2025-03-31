import pytest
from fastapi.testclient import TestClient
import json
from unittest.mock import patch, MagicMock

# Import the FastAPI app
from interfaces.api.app import app, get_orchestrator, get_task_repository, get_db_connector

# Create test client
client = TestClient(app)

# Mock dependencies
@pytest.fixture
def mock_db_connector():
    """Mock database connector"""
    with patch("interfaces.api.app.MongoDBConnector") as mock:
        # Create a mock instance
        instance = MagicMock()
        mock.return_value = instance
        yield instance

@pytest.fixture
def mock_task_repository(mock_db_connector):
    """Mock task repository"""
    with patch("interfaces.api.app.TaskRepository") as mock:
        # Create a mock instance
        instance = MagicMock()
        mock.return_value = instance
        yield instance

@pytest.fixture
def mock_orchestrator():
    """Mock orchestrator"""
    with patch("interfaces.api.app.Orchestrator") as mock:
        # Create a mock instance
        instance = MagicMock()
        mock.return_value = instance
        yield instance

# Override the dependency injection to use our mocks
app.dependency_overrides[get_db_connector] = lambda: MagicMock()
app.dependency_overrides[get_task_repository] = lambda: MagicMock()
app.dependency_overrides[get_orchestrator] = lambda: MagicMock()

class TestAPI:
    """Integration tests for the API"""
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_create_plan(self, mock_orchestrator):
        """Test creating a plan"""
        # Set up the mock to return a plan
        mock_plan = {
            "plan": {
                "steps": [
                    {
                        "id": "step_1",
                        "description": "Set up project structure",
                        "dependencies": [],
                        "estimated_time": 15,
                        "actions": ["Create directory structure", "Initialize git repository"]
                    }
                ]
            },
            "task_id": "mock-task-id"
        }
        mock_orchestrator.create_plan.return_value = mock_plan
        
        # Make the request
        response = client.post(
            "/plans/",
            json={"goal": "Create a simple API"}
        )
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert "plan" in data
        assert "steps" in data["plan"]
        assert "task_id" in data
        
        # Verify the mock was called correctly
        mock_orchestrator.create_plan.assert_called_once_with("Create a simple API")
    
    def test_execute_task(self, mock_orchestrator):
        """Test executing a task"""
        # Set up the mock to return a result
        mock_result = {
            "code": "def hello():\n    return 'Hello, world!'",
            "task_id": "mock-task-id"
        }
        mock_orchestrator.execute_task.return_value = mock_result
        
        # Make the request
        response = client.post(
            "/tasks/",
            json={
                "description": "Implement a hello world function",
                "task_type": "develop",
                "parameters": {"language": "python"}
            }
        )
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        assert "task_id" in data
        
        # Verify the mock was called correctly
        mock_orchestrator.execute_task.assert_called_once_with(
            task_description="Implement a hello world function",
            task_type="develop",
            parameters={"language": "python"}
        )
    
    def test_get_task_history(self, mock_orchestrator):
        """Test getting task history"""
        # Set up the mock to return task history
        mock_history = [
            {
                "id": "task-1",
                "description": "Create plan for: Create a simple API",
                "type": "plan",
                "status": "completed",
                "error": None,
                "result": {"steps": []},
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:01:00"
            },
            {
                "id": "task-2",
                "description": "Implement a hello world function",
                "type": "develop",
                "status": "completed",
                "error": None,
                "result": {"code": "def hello():\n    return 'Hello, world!'"},
                "created_at": "2023-01-01T00:01:00",
                "updated_at": "2023-01-01T00:02:00"
            }
        ]
        mock_orchestrator.get_task_history.return_value = mock_history
        
        # Make the request
        response = client.get("/tasks/")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["id"] == "task-1"
        assert data[1]["id"] == "task-2"
        
        # Verify the mock was called correctly
        mock_orchestrator.get_task_history.assert_called_once()
    
    def test_get_task(self, mock_orchestrator):
        """Test getting a task by ID"""
        # Set up the mock to return a task
        mock_task = {
            "id": "task-1",
            "description": "Create plan for: Create a simple API",
            "type": "plan",
            "status": "completed",
            "error": None,
            "result": {"steps": []},
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:01:00"
        }
        mock_orchestrator.get_task.return_value = mock_task
        
        # Make the request
        response = client.get("/tasks/task-1")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "task-1"
        assert data["description"] == "Create plan for: Create a simple API"
        
        # Verify the mock was called correctly
        mock_orchestrator.get_task.assert_called_once_with("task-1")
    
    def test_get_task_not_found(self, mock_orchestrator):
        """Test getting a non-existent task"""
        # Set up the mock to return None
        mock_orchestrator.get_task.return_value = None
        
        # Make the request
        response = client.get("/tasks/nonexistent")
        
        # Verify the response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]
        
        # Verify the mock was called correctly
        mock_orchestrator.get_task.assert_called_once_with("nonexistent")
    
    def test_create_plan_with_error(self, mock_orchestrator):
        """Test creating a plan with an error"""
        # Set up the mock to return an error
        error_response = {
            "error": "Failed to create plan",
            "task_id": "mock-task-id"
        }
        mock_orchestrator.create_plan.return_value = error_response
        
        # Make the request
        response = client.post(
            "/plans/",
            json={"goal": "Create a simple API"}
        )
        
        # Since our route is set to return an HTTPException for errors,
        # we should get a 400 response
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Failed to create plan" 