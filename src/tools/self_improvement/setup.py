import os
import shutil
import json
from pathlib import Path
from typing import Dict, Any
import hashlib
from datetime import datetime

class SelfImprovementSetup:
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.project_name = "ade_self_improvement"
        self.project_dir = self.workspace_root / "projects" / self.project_name
        self.backup_dir = self.project_dir / "backups"
        self.analysis_dir = self.project_dir / "analysis"
        self.improvements_dir = self.project_dir / "improvements"
        self.reports_dir = self.project_dir / "reports"
        
        # Create necessary directories
        self._create_directories()
        
        # Initialize project metadata
        self.metadata = {
            "project_name": self.project_name,
            "created_at": datetime.now().isoformat(),
            "original_codebase_hash": None,
            "improvement_history": [],
            "current_version": "1.0.0"
        }
    
    def _create_directories(self):
        """Create all necessary directories for the self-improvement project"""
        directories = [
            self.project_dir,
            self.backup_dir,
            self.analysis_dir,
            self.improvements_dir,
            self.reports_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _calculate_codebase_hash(self, directory: Path) -> str:
        """Calculate a hash of the codebase for version tracking"""
        hasher = hashlib.sha256()
        
        for root, _, files in os.walk(directory):
            for file in sorted(files):
                if file.endswith(('.py', '.json', '.yaml', '.yml', '.md')):
                    file_path = Path(root) / file
                    with open(file_path, 'rb') as f:
                        hasher.update(f.read())
        
        return hasher.hexdigest()
    
    def _create_project_config(self):
        """Create project configuration file"""
        config = {
            "name": self.project_name,
            "type": "self_improvement",
            "settings": {
                "isolation_level": "strict",
                "allowed_operations": [
                    "code_analysis",
                    "refactoring",
                    "optimization",
                    "documentation"
                ],
                "backup_frequency": "before_each_improvement",
                "max_improvement_iterations": 5
            },
            "dependencies": {
                "original_codebase": str(self.workspace_root),
                "required_tools": [
                    "pytest",
                    "black",
                    "flake8",
                    "mypy",
                    "pylint"
                ]
            }
        }
        
        config_path = self.project_dir / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _create_isolation_config(self):
        """Create isolation configuration to prevent conflicts"""
        isolation_config = {
            "file_patterns": {
                "exclude": [
                    "**/__pycache__/**",
                    "**/*.pyc",
                    "**/.git/**",
                    "**/venv/**",
                    "**/node_modules/**"
                ],
                "include": [
                    "**/*.py",
                    "**/*.json",
                    "**/*.yaml",
                    "**/*.yml",
                    "**/*.md"
                ]
            },
            "environment": {
                "python_path": str(self.project_dir),
                "env_vars": {
                    "ADE_PROJECT_MODE": "self_improvement",
                    "ADE_ISOLATION_LEVEL": "strict"
                }
            }
        }
        
        isolation_path = self.project_dir / "isolation.json"
        with open(isolation_path, 'w') as f:
            json.dump(isolation_config, f, indent=2)
    
    def copy_codebase(self):
        """Create a copy of the codebase with proper isolation"""
        # Create initial backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"initial_{timestamp}"
        
        # Copy codebase with exclusions
        shutil.copytree(
            self.workspace_root,
            backup_path,
            ignore=shutil.ignore_patterns(
                "__pycache__",
                "*.pyc",
                ".git",
                "venv",
                "node_modules"
            )
        )
        
        # Calculate and store codebase hash
        self.metadata["original_codebase_hash"] = self._calculate_codebase_hash(backup_path)
        
        # Create symlink to current version
        current_link = self.project_dir / "current"
        if current_link.exists():
            current_link.unlink()
        current_link.symlink_to(backup_path)
    
    def setup_project(self):
        """Set up the self-improvement project"""
        # Create project configuration
        self._create_project_config()
        
        # Create isolation configuration
        self._create_isolation_config()
        
        # Create initial analysis directory structure
        analysis_structure = {
            "code_quality": {},
            "performance": {},
            "security": {},
            "documentation": {}
        }
        
        for category, _ in analysis_structure.items():
            (self.analysis_dir / category).mkdir(exist_ok=True)
        
        # Save project metadata
        metadata_path = self.project_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def initialize(self):
        """Initialize the self-improvement project"""
        print(f"Initializing self-improvement project in {self.project_dir}")
        
        # Create project structure
        self.setup_project()
        
        # Copy codebase
        print("Creating codebase copy...")
        self.copy_codebase()
        
        print("Self-improvement project initialized successfully!")
        print(f"Project directory: {self.project_dir}")
        print(f"Current version: {self.metadata['current_version']}")
        print(f"Codebase hash: {self.metadata['original_codebase_hash']}")

def main():
    """Main entry point for the setup script"""
    workspace_root = os.getenv("ADE_WORKSPACE_ROOT", os.getcwd())
    setup = SelfImprovementSetup(workspace_root)
    setup.initialize()

if __name__ == "__main__":
    main() 