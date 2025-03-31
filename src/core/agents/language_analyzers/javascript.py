from typing import Dict, List, Any
import esprima
from esprima import nodes
import os

class JavaScriptAnalyzer:
    def __init__(self):
        self.ast_cache: Dict[str, Any] = {}
        
    def analyze_code(self, file_path: str) -> Dict[str, Any]:
        """Analyze JavaScript code structure and dependencies."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        try:
            ast = esprima.parseScript(content, {'loc': True, 'range': True})
            self.ast_cache[file_path] = ast
            
            analysis = {
                'imports': [],
                'exports': [],
                'classes': [],
                'functions': [],
                'variables': [],
                'dependencies': set(),
                'metrics': self._calculate_metrics(ast)
            }
            
            self._analyze_node(ast, analysis)
            return analysis
            
        except Exception as e:
            return {
                'error': str(e),
                'file_path': file_path
            }
            
    def _analyze_node(self, node: Any, analysis: Dict[str, Any]) -> None:
        """Recursively analyze AST nodes."""
        if isinstance(node, nodes.ImportDeclaration):
            for specifier in node.specifiers:
                if isinstance(specifier, nodes.ImportSpecifier):
                    analysis['imports'].append({
                        'type': 'named',
                        'name': specifier.imported.name,
                        'source': node.source.value
                    })
                elif isinstance(specifier, nodes.ImportDefaultSpecifier):
                    analysis['imports'].append({
                        'type': 'default',
                        'name': specifier.local.name,
                        'source': node.source.value
                    })
                    
        elif isinstance(node, nodes.ExportNamedDeclaration):
            if node.declaration:
                if isinstance(node.declaration, nodes.VariableDeclaration):
                    for decl in node.declaration.declarations:
                        analysis['exports'].append({
                            'type': 'variable',
                            'name': decl.id.name
                        })
                elif isinstance(node.declaration, nodes.FunctionDeclaration):
                    analysis['exports'].append({
                        'type': 'function',
                        'name': node.declaration.id.name
                    })
                    
        elif isinstance(node, nodes.ClassDeclaration):
            analysis['classes'].append({
                'name': node.id.name,
                'superClass': node.superClass.name if node.superClass else None,
                'methods': [
                    {
                        'name': prop.key.name,
                        'type': 'method' if isinstance(prop.value, nodes.FunctionExpression) else 'property'
                    }
                    for prop in node.body.body
                ]
            })
            
        elif isinstance(node, nodes.FunctionDeclaration):
            analysis['functions'].append({
                'name': node.id.name,
                'params': [param.name for param in node.params],
                'async': node.async,
                'generator': node.generator
            })
            
        elif isinstance(node, nodes.VariableDeclaration):
            for decl in node.declarations:
                if isinstance(decl.id, nodes.Identifier):
                    analysis['variables'].append({
                        'name': decl.id.name,
                        'type': 'const' if node.kind == 'const' else 'let' if node.kind == 'let' else 'var'
                    })
                    
        # Recursively analyze child nodes
        for key, value in node.__dict__.items():
            if isinstance(value, (nodes.Node, list)):
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, nodes.Node):
                            self._analyze_node(item, analysis)
                else:
                    self._analyze_node(value, analysis)
                    
    def _calculate_metrics(self, ast: Any) -> Dict[str, Any]:
        """Calculate code metrics."""
        metrics = {
            'complexity': 0,
            'lines': 0,
            'statements': 0,
            'functions': 0,
            'classes': 0
        }
        
        def count_node(node: Any) -> None:
            if isinstance(node, nodes.Node):
                metrics['statements'] += 1
                
                if isinstance(node, nodes.FunctionDeclaration):
                    metrics['functions'] += 1
                elif isinstance(node, nodes.ClassDeclaration):
                    metrics['classes'] += 1
                    
                # Calculate cyclomatic complexity
                if isinstance(node, (nodes.IfStatement, nodes.WhileStatement, 
                                  nodes.ForStatement, nodes.ForInStatement,
                                  nodes.ForOfStatement, nodes.CatchClause,
                                  nodes.LogicalExpression)):
                    metrics['complexity'] += 1
                    
                # Count lines
                if hasattr(node, 'loc'):
                    metrics['lines'] = max(metrics['lines'], node.loc.end.line)
                    
                # Recursively count child nodes
                for value in node.__dict__.values():
                    if isinstance(value, (nodes.Node, list)):
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item, nodes.Node):
                                    count_node(item)
                        else:
                            count_node(value)
                            
        count_node(ast)
        return metrics
        
    def get_dependencies(self, file_path: str) -> List[str]:
        """Get list of dependencies for a file."""
        if file_path not in self.ast_cache:
            self.analyze_code(file_path)
            
        dependencies = set()
        ast = self.ast_cache[file_path]
        
        def collect_dependencies(node: Any) -> None:
            if isinstance(node, nodes.ImportDeclaration):
                dependencies.add(node.source.value)
            elif isinstance(node, nodes.RequireCall):
                if isinstance(node.arguments[0], nodes.Literal):
                    dependencies.add(node.arguments[0].value)
                    
            for value in node.__dict__.values():
                if isinstance(value, (nodes.Node, list)):
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, nodes.Node):
                                collect_dependencies(item)
                    else:
                        collect_dependencies(value)
                        
        collect_dependencies(ast)
        return list(dependencies)
        
    def get_symbols(self, file_path: str) -> Dict[str, List[str]]:
        """Get all symbols (variables, functions, classes) in a file."""
        if file_path not in self.ast_cache:
            self.analyze_code(file_path)
            
        symbols = {
            'variables': [],
            'functions': [],
            'classes': []
        }
        
        def collect_symbols(node: Any) -> None:
            if isinstance(node, nodes.Identifier):
                symbols['variables'].append(node.name)
            elif isinstance(node, nodes.FunctionDeclaration):
                symbols['functions'].append(node.id.name)
            elif isinstance(node, nodes.ClassDeclaration):
                symbols['classes'].append(node.id.name)
                
            for value in node.__dict__.values():
                if isinstance(value, (nodes.Node, list)):
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, nodes.Node):
                                collect_symbols(item)
                    else:
                        collect_symbols(value)
                        
        collect_symbols(self.ast_cache[file_path])
        return symbols 