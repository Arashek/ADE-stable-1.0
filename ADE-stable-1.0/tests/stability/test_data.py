import random
from typing import Dict, List, Any
from datetime import datetime, timedelta

class TestDataGenerator:
    """Generator for test data used in functional tests."""
    
    @staticmethod
    def generate_development_goal() -> Dict[str, Any]:
        """Generate a sample development goal."""
        goals = [
            "Implement user authentication system",
            "Create RESTful API endpoints",
            "Design database schema",
            "Build frontend components",
            "Implement CI/CD pipeline"
        ]
        
        return {
            "id": f"goal_{random.randint(1000, 9999)}",
            "title": random.choice(goals),
            "description": f"Sample development goal for testing {datetime.now().isoformat()}",
            "priority": random.choice(["low", "medium", "high"]),
            "complexity": random.choice(["simple", "moderate", "complex"]),
            "estimated_hours": random.randint(2, 40),
            "created_at": datetime.now().isoformat(),
            "deadline": (datetime.now() + timedelta(days=random.randint(1, 30))).isoformat()
        }
    
    @staticmethod
    def generate_project_structure() -> Dict[str, Any]:
        """Generate a sample project structure."""
        return {
            "name": f"test_project_{random.randint(1000, 9999)}",
            "description": "Sample project for functional testing",
            "structure": {
                "src": {
                    "components": ["Button.tsx", "Card.tsx", "Layout.tsx"],
                    "pages": ["Home.tsx", "Dashboard.tsx", "Settings.tsx"],
                    "utils": ["helpers.ts", "constants.ts"],
                    "api": ["client.ts", "endpoints.ts"]
                },
                "tests": {
                    "unit": ["Button.test.tsx", "Card.test.tsx"],
                    "integration": ["api.test.ts", "auth.test.ts"],
                    "e2e": ["workflow.test.ts"]
                },
                "config": ["webpack.config.js", "tsconfig.json", ".env"]
            },
            "dependencies": {
                "frontend": ["react", "typescript", "tailwindcss"],
                "backend": ["fastapi", "pydantic", "sqlalchemy"],
                "testing": ["pytest", "jest", "cypress"]
            }
        }
    
    @staticmethod
    def generate_expected_results() -> Dict[str, Any]:
        """Generate expected results for test verification."""
        return {
            "code_quality": {
                "linting_score": random.uniform(80, 100),
                "test_coverage": random.uniform(70, 100),
                "complexity_score": random.uniform(60, 100)
            },
            "performance": {
                "response_time": random.uniform(50, 500),
                "memory_usage": random.uniform(50, 200),
                "cpu_usage": random.uniform(20, 80)
            },
            "security": {
                "vulnerability_score": random.uniform(0, 10),
                "compliance_score": random.uniform(80, 100)
            }
        }
    
    @staticmethod
    def generate_agent_capabilities() -> List[Dict[str, Any]]:
        """Generate sample agent capabilities."""
        return [
            {
                "type": "developer",
                "capabilities": ["coding", "testing", "debugging"],
                "languages": ["python", "typescript", "javascript"],
                "frameworks": ["react", "fastapi", "pytest"]
            },
            {
                "type": "architect",
                "capabilities": ["design", "planning", "review"],
                "expertise": ["system_design", "scalability", "security"]
            },
            {
                "type": "qa",
                "capabilities": ["testing", "validation", "verification"],
                "tools": ["pytest", "selenium", "cypress"]
            }
        ]
    
    @staticmethod
    def generate_task_sequence() -> List[Dict[str, Any]]:
        """Generate a sequence of related tasks."""
        tasks = []
        for i in range(random.randint(3, 7)):
            task = {
                "id": f"task_{random.randint(1000, 9999)}",
                "name": f"Task {i+1}",
                "type": random.choice(["development", "testing", "documentation"]),
                "priority": random.choice(["low", "medium", "high"]),
                "dependencies": [t["id"] for t in tasks] if tasks else [],
                "estimated_duration": random.randint(1, 8),
                "status": "pending"
            }
            tasks.append(task)
        return tasks
    
    @staticmethod
    def generate_provider_configs() -> List[Dict[str, Any]]:
        """Generate configurations for different AI providers."""
        return [
            {
                "name": "openai",
                "type": "llm",
                "model": "gpt-4",
                "max_tokens": 2000,
                "temperature": 0.7,
                "capabilities": ["code_generation", "code_review", "documentation"]
            },
            {
                "name": "anthropic",
                "type": "llm",
                "model": "claude-2",
                "max_tokens": 4000,
                "temperature": 0.5,
                "capabilities": ["code_generation", "code_review", "documentation"]
            },
            {
                "name": "github_copilot",
                "type": "code_assistant",
                "capabilities": ["code_completion", "code_suggestion"]
            }
        ] 