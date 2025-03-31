import pytest
import json
import os
from datetime import datetime
from typing import Dict, Any

from src.agents.development.ios_developer import IOSDeveloperAgent
from src.core.providers import ProviderRegistry

@pytest.fixture
def provider_registry():
    """Create a mock provider registry"""
    return ProviderRegistry()

@pytest.fixture
def ios_developer(provider_registry):
    """Create an iOS developer agent instance"""
    return IOSDeveloperAgent(
        agent_id="test_ios_dev",
        provider_registry=provider_registry,
        metadata={"project_dir": "test_project"}
    )

@pytest.mark.asyncio
async def test_create_ios_project(ios_developer):
    """Test creating a new iOS project"""
    task = {
        "type": "create_project",
        "project_name": "TestApp",
        "template": "SwiftUI",
        "target_ios": "15.0"
    }
    
    result = await ios_developer.process_task(task)
    
    assert result["success"] is True
    assert result["project_name"] == "TestApp"
    assert "structure" in result
    assert "files" in result["structure"]
    
    # Verify project structure
    files = result["structure"]["files"]
    assert any(f["path"].endswith("project.pbxproj") for f in files)
    assert any(f["path"].endswith("App.swift") for f in files)
    assert any(f["path"].endswith("ContentView.swift") for f in files)

@pytest.mark.asyncio
async def test_generate_swift_code(ios_developer):
    """Test generating Swift code"""
    task = {
        "type": "generate_swift",
        "requirements": "Create a User model with name and email properties",
        "component_type": "Model",
        "architecture": "MVVM"
    }
    
    result = await ios_developer.process_task(task)
    
    assert result["success"] is True
    assert "implementation_id" in result
    assert "code" in result
    
    # Verify code content
    code = result["code"]
    assert "struct User" in code
    assert "var name: String" in code
    assert "var email: String" in code

@pytest.mark.asyncio
async def test_implement_swiftui(ios_developer):
    """Test implementing SwiftUI components"""
    task = {
        "type": "implement_swiftui",
        "view_name": "UserProfileView",
        "requirements": "Create a profile view with user name and email",
        "style": "modern"
    }
    
    result = await ios_developer.process_task(task)
    
    assert result["success"] is True
    assert "component_id" in result
    assert "code" in result
    
    # Verify SwiftUI view
    code = result["code"]
    assert "struct UserProfileView: View" in code
    assert "var body: some View" in code
    assert "Text" in code

@pytest.mark.asyncio
async def test_setup_architecture(ios_developer):
    """Test setting up project architecture"""
    task = {
        "type": "setup_architecture",
        "project_name": "TestApp",
        "architecture": "Clean",
        "features": ["Authentication", "UserProfile"]
    }
    
    result = await ios_developer.process_task(task)
    
    assert result["success"] is True
    assert "structure" in result
    
    # Verify architecture structure
    structure = result["structure"]
    assert structure["name"] == "TestApp"
    assert structure["architecture"] == "Clean"
    assert "folders" in structure
    
    # Verify folder structure
    folders = structure["folders"]
    assert "App" in folders
    assert "Core" in folders
    assert "Data" in folders
    assert "Domain" in folders
    assert "Presentation" in folders
    assert "Infrastructure" in folders
    assert "Common" in folders

@pytest.mark.asyncio
async def test_write_ios_tests(ios_developer):
    """Test writing iOS tests"""
    task = {
        "type": "write_ios_tests",
        "component": "UserModel",
        "test_type": "unit"
    }
    
    result = await ios_developer.process_task(task)
    
    assert result["success"] is True
    assert "tests" in result
    
    # Verify test content
    tests = result["tests"]
    assert "import XCTest" in tests
    assert "class UserModelTests" in tests
    assert "func test" in tests

@pytest.mark.asyncio
async def test_write_ios_documentation(ios_developer):
    """Test writing iOS documentation"""
    task = {
        "type": "ios_documentation",
        "component": "UserProfileView",
        "doc_type": "code"
    }
    
    result = await ios_developer.process_task(task)
    
    assert result["success"] is True
    assert "documentation" in result
    
    # Verify documentation content
    doc = result["documentation"]
    assert "# UserProfileView" in doc
    assert "## Overview" in doc
    assert "## Usage" in doc

@pytest.mark.asyncio
async def test_error_handling(ios_developer):
    """Test error handling in iOS developer agent"""
    task = {
        "type": "invalid_task",
        "project_name": "TestApp"
    }
    
    result = await ios_developer.process_task(task)
    
    assert result["success"] is False
    assert "error" in result
    assert "Unknown task type" in result["error"]

@pytest.mark.asyncio
async def test_collaboration(ios_developer):
    """Test collaboration with other agents"""
    class MockAgent:
        async def process_task(self, task):
            return {"success": True, "result": "Mock result"}
    
    mock_agent = MockAgent()
    task = {
        "type": "collaborate",
        "other_agent": mock_agent,
        "task": {
            "type": "review_code",
            "code": "struct Test {}"
        }
    }
    
    result = await ios_developer.collaborate(mock_agent, task)
    
    assert result["success"] is True
    assert "result" in result

def test_ios_knowledge_loading(ios_developer):
    """Test loading iOS knowledge base"""
    knowledge = ios_developer.ios_knowledge
    
    assert "frameworks" in knowledge
    assert "patterns" in knowledge
    assert "guidelines" in knowledge
    
    # Verify framework knowledge
    frameworks = knowledge["frameworks"]
    assert "UIKit" in frameworks
    assert "SwiftUI" in frameworks
    assert "CoreData" in frameworks
    assert "Foundation" in frameworks
    
    # Verify pattern knowledge
    patterns = knowledge["patterns"]
    assert "MVVM" in patterns
    assert "Clean Architecture" in patterns
    assert "Coordinator" in patterns
    
    # Verify guideline knowledge
    guidelines = knowledge["guidelines"]
    assert "HIG" in guidelines
    assert "Swift" in guidelines 