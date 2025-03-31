from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
import logging
import sys
import platform
import importlib
import inspect
import re
from pathlib import Path
import yaml
import ast

from .dependency_resolver import DependencyResolver, DependencyInfo

logger = logging.getLogger(__name__)

@dataclass
class CompatibilityResult:
    """Result of compatibility checking"""
    is_compatible: bool
    issues: List[str]
    warnings: List[str]
    suggestions: List[str]
    system_requirements: Dict[str, str]
    tool_requirements: Dict[str, str]

class CompatibilityChecker:
    """Checker for tool compatibility with system and other tools"""
    
    def __init__(self, dependency_resolver: DependencyResolver):
        self.dependency_resolver = dependency_resolver
        self.system_info = self._get_system_info()
        self._load_compatibility_rules()
        
    def _get_system_info(self) -> Dict[str, str]:
        """Get information about the current system"""
        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "system": platform.system()
        }
        
    def _load_compatibility_rules(self) -> None:
        """Load compatibility rules from configuration"""
        try:
            config_path = Path("src/core/tools/config/compatibility.yaml")
            if config_path.exists():
                with open(config_path, "r") as f:
                    self.rules = yaml.safe_load(f)
            else:
                logger.warning("Compatibility rules configuration not found")
                self.rules = {}
                
        except Exception as e:
            logger.error(f"Error loading compatibility rules: {str(e)}")
            self.rules = {}
            
    async def check_compatibility(self, tool_name: str, tool_class: type) -> CompatibilityResult:
        """Check compatibility of a tool with the system and other tools"""
        try:
            issues = []
            warnings = []
            suggestions = []
            
            # Check system requirements
            system_requirements = self._extract_system_requirements(tool_class)
            system_compatible, system_issues = self._check_system_compatibility(system_requirements)
            if not system_compatible:
                issues.extend(system_issues)
                
            # Check dependencies
            dependencies = getattr(tool_class, "dependencies", [])
            dep_compatible, dep_info = await self.dependency_resolver.resolve_dependencies(tool_name, dependencies)
            if not dep_compatible:
                issues.extend([f"Dependency issue: {dep}" for dep in dep_info])
                
            # Check conflicts
            conflicts = await self.dependency_resolver.check_conflicts(tool_name, dep_info)
            if conflicts:
                issues.extend(conflicts)
                
            # Check code compatibility
            code_compatible, code_issues = self._check_code_compatibility(tool_class)
            if not code_compatible:
                issues.extend(code_issues)
                
            # Check resource requirements
            resource_compatible, resource_warnings = self._check_resource_requirements(tool_class)
            if not resource_compatible:
                warnings.extend(resource_warnings)
                
            # Generate suggestions
            suggestions.extend(self._generate_suggestions(issues, warnings))
            
            return CompatibilityResult(
                is_compatible=len(issues) == 0,
                issues=issues,
                warnings=warnings,
                suggestions=suggestions,
                system_requirements=system_requirements,
                tool_requirements=self._extract_tool_requirements(tool_class)
            )
            
        except Exception as e:
            logger.error(f"Error checking compatibility for {tool_name}: {str(e)}")
            return CompatibilityResult(
                is_compatible=False,
                issues=[str(e)],
                warnings=[],
                suggestions=[],
                system_requirements={},
                tool_requirements={}
            )
            
    def _extract_system_requirements(self, tool_class: type) -> Dict[str, str]:
        """Extract system requirements from tool class"""
        requirements = {}
        
        # Check docstring for requirements
        if tool_class.__doc__:
            doc = tool_class.__doc__.lower()
            if "requires" in doc:
                # Extract requirements from docstring
                reqs = re.findall(r"requires:?\s*([^\n]+)", doc)
                for req in reqs:
                    if "python" in req:
                        requirements["python_version"] = req
                    elif "os" in req:
                        requirements["os"] = req
                    elif "processor" in req:
                        requirements["processor"] = req
                        
        # Check class attributes
        if hasattr(tool_class, "system_requirements"):
            requirements.update(tool_class.system_requirements)
            
        return requirements
        
    def _check_system_compatibility(self, requirements: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Check if system meets requirements"""
        issues = []
        
        for req_type, req_value in requirements.items():
            if req_type == "python_version":
                if not self._check_python_version(req_value):
                    issues.append(f"Python version requirement not met: {req_value}")
            elif req_type == "os":
                if not self._check_os_compatibility(req_value):
                    issues.append(f"OS requirement not met: {req_value}")
            elif req_type == "processor":
                if not self._check_processor_compatibility(req_value):
                    issues.append(f"Processor requirement not met: {req_value}")
                    
        return len(issues) == 0, issues
        
    def _check_python_version(self, requirement: str) -> bool:
        """Check if Python version meets requirement"""
        try:
            current_version = sys.version_info
            required_version = tuple(map(int, requirement.split(".")))
            return current_version >= required_version
        except Exception:
            return False
            
    def _check_os_compatibility(self, requirement: str) -> bool:
        """Check if OS meets requirement"""
        try:
            current_os = platform.system().lower()
            required_os = requirement.lower()
            return current_os in required_os or required_os in current_os
        except Exception:
            return False
            
    def _check_processor_compatibility(self, requirement: str) -> bool:
        """Check if processor meets requirement"""
        try:
            current_processor = platform.processor().lower()
            required_processor = requirement.lower()
            return current_processor in required_processor or required_processor in current_processor
        except Exception:
            return False
            
    def _check_code_compatibility(self, tool_class: type) -> Tuple[bool, List[str]]:
        """Check code compatibility"""
        issues = []
        
        try:
            # Get source code
            source = inspect.getsource(tool_class)
            
            # Parse AST
            tree = ast.parse(source)
            
            # Check for incompatible features
            for node in ast.walk(tree):
                # Check for f-strings (Python 3.6+)
                if isinstance(node, ast.JoinedStr) and sys.version_info < (3, 6):
                    issues.append("Tool uses f-strings which require Python 3.6+")
                    
                # Check for walrus operator (Python 3.8+)
                if isinstance(node, ast.NamedExpr) and sys.version_info < (3, 8):
                    issues.append("Tool uses walrus operator which require Python 3.8+")
                    
                # Check for type hints
                if isinstance(node, ast.AnnAssign) and sys.version_info < (3, 6):
                    issues.append("Tool uses type hints which require Python 3.6+")
                    
        except Exception as e:
            logger.error(f"Error checking code compatibility: {str(e)}")
            issues.append(f"Error analyzing code: {str(e)}")
            
        return len(issues) == 0, issues
        
    def _check_resource_requirements(self, tool_class: type) -> Tuple[bool, List[str]]:
        """Check resource requirements"""
        warnings = []
        
        try:
            # Check memory requirements
            if hasattr(tool_class, "max_memory_increase"):
                max_memory = tool_class.max_memory_increase
                if max_memory > 500 * 1024 * 1024:  # 500MB
                    warnings.append(f"Tool requires significant memory: {max_memory / (1024*1024):.1f}MB")
                    
            # Check CPU requirements
            if hasattr(tool_class, "max_cpu_percent"):
                max_cpu = tool_class.max_cpu_percent
                if max_cpu > 80:
                    warnings.append(f"Tool requires significant CPU: {max_cpu}%")
                    
            # Check disk requirements
            if hasattr(tool_class, "max_disk_space"):
                max_disk = tool_class.max_disk_space
                if max_disk > 1 * 1024 * 1024 * 1024:  # 1GB
                    warnings.append(f"Tool requires significant disk space: {max_disk / (1024*1024*1024):.1f}GB")
                    
        except Exception as e:
            logger.error(f"Error checking resource requirements: {str(e)}")
            warnings.append(f"Error checking resources: {str(e)}")
            
        return len(warnings) == 0, warnings
        
    def _extract_tool_requirements(self, tool_class: type) -> Dict[str, str]:
        """Extract tool-specific requirements"""
        requirements = {}
        
        try:
            # Get class attributes
            for attr in dir(tool_class):
                if attr.startswith("requires_"):
                    req_type = attr[8:]  # Remove "requires_" prefix
                    requirements[req_type] = getattr(tool_class, attr)
                    
        except Exception as e:
            logger.error(f"Error extracting tool requirements: {str(e)}")
            
        return requirements
        
    def _generate_suggestions(self, issues: List[str], warnings: List[str]) -> List[str]:
        """Generate suggestions based on issues and warnings"""
        suggestions = []
        
        # Handle issues
        for issue in issues:
            if "Python version" in issue:
                suggestions.append("Consider using a more recent Python version or updating the tool")
            elif "OS requirement" in issue:
                suggestions.append("Consider using a different OS or finding an alternative tool")
            elif "Processor requirement" in issue:
                suggestions.append("Consider using a different processor or finding an alternative tool")
            elif "Dependency issue" in issue:
                suggestions.append("Consider updating dependencies or finding alternative packages")
                
        # Handle warnings
        for warning in warnings:
            if "memory" in warning.lower():
                suggestions.append("Consider implementing memory optimization or using a machine with more RAM")
            elif "cpu" in warning.lower():
                suggestions.append("Consider implementing CPU optimization or using a machine with more cores")
            elif "disk space" in warning.lower():
                suggestions.append("Consider implementing disk space optimization or using a machine with more storage")
                
        return suggestions 