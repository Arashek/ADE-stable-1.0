from typing import Dict, List, Optional, Tuple
import os
import ast
from pathlib import Path
import logging
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Symbol:
    name: str
    type: str
    location: Dict[str, Dict[str, int]]
    documentation: Optional[str] = None

@dataclass
class FileContext:
    path: str
    dependencies: List[str]
    imports: List[str]
    exports: List[str]
    symbols: List[Symbol]

class CodebaseAwarenessService:
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.file_contexts: Dict[str, FileContext] = {}
        self.project_structure = self._build_project_structure()
        self.logger = logging.getLogger(__name__)

    def _build_project_structure(self) -> Dict:
        """Build initial project structure by scanning the workspace."""
        structure = {
            'files': [],
            'directories': [],
            'dependencies': {},
            'symbols': {}
        }

        for root, dirs, files in os.walk(self.workspace_root):
            rel_root = os.path.relpath(root, self.workspace_root)
            
            # Add directories
            for dir_name in dirs:
                structure['directories'].append(os.path.join(rel_root, dir_name))

            # Add files
            for file_name in files:
                if file_name.endswith(('.py', '.ts', '.tsx', '.js', '.jsx')):
                    file_path = os.path.join(rel_root, file_name)
                    structure['files'].append(file_path)
                    # Initialize empty symbols list for the file
                    structure['symbols'][file_path] = []

        return structure

    def analyze_file(self, file_path: str) -> FileContext:
        """Analyze a file and return its context."""
        if file_path in self.file_contexts:
            return self.file_contexts[file_path]

        full_path = self.workspace_root / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse the file based on its extension
        if file_path.endswith('.py'):
            context = self._analyze_python_file(content)
        elif file_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
            context = self._analyze_typescript_file(content)
        else:
            context = FileContext(
                path=file_path,
                dependencies=[],
                imports=[],
                exports=[],
                symbols=[]
            )

        self.file_contexts[file_path] = context
        return context

    def _analyze_python_file(self, content: str) -> FileContext:
        """Analyze a Python file and extract its context."""
        try:
            tree = ast.parse(content)
            imports = []
            exports = []
            symbols = []

            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(self._get_import_name(node))
                elif isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Assign)):
                    symbols.append(self._create_symbol(node))

            return FileContext(
                path="",  # Will be set by caller
                dependencies=self._get_python_dependencies(content),
                imports=imports,
                exports=exports,
                symbols=symbols
            )
        except Exception as e:
            self.logger.error(f"Error analyzing Python file: {e}")
            return FileContext(path="", dependencies=[], imports=[], exports=[], symbols=[])

    def _analyze_typescript_file(self, content: str) -> FileContext:
        """Analyze a TypeScript/JavaScript file and extract its context."""
        # This is a simplified version. In a real implementation,
        # you would use a proper TypeScript/JavaScript parser
        imports = []
        exports = []
        symbols = []

        # Basic regex-based analysis
        import_lines = [line for line in content.split('\n') if line.strip().startswith('import')]
        export_lines = [line for line in content.split('\n') if line.strip().startswith('export')]

        for line in import_lines:
            imports.append(line.strip())
        for line in export_lines:
            exports.append(line.strip())

        return FileContext(
            path="",  # Will be set by caller
            dependencies=self._get_typescript_dependencies(content),
            imports=imports,
            exports=exports,
            symbols=symbols
        )

    def _get_import_name(self, node: ast.AST) -> str:
        """Extract import name from an AST node."""
        if isinstance(node, ast.Import):
            return node.names[0].name
        elif isinstance(node, ast.ImportFrom):
            return f"from {node.module} import {', '.join(n.name for n in node.names)}"
        return ""

    def _create_symbol(self, node: ast.AST) -> Symbol:
        """Create a Symbol object from an AST node."""
        if isinstance(node, ast.FunctionDef):
            return Symbol(
                name=node.name,
                type='function',
                location=self._get_node_location(node),
                documentation=ast.get_docstring(node)
            )
        elif isinstance(node, ast.ClassDef):
            return Symbol(
                name=node.name,
                type='class',
                location=self._get_node_location(node),
                documentation=ast.get_docstring(node)
            )
        elif isinstance(node, ast.Assign):
            return Symbol(
                name=node.targets[0].id,
                type='variable',
                location=self._get_node_location(node)
            )
        return None

    def _get_node_location(self, node: ast.AST) -> Dict[str, Dict[str, int]]:
        """Get the location of an AST node."""
        return {
            'start': {'line': node.lineno, 'column': node.col_offset},
            'end': {'line': getattr(node, 'end_lineno', node.lineno),
                   'column': getattr(node, 'end_col_offset', node.col_offset)}
        }

    def _get_python_dependencies(self, content: str) -> List[str]:
        """Extract Python dependencies from a file."""
        try:
            tree = ast.parse(content)
            dependencies = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    dependencies.append(self._get_import_name(node))
            return dependencies
        except:
            return []

    def _get_typescript_dependencies(self, content: str) -> List[str]:
        """Extract TypeScript/JavaScript dependencies from a file."""
        # This is a simplified version. In a real implementation,
        # you would use a proper TypeScript/JavaScript parser
        dependencies = []
        for line in content.split('\n'):
            if line.strip().startswith('import'):
                dependencies.append(line.strip())
        return dependencies

    def get_dependencies(self, file_path: str) -> List[str]:
        """Get dependencies for a specific file."""
        context = self.analyze_file(file_path)
        return context.dependencies

    def get_symbols(self, file_path: str) -> List[Symbol]:
        """Get symbols defined in a specific file."""
        context = self.analyze_file(file_path)
        return context.symbols

    def find_references(self, symbol: Symbol) -> List[Symbol]:
        """Find all references to a symbol across the codebase."""
        references = []
        for file_path in self.project_structure['files']:
            context = self.analyze_file(file_path)
            for s in context.symbols:
                if s.name == symbol.name:
                    references.append(s)
        return references

    def get_definition(self, symbol: Symbol) -> Optional[Symbol]:
        """Get the definition of a symbol."""
        # In a real implementation, this would use a proper symbol table
        # and handle different scopes and namespaces
        return symbol

    def handle_file_change(self, file_path: str, change_type: str, content: Optional[str] = None) -> None:
        """Handle file changes and update the codebase awareness."""
        if change_type == 'deleted':
            if file_path in self.file_contexts:
                del self.file_contexts[file_path]
            if file_path in self.project_structure['files']:
                self.project_structure['files'].remove(file_path)
        elif change_type in ['created', 'modified']:
            if content is None:
                with open(self.workspace_root / file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            if file_path not in self.project_structure['files']:
                self.project_structure['files'].append(file_path)
            
            # Re-analyze the file
            self.analyze_file(file_path) 