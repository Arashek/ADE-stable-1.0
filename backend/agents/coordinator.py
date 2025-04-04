from typing import Dict, List, Optional
import asyncio
from datetime import datetime
import logging
from uuid import uuid4

from agents.base import BaseAgent
from agents.architecture import ArchitectureAgent
from agents.code_generator import CodeGeneratorAgent
from agents.test_writer import TestWriterAgent
from agents.reviewer import ReviewerAgent
from agents.deployer import DeployerAgent
from models.project import Project, ProjectStatus
from models.task import Task, TaskStatus
from services.utils.telemetry import track_event

logger = logging.getLogger(__name__)

class AgentCoordinator:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {
            'architecture': ArchitectureAgent(),
            'code_generator': CodeGeneratorAgent(),
            'test_writer': TestWriterAgent(),
            'reviewer': ReviewerAgent(),
            'deployer': DeployerAgent()
        }
        
        self.active_tasks: Dict[str, Task] = {}
        self.project_status: Dict[str, ProjectStatus] = {}
        
    async def process_project(self, project: Project) -> Dict:
        """
        Process a new project request autonomously
        """
        project_id = str(uuid4())
        self.project_status[project_id] = ProjectStatus.ANALYZING
        
        try:
            # 1. Analyze requirements and create architecture
            requirements = await self.agents['architecture'].analyze_requirements(
                project.description,
                project.constraints
            )
            
            architecture = await self.agents['architecture'].design_system(
                requirements,
                project.tech_stack
            )
            
            # 2. Generate codebase
            codebase = await self.agents['code_generator'].generate_code(
                architecture,
                project.style_guide
            )
            
            # 3. Write tests
            tests = await self.agents['test_writer'].generate_tests(
                codebase,
                requirements
            )
            
            # 4. Code review and optimization
            review_results = await self.agents['reviewer'].review_code(
                codebase,
                tests,
                project.quality_standards
            )
            
            if review_results['needs_changes']:
                codebase = await self.agents['code_generator'].apply_changes(
                    codebase,
                    review_results['suggestions']
                )
            
            # 5. Setup deployment
            deployment = await self.agents['deployer'].setup_project(
                codebase,
                tests,
                project.deployment_config
            )
            
            self.project_status[project_id] = ProjectStatus.COMPLETED
            
            return {
                'project_id': project_id,
                'status': 'success',
                'architecture': architecture,
                'codebase': codebase,
                'tests': tests,
                'deployment': deployment
            }
            
        except Exception as e:
            logger.error(f"Project {project_id} failed: {str(e)}")
            self.project_status[project_id] = ProjectStatus.FAILED
            raise
            
    async def get_project_status(self, project_id: str) -> ProjectStatus:
        """
        Get current status of a project
        """
        return self.project_status.get(project_id, ProjectStatus.NOT_FOUND)
        
    async def update_project(self, project_id: str, changes: Dict) -> Dict:
        """
        Update an existing project with changes
        """
        if project_id not in self.project_status:
            raise ValueError(f"Project {project_id} not found")
            
        self.project_status[project_id] = ProjectStatus.UPDATING
        
        try:
            # Apply changes to existing project
            updated_codebase = await self.agents['code_generator'].apply_changes(
                changes['codebase'],
                changes['modifications']
            )
            
            # Update tests
            updated_tests = await self.agents['test_writer'].update_tests(
                updated_codebase,
                changes['test_modifications']
            )
            
            # Review changes
            review_results = await self.agents['reviewer'].review_changes(
                updated_codebase,
                updated_tests
            )
            
            self.project_status[project_id] = ProjectStatus.COMPLETED
            
            return {
                'status': 'success',
                'updated_codebase': updated_codebase,
                'updated_tests': updated_tests,
                'review': review_results
            }
            
        except Exception as e:
            logger.error(f"Project update {project_id} failed: {str(e)}")
            self.project_status[project_id] = ProjectStatus.FAILED
            raise
