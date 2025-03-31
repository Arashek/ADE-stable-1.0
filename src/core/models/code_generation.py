"""
Advanced code generation module for the ADE Platform.
Provides template-based code generation, pattern generation, and documentation generation.
"""

import os
import re
import ast
import jinja2
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class CodeTemplate:
    """Represents a code template with metadata and content."""
    name: str
    description: str
    content: str
    parameters: Dict[str, Any]
    tags: List[str]
    language: str
    category: str
    version: str
    author: str
    created_at: datetime
    updated_at: datetime

@dataclass
class CodePattern:
    """Represents a code pattern with its structure and rules."""
    name: str
    description: str
    structure: Dict[str, Any]
    rules: List[Dict[str, Any]]
    examples: List[str]
    anti_patterns: List[str]
    best_practices: List[str]
    language: str
    category: str

@dataclass
class DocumentationTemplate:
    """Represents a documentation template with sections and formatting."""
    name: str
    description: str
    sections: List[Dict[str, Any]]
    format: str
    style: Dict[str, Any]
    examples: List[str]
    language: str
    category: str

class CodeGenerator:
    """Main class for code generation functionality."""
    
    def __init__(self, templates_dir: str = "templates", patterns_dir: str = "patterns"):
        """Initialize the code generator with template and pattern directories."""
        self.templates_dir = Path(templates_dir)
        self.patterns_dir = Path(patterns_dir)
        self.templates: Dict[str, CodeTemplate] = {}
        self.patterns: Dict[str, CodePattern] = {}
        self.docs_templates: Dict[str, DocumentationTemplate] = {}
        self._load_templates()
        self._load_patterns()
        self._load_doc_templates()
        
    def _load_templates(self) -> None:
        """Load all code templates from the templates directory."""
        for template_file in self.templates_dir.glob("**/*.yaml"):
            try:
                template_data = self._load_yaml(template_file)
                template = CodeTemplate(**template_data)
                self.templates[template.name] = template
                logger.info(f"Loaded template: {template.name}")
            except Exception as e:
                logger.error(f"Error loading template {template_file}: {e}")
                
    def _load_patterns(self) -> None:
        """Load all code patterns from the patterns directory."""
        for pattern_file in self.patterns_dir.glob("**/*.yaml"):
            try:
                pattern_data = self._load_yaml(pattern_file)
                pattern = CodePattern(**pattern_data)
                self.patterns[pattern.name] = pattern
                logger.info(f"Loaded pattern: {pattern.name}")
            except Exception as e:
                logger.error(f"Error loading pattern {pattern_file}: {e}")
                
    def _load_doc_templates(self) -> None:
        """Load all documentation templates."""
        docs_dir = self.templates_dir / "documentation"
        for doc_file in docs_dir.glob("**/*.yaml"):
            try:
                doc_data = self._load_yaml(doc_file)
                doc_template = DocumentationTemplate(**doc_data)
                self.docs_templates[doc_template.name] = doc_template
                logger.info(f"Loaded documentation template: {doc_template.name}")
            except Exception as e:
                logger.error(f"Error loading documentation template {doc_file}: {e}")
                
    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load and parse a YAML file."""
        import yaml
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
            
    def generate_code(self, template_name: str, parameters: Dict[str, Any]) -> str:
        """Generate code from a template with given parameters."""
        if template_name not in self.templates:
            raise ValueError(f"Template not found: {template_name}")
            
        template = self.templates[template_name]
        jinja_env = jinja2.Environment(
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        try:
            template_content = jinja_env.from_string(template.content)
            return template_content.render(**parameters)
        except Exception as e:
            logger.error(f"Error generating code from template {template_name}: {e}")
            raise
            
    def generate_pattern(self, pattern_name: str, parameters: Dict[str, Any]) -> str:
        """Generate code following a specific pattern."""
        if pattern_name not in self.patterns:
            raise ValueError(f"Pattern not found: {pattern_name}")
            
        pattern = self.patterns[pattern_name]
        
        # Apply pattern rules
        code_structure = self._apply_pattern_rules(pattern.structure, parameters)
        
        # Generate code from structure
        return self._generate_from_structure(code_structure)
        
    def generate_documentation(self, template_name: str, code: str, 
                             additional_info: Optional[Dict[str, Any]] = None) -> str:
        """Generate documentation for code using a template."""
        if template_name not in self.docs_templates:
            raise ValueError(f"Documentation template not found: {template_name}")
            
        template = self.docs_templates[template_name]
        
        # Analyze code
        code_analysis = self._analyze_code(code)
        
        # Prepare documentation data
        doc_data = {
            'code_analysis': code_analysis,
            'timestamp': datetime.now(),
            **(additional_info or {})
        }
        
        # Generate documentation
        return self._generate_doc_from_template(template, doc_data)
        
    def _apply_pattern_rules(self, structure: Dict[str, Any], 
                           parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Apply pattern rules to generate code structure."""
        result = {}
        
        for key, value in structure.items():
            if isinstance(value, dict):
                result[key] = self._apply_pattern_rules(value, parameters)
            elif isinstance(value, str):
                # Apply parameter substitution
                result[key] = value.format(**parameters)
            else:
                result[key] = value
                
        return result
        
    def _generate_from_structure(self, structure: Dict[str, Any]) -> str:
        """Generate code from a structured representation."""
        code_lines = []
        
        def process_node(node: Dict[str, Any], indent: int = 0):
            if 'type' in node:
                if node['type'] == 'class':
                    code_lines.append(' ' * indent + f"class {node['name']}:")
                    for method in node.get('methods', []):
                        process_node(method, indent + 4)
                elif node['type'] == 'method':
                    code_lines.append(' ' * indent + f"def {node['name']}(self):")
                    for line in node.get('body', []):
                        code_lines.append(' ' * (indent + 4) + line)
                elif node['type'] == 'property':
                    code_lines.append(' ' * indent + f"@{property}")
                    code_lines.append(' ' * indent + f"def {node['name']}(self):")
                    for line in node.get('body', []):
                        code_lines.append(' ' * (indent + 4) + line)
                        
        process_node(structure)
        return '\n'.join(code_lines)
        
    def _analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze code to extract information for documentation."""
        try:
            tree = ast.parse(code)
            analyzer = CodeAnalyzer()
            analyzer.visit(tree)
            return analyzer.get_analysis()
        except Exception as e:
            logger.error(f"Error analyzing code: {e}")
            return {}
            
    def _generate_doc_from_template(self, template: DocumentationTemplate, 
                                  data: Dict[str, Any]) -> str:
        """Generate documentation from a template and data."""
        jinja_env = jinja2.Environment(
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Create template content
        content = []
        for section in template.sections:
            section_template = jinja_env.from_string(section['content'])
            content.append(section_template.render(**data))
            
        return '\n\n'.join(content)
        
    def add_template(self, template: CodeTemplate) -> None:
        """Add a new code template."""
        self.templates[template.name] = template
        self._save_template(template)
        
    def add_pattern(self, pattern: CodePattern) -> None:
        """Add a new code pattern."""
        self.patterns[pattern.name] = pattern
        self._save_pattern(pattern)
        
    def add_doc_template(self, template: DocumentationTemplate) -> None:
        """Add a new documentation template."""
        self.docs_templates[template.name] = template
        self._save_doc_template(template)
        
    def _save_template(self, template: CodeTemplate) -> None:
        """Save a template to disk."""
        template_file = self.templates_dir / f"{template.name}.yaml"
        self._save_yaml(template_file, template.__dict__)
        
    def _save_pattern(self, pattern: CodePattern) -> None:
        """Save a pattern to disk."""
        pattern_file = self.patterns_dir / f"{pattern.name}.yaml"
        self._save_yaml(pattern_file, pattern.__dict__)
        
    def _save_doc_template(self, template: DocumentationTemplate) -> None:
        """Save a documentation template to disk."""
        doc_file = self.templates_dir / "documentation" / f"{template.name}.yaml"
        self._save_yaml(doc_file, template.__dict__)
        
    def _save_yaml(self, file_path: Path, data: Dict[str, Any]) -> None:
        """Save data to a YAML file."""
        import yaml
        os.makedirs(file_path.parent, exist_ok=True)
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

class CodeAnalyzer(ast.NodeVisitor):
    """AST visitor for analyzing code structure."""
    
    def __init__(self):
        self.analysis = {
            'classes': [],
            'functions': [],
            'imports': [],
            'variables': [],
            'decorators': [],
            'docstrings': []
        }
        
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions."""
        class_info = {
            'name': node.name,
            'bases': [base.id for base in node.bases if isinstance(base, ast.Name)],
            'methods': [],
            'docstring': ast.get_docstring(node)
        }
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = {
                    'name': item.name,
                    'args': self._get_function_args(item.args),
                    'docstring': ast.get_docstring(item)
                }
                class_info['methods'].append(method_info)
                
        self.analysis['classes'].append(class_info)
        self.generic_visit(node)
        
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        if not isinstance(node.parent, ast.ClassDef):
            function_info = {
                'name': node.name,
                'args': self._get_function_args(node.args),
                'docstring': ast.get_docstring(node)
            }
            self.analysis['functions'].append(function_info)
        self.generic_visit(node)
        
    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statements."""
        for name in node.names:
            self.analysis['imports'].append({
                'module': name.name,
                'alias': name.asname
            })
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from-import statements."""
        for name in node.names:
            self.analysis['imports'].append({
                'module': node.module,
                'name': name.name,
                'alias': name.asname
            })
        self.generic_visit(node)
        
    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit assignment statements."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.analysis['variables'].append({
                    'name': target.id,
                    'type': self._get_type_hint(node)
                })
        self.generic_visit(node)
        
    def visit_Decorator(self, node: ast.Decorator) -> None:
        """Visit decorators."""
        if isinstance(node.decorator, ast.Name):
            self.analysis['decorators'].append({
                'name': node.decorator.id,
                'target': node.target.id if isinstance(node.target, ast.Name) else None
            })
        self.generic_visit(node)
        
    def _get_function_args(self, args: ast.arguments) -> List[Dict[str, Any]]:
        """Extract function arguments information."""
        arg_info = []
        for arg in args.args:
            arg_info.append({
                'name': arg.arg,
                'type': self._get_type_hint(arg)
            })
        return arg_info
        
    def _get_type_hint(self, node: ast.AST) -> Optional[str]:
        """Extract type hint from a node."""
        if hasattr(node, 'annotation'):
            if isinstance(node.annotation, ast.Name):
                return node.annotation.id
            elif isinstance(node.annotation, ast.Subscript):
                return self._get_subscript_type(node.annotation)
        return None
        
    def _get_subscript_type(self, node: ast.Subscript) -> str:
        """Extract type from subscript annotation."""
        if isinstance(node.value, ast.Name):
            base_type = node.value.id
            if isinstance(node.slice, ast.Name):
                return f"{base_type}[{node.slice.id}]"
            elif isinstance(node.slice, ast.Tuple):
                types = [self._get_type_hint(el) for el in node.slice.elts]
                return f"{base_type}[{', '.join(types)}]"
        return "Any"
        
    def get_analysis(self) -> Dict[str, Any]:
        """Get the complete analysis results."""
        return self.analysis 