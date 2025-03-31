"""Project-wide context management and dependency tracking."""

from typing import Dict, List, Any, Optional, Set, Tuple, Union
from pathlib import Path
import networkx as nx
from dataclasses import dataclass
from collections import defaultdict
import logging
from .enhanced_code_understanding import EnhancedCodeUnderstanding, CodeEntity, LanguageConfig

@dataclass
class ProjectFile:
    """Represents a file in the project with its analysis results."""
    path: str
    language: str
    entities: List[CodeEntity]
    dependencies: List[str]
    imports: List[str]
    exports: List[str]
    analysis: Dict[str, Any]

@dataclass
class SemanticContext:
    """Represents semantic context for code entities."""
    entity: CodeEntity
    scope: str
    type_info: Dict[str, Any]
    references: List[Tuple[str, int]]  # List of (file_path, line_number)
    definitions: List[Tuple[str, int]]  # List of (file_path, line_number)
    dependencies: List[str]
    parent_entity: Optional[str] = None
    child_entities: List[str] = None

class ProjectContext:
    """Manages project-wide context and dependencies."""
    
    def __init__(self, root_dir: str):
        """Initialize project context."""
        self.root_dir = Path(root_dir)
        self.analyzer = EnhancedCodeUnderstanding()
        self.files: Dict[str, ProjectFile] = {}
        self.dependency_graph = nx.DiGraph()
        self.semantic_contexts: Dict[str, SemanticContext] = {}
        self.symbol_table: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        self.type_registry: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)
        
    def analyze_project(self) -> Dict[str, Any]:
        """Analyze entire project and build context."""
        project_analysis = {
            'files': {},
            'dependencies': {},
            'semantic_contexts': {},
            'metrics': {}
        }
        
        # First pass: analyze all files
        for file_path in self._get_project_files():
            try:
                file_analysis = self.analyzer.analyze_file(str(file_path))
                self.files[str(file_path)] = ProjectFile(
                    path=str(file_path),
                    language=file_analysis['language'],
                    entities=file_analysis['entities'],
                    dependencies=file_analysis['dependencies'],
                    imports=self._extract_imports(file_analysis),
                    exports=self._extract_exports(file_analysis),
                    analysis=file_analysis
                )
                project_analysis['files'][str(file_path)] = file_analysis
            except Exception as e:
                self.logger.error(f"Error analyzing {file_path}: {str(e)}")
                
        # Second pass: build dependency graph and semantic contexts
        self._build_dependency_graph()
        self._build_semantic_contexts()
        
        # Add dependency and semantic information to project analysis
        project_analysis['dependencies'] = self._get_dependency_info()
        project_analysis['semantic_contexts'] = self._get_semantic_info()
        
        # Calculate project-wide metrics
        project_analysis['metrics'] = self._calculate_project_metrics()
        
        return project_analysis
        
    def _get_project_files(self) -> List[Path]:
        """Get all relevant files in the project."""
        files = []
        for ext in ['.py', '.js', '.jsx', '.ts', '.tsx']:
            files.extend(self.root_dir.rglob(f'*{ext}'))
        return files
        
    def _extract_imports(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract import statements from analysis."""
        imports = []
        if 'syntax' in analysis and 'imports' in analysis['syntax']:
            for imp in analysis['syntax']['imports']:
                imports.append(imp['text'])
        return imports
        
    def _extract_exports(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract export statements from analysis."""
        exports = []
        if 'syntax' in analysis:
            for entity in analysis['syntax'].get('classes', []):
                exports.append(entity['name'])
            for entity in analysis['syntax'].get('functions', []):
                exports.append(entity['name'])
        return exports
        
    def _build_dependency_graph(self):
        """Build dependency graph between files."""
        for file_path, file_info in self.files.items():
            self.dependency_graph.add_node(file_path)
            
            # Add edges based on imports
            for imp in file_info.imports:
                for other_path, other_info in self.files.items():
                    if imp in other_info.exports:
                        self.dependency_graph.add_edge(file_path, other_path)
                        
    def _build_semantic_contexts(self):
        """Build semantic contexts for all entities."""
        for file_path, file_info in self.files.items():
            for entity in file_info.entities:
                context = SemanticContext(
                    entity=entity,
                    scope=self._determine_scope(entity, file_info),
                    type_info=self._extract_type_info(entity, file_info),
                    references=self._find_references(entity, file_path),
                    definitions=self._find_definitions(entity, file_path),
                    dependencies=self._get_entity_dependencies(entity, file_info)
                )
                self.semantic_contexts[entity.name] = context
                
                # Update symbol table
                self.symbol_table[entity.name].append((file_path, entity.line_number))
                
    def _determine_scope(self, entity: CodeEntity, file_info: ProjectFile) -> str:
        """Determine the scope of an entity."""
        if entity.scope == 'module':
            return 'global'
        elif entity.scope == 'class':
            return 'class'
        elif entity.scope == 'function':
            return 'local'
        return 'unknown'
        
    def _extract_type_info(self, entity: CodeEntity, file_info: ProjectFile) -> Dict[str, Any]:
        """Extract type information for an entity."""
        type_info = {
            'type': entity.type,
            'language': file_info.language,
            'annotations': {},
            'inferred_types': {}
        }
        
        # Extract type annotations from analysis
        if 'syntax' in file_info.analysis:
            if entity.type == 'class':
                for cls in file_info.analysis['syntax'].get('classes', []):
                    if cls['name'] == entity.name:
                        type_info['annotations'] = cls.get('type_annotations', {})
                        break
            elif entity.type == 'function':
                for func in file_info.analysis['syntax'].get('functions', []):
                    if func['name'] == entity.name:
                        type_info['annotations'] = func.get('type_annotations', {})
                        break
                        
        return type_info
        
    def _find_references(self, entity: CodeEntity, file_path: str) -> List[Tuple[str, int]]:
        """Find all references to an entity across files."""
        references = []
        
        # Check current file
        if 'semantics' in self.files[file_path].analysis:
            for ref in self.files[file_path].analysis['semantics'].get('references', {}).get(entity.name, []):
                references.append((file_path, ref['line']))
                
        # Check other files
        for other_path, other_info in self.files.items():
            if other_path != file_path and 'semantics' in other_info.analysis:
                for ref in other_info.analysis['semantics'].get('references', {}).get(entity.name, []):
                    references.append((other_path, ref['line']))
                    
        return references
        
    def _find_definitions(self, entity: CodeEntity, file_path: str) -> List[Tuple[str, int]]:
        """Find all definitions of an entity."""
        definitions = [(file_path, entity.line_number)]
        
        # Check for multiple definitions (e.g., in different files)
        for other_path, other_info in self.files.items():
            if other_path != file_path:
                for other_entity in other_info.entities:
                    if other_entity.name == entity.name:
                        definitions.append((other_path, other_entity.line_number))
                        
        return definitions
        
    def _get_entity_dependencies(self, entity: CodeEntity, file_info: ProjectFile) -> List[str]:
        """Get dependencies for an entity."""
        dependencies = []
        
        # Add direct dependencies from entity
        dependencies.extend(entity.dependencies)
        
        # Add dependencies from file
        dependencies.extend(file_info.dependencies)
        
        # Add dependencies from imports
        for imp in file_info.imports:
            for other_path, other_info in self.files.items():
                if imp in other_info.exports:
                    dependencies.append(other_path)
                    
        return list(set(dependencies))
        
    def _get_dependency_info(self) -> Dict[str, Any]:
        """Get dependency information for the project."""
        return {
            'graph': nx.to_dict_of_dicts(self.dependency_graph),
            'cycles': list(nx.simple_cycles(self.dependency_graph)),
            'topological_order': list(nx.topological_sort(self.dependency_graph)),
            'strongly_connected_components': list(nx.strongly_connected_components(self.dependency_graph))
        }
        
    def _get_semantic_info(self) -> Dict[str, Any]:
        """Get semantic information for the project."""
        return {
            'contexts': {
                name: {
                    'entity': context.entity,
                    'scope': context.scope,
                    'type_info': context.type_info,
                    'references': context.references,
                    'definitions': context.definitions,
                    'dependencies': context.dependencies
                }
                for name, context in self.semantic_contexts.items()
            },
            'symbol_table': dict(self.symbol_table),
            'type_registry': self.type_registry
        }
        
    def _calculate_project_metrics(self) -> Dict[str, Any]:
        """Calculate project-wide metrics."""
        metrics = {
            'total_files': len(self.files),
            'total_entities': len(self.semantic_contexts),
            'dependency_metrics': {
                'average_dependencies': sum(len(f.dependencies) for f in self.files.values()) / len(self.files),
                'max_dependencies': max(len(f.dependencies) for f in self.files.values()),
                'dependency_density': nx.density(self.dependency_graph)
            },
            'complexity_metrics': {
                'average_complexity': sum(
                    f.analysis.get('complexity', {}).get('complexity_score', 0)
                    for f in self.files.values()
                ) / len(self.files),
                'max_complexity': max(
                    f.analysis.get('complexity', {}).get('complexity_score', 0)
                    for f in self.files.values()
                )
            },
            'maintainability_metrics': {
                'average_maintainability': sum(
                    f.analysis.get('maintainability', {}).get('score', 0)
                    for f in self.files.values()
                ) / len(self.files),
                'min_maintainability': min(
                    f.analysis.get('maintainability', {}).get('score', 0)
                    for f in self.files.values()
                )
            }
        }
        
        return metrics
        
    def get_entity_context(self, entity_name: str) -> Optional[SemanticContext]:
        """Get semantic context for a specific entity."""
        return self.semantic_contexts.get(entity_name)
        
    def get_file_dependencies(self, file_path: str) -> List[str]:
        """Get dependencies for a specific file."""
        return list(self.dependency_graph.successors(file_path))
        
    def get_file_dependents(self, file_path: str) -> List[str]:
        """Get files that depend on a specific file."""
        return list(self.dependency_graph.predecessors(file_path))
        
    def get_entity_references(self, entity_name: str) -> List[Tuple[str, int]]:
        """Get all references to a specific entity."""
        context = self.get_entity_context(entity_name)
        return context.references if context else []
        
    def get_entity_definitions(self, entity_name: str) -> List[Tuple[str, int]]:
        """Get all definitions of a specific entity."""
        context = self.get_entity_context(entity_name)
        return context.definitions if context else []
        
    def get_entity_dependencies(self, entity_name: str) -> List[str]:
        """Get dependencies for a specific entity."""
        context = self.get_entity_context(entity_name)
        return context.dependencies if context else []
        
    def get_type_info(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """Get type information for a specific entity."""
        context = self.get_entity_context(entity_name)
        return context.type_info if context else None 