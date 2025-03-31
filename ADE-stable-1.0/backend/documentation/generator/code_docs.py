from typing import Dict, Any, List, Optional
import ast
import inspect
import re
from pathlib import Path
from .base import BaseDocumentationGenerator
from ...config.logging_config import logger

class CodeDocumentationGenerator(BaseDocumentationGenerator):
    """Generator for code documentation"""
    
    def __init__(self, output_dir: str = "docs"):
        super().__init__(output_dir)
        self.supported_languages = {
            ".py": self._analyze_python_code,
            ".js": self._analyze_javascript_code,
            ".ts": self._analyze_typescript_code,
            ".java": self._analyze_java_code,
            ".cpp": self._analyze_cpp_code
        }
        
    def generate_code_docs(self, source_dir: str, exclude_dirs: List[str] = None):
        """Generate documentation for all code files in the source directory"""
        try:
            self.create_output_dirs()
            source_path = Path(source_dir)
            exclude_dirs = exclude_dirs or ["__pycache__", "node_modules", "venv"]
            
            # Find all code files
            code_files = []
            for ext in self.supported_languages.keys():
                code_files.extend(source_path.rglob(f"*{ext}"))
                
            # Filter out excluded directories
            code_files = [
                f for f in code_files
                if not any(exclude in str(f) for exclude in exclude_dirs)
            ]
            
            # Generate documentation for each file
            for file_path in code_files:
                self._generate_file_docs(file_path)
                
            # Generate index and navigation
            self._generate_code_docs_index(code_files)
            
            logger.info("Code documentation generated successfully")
            
        except Exception as e:
            logger.error(f"Error generating code documentation: {str(e)}")
            raise
            
    def _generate_file_docs(self, file_path: Path):
        """Generate documentation for a single file"""
        try:
            # Get file extension and analyzer
            ext = file_path.suffix.lower()
            if ext not in self.supported_languages:
                logger.warning(f"Unsupported file type: {ext}")
                return
                
            analyzer = self.supported_languages[ext]
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Analyze code
            analysis = analyzer(content)
            
            # Generate documentation
            docs = self._create_file_documentation(file_path, analysis)
            
            # Save documentation
            relative_path = file_path.relative_to(file_path.parent.parent)
            output_path = f"code/{relative_path.with_suffix('.md')}"
            self.save_file(docs, output_path)
            
        except Exception as e:
            logger.error(f"Error generating documentation for {file_path}: {str(e)}")
            
    def _analyze_python_code(self, content: str) -> Dict[str, Any]:
        """Analyze Python code and extract documentation"""
        try:
            tree = ast.parse(content)
            analysis = {
                "classes": [],
                "functions": [],
                "imports": [],
                "docstrings": [],
                "comments": []
            }
            
            for node in ast.walk(tree):
                # Extract classes
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "methods": [],
                        "decorators": [d.id for d in node.decorator_list if isinstance(d, ast.Name)]
                    }
                    
                    # Extract methods
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            class_info["methods"].append({
                                "name": child.name,
                                "docstring": ast.get_docstring(child)
                            })
                            
                    analysis["classes"].append(class_info)
                    
                # Extract functions
                elif isinstance(node, ast.FunctionDef):
                    analysis["functions"].append({
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "args": [arg.arg for arg in node.args.args],
                        "decorators": [d.id for d in node.decorator_list if isinstance(d, ast.Name)]
                    })
                    
                # Extract imports
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        analysis["imports"].extend(alias.name for alias in node.names)
                    else:
                        analysis["imports"].append(f"from {node.module} import {', '.join(alias.name for alias in node.names)}")
                        
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing Python code: {str(e)}")
            return {}
            
    def _analyze_javascript_code(self, content: str) -> Dict[str, Any]:
        """Analyze JavaScript code and extract documentation"""
        try:
            analysis = {
                "classes": [],
                "functions": [],
                "imports": [],
                "comments": []
            }
            
            # Extract classes
            class_pattern = r"class\s+(\w+)\s*{([^}]*)}"
            for match in re.finditer(class_pattern, content, re.DOTALL):
                class_name = match.group(1)
                class_content = match.group(2)
                
                # Extract methods
                methods = []
                method_pattern = r"(\w+)\s*\([^)]*\)\s*{([^}]*)}"
                for method_match in re.finditer(method_pattern, class_content):
                    methods.append({
                        "name": method_match.group(1),
                        "docstring": self._extract_jsdoc(method_match.group(0))
                    })
                    
                analysis["classes"].append({
                    "name": class_name,
                    "methods": methods,
                    "docstring": self._extract_jsdoc(match.group(0))
                })
                
            # Extract functions
            function_pattern = r"function\s+(\w+)\s*\([^)]*\)\s*{([^}]*)}"
            for match in re.finditer(function_pattern, content, re.DOTALL):
                analysis["functions"].append({
                    "name": match.group(1),
                    "docstring": self._extract_jsdoc(match.group(0))
                })
                
            # Extract imports
            import_pattern = r"import\s+.*?from\s+['\"](.*?)['\"]"
            analysis["imports"] = re.findall(import_pattern, content)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing JavaScript code: {str(e)}")
            return {}
            
    def _analyze_typescript_code(self, content: str) -> Dict[str, Any]:
        """Analyze TypeScript code and extract documentation"""
        try:
            # Use JavaScript analyzer as base
            analysis = self._analyze_javascript_code(content)
            
            # Add TypeScript-specific analysis
            interface_pattern = r"interface\s+(\w+)\s*{([^}]*)}"
            for match in re.finditer(interface_pattern, content, re.DOTALL):
                analysis["interfaces"] = analysis.get("interfaces", [])
                analysis["interfaces"].append({
                    "name": match.group(1),
                    "properties": self._extract_interface_properties(match.group(2))
                })
                
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing TypeScript code: {str(e)}")
            return {}
            
    def _analyze_java_code(self, content: str) -> Dict[str, Any]:
        """Analyze Java code and extract documentation"""
        try:
            analysis = {
                "classes": [],
                "methods": [],
                "imports": [],
                "comments": []
            }
            
            # Extract classes
            class_pattern = r"class\s+(\w+)\s*{([^}]*)}"
            for match in re.finditer(class_pattern, content, re.DOTALL):
                class_name = match.group(1)
                class_content = match.group(2)
                
                # Extract methods
                methods = []
                method_pattern = r"(public|private|protected)?\s*(\w+)\s+(\w+)\s*\([^)]*\)\s*{([^}]*)}"
                for method_match in re.finditer(method_pattern, class_content):
                    methods.append({
                        "name": method_match.group(3),
                        "return_type": method_match.group(2),
                        "visibility": method_match.group(1),
                        "docstring": self._extract_javadoc(method_match.group(0))
                    })
                    
                analysis["classes"].append({
                    "name": class_name,
                    "methods": methods,
                    "docstring": self._extract_javadoc(match.group(0))
                })
                
            # Extract imports
            import_pattern = r"import\s+([^;]+);"
            analysis["imports"] = re.findall(import_pattern, content)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing Java code: {str(e)}")
            return {}
            
    def _analyze_cpp_code(self, content: str) -> Dict[str, Any]:
        """Analyze C++ code and extract documentation"""
        try:
            analysis = {
                "classes": [],
                "functions": [],
                "includes": [],
                "comments": []
            }
            
            # Extract classes
            class_pattern = r"class\s+(\w+)\s*{([^}]*)}"
            for match in re.finditer(class_pattern, content, re.DOTALL):
                class_name = match.group(1)
                class_content = match.group(2)
                
                # Extract methods
                methods = []
                method_pattern = r"(\w+)\s+(\w+)\s*\([^)]*\)\s*{([^}]*)}"
                for method_match in re.finditer(method_pattern, class_content):
                    methods.append({
                        "name": method_match.group(2),
                        "return_type": method_match.group(1),
                        "docstring": self._extract_cppdoc(method_match.group(0))
                    })
                    
                analysis["classes"].append({
                    "name": class_name,
                    "methods": methods,
                    "docstring": self._extract_cppdoc(match.group(0))
                })
                
            # Extract includes
            include_pattern = r"#include\s+[<\"]([^>\"]+)[>\"]"
            analysis["includes"] = re.findall(include_pattern, content)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing C++ code: {str(e)}")
            return {}
            
    def _extract_jsdoc(self, content: str) -> Optional[str]:
        """Extract JSDoc comments from code"""
        try:
            doc_pattern = r"/\*\*([^*]*\*+[^*/][^*]*\*+|[^*]*\*+/\s*|[^*]*\*+|[^*]*)\*/"
            match = re.search(doc_pattern, content)
            if match:
                return match.group(1).strip()
            return None
        except Exception as e:
            logger.error(f"Error extracting JSDoc: {str(e)}")
            return None
            
    def _extract_javadoc(self, content: str) -> Optional[str]:
        """Extract JavaDoc comments from code"""
        try:
            doc_pattern = r"/\*\*([^*]*\*+[^*/][^*]*\*+|[^*]*\*+/\s*|[^*]*\*+|[^*]*)\*/"
            match = re.search(doc_pattern, content)
            if match:
                return match.group(1).strip()
            return None
        except Exception as e:
            logger.error(f"Error extracting JavaDoc: {str(e)}")
            return None
            
    def _extract_cppdoc(self, content: str) -> Optional[str]:
        """Extract C++ documentation comments from code"""
        try:
            doc_pattern = r"///([^\n]*\n)*"
            match = re.search(doc_pattern, content)
            if match:
                return match.group(0).strip()
            return None
        except Exception as e:
            logger.error(f"Error extracting C++ documentation: {str(e)}")
            return None
            
    def _extract_interface_properties(self, content: str) -> List[Dict[str, Any]]:
        """Extract properties from TypeScript interface"""
        try:
            properties = []
            property_pattern = r"(\w+)\s*:\s*([^;]+);"
            for match in re.finditer(property_pattern, content):
                properties.append({
                    "name": match.group(1),
                    "type": match.group(2).strip()
                })
            return properties
        except Exception as e:
            logger.error(f"Error extracting interface properties: {str(e)}")
            return []
            
    def _create_file_documentation(self, file_path: Path, analysis: Dict[str, Any]) -> str:
        """Create markdown documentation for a file"""
        try:
            template = self.load_template("code_docs.md")
            return template.render(
                file_path=file_path,
                analysis=analysis,
                version_info=self.generate_version_info()
            )
        except Exception as e:
            logger.error(f"Error creating file documentation: {str(e)}")
            return ""
            
    def _generate_code_docs_index(self, code_files: List[Path]):
        """Generate index and navigation for code documentation"""
        try:
            # Create file tree
            file_tree = self._create_file_tree(code_files)
            
            # Generate index
            template = self.load_template("code_index.md")
            index_content = template.render(
                file_tree=file_tree,
                version_info=self.generate_version_info()
            )
            
            # Save index
            self.save_file(index_content, "code/index.md")
            
        except Exception as e:
            logger.error(f"Error generating code documentation index: {str(e)}")
            raise
            
    def _create_file_tree(self, code_files: List[Path]) -> Dict[str, Any]:
        """Create a tree structure of code files"""
        try:
            tree = {}
            for file_path in code_files:
                parts = file_path.parts
                current = tree
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = {
                    "type": "file",
                    "path": str(file_path),
                    "extension": file_path.suffix
                }
            return tree
        except Exception as e:
            logger.error(f"Error creating file tree: {str(e)}")
            return {} 