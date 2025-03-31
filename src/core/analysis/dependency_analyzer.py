from typing import Dict, List, Any, Optional, Set, Tuple
import logging
from dataclasses import dataclass
from enum import Enum
import tree_sitter
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
import json
import re

logger = logging.getLogger(__name__)

class DependencyType(Enum):
    IMPORT = "import"
    INHERITANCE = "inheritance"
    COMPOSITION = "composition"
    FUNCTION_CALL = "function_call"
    VARIABLE_REFERENCE = "variable_reference"
    TYPE_REFERENCE = "type_reference"
    MODULE_DEPENDENCY = "module_dependency"

@dataclass
class Dependency:
    source: str
    target: str
    type: DependencyType
    location: str
    context: Dict[str, Any]
    weight: float = 1.0

class DependencyAnalyzer:
    """Advanced dependency analysis system with visualization capabilities."""
    
    def __init__(self):
        """Initialize the dependency analyzer."""
        self.dependency_graph = nx.DiGraph()
        self.module_map: Dict[str, str] = {}
        self._initialize_analyzers()
        
    def _initialize_analyzers(self):
        """Initialize language-specific dependency analyzers."""
        self.analyzers = {
            "python": self._analyze_python_dependencies,
            "javascript": self._analyze_javascript_dependencies,
            "typescript": self._analyze_typescript_dependencies,
            "java": self._analyze_java_dependencies,
            "cpp": self._analyze_cpp_dependencies
        }
        
    def analyze_project(self, project_root: str) -> nx.DiGraph:
        """Analyze dependencies across the entire project."""
        try:
            # Clear existing graph
            self.dependency_graph.clear()
            
            # Get all source files
            source_files = self._get_source_files(project_root)
            
            # Analyze each file
            for file_path in source_files:
                self._analyze_file(file_path)
                
            # Analyze cross-file dependencies
            self._analyze_cross_file_dependencies()
            
            # Detect circular dependencies
            self._detect_circular_dependencies()
            
            return self.dependency_graph
            
        except Exception as e:
            logger.error(f"Error analyzing project dependencies: {e}")
            raise
            
    def _get_source_files(self, project_root: str) -> List[str]:
        """Get all source files in the project."""
        source_files = []
        extensions = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".h": "cpp",
            ".hpp": "cpp"
        }
        
        for ext, lang in extensions.items():
            for file_path in Path(project_root).rglob(f"*{ext}"):
                source_files.append(str(file_path))
                self.module_map[str(file_path)] = lang
                
        return source_files
        
    def _analyze_file(self, file_path: str) -> None:
        """Analyze dependencies in a single file."""
        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Get language
            language = self.module_map.get(file_path)
            if not language:
                return
                
            # Parse code
            tree = self._parse_code(file_path, content, language)
            
            # Analyze dependencies
            analyzer = self.analyzers.get(language)
            if analyzer:
                dependencies = analyzer(tree, file_path)
                self._add_dependencies(dependencies)
                
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            
    def _parse_code(self, file_path: str, content: str, language: str) -> tree_sitter.Tree:
        """Parse code using tree-sitter."""
        parser = tree_sitter.Parser()
        parser.set_language(tree_sitter.Language(f"build/{language}.so", language))
        return parser.parse(bytes(content, "utf8"))
        
    def _analyze_python_dependencies(self, tree: tree_sitter.Tree, file_path: str) -> List[Dependency]:
        """Analyze Python dependencies."""
        dependencies = []
        
        def traverse(node: tree_sitter.Node):
            # Import statements
            if node.type == "import_statement":
                module_name = node.child_by_field_name("name").text.decode("utf8")
                dependencies.append(Dependency(
                    source=file_path,
                    target=module_name,
                    type=DependencyType.IMPORT,
                    location=f"{node.start_point[0]}:{node.end_point[0]}",
                    context={"module": module_name}
                ))
                
            # Class inheritance
            elif node.type == "class_definition":
                class_name = node.child_by_field_name("name").text.decode("utf8")
                for base in node.child_by_field_name("superclasses").children:
                    if base.type == "identifier":
                        base_name = base.text.decode("utf8")
                        dependencies.append(Dependency(
                            source=class_name,
                            target=base_name,
                            type=DependencyType.INHERITANCE,
                            location=f"{node.start_point[0]}:{node.end_point[0]}",
                            context={"class": class_name, "base": base_name}
                        ))
                        
            # Function calls
            elif node.type == "call":
                if node.child_by_field_name("function").type == "identifier":
                    func_name = node.child_by_field_name("function").text.decode("utf8")
                    dependencies.append(Dependency(
                        source=file_path,
                        target=func_name,
                        type=DependencyType.FUNCTION_CALL,
                        location=f"{node.start_point[0]}:{node.end_point[0]}",
                        context={"function": func_name}
                    ))
                    
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return dependencies
        
    def _analyze_javascript_dependencies(self, tree: tree_sitter.Tree, file_path: str) -> List[Dependency]:
        """Analyze JavaScript dependencies."""
        dependencies = []
        
        def traverse(node: tree_sitter.Node):
            # Import statements
            if node.type == "import_statement":
                module_name = node.child_by_field_name("source").text.decode("utf8")
                dependencies.append(Dependency(
                    source=file_path,
                    target=module_name,
                    type=DependencyType.IMPORT,
                    location=f"{node.start_point[0]}:{node.end_point[0]}",
                    context={"module": module_name}
                ))
                
            # Class inheritance
            elif node.type == "class_extends_clause":
                class_name = node.parent.child_by_field_name("name").text.decode("utf8")
                base_name = node.child_by_field_name("value").text.decode("utf8")
                dependencies.append(Dependency(
                    source=class_name,
                    target=base_name,
                    type=DependencyType.INHERITANCE,
                    location=f"{node.start_point[0]}:{node.end_point[0]}",
                    context={"class": class_name, "base": base_name}
                ))
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return dependencies
        
    def _analyze_typescript_dependencies(self, tree: tree_sitter.Tree, file_path: str) -> List[Dependency]:
        """Analyze TypeScript dependencies."""
        # Similar to JavaScript but with additional type dependencies
        return self._analyze_javascript_dependencies(tree, file_path)
        
    def _analyze_java_dependencies(self, tree: tree_sitter.Tree, file_path: str) -> List[Dependency]:
        """Analyze Java dependencies."""
        dependencies = []
        
        def traverse(node: tree_sitter.Node):
            # Import statements
            if node.type == "import_declaration":
                module_name = node.child_by_field_name("name").text.decode("utf8")
                dependencies.append(Dependency(
                    source=file_path,
                    target=module_name,
                    type=DependencyType.IMPORT,
                    location=f"{node.start_point[0]}:{node.end_point[0]}",
                    context={"module": module_name}
                ))
                
            # Class inheritance
            elif node.type == "extends_clause":
                class_name = node.parent.child_by_field_name("name").text.decode("utf8")
                base_name = node.child_by_field_name("value").text.decode("utf8")
                dependencies.append(Dependency(
                    source=class_name,
                    target=base_name,
                    type=DependencyType.INHERITANCE,
                    location=f"{node.start_point[0]}:{node.end_point[0]}",
                    context={"class": class_name, "base": base_name}
                ))
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return dependencies
        
    def _analyze_cpp_dependencies(self, tree: tree_sitter.Tree, file_path: str) -> List[Dependency]:
        """Analyze C++ dependencies."""
        dependencies = []
        
        def traverse(node: tree_sitter.Node):
            # Include statements
            if node.type == "preproc_include":
                include_path = node.child_by_field_name("path").text.decode("utf8")
                dependencies.append(Dependency(
                    source=file_path,
                    target=include_path,
                    type=DependencyType.IMPORT,
                    location=f"{node.start_point[0]}:{node.end_point[0]}",
                    context={"include": include_path}
                ))
                
            # Class inheritance
            elif node.type == "base_class_clause":
                class_name = node.parent.child_by_field_name("name").text.decode("utf8")
                base_name = node.child_by_field_name("value").text.decode("utf8")
                dependencies.append(Dependency(
                    source=class_name,
                    target=base_name,
                    type=DependencyType.INHERITANCE,
                    location=f"{node.start_point[0]}:{node.end_point[0]}",
                    context={"class": class_name, "base": base_name}
                ))
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return dependencies
        
    def _add_dependencies(self, dependencies: List[Dependency]) -> None:
        """Add dependencies to the graph."""
        for dep in dependencies:
            self.dependency_graph.add_edge(
                dep.source,
                dep.target,
                type=dep.type,
                location=dep.location,
                context=dep.context,
                weight=dep.weight
            )
            
    def _analyze_cross_file_dependencies(self) -> None:
        """Analyze dependencies between files."""
        # Implement cross-file dependency analysis
        pass
        
    def _detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in the graph."""
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            if cycles:
                logger.warning(f"Found {len(cycles)} circular dependencies")
                for cycle in cycles:
                    logger.warning(f"Circular dependency: {' -> '.join(cycle)}")
            return cycles
        except Exception as e:
            logger.error(f"Error detecting circular dependencies: {e}")
            return []
            
    def visualize_dependencies(self, output_path: str) -> None:
        """Visualize the dependency graph."""
        try:
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(self.dependency_graph)
            
            # Draw nodes
            nx.draw_networkx_nodes(
                self.dependency_graph,
                pos,
                node_size=1000,
                node_color="lightblue",
                alpha=0.7
            )
            
            # Draw edges
            nx.draw_networkx_edges(
                self.dependency_graph,
                pos,
                edge_color="gray",
                arrows=True,
                arrowsize=20
            )
            
            # Draw labels
            nx.draw_networkx_labels(
                self.dependency_graph,
                pos,
                font_size=8,
                font_family="sans-serif"
            )
            
            plt.title("Project Dependency Graph")
            plt.axis("off")
            plt.savefig(output_path, format="png", dpi=300, bbox_inches="tight")
            plt.close()
            
        except Exception as e:
            logger.error(f"Error visualizing dependencies: {e}")
            raise
            
    def export_dependencies(self, output_path: str) -> None:
        """Export dependencies to JSON format."""
        try:
            data = {
                "nodes": list(self.dependency_graph.nodes()),
                "edges": [
                    {
                        "source": u,
                        "target": v,
                        "type": d["type"].value,
                        "location": d["location"],
                        "context": d["context"],
                        "weight": d["weight"]
                    }
                    for u, v, d in self.dependency_graph.edges(data=True)
                ]
            }
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error exporting dependencies: {e}")
            raise
            
    def analyze_impact(self, file_path: str) -> Dict[str, Any]:
        """Analyze the impact of changes to a file."""
        try:
            # Get all files that depend on this file
            dependent_files = list(self.dependency_graph.predecessors(file_path))
            
            # Get all files this file depends on
            dependencies = list(self.dependency_graph.successors(file_path))
            
            # Calculate impact metrics
            impact_score = len(dependent_files) / (len(dependencies) + 1)  # Avoid division by zero
            
            return {
                "file": file_path,
                "dependent_files": dependent_files,
                "dependencies": dependencies,
                "impact_score": impact_score,
                "total_dependents": len(dependent_files),
                "total_dependencies": len(dependencies)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing impact for {file_path}: {e}")
            return {} 