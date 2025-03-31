from typing import Dict, List, Any
import javalang
from javalang.tree import Node
import os

class JavaAnalyzer:
    def __init__(self):
        self.ast_cache: Dict[str, Any] = {}
        
    def analyze_code(self, file_path: str) -> Dict[str, Any]:
        """Analyze Java code structure and dependencies."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        try:
            tree = javalang.parse.parse(content)
            self.ast_cache[file_path] = tree
            
            analysis = {
                'imports': [],
                'package': None,
                'classes': [],
                'interfaces': [],
                'enums': [],
                'methods': [],
                'fields': [],
                'dependencies': set(),
                'metrics': self._calculate_metrics(tree)
            }
            
            self._analyze_node(tree, analysis)
            return analysis
            
        except Exception as e:
            return {
                'error': str(e),
                'file_path': file_path
            }
            
    def _analyze_node(self, node: Node, analysis: Dict[str, Any]) -> None:
        """Recursively analyze AST nodes."""
        if isinstance(node, javalang.tree.PackageDeclaration):
            analysis['package'] = '.'.join(node.name)
            
        elif isinstance(node, javalang.tree.Import):
            analysis['imports'].append(node.path)
            
        elif isinstance(node, javalang.tree.ClassDeclaration):
            class_info = {
                'name': node.name,
                'modifiers': list(node.modifiers),
                'extends': node.extends.name if node.extends else None,
                'implements': [impl.name for impl in node.implements] if node.implements else [],
                'methods': [],
                'fields': []
            }
            
            for member in node.body:
                if isinstance(member, javalang.tree.MethodDeclaration):
                    class_info['methods'].append({
                        'name': member.name,
                        'return_type': member.return_type.name if member.return_type else 'void',
                        'modifiers': list(member.modifiers),
                        'parameters': [
                            {
                                'name': param.name,
                                'type': param.type.name
                            }
                            for param in member.parameters
                        ]
                    })
                elif isinstance(member, javalang.tree.FieldDeclaration):
                    for declarator in member.declarators:
                        class_info['fields'].append({
                            'name': declarator.name,
                            'type': member.type.name,
                            'modifiers': list(member.modifiers)
                        })
                        
            analysis['classes'].append(class_info)
            
        elif isinstance(node, javalang.tree.InterfaceDeclaration):
            interface_info = {
                'name': node.name,
                'modifiers': list(node.modifiers),
                'extends': [impl.name for impl in node.extends] if node.extends else [],
                'methods': []
            }
            
            for member in node.body:
                if isinstance(member, javalang.tree.MethodDeclaration):
                    interface_info['methods'].append({
                        'name': member.name,
                        'return_type': member.return_type.name if member.return_type else 'void',
                        'modifiers': list(member.modifiers),
                        'parameters': [
                            {
                                'name': param.name,
                                'type': param.type.name
                            }
                            for param in member.parameters
                        ]
                    })
                    
            analysis['interfaces'].append(interface_info)
            
        elif isinstance(node, javalang.tree.EnumDeclaration):
            enum_info = {
                'name': node.name,
                'modifiers': list(node.modifiers),
                'implements': [impl.name for impl in node.implements] if node.implements else [],
                'constants': [],
                'methods': []
            }
            
            for member in node.body:
                if isinstance(member, javalang.tree.EnumConstant):
                    enum_info['constants'].append(member.name)
                elif isinstance(member, javalang.tree.MethodDeclaration):
                    enum_info['methods'].append({
                        'name': member.name,
                        'return_type': member.return_type.name if member.return_type else 'void',
                        'modifiers': list(member.modifiers),
                        'parameters': [
                            {
                                'name': param.name,
                                'type': param.type.name
                            }
                            for param in member.parameters
                        ]
                    })
                    
            analysis['enums'].append(enum_info)
            
    def _calculate_metrics(self, tree: Node) -> Dict[str, Any]:
        """Calculate code metrics."""
        metrics = {
            'complexity': 0,
            'lines': 0,
            'statements': 0,
            'methods': 0,
            'classes': 0,
            'interfaces': 0,
            'enums': 0
        }
        
        def count_node(node: Node) -> None:
            if isinstance(node, Node):
                metrics['statements'] += 1
                
                if isinstance(node, javalang.tree.MethodDeclaration):
                    metrics['methods'] += 1
                elif isinstance(node, javalang.tree.ClassDeclaration):
                    metrics['classes'] += 1
                elif isinstance(node, javalang.tree.InterfaceDeclaration):
                    metrics['interfaces'] += 1
                elif isinstance(node, javalang.tree.EnumDeclaration):
                    metrics['enums'] += 1
                    
                # Calculate cyclomatic complexity
                if isinstance(node, (javalang.tree.IfStatement, javalang.tree.WhileStatement,
                                  javalang.tree.ForStatement, javalang.tree.DoStatement,
                                  javalang.tree.CatchClause, javalang.tree.ConditionalExpression)):
                    metrics['complexity'] += 1
                    
                # Count lines
                if hasattr(node, 'position'):
                    metrics['lines'] = max(metrics['lines'], node.position.line)
                    
                # Recursively count child nodes
                for value in node.__dict__.values():
                    if isinstance(value, (Node, list)):
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item, Node):
                                    count_node(item)
                        else:
                            count_node(value)
                            
        count_node(tree)
        return metrics
        
    def get_dependencies(self, file_path: str) -> List[str]:
        """Get list of dependencies for a file."""
        if file_path not in self.ast_cache:
            self.analyze_code(file_path)
            
        dependencies = set()
        tree = self.ast_cache[file_path]
        
        def collect_dependencies(node: Node) -> None:
            if isinstance(node, javalang.tree.Import):
                dependencies.add(node.path)
            elif isinstance(node, javalang.tree.ClassDeclaration):
                if node.extends:
                    dependencies.add(node.extends.name)
                for impl in node.implements or []:
                    dependencies.add(impl.name)
            elif isinstance(node, javalang.tree.InterfaceDeclaration):
                for impl in node.extends or []:
                    dependencies.add(impl.name)
                    
            for value in node.__dict__.values():
                if isinstance(value, (Node, list)):
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, Node):
                                collect_dependencies(item)
                    else:
                        collect_dependencies(value)
                        
        collect_dependencies(tree)
        return list(dependencies)
        
    def get_symbols(self, file_path: str) -> Dict[str, List[str]]:
        """Get all symbols (fields, methods, classes) in a file."""
        if file_path not in self.ast_cache:
            self.analyze_code(file_path)
            
        symbols = {
            'fields': [],
            'methods': [],
            'classes': [],
            'interfaces': [],
            'enums': []
        }
        
        def collect_symbols(node: Node) -> None:
            if isinstance(node, javalang.tree.FieldDeclaration):
                for declarator in node.declarators:
                    symbols['fields'].append(declarator.name)
            elif isinstance(node, javalang.tree.MethodDeclaration):
                symbols['methods'].append(node.name)
            elif isinstance(node, javalang.tree.ClassDeclaration):
                symbols['classes'].append(node.name)
            elif isinstance(node, javalang.tree.InterfaceDeclaration):
                symbols['interfaces'].append(node.name)
            elif isinstance(node, javalang.tree.EnumDeclaration):
                symbols['enums'].append(node.name)
                
            for value in node.__dict__.values():
                if isinstance(value, (Node, list)):
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, Node):
                                collect_symbols(item)
                    else:
                        collect_symbols(value)
                        
        collect_symbols(self.ast_cache[file_path])
        return symbols 