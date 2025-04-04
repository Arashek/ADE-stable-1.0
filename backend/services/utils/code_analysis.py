from typing import Dict, List, Optional, Any
import logging
import os
import re
from pathlib import Path

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    """Utility class for analyzing code and extracting information"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
    
    def analyze_project_structure(self, project_path: str) -> Dict[str, Any]:
        """Analyze the project structure and return information about it
        
        Args:
            project_path: Path to the project root
            
        Returns:
            Dictionary with project structure information
        """
        self.logger.info(f"Analyzing project structure at: {project_path}")
        
        if not os.path.exists(project_path):
            self.logger.error(f"Project path does not exist: {project_path}")
            return {"error": "Project path does not exist"}
            
        result = {
            "path": project_path,
            "files_count": 0,
            "directories_count": 0,
            "file_extensions": {},
            "root_directories": [],
            "estimated_loc": 0,
            "readme_exists": False,
            "license_exists": False,
            "gitignore_exists": False,
            "has_tests": False,
            "detected_languages": [],
            "package_files": []
        }
        
        languages_detected = set()
        
        try:
            # Walk through project directory
            for root, dirs, files in os.walk(project_path):
                # Skip hidden directories and common excludes
                dirs[:] = [d for d in dirs if not d.startswith('.') and 
                          d not in ['node_modules', 'venv', '.venv', '__pycache__', 'dist', 'build']]
                
                # If this is the top level, collect root directories
                if root == project_path:
                    result["root_directories"] = dirs.copy()
                
                result["directories_count"] += len(dirs)
                result["files_count"] += len(files)
                
                # Check for special files
                for file in files:
                    file_lower = file.lower()
                    
                    # Check extensions
                    _, ext = os.path.splitext(file)
                    if ext:
                        ext = ext.lstrip('.')
                        result["file_extensions"][ext] = result["file_extensions"].get(ext, 0) + 1
                        
                        # Detect language based on extension
                        lang = self._get_language_from_extension(ext)
                        if lang:
                            languages_detected.add(lang)
                    
                    # Check for common project files
                    if file_lower in ['readme.md', 'readme.txt', 'readme']:
                        result["readme_exists"] = True
                    elif file_lower in ['license', 'license.md', 'license.txt']:
                        result["license_exists"] = True
                    elif file_lower == '.gitignore':
                        result["gitignore_exists"] = True
                    
                    # Check for package management files
                    if file_lower in ['package.json', 'requirements.txt', 'setup.py', 
                                     'pom.xml', 'build.gradle', 'composer.json']:
                        result["package_files"].append(os.path.join(root, file))
                    
                    # Estimate lines of code for source files
                    if self._is_source_file(file):
                        try:
                            filepath = os.path.join(root, file)
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = f.readlines()
                                result["estimated_loc"] += len(lines)
                        except Exception as e:
                            self.logger.warning(f"Error reading file {filepath}: {str(e)}")
                
                # Check for tests
                if not result["has_tests"] and any(d.lower() in ['test', 'tests', 'spec', 'specs'] for d in dirs):
                    result["has_tests"] = True
                if not result["has_tests"] and any('test' in f.lower() for f in files):
                    result["has_tests"] = True
        
        except Exception as e:
            self.logger.error(f"Error analyzing project structure: {str(e)}")
            result["error"] = str(e)
        
        result["detected_languages"] = list(languages_detected)
        return result
    
    def _get_language_from_extension(self, ext: str) -> Optional[str]:
        """Get programming language from file extension"""
        ext_to_lang = {
            'py': 'Python',
            'js': 'JavaScript',
            'ts': 'TypeScript',
            'jsx': 'JavaScript',
            'tsx': 'TypeScript',
            'html': 'HTML',
            'css': 'CSS',
            'scss': 'SCSS',
            'java': 'Java',
            'c': 'C',
            'cpp': 'C++',
            'cs': 'C#',
            'go': 'Go',
            'rb': 'Ruby',
            'php': 'PHP',
            'swift': 'Swift',
            'kt': 'Kotlin',
            'rs': 'Rust',
            'scala': 'Scala',
            'sh': 'Shell',
            'ps1': 'PowerShell',
            'sql': 'SQL'
        }
        return ext_to_lang.get(ext.lower())
    
    def _is_source_file(self, filename: str) -> bool:
        """Check if a file is likely to be a source code file"""
        source_extensions = {
            'py', 'js', 'ts', 'jsx', 'tsx', 'html', 'css', 'scss', 'java', 
            'c', 'cpp', 'cs', 'go', 'rb', 'php', 'swift', 'kt', 'rs', 'scala'
        }
        _, ext = os.path.splitext(filename)
        return ext.lstrip('.').lower() in source_extensions
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file and extract information about it
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Dictionary with file information
        """
        self.logger.info(f"Analyzing file: {file_path}")
        
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            self.logger.error(f"File does not exist: {file_path}")
            return {"error": "File does not exist"}
            
        result = {
            "path": file_path,
            "size_bytes": os.path.getsize(file_path),
            "extension": os.path.splitext(file_path)[1].lstrip('.').lower(),
            "lines_count": 0,
            "functions_count": 0,
            "classes_count": 0,
            "imports_count": 0,
            "imports": [],
            "complexity_estimate": 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                result["lines_count"] = len(lines)
                
                # Detect language
                result["language"] = self._get_language_from_extension(result["extension"])
                
                # Perform language-specific analysis
                if result.get("language") == "Python":
                    self._analyze_python_file(content, result)
                elif result.get("language") in ["JavaScript", "TypeScript"]:
                    self._analyze_js_file(content, result)
                # Add more language analyzers as needed
        
        except Exception as e:
            self.logger.error(f"Error analyzing file {file_path}: {str(e)}")
            result["error"] = str(e)
            
        return result
    
    def _analyze_python_file(self, content: str, result: Dict[str, Any]) -> None:
        """Analyze Python file content and update result dict"""
        # Count imports
        import_pattern = r'^import\s+(\w+)|^from\s+(\w+).*import'
        imports = []
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Find imports
            match = re.match(import_pattern, line)
            if match:
                module = match.group(1) or match.group(2)
                if module and module not in imports:
                    imports.append(module)
        
        # Count function definitions
        func_pattern = r'def\s+(\w+)\s*\('
        result["functions_count"] = len(re.findall(func_pattern, content))
        
        # Count class definitions
        class_pattern = r'class\s+(\w+)'
        result["classes_count"] = len(re.findall(class_pattern, content))
        
        # Store imports
        result["imports"] = imports
        result["imports_count"] = len(imports)
        
        # Estimate complexity (very basic)
        complexity = 0
        complexity += result["lines_count"] / 100
        complexity += result["functions_count"] * 0.5
        complexity += result["classes_count"] * 1.5
        
        # Add points for control flow statements
        control_flow = len(re.findall(r'\b(if|else|elif|for|while|try|except)\b', content))
        complexity += control_flow * 0.3
        
        result["complexity_estimate"] = round(complexity, 2)
    
    def _analyze_js_file(self, content: str, result: Dict[str, Any]) -> None:
        """Analyze JavaScript/TypeScript file content and update result dict"""
        # Count imports
        import_pattern = r'(import|require)\s+.*?[\'"](.+?)[\'"]'
        imports = []
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Find imports
            for match in re.finditer(import_pattern, line):
                module = match.group(2)
                if module and module not in imports:
                    imports.append(module)
        
        # Count function definitions
        # This is a simplified approach (doesn't catch all JS function forms)
        func_patterns = [
            r'function\s+(\w+)\s*\(',  # Named functions
            r'const\s+(\w+)\s*=\s*function',  # Function expressions
            r'const\s+(\w+)\s*=\s*\(',  # Arrow functions
            r'(\w+)\s*:\s*function'  # Object methods
        ]
        
        functions_count = 0
        for pattern in func_patterns:
            functions_count += len(re.findall(pattern, content))
            
        result["functions_count"] = functions_count
        
        # Count class definitions
        class_pattern = r'class\s+(\w+)'
        result["classes_count"] = len(re.findall(class_pattern, content))
        
        # Store imports
        result["imports"] = imports
        result["imports_count"] = len(imports)
        
        # Estimate complexity (very basic)
        complexity = 0
        complexity += result["lines_count"] / 100
        complexity += result["functions_count"] * 0.5
        complexity += result["classes_count"] * 1.5
        
        # Add points for control flow statements
        control_flow = len(re.findall(r'\b(if|else|for|while|try|catch|switch)\b', content))
        complexity += control_flow * 0.3
        
        result["complexity_estimate"] = round(complexity, 2)
    
    def find_dependencies(self, project_path: str) -> Dict[str, List[str]]:
        """Find and analyze project dependencies
        
        Args:
            project_path: Path to the project root
            
        Returns:
            Dictionary with dependency information
        """
        self.logger.info(f"Finding dependencies for project: {project_path}")
        
        result = {
            "python_packages": [],
            "node_packages": [],
            "other_dependencies": []
        }
        
        # Look for requirements.txt (Python)
        req_path = os.path.join(project_path, "requirements.txt")
        if os.path.exists(req_path):
            try:
                with open(req_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Parse requirement line (simplified)
                            package = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                            if package:
                                result["python_packages"].append(package)
            except Exception as e:
                self.logger.warning(f"Error parsing requirements.txt: {str(e)}")
        
        # Look for package.json (Node.js)
        pkg_path = os.path.join(project_path, "package.json")
        if os.path.exists(pkg_path):
            try:
                import json
                with open(pkg_path, 'r', encoding='utf-8') as f:
                    pkg_data = json.load(f)
                    
                    # Extract dependencies
                    dependencies = pkg_data.get("dependencies", {})
                    dev_dependencies = pkg_data.get("devDependencies", {})
                    
                    for dep in list(dependencies.keys()) + list(dev_dependencies.keys()):
                        result["node_packages"].append(dep)
            except Exception as e:
                self.logger.warning(f"Error parsing package.json: {str(e)}")
        
        return result
