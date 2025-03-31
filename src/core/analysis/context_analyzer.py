from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
import re
import logging
from datetime import datetime

@dataclass
class ContextInfo:
    """Represents analyzed context information."""
    error_type: str
    error_message: str
    stack_trace: Optional[List[str]] = None
    code_context: Optional[Dict[str, Any]] = None
    environment_info: Optional[Dict[str, Any]] = None
    related_patterns: Set[str] = None
    severity: str = "unknown"
    category: str = "unknown"
    subcategory: str = "unknown"
    timestamp: datetime = None

class ContextAnalyzer:
    """Analyzes context from error messages and code to provide rich context information."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_type_patterns = {
            "runtime": r"(TypeError|ValueError|AttributeError|IndexError|KeyError|NameError)",
            "database": r"(DatabaseError|OperationalError|IntegrityError|ProgrammingError)",
            "network": r"(ConnectionError|TimeoutError|SSLError|HTTPError)",
            "filesystem": r"(FileNotFoundError|PermissionError|OSError)",
            "system": r"(MemoryError|ResourceExhaustedError|SystemError)"
        }
        
        self.severity_patterns = {
            "critical": r"(MemoryError|SystemError|ResourceExhaustedError)",
            "high": r"(DatabaseError|ConnectionError|PermissionError)",
            "medium": r"(TypeError|ValueError|AttributeError|IndexError)",
            "low": r"(Warning|DeprecationWarning|UserWarning)"
        }
    
    def analyze_error_message(self, error_message: str) -> Dict[str, Any]:
        """Analyze error message to extract key information."""
        context = {
            "error_type": None,
            "severity": "unknown",
            "category": "unknown",
            "subcategory": "unknown",
            "patterns": set()
        }
        
        # Determine error type and category
        for category, pattern in self.error_type_patterns.items():
            if re.search(pattern, error_message):
                context["category"] = category
                context["error_type"] = re.search(pattern, error_message).group(1)
                break
        
        # Determine severity
        for severity, pattern in self.severity_patterns.items():
            if re.search(pattern, error_message):
                context["severity"] = severity
                break
        
        # Extract subcategory based on error type
        if context["error_type"]:
            if "Type" in context["error_type"]:
                context["subcategory"] = "type_error"
            elif "Value" in context["error_type"]:
                context["subcategory"] = "value_error"
            elif "Attribute" in context["error_type"]:
                context["subcategory"] = "attribute_error"
            elif "Index" in context["error_type"]:
                context["subcategory"] = "index_error"
            elif "Key" in context["error_type"]:
                context["subcategory"] = "key_error"
            elif "Name" in context["error_type"]:
                context["subcategory"] = "name_error"
        
        return context
    
    def analyze_stack_trace(self, stack_trace: List[str]) -> Dict[str, Any]:
        """Analyze stack trace to extract code context."""
        context = {
            "file_paths": set(),
            "line_numbers": set(),
            "function_names": set(),
            "module_names": set()
        }
        
        for line in stack_trace:
            # Extract file path and line number
            file_match = re.search(r'File "([^"]+)", line (\d+)', line)
            if file_match:
                context["file_paths"].add(file_match.group(1))
                context["line_numbers"].add(int(file_match.group(2)))
            
            # Extract function name
            func_match = re.search(r'in ([a-zA-Z_][a-zA-Z0-9_]*)', line)
            if func_match:
                context["function_names"].add(func_match.group(1))
            
            # Extract module name
            module_match = re.search(r'from ([a-zA-Z_][a-zA-Z0-9_]*) import', line)
            if module_match:
                context["module_names"].add(module_match.group(1))
        
        return context
    
    def analyze_code_context(self, code_snippet: str, line_number: int) -> Dict[str, Any]:
        """Analyze code context around the error location."""
        context = {
            "line_number": line_number,
            "surrounding_lines": [],
            "variables": set(),
            "function_calls": set(),
            "imports": set()
        }
        
        # Split code into lines
        lines = code_snippet.split('\n')
        start_line = max(0, line_number - 3)
        end_line = min(len(lines), line_number + 3)
        
        # Get surrounding lines
        context["surrounding_lines"] = lines[start_line:end_line]
        
        # Extract variables and function calls
        for line in context["surrounding_lines"]:
            # Extract variable assignments
            var_match = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=', line)
            context["variables"].update(var_match)
            
            # Extract function calls
            func_match = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', line)
            context["function_calls"].update(func_match)
            
            # Extract imports
            import_match = re.findall(r'from\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
            context["imports"].update(import_match)
        
        return context
    
    def analyze_environment(self, env_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze environment information."""
        context = {
            "python_version": env_info.get("python_version"),
            "os_info": env_info.get("os_info"),
            "dependencies": env_info.get("dependencies", {}),
            "environment_vars": env_info.get("environment_vars", {}),
            "resource_usage": env_info.get("resource_usage", {})
        }
        
        # Add resource usage analysis
        if "resource_usage" in env_info:
            usage = env_info["resource_usage"]
            if usage.get("memory_usage", 0) > 0.8:  # 80% memory usage
                context["resource_issues"] = ["high_memory_usage"]
            if usage.get("cpu_usage", 0) > 0.9:  # 90% CPU usage
                context["resource_issues"] = context.get("resource_issues", []) + ["high_cpu_usage"]
        
        return context
    
    def analyze(self, error_message: str, stack_trace: Optional[List[str]] = None,
                code_context: Optional[Dict[str, Any]] = None,
                environment_info: Optional[Dict[str, Any]] = None) -> ContextInfo:
        """Perform comprehensive context analysis."""
        try:
            # Analyze error message
            error_context = self.analyze_error_message(error_message)
            
            # Analyze stack trace if available
            stack_context = {}
            if stack_trace:
                stack_context = self.analyze_stack_trace(stack_trace)
            
            # Analyze code context if available
            code_context_info = {}
            if code_context and "code_snippet" in code_context:
                code_context_info = self.analyze_code_context(
                    code_context["code_snippet"],
                    code_context.get("line_number", 0)
                )
            
            # Analyze environment info if available
            env_context = {}
            if environment_info:
                env_context = self.analyze_environment(environment_info)
            
            # Create context info
            context_info = ContextInfo(
                error_type=error_context["error_type"],
                error_message=error_message,
                stack_trace=stack_trace,
                code_context=code_context_info,
                environment_info=env_context,
                related_patterns=error_context["patterns"],
                severity=error_context["severity"],
                category=error_context["category"],
                subcategory=error_context["subcategory"],
                timestamp=datetime.now()
            )
            
            return context_info
            
        except Exception as e:
            self.logger.error(f"Error analyzing context: {str(e)}")
            return ContextInfo(
                error_type="unknown",
                error_message=error_message,
                timestamp=datetime.now()
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about context analysis."""
        return {
            "error_type_patterns": len(self.error_type_patterns),
            "severity_patterns": len(self.severity_patterns),
            "categories": list(self.error_type_patterns.keys()),
            "severity_levels": list(self.severity_patterns.keys())
        } 