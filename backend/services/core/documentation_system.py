from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import ast
import re
from datetime import datetime
import yaml
import json
from jinja2 import Environment, FileSystemLoader
import markdown2

from .monitoring import MonitoringService

logger = logging.getLogger(__name__)

class DocumentationType:
    API = "api"
    USER_GUIDE = "user_guide"
    TECHNICAL = "technical"
    CODE = "code"
    DEPLOYMENT = "deployment"

class DocumentationSystem:
    """System for generating and managing documentation"""
    
    def __init__(self, project_dir: str, template_dir: str):
        self.project_dir = Path(project_dir)
        self.template_dir = Path(template_dir)
        self.monitoring = MonitoringService()
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
        
        # Documentation storage
        self.docs: Dict[str, Dict[str, Any]] = {}
        
    async def generate_documentation(
        self,
        project_id: str,
        doc_type: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate documentation based on type"""
        try:
            options = options or {}
            
            if doc_type == DocumentationType.API:
                doc = await self._generate_api_docs(options)
            elif doc_type == DocumentationType.USER_GUIDE:
                doc = await self._generate_user_guide(options)
            elif doc_type == DocumentationType.TECHNICAL:
                doc = await self._generate_technical_docs(options)
            elif doc_type == DocumentationType.CODE:
                doc = await self._generate_code_docs(options)
            elif doc_type == DocumentationType.DEPLOYMENT:
                doc = await self._generate_deployment_docs(options)
            else:
                raise ValueError(f"Unknown documentation type: {doc_type}")
                
            # Store documentation
            doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.docs[doc_id] = {
                'id': doc_id,
                'project_id': project_id,
                'type': doc_type,
                'content': doc,
                'generated_at': datetime.now().isoformat(),
                'options': options
            }
            
            return self.docs[doc_id]
            
        except Exception as e:
            logger.error(f"Error generating {doc_type} documentation: {str(e)}")
            self.monitoring.record_error(
                error_id=f'doc_generation_{doc_type}',
                error=str(e)
            )
            raise
            
    async def _generate_api_docs(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate API documentation"""
        api_docs = {
            'endpoints': [],
            'models': [],
            'examples': [] if options.get('include_examples') else None,
            'schemas': [] if options.get('include_schemas') else None
        }
        
        # Parse FastAPI/Flask routes
        for file in self.project_dir.rglob('*.py'):
            try:
                code = file.read_text()
                tree = ast.parse(code)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Look for route decorators
                        for decorator in node.decorator_list:
                            if (isinstance(decorator, ast.Call) and
                                isinstance(decorator.func, ast.Attribute) and
                                decorator.func.attr in ['get', 'post', 'put', 'delete']):
                                
                                endpoint = self._parse_endpoint(node, decorator)
                                api_docs['endpoints'].append(endpoint)
                                
                    elif isinstance(node, ast.ClassDef):
                        # Look for Pydantic models
                        if any(base.id == 'BaseModel' 
                              for base in node.bases 
                              if isinstance(base, ast.Name)):
                            
                            model = self._parse_model(node)
                            api_docs['models'].append(model)
                            
            except Exception as e:
                logger.error(f"Error parsing {file}: {str(e)}")
                
        return api_docs
        
    async def _generate_user_guide(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate user guide documentation"""
        sections = options.get('sections', ['introduction', 'getting_started',
                                          'features', 'tutorials'])
        
        guide = {
            'title': 'User Guide',
            'sections': []
        }
        
        for section in sections:
            template = self.jinja_env.get_template(f'user_guide/{section}.md.j2')
            content = template.render(
                project_name=self.project_dir.name,
                include_examples=options.get('include_examples', True)
            )
            
            guide['sections'].append({
                'id': section,
                'title': section.replace('_', ' ').title(),
                'content': markdown2.markdown(content),
                'examples': await self._generate_examples(section)
                if options.get('include_examples') else None
            })
            
        return guide
        
    async def _generate_technical_docs(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate technical documentation"""
        docs = {
            'title': 'Technical Documentation',
            'architecture': await self._generate_architecture_docs()
            if options.get('include_architecture') else None,
            'components': [],
            'dependencies': await self._analyze_dependencies(),
            'deployment': await self._generate_deployment_docs(options)
            if options.get('include_deployment') else None
        }
        
        # Analyze components
        for file in self.project_dir.rglob('*.py'):
            try:
                code = file.read_text()
                tree = ast.parse(code)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        component = self._parse_component(node, code)
                        if component:
                            docs['components'].append(component)
                            
            except Exception as e:
                logger.error(f"Error analyzing {file}: {str(e)}")
                
        return docs
        
    async def _generate_code_docs(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code documentation"""
        docs = {
            'modules': [],
            'classes': [],
            'functions': [],
            'metrics': {
                'total_lines': 0,
                'code_lines': 0,
                'doc_coverage': 0.0
            }
        }
        
        total_items = 0
        documented_items = 0
        
        for file in self.project_dir.rglob('*.py'):
            try:
                code = file.read_text()
                tree = ast.parse(code)
                
                # Module documentation
                if ast.get_docstring(tree):
                    documented_items += 1
                total_items += 1
                
                docs['modules'].append({
                    'name': file.relative_to(self.project_dir).as_posix(),
                    'docstring': ast.get_docstring(tree),
                    'imports': self._extract_imports(tree)
                })
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if ast.get_docstring(node):
                            documented_items += 1
                        total_items += 1
                        
                        docs['classes'].append({
                            'name': node.name,
                            'docstring': ast.get_docstring(node),
                            'methods': self._extract_methods(node),
                            'file': file.relative_to(self.project_dir).as_posix()
                        })
                        
                    elif isinstance(node, ast.FunctionDef):
                        if ast.get_docstring(node):
                            documented_items += 1
                        total_items += 1
                        
                        docs['functions'].append({
                            'name': node.name,
                            'docstring': ast.get_docstring(node),
                            'arguments': self._extract_arguments(node),
                            'returns': self._extract_return_type(node),
                            'file': file.relative_to(self.project_dir).as_posix()
                        })
                        
                # Update metrics
                docs['metrics']['total_lines'] += len(code.splitlines())
                docs['metrics']['code_lines'] += len([l for l in code.splitlines()
                                                    if l.strip() and not l.strip().startswith('#')])
                
            except Exception as e:
                logger.error(f"Error documenting {file}: {str(e)}")
                
        docs['metrics']['doc_coverage'] = (documented_items / total_items
                                         if total_items > 0 else 0.0)
        
        return docs
        
    async def _generate_deployment_docs(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate deployment documentation"""
        docs = {
            'title': 'Deployment Guide',
            'requirements': await self._analyze_requirements(),
            'docker': await self._analyze_docker(),
            'environment': await self._analyze_environment(),
            'scripts': await self._analyze_scripts()
        }
        
        return docs
        
    def _parse_endpoint(self, node: ast.FunctionDef, decorator: ast.Call) -> Dict[str, Any]:
        """Parse API endpoint information"""
        endpoint = {
            'name': node.name,
            'method': decorator.func.attr,
            'path': '',
            'parameters': self._extract_arguments(node),
            'returns': self._extract_return_type(node),
            'docstring': ast.get_docstring(node)
        }
        
        # Extract path from decorator
        if decorator.args:
            endpoint['path'] = decorator.args[0].s
            
        return endpoint
        
    def _parse_model(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Parse Pydantic model information"""
        return {
            'name': node.name,
            'fields': self._extract_model_fields(node),
            'docstring': ast.get_docstring(node)
        }
        
    def _parse_component(self, node: ast.ClassDef, code: str) -> Optional[Dict[str, Any]]:
        """Parse component information"""
        # Check if it's a component (has certain base classes or decorators)
        if not any(base.id in ['Component', 'Service', 'Manager']
                  for base in node.bases
                  if isinstance(base, ast.Name)):
            return None
            
        return {
            'name': node.name,
            'type': next(base.id for base in node.bases
                        if isinstance(base, ast.Name)
                        and base.id in ['Component', 'Service', 'Manager']),
            'methods': self._extract_methods(node),
            'dependencies': self._extract_dependencies_from_code(code),
            'docstring': ast.get_docstring(node)
        }
        
    def _extract_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract import information"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append({
                        'name': name.name,
                        'alias': name.asname
                    })
            elif isinstance(node, ast.ImportFrom):
                imports.append({
                    'module': node.module,
                    'names': [{'name': n.name, 'alias': n.asname}
                             for n in node.names]
                })
        return imports
        
    def _extract_methods(self, node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Extract method information"""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append({
                    'name': item.name,
                    'arguments': self._extract_arguments(item),
                    'returns': self._extract_return_type(item),
                    'docstring': ast.get_docstring(item),
                    'is_async': isinstance(item, ast.AsyncFunctionDef)
                })
        return methods
        
    def _extract_arguments(self, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """Extract function arguments"""
        args = []
        for arg in node.args.args:
            args.append({
                'name': arg.arg,
                'type': self._extract_type_annotation(arg.annotation)
                if hasattr(arg, 'annotation') and arg.annotation else None
            })
        return args
        
    def _extract_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract function return type"""
        if node.returns:
            return self._extract_type_annotation(node.returns)
        return None
        
    def _extract_type_annotation(self, node: Optional[ast.AST]) -> Optional[str]:
        """Extract type annotation"""
        if node is None:
            return None
            
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            value = self._extract_type_annotation(node.value)
            slice_value = self._extract_type_annotation(node.slice)
            return f"{value}[{slice_value}]"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return None
        
    def _extract_model_fields(self, node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Extract Pydantic model fields"""
        fields = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                fields.append({
                    'name': item.target.id,
                    'type': self._extract_type_annotation(item.annotation),
                    'default': self._extract_default_value(item.value)
                    if item.value else None
                })
        return fields
        
    def _extract_default_value(self, node: ast.AST) -> Any:
        """Extract default value from AST node"""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.List):
            return [self._extract_default_value(elt) for elt in node.elts]
        elif isinstance(node, ast.Dict):
            return {
                self._extract_default_value(k): self._extract_default_value(v)
                for k, v in zip(node.keys, node.values)
            }
        return None
        
    async def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies"""
        deps = {
            'python': {},
            'node': None,
            'system': []
        }
        
        # Python dependencies
        requirements_file = self.project_dir / 'requirements.txt'
        if requirements_file.exists():
            deps['python']['requirements'] = requirements_file.read_text().splitlines()
            
        pipfile = self.project_dir / 'Pipfile'
        if pipfile.exists():
            deps['python']['pipfile'] = toml.load(pipfile)
            
        # Node dependencies
        package_json = self.project_dir / 'package.json'
        if package_json.exists():
            deps['node'] = json.loads(package_json.read_text())
            
        # System dependencies from Dockerfile
        dockerfile = self.project_dir / 'Dockerfile'
        if dockerfile.exists():
            content = dockerfile.read_text()
            # Extract apt-get install commands
            installs = re.findall(r'apt-get install -y\s+([^\n]+)', content)
            deps['system'].extend(
                pkg.strip()
                for line in installs
                for pkg in line.split()
            )
            
        return deps
        
    async def _analyze_requirements(self) -> Dict[str, Any]:
        """Analyze deployment requirements"""
        reqs = {
            'system': {
                'cpu': 'Not specified',
                'memory': 'Not specified',
                'disk': 'Not specified'
            },
            'services': [],
            'ports': [],
            'environment': []
        }
        
        # Check docker-compose
        compose_file = self.project_dir / 'docker-compose.yml'
        if compose_file.exists():
            compose = yaml.safe_load(compose_file.read_text())
            
            for service in compose.get('services', {}).values():
                reqs['services'].append({
                    'name': service.get('container_name', 'unknown'),
                    'image': service.get('image'),
                    'ports': service.get('ports', []),
                    'environment': service.get('environment', [])
                })
                
                # Extract resource limits
                if 'deploy' in service:
                    resources = service['deploy'].get('resources', {})
                    limits = resources.get('limits', {})
                    reqs['system'].update({
                        'cpu': limits.get('cpus', 'Not specified'),
                        'memory': limits.get('memory', 'Not specified')
                    })
                    
        return reqs
        
    async def _analyze_docker(self) -> Dict[str, Any]:
        """Analyze Docker configuration"""
        docker = {
            'images': [],
            'networks': [],
            'volumes': []
        }
        
        # Parse Dockerfile
        dockerfile = self.project_dir / 'Dockerfile'
        if dockerfile.exists():
            content = dockerfile.read_text()
            docker['images'].append({
                'base': re.search(r'FROM\s+([^\n]+)', content).group(1),
                'steps': len(re.findall(r'RUN\s+', content)),
                'ports': re.findall(r'EXPOSE\s+(\d+)', content),
                'commands': re.findall(r'CMD\s+([^\n]+)', content)
            })
            
        # Parse docker-compose
        compose_file = self.project_dir / 'docker-compose.yml'
        if compose_file.exists():
            compose = yaml.safe_load(compose_file.read_text())
            docker['networks'] = list(compose.get('networks', {}).keys())
            docker['volumes'] = list(compose.get('volumes', {}).keys())
            
        return docker
        
    async def _analyze_environment(self) -> Dict[str, Any]:
        """Analyze environment configuration"""
        env = {
            'variables': [],
            'configs': []
        }
        
        # Check .env files
        for env_file in self.project_dir.glob('.env*'):
            if env_file.is_file():
                vars = []
                for line in env_file.read_text().splitlines():
                    if '=' in line and not line.startswith('#'):
                        key = line.split('=')[0]
                        vars.append({
                            'name': key,
                            'required': not any(
                                line.lower().startswith(('#optional', '# optional'))
                                for line in env_file.read_text().splitlines()
                                if line.startswith('#') and key in line
                            )
                        })
                env['variables'].extend(vars)
                
        # Check config files
        for config_file in self.project_dir.rglob('*.yaml'):
            if config_file.is_file():
                try:
                    config = yaml.safe_load(config_file.read_text())
                    env['configs'].append({
                        'file': config_file.relative_to(self.project_dir).as_posix(),
                        'keys': list(config.keys())
                    })
                except Exception as e:
                    logger.error(f"Error parsing {config_file}: {str(e)}")
                    
        return env
        
    async def _analyze_scripts(self) -> Dict[str, Any]:
        """Analyze deployment scripts"""
        scripts = []
        
        # Look for shell scripts
        for script in self.project_dir.rglob('*.sh'):
            if script.is_file():
                content = script.read_text()
                scripts.append({
                    'name': script.name,
                    'path': script.relative_to(self.project_dir).as_posix(),
                    'description': next(
                        (line.lstrip('#').strip()
                         for line in content.splitlines()
                         if line.strip().startswith('#')),
                        'No description'
                    ),
                    'commands': len([line
                                   for line in content.splitlines()
                                   if line.strip() and not line.strip().startswith('#')])
                })
                
        return scripts
        
    async def _generate_examples(self, section: str) -> List[Dict[str, Any]]:
        """Generate examples for documentation"""
        examples = []
        
        # Load example templates
        example_dir = self.template_dir / 'examples' / section
        if example_dir.exists():
            for example in example_dir.glob('*.md.j2'):
                template = self.jinja_env.get_template(
                    str(example.relative_to(self.template_dir))
                )
                content = template.render()
                
                examples.append({
                    'title': example.stem.replace('_', ' ').title(),
                    'content': markdown2.markdown(content)
                })
                
        return examples
