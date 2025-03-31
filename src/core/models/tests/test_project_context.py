"""Tests for project context management."""

import unittest
from pathlib import Path
from typing import Dict, Any
from ..project_context import ProjectContext, ProjectFile, SemanticContext
from ..enhanced_code_understanding import CodeEntity

class TestProjectContext(unittest.TestCase):
    """Tests for project context management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent / "test_data"
        self.context = ProjectContext(str(self.test_dir))
        
    def test_project_analysis(self):
        """Test comprehensive project analysis."""
        analysis = self.context.analyze_project()
        
        # Check basic structure
        self.assertIn('files', analysis)
        self.assertIn('dependencies', analysis)
        self.assertIn('semantic_contexts', analysis)
        self.assertIn('metrics', analysis)
        
        # Check files
        self.assertGreater(len(analysis['files']), 0)
        for file_path, file_analysis in analysis['files'].items():
            self.assertIn('language', file_analysis)
            self.assertIn('entities', file_analysis)
            self.assertIn('dependencies', file_analysis)
            
        # Check dependencies
        deps = analysis['dependencies']
        self.assertIn('graph', deps)
        self.assertIn('cycles', deps)
        self.assertIn('topological_order', deps)
        self.assertIn('strongly_connected_components', deps)
        
        # Check semantic contexts
        contexts = analysis['semantic_contexts']
        self.assertIn('contexts', contexts)
        self.assertIn('symbol_table', contexts)
        self.assertIn('type_registry', contexts)
        
        # Check metrics
        metrics = analysis['metrics']
        self.assertIn('total_files', metrics)
        self.assertIn('total_entities', metrics)
        self.assertIn('dependency_metrics', metrics)
        self.assertIn('complexity_metrics', metrics)
        self.assertIn('maintainability_metrics', metrics)
        
    def test_dependency_tracking(self):
        """Test cross-file dependency tracking."""
        analysis = self.context.analyze_project()
        
        # Check dependency graph
        graph = analysis['dependencies']['graph']
        self.assertIsInstance(graph, dict)
        
        # Check for cycles
        cycles = analysis['dependencies']['cycles']
        self.assertIsInstance(cycles, list)
        
        # Check topological order
        topo_order = analysis['dependencies']['topological_order']
        self.assertIsInstance(topo_order, list)
        self.assertEqual(len(topo_order), len(analysis['files']))
        
        # Check strongly connected components
        scc = analysis['dependencies']['strongly_connected_components']
        self.assertIsInstance(scc, list)
        
        # Test dependency queries
        for file_path in analysis['files']:
            deps = self.context.get_file_dependencies(file_path)
            self.assertIsInstance(deps, list)
            
            dependents = self.context.get_file_dependents(file_path)
            self.assertIsInstance(dependents, list)
            
    def test_semantic_analysis(self):
        """Test semantic code analysis."""
        analysis = self.context.analyze_project()
        
        # Check semantic contexts
        contexts = analysis['semantic_contexts']['contexts']
        self.assertGreater(len(contexts), 0)
        
        for name, context in contexts.items():
            # Check context structure
            self.assertIn('entity', context)
            self.assertIn('scope', context)
            self.assertIn('type_info', context)
            self.assertIn('references', context)
            self.assertIn('definitions', context)
            self.assertIn('dependencies', context)
            
            # Check entity information
            entity = context['entity']
            self.assertIsInstance(entity, CodeEntity)
            self.assertEqual(entity.name, name)
            
            # Check scope
            self.assertIn(context['scope'], ['global', 'class', 'local', 'unknown'])
            
            # Check type information
            type_info = context['type_info']
            self.assertIn('type', type_info)
            self.assertIn('language', type_info)
            self.assertIn('annotations', type_info)
            self.assertIn('inferred_types', type_info)
            
            # Check references and definitions
            self.assertIsInstance(context['references'], list)
            self.assertIsInstance(context['definitions'], list)
            
            # Check dependencies
            self.assertIsInstance(context['dependencies'], list)
            
    def test_entity_context(self):
        """Test entity context management."""
        analysis = self.context.analyze_project()
        
        # Get all entities
        entities = []
        for file_analysis in analysis['files'].values():
            entities.extend(file_analysis['entities'])
            
        self.assertGreater(len(entities), 0)
        
        for entity in entities:
            # Get entity context
            context = self.context.get_entity_context(entity.name)
            self.assertIsNotNone(context)
            self.assertIsInstance(context, SemanticContext)
            
            # Check context properties
            self.assertEqual(context.entity, entity)
            self.assertIn(context.scope, ['global', 'class', 'local', 'unknown'])
            self.assertIsInstance(context.type_info, dict)
            self.assertIsInstance(context.references, list)
            self.assertIsInstance(context.definitions, list)
            self.assertIsInstance(context.dependencies, list)
            
            # Test entity queries
            refs = self.context.get_entity_references(entity.name)
            self.assertIsInstance(refs, list)
            
            defs = self.context.get_entity_definitions(entity.name)
            self.assertIsInstance(defs, list)
            self.assertGreater(len(defs), 0)
            
            deps = self.context.get_entity_dependencies(entity.name)
            self.assertIsInstance(deps, list)
            
            type_info = self.context.get_type_info(entity.name)
            self.assertIsNotNone(type_info)
            self.assertIsInstance(type_info, dict)
            
    def test_project_metrics(self):
        """Test project-wide metrics calculation."""
        analysis = self.context.analyze_project()
        metrics = analysis['metrics']
        
        # Check basic metrics
        self.assertGreater(metrics['total_files'], 0)
        self.assertGreater(metrics['total_entities'], 0)
        
        # Check dependency metrics
        dep_metrics = metrics['dependency_metrics']
        self.assertGreaterEqual(dep_metrics['average_dependencies'], 0)
        self.assertGreaterEqual(dep_metrics['max_dependencies'], 0)
        self.assertGreaterEqual(dep_metrics['dependency_density'], 0)
        self.assertLessEqual(dep_metrics['dependency_density'], 1)
        
        # Check complexity metrics
        comp_metrics = metrics['complexity_metrics']
        self.assertGreaterEqual(comp_metrics['average_complexity'], 0)
        self.assertGreaterEqual(comp_metrics['max_complexity'], 0)
        
        # Check maintainability metrics
        maint_metrics = metrics['maintainability_metrics']
        self.assertGreaterEqual(maint_metrics['average_maintainability'], 0)
        self.assertLessEqual(maint_metrics['average_maintainability'], 1)
        self.assertGreaterEqual(maint_metrics['min_maintainability'], 0)
        self.assertLessEqual(maint_metrics['min_maintainability'], 1)
        
    def test_symbol_table(self):
        """Test symbol table management."""
        analysis = self.context.analyze_project()
        
        # Check symbol table
        symbol_table = analysis['semantic_contexts']['symbol_table']
        self.assertIsInstance(symbol_table, dict)
        
        # Check entries
        for symbol, locations in symbol_table.items():
            self.assertIsInstance(locations, list)
            self.assertGreater(len(locations), 0)
            
            for file_path, line_number in locations:
                self.assertIsInstance(file_path, str)
                self.assertIsInstance(line_number, int)
                self.assertGreater(line_number, 0)
                
    def test_type_registry(self):
        """Test type registry management."""
        analysis = self.context.analyze_project()
        
        # Check type registry
        type_registry = analysis['semantic_contexts']['type_registry']
        self.assertIsInstance(type_registry, dict)
        
        # Check type information
        for type_name, type_info in type_registry.items():
            self.assertIsInstance(type_info, dict)
            self.assertIn('type', type_info)
            self.assertIn('language', type_info)
            self.assertIn('annotations', type_info)
            self.assertIn('inferred_types', type_info)
            
    def test_error_handling(self):
        """Test error handling in project analysis."""
        # Test with invalid directory
        with self.assertRaises(Exception):
            ProjectContext("/invalid/directory")
            
        # Test with empty directory
        empty_dir = self.test_dir / "empty"
        empty_dir.mkdir(exist_ok=True)
        context = ProjectContext(str(empty_dir))
        analysis = context.analyze_project()
        
        # Check empty analysis
        self.assertEqual(len(analysis['files']), 0)
        self.assertEqual(len(analysis['semantic_contexts']['contexts']), 0)
        self.assertEqual(analysis['metrics']['total_files'], 0)
        self.assertEqual(analysis['metrics']['total_entities'], 0)
        
        # Clean up
        empty_dir.rmdir()

if __name__ == '__main__':
    unittest.main() 