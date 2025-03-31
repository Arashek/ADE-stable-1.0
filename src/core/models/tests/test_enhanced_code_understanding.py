"""Tests for the enhanced code understanding system."""

import unittest
from pathlib import Path
from typing import Dict, Any
from ..enhanced_code_understanding import EnhancedCodeUnderstanding, CodeEntity, LanguageConfig

class TestEnhancedCodeUnderstanding(unittest.TestCase):
    """Test cases for the EnhancedCodeUnderstanding class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = EnhancedCodeUnderstanding()
        self.test_file = Path(__file__).parent / "test_data" / "sample.py"
        self.test_js_file = Path(__file__).parent / "test_data" / "sample.js"
        
    def test_detect_language(self):
        """Test language detection."""
        # Test Python detection
        self.assertEqual(self.analyzer.detect_language(str(self.test_file)), 'python')
        
        # Test JavaScript detection
        self.assertEqual(self.analyzer.detect_language(str(self.test_js_file)), 'javascript')
        
        # Test unsupported file
        self.assertIsNone(self.analyzer.detect_language('test.unknown'))
        
    def test_language_configs(self):
        """Test language configurations."""
        configs = self.analyzer.language_configs
        
        # Check Python config
        self.assertIn('python', configs)
        python_config = configs['python']
        self.assertEqual(python_config.name, 'Python')
        self.assertIn('.py', python_config.file_extensions)
        self.assertEqual(python_config.parser_name, 'python')
        self.assertIn('def', python_config.keywords)
        self.assertIn('int', python_config.builtin_types)
        
        # Check JavaScript config
        self.assertIn('javascript', configs)
        js_config = configs['javascript']
        self.assertEqual(js_config.name, 'JavaScript')
        self.assertIn('.js', js_config.file_extensions)
        self.assertEqual(js_config.parser_name, 'javascript')
        self.assertIn('function', js_config.keywords)
        self.assertIn('string', js_config.builtin_types)
        
    def test_analyze_style(self):
        """Test style analysis."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        config = self.analyzer.language_configs['python']
        
        style = self.analyzer._analyze_style(tree, config)
        
        self.assertIn('naming_conventions', style)
        self.assertIn('docstrings', style)
        self.assertIn('type_annotations', style)
        self.assertIn('style_violations', style)
        
        # Check naming conventions
        for convention in style['naming_conventions']:
            self.assertIn('pattern', convention)
            self.assertIn('match', convention)
            self.assertIn('line', convention)
            
        # Check docstrings
        for docstring in style['docstrings']:
            self.assertIn('pattern', docstring)
            self.assertIn('match', docstring)
            self.assertIn('line', docstring)
            
        # Check type annotations
        for annotation in style['type_annotations']:
            self.assertIn('pattern', annotation)
            self.assertIn('match', annotation)
            self.assertIn('line', annotation)
            
    def test_analyze_complexity(self):
        """Test complexity analysis."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        config = self.analyzer.language_configs['python']
        
        complexity = self.analyzer._analyze_complexity(tree, config)
        
        self.assertIn('nesting_levels', complexity)
        self.assertIn('long_functions', complexity)
        self.assertIn('complex_conditions', complexity)
        self.assertIn('complexity_score', complexity)
        
        # Check nesting levels
        for nesting in complexity['nesting_levels']:
            self.assertIn('pattern', nesting)
            self.assertIn('match', nesting)
            self.assertIn('line', nesting)
            
        # Check long functions
        for func in complexity['long_functions']:
            self.assertIn('pattern', func)
            self.assertIn('match', func)
            self.assertIn('line', func)
            
        # Check complex conditions
        for condition in complexity['complex_conditions']:
            self.assertIn('pattern', condition)
            self.assertIn('match', condition)
            self.assertIn('line', condition)
            
        # Check complexity score
        self.assertIsInstance(complexity['complexity_score'], int)
        self.assertGreaterEqual(complexity['complexity_score'], 0)
        
    def test_analyze_file_with_language(self):
        """Test file analysis with language detection."""
        analysis = self.analyzer.analyze_file(str(self.test_file))
        
        # Check language-specific analysis
        self.assertIn('language', analysis)
        self.assertEqual(analysis['language'], 'python')
        
        # Check style analysis
        self.assertIn('style', analysis)
        style = analysis['style']
        self.assertIn('naming_conventions', style)
        self.assertIn('docstrings', style)
        self.assertIn('type_annotations', style)
        
        # Check complexity analysis
        self.assertIn('complexity', analysis)
        complexity = analysis['complexity']
        self.assertIn('nesting_levels', complexity)
        self.assertIn('long_functions', complexity)
        self.assertIn('complex_conditions', complexity)
        
        # Check language-specific patterns
        self.assertIn('security', analysis)
        security = analysis['security']
        self.assertIn('vulnerabilities', security)
        self.assertIn('risk_level', security)
        
        self.assertIn('performance', analysis)
        performance = analysis['performance']
        self.assertIn('issues', performance)
        self.assertIn('impact_level', performance)
        
    def test_entity_language(self):
        """Test language information in code entities."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        config = self.analyzer.language_configs['python']
        
        entities = self.analyzer._extract_entities(tree, str(self.test_file), config)
        
        for entity in entities:
            self.assertIsInstance(entity, CodeEntity)
            self.assertEqual(entity.language, 'Python')
            
    def test_unsupported_file(self):
        """Test handling of unsupported file types."""
        analysis = self.analyzer.analyze_file('test.unknown')
        self.assertEqual(analysis, {})
        
    def test_analyze_file(self):
        """Test comprehensive file analysis."""
        analysis = self.analyzer.analyze_file(str(self.test_file))
        
        # Check analysis structure
        self.assertIn('ast', analysis)
        self.assertIn('syntax', analysis)
        self.assertIn('semantics', analysis)
        self.assertIn('control_flow', analysis)
        self.assertIn('data_flow', analysis)
        self.assertIn('entities', analysis)
        self.assertIn('dependencies', analysis)
        
    def test_extract_ast(self):
        """Test AST extraction."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        ast = self.analyzer._extract_ast(tree)
        
        self.assertIsInstance(ast, dict)
        self.assertIn('type', ast)
        self.assertIn('children', ast)
        
    def test_analyze_syntax(self):
        """Test syntax analysis."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        syntax = self.analyzer._analyze_syntax(tree)
        
        self.assertIsInstance(syntax, dict)
        self.assertIn('imports', syntax)
        self.assertIn('classes', syntax)
        self.assertIn('functions', syntax)
        self.assertIn('variables', syntax)
        
    def test_analyze_semantics(self):
        """Test semantic analysis."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        semantics = self.analyzer._analyze_semantics(tree)
        
        self.assertIsInstance(semantics, dict)
        self.assertIn('scope', semantics)
        self.assertIn('references', semantics)
        self.assertIn('definitions', semantics)
        
    def test_analyze_control_flow(self):
        """Test control flow analysis."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        control_flow = self.analyzer._analyze_control_flow(tree)
        
        self.assertIsInstance(control_flow, dict)
        self.assertIn('branches', control_flow)
        self.assertIn('loops', control_flow)
        self.assertIn('exceptions', control_flow)
        
    def test_analyze_data_flow(self):
        """Test data flow analysis."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        data_flow = self.analyzer._analyze_data_flow(tree)
        
        self.assertIsInstance(data_flow, dict)
        self.assertIn('definitions', data_flow)
        self.assertIn('uses', data_flow)
        self.assertIn('dependencies', data_flow)
        
    def test_extract_entities(self):
        """Test entity extraction."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        entities = self.analyzer._extract_entities(tree, str(self.test_file))
        
        self.assertIsInstance(entities, list)
        for entity in entities:
            self.assertIsInstance(entity, CodeEntity)
            self.assertIsInstance(entity.name, str)
            self.assertIsInstance(entity.type, str)
            self.assertIsInstance(entity.file_path, str)
            
    def test_analyze_dependencies(self):
        """Test dependency analysis."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        dependencies = self.analyzer._analyze_dependencies(tree, str(self.test_file))
        
        self.assertIsInstance(dependencies, dict)
        self.assertIn(str(self.test_file), dependencies)
        
    def test_determine_scope(self):
        """Test scope determination."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        
        # Find a function definition node
        def find_function_node(node):
            if node.type == 'function_definition':
                return node
            for child in node.children:
                result = find_function_node(child)
                if result:
                    return result
            return None
            
        function_node = find_function_node(tree.root_node)
        if function_node:
            scope = self.analyzer._determine_scope(function_node)
            self.assertIn(scope, ['function', 'class', 'module'])
            
    def test_extract_dependencies(self):
        """Test dependency extraction."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        
        # Find a class definition node
        def find_class_node(node):
            if node.type == 'class_definition':
                return node
            for child in node.children:
                result = find_class_node(child)
                if result:
                    return result
            return None
            
        class_node = find_class_node(tree.root_node)
        if class_node:
            dependencies = self.analyzer._extract_dependencies(class_node)
            self.assertIsInstance(dependencies, list)
            
    def test_extract_references(self):
        """Test reference extraction."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        
        # Find a class definition node
        def find_class_node(node):
            if node.type == 'class_definition':
                return node
            for child in node.children:
                result = find_class_node(child)
                if result:
                    return result
            return None
            
        class_node = find_class_node(tree.root_node)
        if class_node:
            references = self.analyzer._extract_references(class_node)
            self.assertIsInstance(references, list)
            
    def test_extract_docstring(self):
        """Test docstring extraction."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        
        # Find a function definition node
        def find_function_node(node):
            if node.type == 'function_definition':
                return node
            for child in node.children:
                result = find_function_node(child)
                if result:
                    return result
            return None
            
        function_node = find_function_node(tree.root_node)
        if function_node:
            docstring = self.analyzer._extract_docstring(function_node)
            self.assertIsInstance(docstring, (str, type(None)))
            
    def test_extract_base_classes(self):
        """Test base class extraction."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        
        # Find a class definition node
        def find_class_node(node):
            if node.type == 'class_definition':
                return node
            for child in node.children:
                result = find_class_node(child)
                if result:
                    return result
            return None
            
        class_node = find_class_node(tree.root_node)
        if class_node:
            bases = self.analyzer._extract_base_classes(class_node)
            self.assertIsInstance(bases, list)
            
    def test_extract_parameters(self):
        """Test parameter extraction."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        
        # Find a function definition node
        def find_function_node(node):
            if node.type == 'function_definition':
                return node
            for child in node.children:
                result = find_function_node(child)
                if result:
                    return result
            return None
            
        function_node = find_function_node(tree.root_node)
        if function_node:
            parameters = self.analyzer._extract_parameters(function_node)
            self.assertIsInstance(parameters, list)
            
    def test_extract_return_type(self):
        """Test return type extraction."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        
        # Find a function definition node
        def find_function_node(node):
            if node.type == 'function_definition':
                return node
            for child in node.children:
                result = find_function_node(child)
                if result:
                    return result
            return None
            
        function_node = find_function_node(tree.root_node)
        if function_node:
            return_type = self.analyzer._extract_return_type(function_node)
            self.assertIsInstance(return_type, (str, type(None)))
            
    def test_extract_type_annotation(self):
        """Test type annotation extraction."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        
        # Find a variable declaration node
        def find_variable_node(node):
            if node.type == 'variable_declaration':
                return node
            for child in node.children:
                result = find_variable_node(child)
                if result:
                    return result
            return None
            
        variable_node = find_variable_node(tree.root_node)
        if variable_node:
            type_annotation = self.analyzer._extract_type_annotation(variable_node)
            self.assertIsInstance(type_annotation, (str, type(None)))
            
    def test_extract_condition(self):
        """Test condition extraction."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        
        # Find an if statement node
        def find_if_node(node):
            if node.type == 'if_statement':
                return node
            for child in node.children:
                result = find_if_node(child)
                if result:
                    return result
            return None
            
        if_node = find_if_node(tree.root_node)
        if if_node:
            condition = self.analyzer._extract_condition(if_node)
            self.assertIsInstance(condition, (str, type(None)))
            
    def test_extract_exception_handlers(self):
        """Test exception handler extraction."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        
        # Find a try statement node
        def find_try_node(node):
            if node.type == 'try_statement':
                return node
            for child in node.children:
                result = find_try_node(child)
                if result:
                    return result
            return None
            
        try_node = find_try_node(tree.root_node)
        if try_node:
            handlers = self.analyzer._extract_exception_handlers(try_node)
            self.assertIsInstance(handlers, list)
            
    def test_extract_exception_type(self):
        """Test exception type extraction."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        
        # Find an except clause node
        def find_except_node(node):
            if node.type == 'except_clause':
                return node
            for child in node.children:
                result = find_except_node(child)
                if result:
                    return result
            return None
            
        except_node = find_except_node(tree.root_node)
        if except_node:
            exception_type = self.analyzer._extract_exception_type(except_node)
            self.assertIsInstance(exception_type, (str, type(None)))
            
    def test_extract_return_value(self):
        """Test return value extraction."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        
        # Find a return statement node
        def find_return_node(node):
            if node.type == 'return_statement':
                return node
            for child in node.children:
                result = find_return_node(child)
                if result:
                    return result
            return None
            
        return_node = find_return_node(tree.root_node)
        if return_node:
            return_value = self.analyzer._extract_return_value(return_node)
            self.assertIsInstance(return_value, (str, type(None)))
            
    def test_extract_assignment_value(self):
        """Test assignment value extraction."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        
        # Find an assignment node
        def find_assignment_node(node):
            if node.type == 'assignment':
                return node
            for child in node.children:
                result = find_assignment_node(child)
                if result:
                    return result
            return None
            
        assignment_node = find_assignment_node(tree.root_node)
        if assignment_node:
            value = self.analyzer._extract_assignment_value(assignment_node)
            self.assertIsInstance(value, (str, type(None)))
            
    def test_extract_import_module(self):
        """Test import module extraction."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        
        # Find an import statement node
        def find_import_node(node):
            if node.type == 'import_statement':
                return node
            for child in node.children:
                result = find_import_node(child)
                if result:
                    return result
            return None
            
        import_node = find_import_node(tree.root_node)
        if import_node:
            module = self.analyzer._extract_import_module(import_node)
            self.assertIsInstance(module, str)
            
    def test_extract_call_target(self):
        """Test call target extraction."""
        with open(self.test_file, 'rb') as f:
            source_code = f.read()
        tree = self.analyzer.ast_parser.parse(source_code)
        
        # Find a call node
        def find_call_node(node):
            if node.type == 'call':
                return node
            for child in node.children:
                result = find_call_node(child)
                if result:
                    return result
            return None
            
        call_node = find_call_node(tree.root_node)
        if call_node:
            target = self.analyzer._extract_call_target(call_node)
            self.assertIsInstance(target, (str, type(None)))

if __name__ == '__main__':
    unittest.main() 