from typing import Dict, List, Optional
import asyncio
from datetime import datetime
import logging
from uuid import uuid4

from models.codebase import Codebase, File
from services.utils.llm import LLMClient
from services.utils.code_analysis import CodeAnalyzer
from services.utils.telemetry import track_event

logger = logging.getLogger(__name__)

class CodeGeneratorAgent:
    def __init__(self):
        self.llm_client = LLMClient()
        self.code_analyzer = CodeAnalyzer()
        
    async def generate_code(self, architecture: Dict, style_guide: Optional[Dict] = None) -> Codebase:
        """
        Generate complete codebase from architecture specification
        """
        codebase = Codebase()
        
        # Generate project structure
        structure = await self._generate_project_structure(architecture)
        
        # Generate each component
        for component in architecture['components']:
            files = await self._generate_component(
                component,
                style_guide,
                structure['dependencies']
            )
            codebase.add_files(files)
            
        # Generate configuration files
        config_files = await self._generate_config_files(
            architecture,
            structure['config']
        )
        codebase.add_files(config_files)
        
        # Generate documentation
        docs = await self._generate_documentation(
            architecture,
            codebase
        )
        codebase.add_files(docs)
        
        return codebase
        
    async def apply_changes(self, codebase: Codebase, modifications: Dict) -> Codebase:
        """
        Apply changes to existing codebase
        """
        # Create copy of codebase
        updated_codebase = codebase.copy()
        
        for file_path, changes in modifications.items():
            if changes['action'] == 'modify':
                await self._modify_file(updated_codebase, file_path, changes['content'])
            elif changes['action'] == 'create':
                await self._create_file(updated_codebase, file_path, changes['content'])
            elif changes['action'] == 'delete':
                updated_codebase.remove_file(file_path)
                
        # Update dependencies if needed
        if 'dependencies' in modifications:
            await self._update_dependencies(updated_codebase, modifications['dependencies'])
            
        return updated_codebase
        
    async def _generate_project_structure(self, architecture: Dict) -> Dict:
        """
        Generate project structure including dependencies
        """
        structure_prompt = self._build_structure_prompt(architecture)
        
        structure = await self.llm_client.generate(
            structure_prompt,
            temperature=0.7,
            max_tokens=2000
        )
        
        return self._parse_structure(structure)
        
    async def _generate_component(self, component: Dict, style_guide: Optional[Dict], dependencies: Dict) -> List[File]:
        """
        Generate code files for a component
        """
        files = []
        
        # Generate main component code
        main_code = await self._generate_component_code(
            component,
            style_guide,
            dependencies
        )
        files.append(File(
            path=component['path'],
            content=main_code
        ))
        
        # Generate tests
        test_code = await self._generate_component_tests(
            component,
            main_code
        )
        files.append(File(
            path=f"tests/{component['path']}",
            content=test_code
        ))
        
        return files
        
    async def _generate_config_files(self, architecture: Dict, config: Dict) -> List[File]:
        """
        Generate configuration files for the project
        """
        config_files = []
        
        # Generate dependency management files
        if 'python' in architecture['tech_stack']:
            requirements = await self._generate_requirements_txt(config['dependencies'])
            config_files.append(File(
                path='requirements.txt',
                content=requirements
            ))
            
        if 'node' in architecture['tech_stack']:
            package_json = await self._generate_package_json(config['dependencies'])
            config_files.append(File(
                path='package.json',
                content=package_json
            ))
            
        # Generate deployment configs
        if config.get('kubernetes'):
            k8s_configs = await self._generate_kubernetes_configs(config['kubernetes'])
            config_files.extend(k8s_configs)
            
        return config_files
        
    async def _generate_documentation(self, architecture: Dict, codebase: Codebase) -> List[File]:
        """
        Generate project documentation
        """
        docs = []
        
        # Generate README
        readme = await self._generate_readme(architecture, codebase)
        docs.append(File(
            path='README.md',
            content=readme
        ))
        
        # Generate API documentation
        if architecture.get('api'):
            api_docs = await self._generate_api_docs(architecture['api'], codebase)
            docs.append(File(
                path='docs/api.md',
                content=api_docs
            ))
            
        # Generate deployment documentation
        deploy_docs = await self._generate_deployment_docs(architecture, codebase)
        docs.append(File(
            path='docs/deployment.md',
            content=deploy_docs
        ))
        
        return docs
        
    def _build_structure_prompt(self, architecture: Dict) -> str:
        """
        Build prompt for generating project structure
        """
        return f"""
        Generate a complete project structure for the following architecture:
        
        Architecture:
        {architecture}
        
        Please include:
        1. Directory structure
        2. File organization
        3. Dependencies
        4. Configuration files
        5. Build system setup
        6. Test organization
        7. Documentation structure
        """
