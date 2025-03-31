from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
import logging
import pkg_resources
import importlib
import re
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)

@dataclass
class DependencyInfo:
    """Information about a tool dependency"""
    name: str
    version: str
    required_by: str
    is_optional: bool
    conflicts: List[str]
    alternatives: List[str]

class DependencyResolver:
    """Resolver for tool dependencies and version compatibility"""
    
    def __init__(self):
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.version_constraints: Dict[str, str] = {}
        self.installed_packages: Dict[str, str] = {}
        self._load_installed_packages()
        
    def _load_installed_packages(self) -> None:
        """Load information about installed packages"""
        try:
            for package in pkg_resources.working_set:
                self.installed_packages[package.key] = package.version
        except Exception as e:
            logger.error(f"Error loading installed packages: {str(e)}")
            
    async def resolve_dependencies(self, tool_name: str, dependencies: List[str]) -> Tuple[bool, List[DependencyInfo]]:
        """Resolve dependencies for a tool"""
        try:
            resolved_deps = []
            conflicts = []
            
            for dep in dependencies:
                # Parse dependency string
                name, version = self._parse_dependency(dep)
                
                # Check if dependency is installed
                if name in self.installed_packages:
                    installed_version = self.installed_packages[name]
                    if self._check_version_compatibility(installed_version, version):
                        resolved_deps.append(DependencyInfo(
                            name=name,
                            version=installed_version,
                            required_by=tool_name,
                            is_optional=False,
                            conflicts=[],
                            alternatives=[]
                        ))
                    else:
                        conflicts.append(f"Version mismatch for {name}: required {version}, installed {installed_version}")
                else:
                    # Check for alternative packages
                    alternatives = self._find_alternative_packages(name)
                    if alternatives:
                        resolved_deps.append(DependencyInfo(
                            name=name,
                            version=version,
                            required_by=tool_name,
                            is_optional=True,
                            conflicts=[],
                            alternatives=alternatives
                        ))
                    else:
                        conflicts.append(f"Missing dependency: {name}")
                        
            return len(conflicts) == 0, resolved_deps
            
        except Exception as e:
            logger.error(f"Error resolving dependencies for {tool_name}: {str(e)}")
            return False, []
            
    def _parse_dependency(self, dependency: str) -> Tuple[str, str]:
        """Parse a dependency string into name and version"""
        try:
            # Handle different dependency formats
            if ">=" in dependency:
                name, version = dependency.split(">=")
                return name.strip(), f">={version.strip()}"
            elif "==" in dependency:
                name, version = dependency.split("==")
                return name.strip(), f"=={version.strip()}"
            elif "<=" in dependency:
                name, version = dependency.split("<=")
                return name.strip(), f"<={version.strip()}"
            else:
                return dependency.strip(), ">=0.0.0"
                
        except Exception as e:
            logger.error(f"Error parsing dependency {dependency}: {str(e)}")
            return dependency.strip(), ">=0.0.0"
            
    def _check_version_compatibility(self, installed: str, required: str) -> bool:
        """Check if installed version meets requirements"""
        try:
            if required.startswith(">="):
                return pkg_resources.parse_version(installed) >= pkg_resources.parse_version(required[2:])
            elif required.startswith("=="):
                return pkg_resources.parse_version(installed) == pkg_resources.parse_version(required[2:])
            elif required.startswith("<="):
                return pkg_resources.parse_version(installed) <= pkg_resources.parse_version(required[2:])
            else:
                return True
                
        except Exception as e:
            logger.error(f"Error checking version compatibility: {str(e)}")
            return False
            
    def _find_alternative_packages(self, package_name: str) -> List[str]:
        """Find alternative packages that provide similar functionality"""
        try:
            alternatives = []
            
            # Load package alternatives from configuration
            config_path = Path("src/core/tools/config/alternatives.yaml")
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)
                    if package_name in config:
                        alternatives.extend(config[package_name])
                        
            # Check for common alternatives
            common_alternatives = {
                "requests": ["aiohttp", "httpx"],
                "pandas": ["dask", "vaex"],
                "numpy": ["cupy", "jax"],
                "tensorflow": ["pytorch", "jax"],
                "scikit-learn": ["xgboost", "lightgbm"]
            }
            
            if package_name in common_alternatives:
                alternatives.extend(common_alternatives[package_name])
                
            return list(set(alternatives))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error finding alternative packages: {str(e)}")
            return []
            
    async def check_conflicts(self, tool_name: str, dependencies: List[DependencyInfo]) -> List[str]:
        """Check for dependency conflicts"""
        try:
            conflicts = []
            
            for dep in dependencies:
                # Check version conflicts
                if dep.name in self.version_constraints:
                    if not self._check_version_compatibility(dep.version, self.version_constraints[dep.name]):
                        conflicts.append(
                            f"Version conflict for {dep.name}: "
                            f"{tool_name} requires {dep.version}, "
                            f"but {self.version_constraints[dep.name]} is required"
                        )
                        
                # Check dependency conflicts
                if dep.name in self.dependency_graph:
                    for other_dep in self.dependency_graph[dep.name]:
                        if other_dep in dep.conflicts:
                            conflicts.append(
                                f"Dependency conflict: {dep.name} conflicts with {other_dep}"
                            )
                            
            return conflicts
            
        except Exception as e:
            logger.error(f"Error checking conflicts for {tool_name}: {str(e)}")
            return []
            
    async def update_dependency_graph(self, tool_name: str, dependencies: List[DependencyInfo]) -> None:
        """Update the dependency graph with new dependencies"""
        try:
            for dep in dependencies:
                if dep.name not in self.dependency_graph:
                    self.dependency_graph[dep.name] = set()
                self.dependency_graph[dep.name].add(tool_name)
                
                # Update version constraints
                if not dep.is_optional:
                    self.version_constraints[dep.name] = dep.version
                    
        except Exception as e:
            logger.error(f"Error updating dependency graph: {str(e)}")
            
    async def get_dependency_path(self, tool_name: str) -> List[str]:
        """Get the dependency path for a tool"""
        try:
            path = []
            visited = set()
            
            async def traverse(name: str) -> None:
                if name in visited:
                    return
                    
                visited.add(name)
                path.append(name)
                
                if name in self.dependency_graph:
                    for dep in self.dependency_graph[name]:
                        await traverse(dep)
                        
            await traverse(tool_name)
            return path
            
        except Exception as e:
            logger.error(f"Error getting dependency path for {tool_name}: {str(e)}")
            return [] 