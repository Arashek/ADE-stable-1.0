from typing import Dict, Any, List, Optional
import os
import re
from pathlib import Path
from .base import BaseDocumentationGenerator
from ...config.logging_config import logger

class UserDocumentationGenerator(BaseDocumentationGenerator):
    """Generator for user-facing documentation"""
    
    def __init__(self, output_dir: str = "docs"):
        super().__init__(output_dir)
        self.sections = {
            "getting_started": [],
            "user_guides": [],
            "admin_guides": [],
            "tutorials": [],
            "troubleshooting": []
        }
        
    def generate_user_docs(self, source_dir: str, config: Dict[str, Any] = None):
        """Generate user documentation"""
        try:
            self.create_output_dirs()
            source_path = Path(source_dir)
            config = config or {}
            
            # Generate documentation sections
            self._generate_getting_started()
            self._generate_user_guides()
            self._generate_admin_guides()
            self._generate_tutorials()
            self._generate_troubleshooting()
            
            # Generate navigation and index
            self._generate_user_docs_navigation()
            self._generate_user_docs_index()
            
            logger.info("User documentation generated successfully")
            
        except Exception as e:
            logger.error(f"Error generating user documentation: {str(e)}")
            raise
            
    def _generate_getting_started(self):
        """Generate getting started documentation"""
        try:
            template = self.load_template("getting_started.md")
            content = template.render(
                version_info=self.generate_version_info(),
                sections=[
                    {
                        "title": "Introduction",
                        "content": self._load_content("user/introduction.md")
                    },
                    {
                        "title": "Installation",
                        "content": self._load_content("user/installation.md")
                    },
                    {
                        "title": "Quick Start",
                        "content": self._load_content("user/quick_start.md")
                    }
                ]
            )
            self.save_file(content, "user/getting_started.md")
            self.sections["getting_started"].append("getting_started.md")
            
        except Exception as e:
            logger.error(f"Error generating getting started documentation: {str(e)}")
            raise
            
    def _generate_user_guides(self):
        """Generate user guides"""
        try:
            template = self.load_template("user_guides.md")
            content = template.render(
                version_info=self.generate_version_info(),
                guides=[
                    {
                        "title": "User Interface",
                        "content": self._load_content("user/ui_guide.md")
                    },
                    {
                        "title": "Features",
                        "content": self._load_content("user/features.md")
                    },
                    {
                        "title": "Workflows",
                        "content": self._load_content("user/workflows.md")
                    }
                ]
            )
            self.save_file(content, "user/user_guides.md")
            self.sections["user_guides"].append("user_guides.md")
            
        except Exception as e:
            logger.error(f"Error generating user guides: {str(e)}")
            raise
            
    def _generate_admin_guides(self):
        """Generate administrator guides"""
        try:
            template = self.load_template("admin_guides.md")
            content = template.render(
                version_info=self.generate_version_info(),
                guides=[
                    {
                        "title": "System Administration",
                        "content": self._load_content("user/admin/system.md")
                    },
                    {
                        "title": "User Management",
                        "content": self._load_content("user/admin/users.md")
                    },
                    {
                        "title": "Security",
                        "content": self._load_content("user/admin/security.md")
                    }
                ]
            )
            self.save_file(content, "user/admin_guides.md")
            self.sections["admin_guides"].append("admin_guides.md")
            
        except Exception as e:
            logger.error(f"Error generating admin guides: {str(e)}")
            raise
            
    def _generate_tutorials(self):
        """Generate tutorials"""
        try:
            template = self.load_template("tutorials.md")
            content = template.render(
                version_info=self.generate_version_info(),
                tutorials=[
                    {
                        "title": "Basic Usage",
                        "content": self._load_content("user/tutorials/basic.md")
                    },
                    {
                        "title": "Advanced Features",
                        "content": self._load_content("user/tutorials/advanced.md")
                    },
                    {
                        "title": "Integration",
                        "content": self._load_content("user/tutorials/integration.md")
                    }
                ]
            )
            self.save_file(content, "user/tutorials.md")
            self.sections["tutorials"].append("tutorials.md")
            
        except Exception as e:
            logger.error(f"Error generating tutorials: {str(e)}")
            raise
            
    def _generate_troubleshooting(self):
        """Generate troubleshooting documentation"""
        try:
            template = self.load_template("troubleshooting.md")
            content = template.render(
                version_info=self.generate_version_info(),
                sections=[
                    {
                        "title": "Common Issues",
                        "content": self._load_content("user/troubleshooting/common.md")
                    },
                    {
                        "title": "Error Messages",
                        "content": self._load_content("user/troubleshooting/errors.md")
                    },
                    {
                        "title": "Support",
                        "content": self._load_content("user/troubleshooting/support.md")
                    }
                ]
            )
            self.save_file(content, "user/troubleshooting.md")
            self.sections["troubleshooting"].append("troubleshooting.md")
            
        except Exception as e:
            logger.error(f"Error generating troubleshooting documentation: {str(e)}")
            raise
            
    def _generate_user_docs_navigation(self):
        """Generate navigation for user documentation"""
        try:
            template = self.load_template("user_navigation.md")
            content = template.render(
                sections=self.sections,
                version_info=self.generate_version_info()
            )
            self.save_file(content, "user/navigation.md")
        except Exception as e:
            logger.error(f"Error generating user documentation navigation: {str(e)}")
            raise
            
    def _generate_user_docs_index(self):
        """Generate index for user documentation"""
        try:
            template = self.load_template("user_index.md")
            content = template.render(
                sections=self.sections,
                version_info=self.generate_version_info()
            )
            self.save_file(content, "user/index.md")
        except Exception as e:
            logger.error(f"Error generating user documentation index: {str(e)}")
            raise
            
    def _load_content(self, file_path: str) -> str:
        """Load content from a markdown file"""
        try:
            full_path = self.output_dir / file_path
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    return f.read()
            return ""
        except Exception as e:
            logger.error(f"Error loading content from {file_path}: {str(e)}")
            return ""
            
    def generate_installation_guide(self, config: Dict[str, Any] = None) -> str:
        """Generate installation guide"""
        try:
            template = self.load_template("installation_guide.md")
            content = template.render(
                version_info=self.generate_version_info(),
                requirements=self._get_system_requirements(),
                steps=self._get_installation_steps(),
                config=config or {}
            )
            return content
        except Exception as e:
            logger.error(f"Error generating installation guide: {str(e)}")
            return ""
            
    def _get_system_requirements(self) -> Dict[str, Any]:
        """Get system requirements"""
        try:
            return {
                "hardware": {
                    "cpu": "2+ cores",
                    "memory": "4GB+ RAM",
                    "storage": "20GB+ free space"
                },
                "software": {
                    "os": ["Windows 10+", "macOS 10.15+", "Linux (Ubuntu 20.04+)"],
                    "python": "3.8+",
                    "node": "14+"
                },
                "dependencies": [
                    "PostgreSQL 12+",
                    "Redis 6+",
                    "Nginx 1.18+"
                ]
            }
        except Exception as e:
            logger.error(f"Error getting system requirements: {str(e)}")
            return {}
            
    def _get_installation_steps(self) -> List[Dict[str, Any]]:
        """Get installation steps"""
        try:
            return [
                {
                    "title": "Prerequisites",
                    "steps": [
                        "Install Python 3.8 or higher",
                        "Install Node.js 14 or higher",
                        "Install PostgreSQL 12 or higher",
                        "Install Redis 6 or higher"
                    ]
                },
                {
                    "title": "Backend Setup",
                    "steps": [
                        "Clone the repository",
                        "Create and activate virtual environment",
                        "Install Python dependencies",
                        "Configure environment variables",
                        "Run database migrations",
                        "Start the backend server"
                    ]
                },
                {
                    "title": "Frontend Setup",
                    "steps": [
                        "Navigate to frontend directory",
                        "Install Node.js dependencies",
                        "Configure environment variables",
                        "Build the frontend application",
                        "Start the frontend development server"
                    ]
                },
                {
                    "title": "Nginx Configuration",
                    "steps": [
                        "Install Nginx",
                        "Configure Nginx for the application",
                        "Set up SSL certificates",
                        "Start Nginx service"
                    ]
                }
            ]
        except Exception as e:
            logger.error(f"Error getting installation steps: {str(e)}")
            return []
            
    def generate_deployment_guide(self, config: Dict[str, Any] = None) -> str:
        """Generate deployment guide"""
        try:
            template = self.load_template("deployment_guide.md")
            content = template.render(
                version_info=self.generate_version_info(),
                environments=self._get_deployment_environments(),
                steps=self._get_deployment_steps(),
                config=config or {}
            )
            return content
        except Exception as e:
            logger.error(f"Error generating deployment guide: {str(e)}")
            return ""
            
    def _get_deployment_environments(self) -> Dict[str, Any]:
        """Get deployment environments"""
        try:
            return {
                "development": {
                    "description": "Local development environment",
                    "requirements": ["Docker", "Docker Compose"],
                    "steps": [
                        "Build development containers",
                        "Start development environment",
                        "Access development server"
                    ]
                },
                "staging": {
                    "description": "Staging environment for testing",
                    "requirements": ["AWS account", "Terraform"],
                    "steps": [
                        "Configure AWS credentials",
                        "Initialize Terraform",
                        "Apply infrastructure",
                        "Deploy application"
                    ]
                },
                "production": {
                    "description": "Production environment",
                    "requirements": ["AWS account", "Terraform", "CI/CD pipeline"],
                    "steps": [
                        "Configure production environment",
                        "Set up monitoring",
                        "Configure backup strategy",
                        "Deploy with zero downtime"
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Error getting deployment environments: {str(e)}")
            return {}
            
    def _get_deployment_steps(self) -> List[Dict[str, Any]]:
        """Get deployment steps"""
        try:
            return [
                {
                    "title": "Pre-deployment",
                    "steps": [
                        "Update version numbers",
                        "Run tests",
                        "Build application",
                        "Create deployment package"
                    ]
                },
                {
                    "title": "Deployment",
                    "steps": [
                        "Backup current version",
                        "Deploy new version",
                        "Run database migrations",
                        "Verify deployment"
                    ]
                },
                {
                    "title": "Post-deployment",
                    "steps": [
                        "Monitor application health",
                        "Check logs for errors",
                        "Verify functionality",
                        "Update documentation"
                    ]
                }
            ]
        except Exception as e:
            logger.error(f"Error getting deployment steps: {str(e)}")
            return [] 