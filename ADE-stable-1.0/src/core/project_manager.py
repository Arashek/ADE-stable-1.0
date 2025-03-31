import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import yaml
from datetime import datetime
import git
from git import GitCommandError
import shutil
import os
from .integrations.github import GitHubClient
from .integrations.gitlab import GitLabClient
from .integrations.bitbucket import BitBucketClient
from .models.repository import Repository
from .models.project import Project, ProjectTemplate

logger = logging.getLogger(__name__)

class ProjectManager:
    """Manages projects in the ADE Platform"""
    
    def __init__(self, projects_dir: str = "projects"):
        """Initialize the project manager
        
        Args:
            projects_dir: Directory for storing projects
        """
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.github_client = GitHubClient()
        self.gitlab_client = GitLabClient()
        self.bitbucket_client = BitBucketClient()
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, ProjectTemplate]:
        """Load project templates from templates directory."""
        templates = {}
        templates_dir = Path(__file__).parent / "templates"
        if templates_dir.exists():
            for template_dir in templates_dir.iterdir():
                if template_dir.is_dir():
                    template_config = template_dir / "config.yaml"
                    if template_config.exists():
                        with open(template_config) as f:
                            config = yaml.safe_load(f)
                            templates[template_dir.name] = ProjectTemplate(
                                name=template_dir.name,
                                description=config.get("description", ""),
                                structure=config.get("structure", {}),
                                dependencies=config.get("dependencies", {}),
                                setup_scripts=config.get("setup_scripts", [])
                            )
        return templates
        
    async def create_project(
        self,
        name: str,
        config: Dict,
        template: Optional[str] = None,
        repository_url: Optional[str] = None,
        branch: Optional[str] = None
    ) -> Optional[Project]:
        """Create a new project
        
        Args:
            name: Project name
            config: Project configuration
            template: Optional template to use
            repository_url: Optional repository URL to clone
            branch: Optional branch to clone
            
        Returns:
            Project if successful, None otherwise
        """
        try:
            # Create project directory
            project_dir = self.projects_dir / name
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize repository if URL provided
            repository = None
            if repository_url:
                repository = await self._clone_repository(repository_url, branch)
                if not repository:
                    return None
                    
            # Apply template if specified
            if template and template in self.templates:
                await self._apply_template(project_dir, template)
                
            # Create project structure
            (project_dir / "src").mkdir(exist_ok=True)
            (project_dir / "tests").mkdir(exist_ok=True)
            (project_dir / "docs").mkdir(exist_ok=True)
            (project_dir / "data").mkdir(exist_ok=True)
            
            # Save project configuration
            config_file = project_dir / "config.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
                
            # Create project metadata
            metadata = {
                "name": name,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "active",
                "template": template,
                "repository": repository.to_dict() if repository else None
            }
            
            metadata_file = project_dir / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)
                
            # Create project object
            project = Project(
                id=str(project_dir),
                name=name,
                directory=str(project_dir),
                config=config,
                metadata=metadata,
                repository=repository
            )
            
            logger.info(f"Created project: {name}")
            return project
            
        except Exception as e:
            logger.error(f"Failed to create project {name}: {str(e)}")
            return None
            
    async def _clone_repository(
        self,
        url: str,
        branch: Optional[str] = None
    ) -> Optional[Repository]:
        """Clone a repository from a URL."""
        try:
            # Determine repository type
            if "github.com" in url:
                client = self.github_client
            elif "gitlab.com" in url:
                client = self.gitlab_client
            elif "bitbucket.org" in url:
                client = self.bitbucket_client
            else:
                raise ValueError("Unsupported repository type")
                
            # Clone repository
            repository = await client.clone_repository(url, branch)
            return repository
            
        except Exception as e:
            logger.error(f"Failed to clone repository {url}: {str(e)}")
            return None
            
    async def _apply_template(
        self,
        project_dir: Path,
        template_name: str
    ) -> bool:
        """Apply a project template."""
        try:
            template = self.templates[template_name]
            template_dir = Path(__file__).parent / "templates" / template_name
            
            # Copy template files
            for source, target in template.structure.items():
                source_path = template_dir / source
                target_path = project_dir / target
                
                if source_path.is_file():
                    shutil.copy2(source_path, target_path)
                elif source_path.is_dir():
                    shutil.copytree(source_path, target_path)
                    
            # Install dependencies
            if template.dependencies:
                await self._install_dependencies(project_dir, template.dependencies)
                
            # Run setup scripts
            for script in template.setup_scripts:
                await self._run_setup_script(project_dir, script)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply template {template_name}: {str(e)}")
            return False
            
    async def _install_dependencies(
        self,
        project_dir: Path,
        dependencies: Dict[str, Any]
    ) -> bool:
        """Install project dependencies."""
        try:
            # Create requirements.txt if needed
            if "python" in dependencies:
                requirements_file = project_dir / "requirements.txt"
                with open(requirements_file, 'w') as f:
                    for package, version in dependencies["python"].items():
                        f.write(f"{package}=={version}\n")
                        
            # Create package.json if needed
            if "node" in dependencies:
                package_json = project_dir / "package.json"
                with open(package_json, 'w') as f:
                    json.dump({
                        "name": project_dir.name,
                        "version": "1.0.0",
                        "dependencies": dependencies["node"]
                    }, f, indent=4)
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to install dependencies: {str(e)}")
            return False
            
    async def _run_setup_script(
        self,
        project_dir: Path,
        script: str
    ) -> bool:
        """Run a setup script."""
        try:
            script_path = project_dir / script
            if script_path.exists():
                os.chmod(script_path, 0o755)  # Make executable
                import subprocess
                subprocess.run([str(script_path)], cwd=str(project_dir), check=True)
            return True
            
        except Exception as e:
            logger.error(f"Failed to run setup script {script}: {str(e)}")
            return False 