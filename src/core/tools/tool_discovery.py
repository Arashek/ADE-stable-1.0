from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import logging
import importlib
import inspect
import pkg_resources
from dataclasses import dataclass
import json
import yaml
import ast
import re
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ToolMetadata:
    """Metadata for discovered tools"""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str]
    requirements: List[str]
    capabilities: List[str]
    parameters: Dict[str, Any]
    return_type: str
    compatibility: Dict[str, Any]
    last_updated: datetime

class ToolDiscovery:
    """Enhanced tool discovery and compatibility checking"""
    
    def __init__(self):
        self.discovered_tools: Dict[str, ToolMetadata] = {}
        self.tool_dependencies: Dict[str, Set[str]] = {}
        self.compatibility_matrix: Dict[str, Dict[str, bool]] = {}
        
    def discover_tools(self, search_paths: List[str]) -> List[ToolMetadata]:
        """Discover tools in specified paths"""
        discovered = []
        
        for path in search_paths:
            try:
                # Scan directory for Python files
                for file_path in Path(path).rglob("*.py"):
                    tools = self._scan_file(file_path)
                    discovered.extend(tools)
                    
                # Scan for package dependencies
                self._scan_dependencies(path)
                
            except Exception as e:
                logger.error(f"Error discovering tools in {path}: {e}")
                
        return discovered
        
    def _scan_file(self, file_path: Path) -> List[ToolMetadata]:
        """Scan a Python file for tools"""
        tools = []
        
        try:
            # Parse file
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read())
                
            # Find tool definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if self._is_tool_function(node):
                        tool = self._extract_tool_metadata(node, file_path)
                        if tool:
                            tools.append(tool)
                            
        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {e}")
            
        return tools
        
    def _is_tool_function(self, node: ast.FunctionDef) -> bool:
        """Check if a function is a tool"""
        # Check for tool decorator
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "tool":
                return True
                
        # Check for tool-related docstring
        if node.body and isinstance(node.body[0], ast.Expr):
            if isinstance(node.body[0].value, ast.Constant):
                docstring = node.body[0].value.value.lower()
                if "tool" in docstring or "command" in docstring:
                    return True
                    
        return False
        
    def _extract_tool_metadata(self, node: ast.FunctionDef, file_path: Path) -> Optional[ToolMetadata]:
        """Extract metadata from a tool function"""
        try:
            # Get function signature
            sig = inspect.signature(eval(node.name))
            
            # Extract parameters
            parameters = {}
            for param_name, param in sig.parameters.items():
                parameters[param_name] = {
                    "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                    "default": str(param.default) if param.default != inspect.Parameter.empty else None,
                    "required": param.default == inspect.Parameter.empty
                }
                
            # Get return type
            return_type = str(sig.return_annotation) if sig.return_annotation != inspect.Parameter.empty else "Any"
            
            # Get docstring
            docstring = ast.get_docstring(node) or ""
            
            # Extract dependencies from imports
            dependencies = self._extract_dependencies(file_path)
            
            # Extract requirements from docstring
            requirements = self._extract_requirements(docstring)
            
            # Extract capabilities from docstring
            capabilities = self._extract_capabilities(docstring)
            
            # Create tool metadata
            return ToolMetadata(
                name=node.name,
                version=self._get_package_version(file_path),
                description=docstring.split("\n")[0],
                author=self._extract_author(docstring),
                dependencies=dependencies,
                requirements=requirements,
                capabilities=capabilities,
                parameters=parameters,
                return_type=return_type,
                compatibility=self._check_compatibility(dependencies),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error extracting tool metadata: {e}")
            return None
            
    def _extract_dependencies(self, file_path: Path) -> List[str]:
        """Extract dependencies from a Python file"""
        dependencies = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Find import statements
            import_pattern = r"^(?:from\s+(\w+)\s+import|\s*import\s+(\w+))"
            for line in content.split("\n"):
                match = re.match(import_pattern, line)
                if match:
                    module = match.group(1) or match.group(2)
                    if module:
                        dependencies.append(module)
                        
        except Exception as e:
            logger.error(f"Error extracting dependencies: {e}")
            
        return dependencies
        
    def _extract_requirements(self, docstring: str) -> List[str]:
        """Extract requirements from docstring"""
        requirements = []
        
        # Look for requirements section
        if "requirements:" in docstring.lower():
            requirements_section = docstring.split("requirements:")[1].split("\n")[0]
            requirements = [req.strip() for req in requirements_section.split(",")]
            
        return requirements
        
    def _extract_capabilities(self, docstring: str) -> List[str]:
        """Extract capabilities from docstring"""
        capabilities = []
        
        # Look for capabilities section
        if "capabilities:" in docstring.lower():
            capabilities_section = docstring.split("capabilities:")[1].split("\n")[0]
            capabilities = [cap.strip() for cap in capabilities_section.split(",")]
            
        return capabilities
        
    def _extract_author(self, docstring: str) -> str:
        """Extract author from docstring"""
        # Look for author section
        if "author:" in docstring.lower():
            author_section = docstring.split("author:")[1].split("\n")[0]
            return author_section.strip()
            
        return "Unknown"
        
    def _get_package_version(self, file_path: Path) -> str:
        """Get package version from setup.py or pyproject.toml"""
        try:
            # Check setup.py
            setup_path = file_path.parent / "setup.py"
            if setup_path.exists():
                with open(setup_path, 'r') as f:
                    content = f.read()
                    version_match = re.search(r"version=['\"]([^'\"]+)['\"]", content)
                    if version_match:
                        return version_match.group(1)
                        
            # Check pyproject.toml
            pyproject_path = file_path.parent / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, 'r') as f:
                    content = f.read()
                    version_match = re.search(r"version\s*=\s*['\"]([^'\"]+)['\"]", content)
                    if version_match:
                        return version_match.group(1)
                        
        except Exception as e:
            logger.error(f"Error getting package version: {e}")
            
        return "0.0.0"
        
    def _check_compatibility(self, dependencies: List[str]) -> Dict[str, Any]:
        """Check compatibility of dependencies"""
        compatibility = {}
        
        for dep in dependencies:
            try:
                # Check if package is installed
                pkg = pkg_resources.get_distribution(dep)
                
                # Get version constraints
                version_constraints = self._get_version_constraints(dep)
                
                # Check version compatibility
                is_compatible = self._check_version_compatibility(
                    pkg.version,
                    version_constraints
                )
                
                compatibility[dep] = {
                    "installed": True,
                    "version": pkg.version,
                    "compatible": is_compatible,
                    "constraints": version_constraints
                }
                
            except pkg_resources.DistributionNotFound:
                compatibility[dep] = {
                    "installed": False,
                    "version": None,
                    "compatible": False,
                    "constraints": None
                }
                
        return compatibility
        
    def _get_version_constraints(self, package: str) -> Dict[str, str]:
        """Get version constraints for a package"""
        constraints = {}
        
        try:
            # Check setup.py
            setup_path = Path(package) / "setup.py"
            if setup_path.exists():
                with open(setup_path, 'r') as f:
                    content = f.read()
                    install_requires = re.search(r"install_requires\s*=\s*\[(.*?)\]", content)
                    if install_requires:
                        for req in install_requires.group(1).split(","):
                            req = req.strip().strip("'\"")
                            if ">=" in req:
                                pkg, version = req.split(">=")
                                constraints[pkg.strip()] = f">={version.strip()}"
                            elif "==" in req:
                                pkg, version = req.split("==")
                                constraints[pkg.strip()] = f"=={version.strip()}"
                                
        except Exception as e:
            logger.error(f"Error getting version constraints: {e}")
            
        return constraints
        
    def _check_version_compatibility(self, 
                                   installed_version: str,
                                   constraints: Dict[str, str]) -> bool:
        """Check if installed version meets constraints"""
        try:
            for pkg, constraint in constraints.items():
                if not pkg_resources.parse_version(installed_version) >= pkg_resources.parse_version(constraint):
                    return False
            return True
        except Exception:
            return False
            
    def _scan_dependencies(self, path: str) -> None:
        """Scan for package dependencies"""
        try:
            # Find setup.py or pyproject.toml
            setup_path = Path(path) / "setup.py"
            pyproject_path = Path(path) / "pyproject.toml"
            
            if setup_path.exists():
                self._scan_setup_py(setup_path)
            elif pyproject_path.exists():
                self._scan_pyproject_toml(pyproject_path)
                
        except Exception as e:
            logger.error(f"Error scanning dependencies: {e}")
            
    def _scan_setup_py(self, setup_path: Path) -> None:
        """Scan setup.py for dependencies"""
        try:
            with open(setup_path, 'r') as f:
                content = f.read()
                
            # Find install_requires
            install_requires = re.search(r"install_requires\s*=\s*\[(.*?)\]", content)
            if install_requires:
                for req in install_requires.group(1).split(","):
                    req = req.strip().strip("'\"")
                    if ">=" in req:
                        pkg, version = req.split(">=")
                        self.tool_dependencies[pkg.strip()] = {version.strip()}
                        
        except Exception as e:
            logger.error(f"Error scanning setup.py: {e}")
            
    def _scan_pyproject_toml(self, pyproject_path: Path) -> None:
        """Scan pyproject.toml for dependencies"""
        try:
            with open(pyproject_path, 'r') as f:
                content = f.read()
                
            # Find dependencies section
            dependencies = re.search(r"\[tool\.poetry\.dependencies\](.*?)\[", content, re.DOTALL)
            if dependencies:
                for line in dependencies.group(1).split("\n"):
                    if "=" in line:
                        pkg, version = line.split("=")
                        self.tool_dependencies[pkg.strip()] = {version.strip()}
                        
        except Exception as e:
            logger.error(f"Error scanning pyproject.toml: {e}")
            
    def get_tool_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """Get metadata for a specific tool"""
        return self.discovered_tools.get(tool_name)
        
    def get_compatibility_matrix(self) -> Dict[str, Dict[str, bool]]:
        """Get compatibility matrix for all tools"""
        return self.compatibility_matrix
        
    def get_tool_dependencies(self) -> Dict[str, Set[str]]:
        """Get dependencies for all tools"""
        return self.tool_dependencies 