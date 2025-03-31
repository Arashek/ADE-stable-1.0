from typing import Dict, Any, List, Optional
import ast
import re
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
from .base import BaseDocumentationGenerator
from ...config.logging_config import logger

class ArchitectureDocumentationGenerator(BaseDocumentationGenerator):
    """Generator for system architecture documentation"""
    
    def __init__(self, output_dir: str = "docs"):
        super().__init__(output_dir)
        self.graph = nx.DiGraph()
        self.components = {}
        self.relationships = []
        self.data_flows = []
        
    def generate_architecture_docs(self, source_dir: str, config: Dict[str, Any] = None):
        """Generate architecture documentation"""
        try:
            self.create_output_dirs()
            source_path = Path(source_dir)
            config = config or {}
            
            # Analyze system components
            self._analyze_components(source_path)
            
            # Analyze relationships
            self._analyze_relationships(source_path)
            
            # Analyze data flows
            self._analyze_data_flows(source_path)
            
            # Generate documentation
            self._generate_component_docs()
            self._generate_relationship_docs()
            self._generate_data_flow_docs()
            
            # Generate diagrams
            self._generate_component_diagram()
            self._generate_relationship_diagram()
            self._generate_data_flow_diagram()
            
            # Generate architecture overview
            self._generate_architecture_overview()
            
            logger.info("Architecture documentation generated successfully")
            
        except Exception as e:
            logger.error(f"Error generating architecture documentation: {str(e)}")
            raise
            
    def _analyze_components(self, source_path: Path):
        """Analyze system components"""
        try:
            # Find Python files
            python_files = list(source_path.rglob("*.py"))
            
            for file_path in python_files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                
                # Analyze classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        component = {
                            "name": node.name,
                            "type": "class",
                            "file": str(file_path),
                            "docstring": ast.get_docstring(node),
                            "methods": [],
                            "dependencies": []
                        }
                        
                        # Extract methods
                        for child in node.body:
                            if isinstance(child, ast.FunctionDef):
                                component["methods"].append({
                                    "name": child.name,
                                    "docstring": ast.get_docstring(child)
                                })
                                
                        # Extract dependencies
                        for child in ast.walk(node):
                            if isinstance(child, ast.Import):
                                component["dependencies"].extend(
                                    alias.name for alias in child.names
                                )
                            elif isinstance(child, ast.ImportFrom):
                                component["dependencies"].append(child.module)
                                
                        self.components[node.name] = component
                        self.graph.add_node(node.name, **component)
                        
                # Analyze functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        component = {
                            "name": node.name,
                            "type": "function",
                            "file": str(file_path),
                            "docstring": ast.get_docstring(node),
                            "dependencies": []
                        }
                        
                        # Extract dependencies
                        for child in ast.walk(node):
                            if isinstance(child, ast.Import):
                                component["dependencies"].extend(
                                    alias.name for alias in child.names
                                )
                            elif isinstance(child, ast.ImportFrom):
                                component["dependencies"].append(child.module)
                                
                        self.components[node.name] = component
                        self.graph.add_node(node.name, **component)
                        
        except Exception as e:
            logger.error(f"Error analyzing components: {str(e)}")
            raise
            
    def _analyze_relationships(self, source_path: Path):
        """Analyze relationships between components"""
        try:
            for component_name, component in self.components.items():
                # Analyze dependencies
                for dep in component["dependencies"]:
                    if dep in self.components:
                        relationship = {
                            "source": component_name,
                            "target": dep,
                            "type": "dependency",
                            "description": f"{component_name} depends on {dep}"
                        }
                        self.relationships.append(relationship)
                        self.graph.add_edge(component_name, dep, **relationship)
                        
                # Analyze method calls
                if component["type"] == "class":
                    for method in component["methods"]:
                        # Find method calls in the code
                        method_calls = self._find_method_calls(
                            source_path,
                            component_name,
                            method["name"]
                        )
                        
                        for call in method_calls:
                            relationship = {
                                "source": component_name,
                                "target": call,
                                "type": "method_call",
                                "description": f"{component_name}.{method['name']} is called by {call}"
                            }
                            self.relationships.append(relationship)
                            self.graph.add_edge(component_name, call, **relationship)
                            
        except Exception as e:
            logger.error(f"Error analyzing relationships: {str(e)}")
            raise
            
    def _analyze_data_flows(self, source_path: Path):
        """Analyze data flows between components"""
        try:
            for component_name, component in self.components.items():
                # Analyze function parameters and return values
                if component["type"] == "function":
                    data_flow = {
                        "component": component_name,
                        "inputs": self._extract_function_inputs(component),
                        "outputs": self._extract_function_outputs(component),
                        "description": component["docstring"]
                    }
                    self.data_flows.append(data_flow)
                    
                # Analyze class methods
                elif component["type"] == "class":
                    for method in component["methods"]:
                        data_flow = {
                            "component": f"{component_name}.{method['name']}",
                            "inputs": self._extract_method_inputs(component, method),
                            "outputs": self._extract_method_outputs(component, method),
                            "description": method["docstring"]
                        }
                        self.data_flows.append(data_flow)
                        
        except Exception as e:
            logger.error(f"Error analyzing data flows: {str(e)}")
            raise
            
    def _find_method_calls(self, source_path: Path, class_name: str, method_name: str) -> List[str]:
        """Find components that call a specific method"""
        try:
            calls = []
            for file_path in source_path.rglob("*.py"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for method calls
                pattern = f"{class_name}\(.*?\)\.{method_name}\("
                matches = re.finditer(pattern, content)
                
                for match in matches:
                    # Find the calling component
                    context = content[max(0, match.start()-100):match.start()]
                    for comp_name in self.components:
                        if comp_name in context:
                            calls.append(comp_name)
                            break
                            
            return list(set(calls))
        except Exception as e:
            logger.error(f"Error finding method calls: {str(e)}")
            return []
            
    def _extract_function_inputs(self, component: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract function input parameters"""
        try:
            inputs = []
            file_path = Path(component["file"])
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == component["name"]:
                    for arg in node.args.args:
                        inputs.append({
                            "name": arg.arg,
                            "type": self._get_annotation_type(arg.annotation) if arg.annotation else "any"
                        })
                    break
                    
            return inputs
        except Exception as e:
            logger.error(f"Error extracting function inputs: {str(e)}")
            return []
            
    def _extract_function_outputs(self, component: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract function return values"""
        try:
            outputs = []
            file_path = Path(component["file"])
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == component["name"]:
                    if node.returns:
                        outputs.append({
                            "name": "return",
                            "type": self._get_annotation_type(node.returns)
                        })
                    break
                    
            return outputs
        except Exception as e:
            logger.error(f"Error extracting function outputs: {str(e)}")
            return []
            
    def _extract_method_inputs(self, component: Dict[str, Any], method: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract method input parameters"""
        try:
            inputs = []
            file_path = Path(component["file"])
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == component["name"]:
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef) and child.name == method["name"]:
                            for arg in child.args.args:
                                inputs.append({
                                    "name": arg.arg,
                                    "type": self._get_annotation_type(arg.annotation) if arg.annotation else "any"
                                })
                            break
                    break
                    
            return inputs
        except Exception as e:
            logger.error(f"Error extracting method inputs: {str(e)}")
            return []
            
    def _extract_method_outputs(self, component: Dict[str, Any], method: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract method return values"""
        try:
            outputs = []
            file_path = Path(component["file"])
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == component["name"]:
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef) and child.name == method["name"]:
                            if child.returns:
                                outputs.append({
                                    "name": "return",
                                    "type": self._get_annotation_type(child.returns)
                                })
                            break
                    break
                    
            return outputs
        except Exception as e:
            logger.error(f"Error extracting method outputs: {str(e)}")
            return []
            
    def _get_annotation_type(self, annotation: ast.AST) -> str:
        """Get type from annotation"""
        try:
            if isinstance(annotation, ast.Name):
                return annotation.id
            elif isinstance(annotation, ast.Subscript):
                return f"{annotation.value.id}[{self._get_annotation_type(annotation.slice)}]"
            elif isinstance(annotation, ast.BinOp):
                return f"{self._get_annotation_type(annotation.left)} | {self._get_annotation_type(annotation.right)}"
            else:
                return "any"
        except Exception as e:
            logger.error(f"Error getting annotation type: {str(e)}")
            return "any"
            
    def _generate_component_docs(self):
        """Generate component documentation"""
        try:
            template = self.load_template("component_docs.md")
            content = template.render(
                components=self.components,
                version_info=self.generate_version_info()
            )
            self.save_file(content, "architecture/components.md")
        except Exception as e:
            logger.error(f"Error generating component documentation: {str(e)}")
            raise
            
    def _generate_relationship_docs(self):
        """Generate relationship documentation"""
        try:
            template = self.load_template("relationship_docs.md")
            content = template.render(
                relationships=self.relationships,
                version_info=self.generate_version_info()
            )
            self.save_file(content, "architecture/relationships.md")
        except Exception as e:
            logger.error(f"Error generating relationship documentation: {str(e)}")
            raise
            
    def _generate_data_flow_docs(self):
        """Generate data flow documentation"""
        try:
            template = self.load_template("data_flow_docs.md")
            content = template.render(
                data_flows=self.data_flows,
                version_info=self.generate_version_info()
            )
            self.save_file(content, "architecture/data_flows.md")
        except Exception as e:
            logger.error(f"Error generating data flow documentation: {str(e)}")
            raise
            
    def _generate_component_diagram(self):
        """Generate component diagram"""
        try:
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(self.graph)
            
            # Draw nodes
            nx.draw_networkx_nodes(
                self.graph,
                pos,
                node_color='lightblue',
                node_size=2000
            )
            
            # Draw edges
            nx.draw_networkx_edges(
                self.graph,
                pos,
                edge_color='gray',
                arrows=True
            )
            
            # Draw labels
            nx.draw_networkx_labels(
                self.graph,
                pos,
                font_size=8,
                font_weight='bold'
            )
            
            # Save diagram
            plt.savefig(self.output_dir / "architecture/component_diagram.png")
            plt.close()
            
        except Exception as e:
            logger.error(f"Error generating component diagram: {str(e)}")
            raise
            
    def _generate_relationship_diagram(self):
        """Generate relationship diagram"""
        try:
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(self.graph)
            
            # Draw nodes
            nx.draw_networkx_nodes(
                self.graph,
                pos,
                node_color='lightgreen',
                node_size=2000
            )
            
            # Draw edges with relationship types
            edge_labels = nx.get_edge_attributes(self.graph, 'type')
            nx.draw_networkx_edges(
                self.graph,
                pos,
                edge_color='gray',
                arrows=True
            )
            nx.draw_networkx_edge_labels(
                self.graph,
                pos,
                edge_labels=edge_labels,
                font_size=6
            )
            
            # Draw labels
            nx.draw_networkx_labels(
                self.graph,
                pos,
                font_size=8,
                font_weight='bold'
            )
            
            # Save diagram
            plt.savefig(self.output_dir / "architecture/relationship_diagram.png")
            plt.close()
            
        except Exception as e:
            logger.error(f"Error generating relationship diagram: {str(e)}")
            raise
            
    def _generate_data_flow_diagram(self):
        """Generate data flow diagram"""
        try:
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(self.graph)
            
            # Draw nodes
            nx.draw_networkx_nodes(
                self.graph,
                pos,
                node_color='lightpink',
                node_size=2000
            )
            
            # Draw edges with data flow information
            edge_labels = {
                (u, v): f"{self.graph[u][v].get('type', '')}\n{self.graph[u][v].get('description', '')}"
                for u, v in self.graph.edges()
            }
            nx.draw_networkx_edges(
                self.graph,
                pos,
                edge_color='gray',
                arrows=True
            )
            nx.draw_networkx_edge_labels(
                self.graph,
                pos,
                edge_labels=edge_labels,
                font_size=6
            )
            
            # Draw labels
            nx.draw_networkx_labels(
                self.graph,
                pos,
                font_size=8,
                font_weight='bold'
            )
            
            # Save diagram
            plt.savefig(self.output_dir / "architecture/data_flow_diagram.png")
            plt.close()
            
        except Exception as e:
            logger.error(f"Error generating data flow diagram: {str(e)}")
            raise
            
    def _generate_architecture_overview(self):
        """Generate architecture overview documentation"""
        try:
            template = self.load_template("architecture_overview.md")
            content = template.render(
                components=self.components,
                relationships=self.relationships,
                data_flows=self.data_flows,
                version_info=self.generate_version_info()
            )
            self.save_file(content, "architecture/overview.md")
        except Exception as e:
            logger.error(f"Error generating architecture overview: {str(e)}")
            raise 