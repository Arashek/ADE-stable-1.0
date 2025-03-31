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
TEST_PROJECT_DIR = "test_projects/auth_app"
TEST_TIMEOUT = timedelta(minutes=10)

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
    """Create authentication project configuration"""
    return {
        "name": "auth_app",
        "description": "Authentication and authorization application",
        "language": "python",
        "dependencies": [
            "fastapi==0.68.0",
            "uvicorn==0.15.0",
            "sqlalchemy==1.4.23",
            "python-jose[cryptography]==3.3.0",
            "passlib[bcrypt]==1.7.4",
            "python-multipart==0.0.5",
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
                "name": "implement_auth",
                "description": "Implement authentication system",
                "type": "development",
                "dependencies": ["create_database"]
            },
            {
                "name": "write_tests",
                "description": "Write authentication tests",
                "type": "testing",
                "dependencies": ["implement_auth"]
            }
        ]
    }

class TestAuthWorkflow:
    """Test authentication and authorization workflows"""
    
    async def test_user_registration(self, workflow_runner):
        """Test user registration workflow"""
        async def setup_auth():
            # Create authentication models
            with open(os.path.join(TEST_PROJECT_DIR, "app/models.py"), "w") as f:
                f.write("""
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
""")
            
            # Create authentication utilities
            with open(os.path.join(TEST_PROJECT_DIR, "app/auth.py"), "w") as f:
                f.write("""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Security configuration
SECRET_KEY = "test_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
""")
            
            return {"auth_setup": "completed"}
        
        async def register_user():
            # Create registration endpoint
            with open(os.path.join(TEST_PROJECT_DIR, "app/main.py"), "w") as f:
                f.write("""
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import User
from .auth import get_password_hash

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
async def register(username: str, email: str, password: str, db: Session = Depends(get_db)):
    # Check if user exists
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "User registered successfully"}
""")
            
            return {"registration_endpoint": "created"}
        
        workflow_runner.add_step(
            name="setup_auth",
            action=setup_auth,
            timeout=timedelta(seconds=10)
        )
        
        workflow_runner.add_step(
            name="register_user",
            action=register_user,
            timeout=timedelta(seconds=10),
            dependencies=["setup_auth"]
        )
        
        results = await workflow_runner.execute()
        assert results["setup_auth"]["auth_setup"] == "completed"
        assert results["register_user"]["registration_endpoint"] == "created"
    
    async def test_user_login(self, workflow_runner):
        """Test user login workflow"""
        async def implement_login():
            # Add login endpoint
            with open(os.path.join(TEST_PROJECT_DIR, "app/main.py"), "a") as f:
                f.write("""
from fastapi.security import OAuth2PasswordRequestForm
from .auth import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
""")
            
            return {"login_endpoint": "created"}
        
        workflow_runner.add_step(
            name="implement_login",
            action=implement_login,
            timeout=timedelta(seconds=10)
        )
        
        result = await workflow_runner.execute_step(workflow_runner.steps["implement_login"])
        assert result["login_endpoint"] == "created"
    
    async def test_token_management(self, workflow_runner):
        """Test token management and expiration"""
        async def implement_token_management():
            # Add token validation and refresh
            with open(os.path.join(TEST_PROJECT_DIR, "app/main.py"), "a") as f:
                f.write("""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from .auth import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/token/refresh")
async def refresh_token(current_user: User = Depends(get_current_user)):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
""")
            
            return {"token_management": "implemented"}
        
        workflow_runner.add_step(
            name="implement_token_management",
            action=implement_token_management,
            timeout=timedelta(seconds=10)
        )
        
        result = await workflow_runner.execute_step(workflow_runner.steps["implement_token_management"])
        assert result["token_management"] == "implemented"
    
    async def test_permission_controls(self, workflow_runner):
        """Test permission controls and role-based access"""
        async def implement_permissions():
            # Add permission-based endpoints
            with open(os.path.join(TEST_PROJECT_DIR, "app/main.py"), "a") as f:
                f.write("""
from typing import List
from fastapi import Depends, HTTPException, status

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

@app.get("/users/", response_model=List[User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@app.put("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    db.commit()
    return {"message": "User activated successfully"}
""")
            
            return {"permissions": "implemented"}
        
        workflow_runner.add_step(
            name="implement_permissions",
            action=implement_permissions,
            timeout=timedelta(seconds=10)
        )
        
        result = await workflow_runner.execute_step(workflow_runner.steps["implement_permissions"])
        assert result["permissions"] == "implemented"
    
    async def test_complete_auth_workflow(self, workflow_runner, project_config):
        """Test complete authentication workflow"""
        # Add setup step
        async def setup_project():
            os.makedirs(TEST_PROJECT_DIR, exist_ok=True)
            with open(os.path.join(TEST_PROJECT_DIR, "requirements.txt"), "w") as f:
                f.write("\n".join(project_config["dependencies"]))
            return {"project_dir": TEST_PROJECT_DIR}
        
        # Add database setup step
        async def create_database():
            with open(os.path.join(TEST_PROJECT_DIR, "app/database.py"), "w") as f:
                f.write("""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

engine = create_engine('sqlite:///test.db')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
""")
            return {"database": "created"}
        
        # Add test implementation step
        async def write_tests():
            with open(os.path.join(TEST_PROJECT_DIR, "tests/test_auth.py"), "w") as f:
                f.write("""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import User
from app.database import SessionLocal
from app.auth import get_password_hash

client = TestClient(app)

@pytest.fixture
def test_user():
    db = SessionLocal()
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass"),
        is_active=True,
        is_superuser=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()
    db.close()

def test_register_user():
    response = client.post(
        "/register",
        data={"username": "newuser", "email": "new@example.com", "password": "newpass"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "User registered successfully"}

def test_login_user(test_user):
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_read_users_me(test_user):
    # Login to get token
    login_response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpass"}
    )
    token = login_response.json()["access_token"]
    
    # Test protected endpoint
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
""")
            return {"tests": "written"}
        
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
            name="write_tests",
            action=write_tests,
            timeout=timedelta(seconds=10),
            dependencies=["create_database"]
        )
        
        # Execute workflow
        results = await workflow_runner.execute()
        
        # Verify results
        assert results["setup_project"]["project_dir"] == TEST_PROJECT_DIR
        assert results["create_database"]["database"] == "created"
        assert results["write_tests"]["tests"] == "written"
        
        # Verify workflow status
        summary = workflow_runner.get_execution_summary()
        assert summary["status"] == "completed"
        assert all(step["status"] == "completed" for step in summary["steps"].values())
        
        # Verify final artifacts
        assert os.path.exists(os.path.join(TEST_PROJECT_DIR, "requirements.txt"))
        assert os.path.exists(os.path.join(TEST_PROJECT_DIR, "app/database.py"))
        assert os.path.exists(os.path.join(TEST_PROJECT_DIR, "app/models.py"))
        assert os.path.exists(os.path.join(TEST_PROJECT_DIR, "app/auth.py"))
        assert os.path.exists(os.path.join(TEST_PROJECT_DIR, "app/main.py"))
        assert os.path.exists(os.path.join(TEST_PROJECT_DIR, "tests/test_auth.py")) 