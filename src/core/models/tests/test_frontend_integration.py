"""Integration tests for frontend components."""

import unittest
from pathlib import Path
from typing import Dict, Any
from ..enhanced_code_understanding import EnhancedCodeUnderstanding, CodeEntity, LanguageConfig

class TestFrontendIntegration(unittest.TestCase):
    """Integration tests for frontend components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = EnhancedCodeUnderstanding()
        self.test_js_file = Path(__file__).parent / "test_data" / "sample.js"
        
    def test_frontend_security_analysis(self):
        """Test security analysis of frontend code."""
        analysis = self.analyzer.analyze_file(str(self.test_js_file))
        
        # Check XSS vulnerabilities
        security = analysis['security']
        self.assertIn('vulnerabilities', security)
        xss_vulns = [v for v in security['vulnerabilities'] if v['type'] == 'xss']
        self.assertGreater(len(xss_vulns), 0)
        
        # Check DOM-based XSS
        dom_xss_vulns = [v for v in security['vulnerabilities'] if v['type'] == 'dom_based_xss']
        self.assertGreater(len(dom_xss_vulns), 0)
        
        # Check eval injection
        eval_vulns = [v for v in security['vulnerabilities'] if v['type'] == 'eval_injection']
        self.assertGreater(len(eval_vulns), 0)
        
        # Check prototype pollution
        proto_vulns = [v for v in security['vulnerabilities'] if v['type'] == 'prototype_pollution']
        self.assertGreater(len(proto_vulns), 0)
        
    def test_frontend_performance_analysis(self):
        """Test performance analysis of frontend code."""
        analysis = self.analyzer.analyze_file(str(self.test_js_file))
        
        # Check memory leaks
        performance = analysis['performance']
        self.assertIn('issues', performance)
        memory_leaks = [i for i in performance['issues'] if i['type'] == 'memory_leak']
        self.assertGreater(len(memory_leaks), 0)
        
        # Check inefficient DOM operations
        dom_issues = [i for i in performance['issues'] if i['type'] == 'inefficient_dom_operation']
        self.assertGreater(len(dom_issues), 0)
        
        # Check inefficient loops
        loop_issues = [i for i in performance['issues'] if i['type'] == 'inefficient_loop']
        self.assertGreater(len(loop_issues), 0)
        
        # Check inefficient array operations
        array_issues = [i for i in performance['issues'] if i['type'] == 'inefficient_array_operation']
        self.assertGreater(len(array_issues), 0)
        
    def test_frontend_style_analysis(self):
        """Test style analysis of frontend code."""
        analysis = self.analyzer.analyze_file(str(self.test_js_file))
        
        # Check naming conventions
        style = analysis['style']
        self.assertIn('naming_conventions', style)
        naming_violations = [v for v in style['naming_conventions'] if not v['match'].startswith('_')]
        self.assertGreater(len(naming_violations), 0)
        
        # Check documentation
        self.assertIn('docstrings', style)
        self.assertGreater(len(style['docstrings']), 0)
        
        # Check type annotations
        self.assertIn('type_annotations', style)
        self.assertGreater(len(style['type_annotations']), 0)
        
    def test_frontend_complexity_analysis(self):
        """Test complexity analysis of frontend code."""
        analysis = self.analyzer.analyze_file(str(self.test_js_file))
        
        # Check nesting levels
        complexity = analysis['complexity']
        self.assertIn('nesting_levels', complexity)
        self.assertGreater(len(complexity['nesting_levels']), 0)
        
        # Check long functions
        self.assertIn('long_functions', complexity)
        self.assertGreater(len(complexity['long_functions']), 0)
        
        # Check complex conditions
        self.assertIn('complex_conditions', complexity)
        self.assertGreater(len(complexity['complex_conditions']), 0)
        
        # Check complexity score
        self.assertIn('complexity_score', complexity)
        self.assertGreater(complexity['complexity_score'], 0)
        
    def test_frontend_entity_analysis(self):
        """Test entity analysis of frontend code."""
        analysis = self.analyzer.analyze_file(str(self.test_js_file))
        
        # Check entities
        self.assertIn('entities', analysis)
        entities = analysis['entities']
        
        # Check User class
        user_class = next((e for e in entities if e.name == 'User'), None)
        self.assertIsNotNone(user_class)
        self.assertEqual(user_class.type, 'class')
        self.assertEqual(user_class.language, 'JavaScript')
        
        # Check UserManager class
        user_manager = next((e for e in entities if e.name == 'UserManager'), None)
        self.assertIsNotNone(user_manager)
        self.assertEqual(user_manager.type, 'class')
        self.assertEqual(user_manager.language, 'JavaScript')
        
        # Check methods
        methods = [e for e in entities if e.type == 'function']
        self.assertGreater(len(methods), 0)
        
    def test_frontend_dependency_analysis(self):
        """Test dependency analysis of frontend code."""
        analysis = self.analyzer.analyze_file(str(self.test_js_file))
        
        # Check dependencies
        self.assertIn('dependencies', analysis)
        dependencies = analysis['dependencies']
        
        # Check DOM dependencies
        dom_deps = [d for d in dependencies if 'document' in d]
        self.assertGreater(len(dom_deps), 0)
        
        # Check event listener dependencies
        event_deps = [d for d in dependencies if 'addEventListener' in d]
        self.assertGreater(len(event_deps), 0)
        
        # Check storage dependencies
        storage_deps = [d for d in dependencies if 'localStorage' in d or 'sessionStorage' in d]
        self.assertGreater(len(storage_deps), 0)
        
    def test_frontend_control_flow_analysis(self):
        """Test control flow analysis of frontend code."""
        analysis = self.analyzer.analyze_file(str(self.test_js_file))
        
        # Check control flow
        self.assertIn('control_flow', analysis)
        control_flow = analysis['control_flow']
        
        # Check branches
        self.assertIn('branches', control_flow)
        self.assertGreater(len(control_flow['branches']), 0)
        
        # Check loops
        self.assertIn('loops', control_flow)
        self.assertGreater(len(control_flow['loops']), 0)
        
        # Check exceptions
        self.assertIn('exceptions', control_flow)
        self.assertGreater(len(control_flow['exceptions']), 0)
        
    def test_frontend_data_flow_analysis(self):
        """Test data flow analysis of frontend code."""
        analysis = self.analyzer.analyze_file(str(self.test_js_file))
        
        # Check data flow
        self.assertIn('data_flow', analysis)
        data_flow = analysis['data_flow']
        
        # Check definitions
        self.assertIn('definitions', data_flow)
        self.assertGreater(len(data_flow['definitions']), 0)
        
        # Check uses
        self.assertIn('uses', data_flow)
        self.assertGreater(len(data_flow['uses']), 0)
        
        # Check dependencies
        self.assertIn('dependencies', data_flow)
        self.assertGreater(len(data_flow['dependencies']), 0)
        
    def test_frontend_maintainability_analysis(self):
        """Test maintainability analysis of frontend code."""
        analysis = self.analyzer.analyze_file(str(self.test_js_file))
        
        # Check maintainability
        self.assertIn('maintainability', analysis)
        maintainability = analysis['maintainability']
        
        # Check score
        self.assertIn('score', maintainability)
        self.assertGreaterEqual(maintainability['score'], 0)
        self.assertLessEqual(maintainability['score'], 1)
        
        # Check factors
        self.assertIn('factors', maintainability)
        self.assertGreater(len(maintainability['factors']), 0)
        
        # Check recommendations
        self.assertIn('recommendations', maintainability)
        self.assertGreater(len(maintainability['recommendations']), 0)
        
    def test_frontend_test_coverage_analysis(self):
        """Test test coverage analysis of frontend code."""
        analysis = self.analyzer.analyze_file(str(self.test_js_file))
        
        # Check test coverage
        self.assertIn('test_coverage', analysis)
        coverage = analysis['test_coverage']
        
        # Check overall coverage
        self.assertIn('overall_coverage', coverage)
        self.assertGreaterEqual(coverage['overall_coverage'], 0)
        self.assertLessEqual(coverage['overall_coverage'], 1)
        
        # Check function coverage
        self.assertIn('function_coverage', coverage)
        self.assertGreater(len(coverage['function_coverage']), 0)
        
        # Check class coverage
        self.assertIn('class_coverage', coverage)
        self.assertGreater(len(coverage['class_coverage']), 0)
        
        # Check missing tests
        self.assertIn('missing_tests', coverage)
        self.assertGreater(len(coverage['missing_tests']), 0)
        
    def test_frontend_documentation_analysis(self):
        """Test documentation analysis of frontend code."""
        analysis = self.analyzer.analyze_file(str(self.test_js_file))
        
        # Check documentation
        self.assertIn('documentation', analysis)
        documentation = analysis['documentation']
        
        # Check docstring coverage
        self.assertIn('docstring_coverage', documentation)
        self.assertGreaterEqual(documentation['docstring_coverage'], 0)
        self.assertLessEqual(documentation['docstring_coverage'], 1)
        
        # Check parameter documentation
        self.assertIn('parameter_documentation', documentation)
        self.assertGreaterEqual(documentation['parameter_documentation'], 0)
        self.assertLessEqual(documentation['parameter_documentation'], 1)
        
        # Check return documentation
        self.assertIn('return_documentation', documentation)
        self.assertGreaterEqual(documentation['return_documentation'], 0)
        self.assertLessEqual(documentation['return_documentation'], 1)
        
        # Check missing docs
        self.assertIn('missing_docs', documentation)
        self.assertGreater(len(documentation['missing_docs']), 0)
        
        # Check quality score
        self.assertIn('quality_score', documentation)
        self.assertGreaterEqual(documentation['quality_score'], 0)
        self.assertLessEqual(documentation['quality_score'], 1)
        
    def test_frontend_code_quality_analysis(self):
        """Test code quality analysis of frontend code."""
        analysis = self.analyzer.analyze_file(str(self.test_js_file))
        
        # Check code quality
        self.assertIn('code_quality', analysis)
        quality = analysis['code_quality']
        
        # Check score
        self.assertIn('score', quality)
        self.assertGreaterEqual(quality['score'], 0)
        self.assertLessEqual(quality['score'], 1)
        
        # Check issues
        self.assertIn('issues', quality)
        self.assertGreater(len(quality['issues']), 0)
        
        # Check recommendations
        self.assertIn('recommendations', quality)
        self.assertGreater(len(quality['recommendations']), 0)

if __name__ == '__main__':
    unittest.main() 