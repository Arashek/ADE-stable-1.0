"""
Advanced code analysis capabilities including semantic understanding,
dependency analysis, impact analysis, and quality metrics.
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import ast
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import radon.complexity as radon_complexity
import radon.metrics as radon_metrics
import radon.visitors as radon_visitors
import logging
import re
from pathlib import Path

class CodeMetricType(Enum):
    """Types of code metrics that can be collected."""
    COMPLEXITY = "complexity"
    MAINTAINABILITY = "maintainability"
    TEST_COVERAGE = "test_coverage"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    PERFORMANCE = "performance"
    CUSTOM = "custom"

@dataclass
class CodeMetric:
    """Code metric data structure."""
    name: str
    value: float
    type: CodeMetricType
    file_path: str
    line_numbers: Optional[List[int]] = None
    context: Optional[Dict[str, Any]] = None

class SemanticCodeAnalyzer:
    """Analyzer for deep semantic code understanding."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.logger = logging.getLogger(__name__)
        
    def analyze_code_semantics(self, code: str) -> Dict[str, Any]:
        """Analyze code semantics using NLP techniques."""
        # Parse code into AST
        tree = ast.parse(code)
        
        # Extract code features
        features = self._extract_code_features(tree)
        
        # Generate semantic representation
        semantic_rep = self._generate_semantic_representation(features)
        
        # Identify code patterns
        patterns = self._identify_code_patterns(tree)
        
        # Analyze code intent
        intent = self._analyze_code_intent(features)
        
        return {
            "features": features,
            "semantic_representation": semantic_rep,
            "patterns": patterns,
            "intent": intent
        }
        
    def _extract_code_features(self, tree: ast.AST) -> Dict[str, Any]:
        """Extract features from code AST."""
        features = {
            "functions": [],
            "classes": [],
            "imports": [],
            "variables": [],
            "control_structures": []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                features["functions"].append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "decorators": [decorator.id for decorator in node.decorator_list]
                })
            elif isinstance(node, ast.ClassDef):
                features["classes"].append({
                    "name": node.name,
                    "bases": [base.id for base in node.bases],
                    "methods": [method.name for method in node.body if isinstance(method, ast.FunctionDef)]
                })
            elif isinstance(node, ast.Import):
                features["imports"].extend([name.name for name in node.names])
            elif isinstance(node, ast.ImportFrom):
                features["imports"].extend([f"{node.module}.{name.name}" for name in node.names])
            elif isinstance(node, ast.Assign):
                features["variables"].extend([target.id for target in node.targets])
            elif isinstance(node, (ast.If, ast.For, ast.While)):
                features["control_structures"].append(type(node).__name__)
                
        return features
        
    def _generate_semantic_representation(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Generate semantic representation of code."""
        # Convert features to text representation
        text_rep = self._features_to_text(features)
        
        # Generate TF-IDF vectors
        vectors = self.vectorizer.fit_transform([text_rep])
        
        # Calculate semantic similarity with common patterns
        patterns = self._get_common_patterns()
        pattern_vectors = self.vectorizer.transform(patterns)
        similarities = cosine_similarity(vectors, pattern_vectors)
        
        return {
            "text_representation": text_rep,
            "vector_representation": vectors.toarray().tolist(),
            "pattern_similarities": similarities.tolist()
        }
        
    def _identify_code_patterns(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Identify common code patterns."""
        patterns = []
        
        # Design patterns
        patterns.extend(self._identify_design_patterns(tree))
        
        # Anti-patterns
        patterns.extend(self._identify_anti_patterns(tree))
        
        # Code smells
        patterns.extend(self._identify_code_smells(tree))
        
        return patterns
        
    def _analyze_code_intent(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code intent and purpose."""
        intent = {
            "primary_purpose": "",
            "secondary_purposes": [],
            "complexity_level": "",
            "maintenance_requirements": []
        }
        
        # Analyze function names and docstrings
        function_names = [f["name"] for f in features["functions"]]
        intent["primary_purpose"] = self._infer_primary_purpose(function_names)
        
        # Analyze class structure
        class_methods = [c["methods"] for c in features["classes"]]
        intent["secondary_purposes"] = self._infer_secondary_purposes(class_methods)
        
        # Analyze control structures
        control_structures = features["control_structures"]
        intent["complexity_level"] = self._assess_complexity(control_structures)
        
        # Analyze dependencies
        imports = features["imports"]
        intent["maintenance_requirements"] = self._assess_maintenance_requirements(imports)
        
        return intent

class DependencyAnalyzer:
    """Analyzer for cross-file dependencies."""
    
    def __init__(self):
        self.dependency_graph = nx.DiGraph()
        self.logger = logging.getLogger(__name__)
        
    def analyze_dependencies(self, files: List[str]) -> Dict[str, Any]:
        """Analyze dependencies between files."""
        # Build dependency graph
        self._build_dependency_graph(files)
        
        # Analyze import dependencies
        import_deps = self._analyze_import_dependencies()
        
        # Analyze function calls
        function_deps = self._analyze_function_dependencies()
        
        # Analyze class inheritance
        class_deps = self._analyze_class_dependencies()
        
        # Calculate dependency metrics
        metrics = self._calculate_dependency_metrics()
        
        return {
            "import_dependencies": import_deps,
            "function_dependencies": function_deps,
            "class_dependencies": class_deps,
            "dependency_metrics": metrics
        }
        
    def _build_dependency_graph(self, files: List[str]) -> None:
        """Build a graph of file dependencies."""
        for file_path in files:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Parse file content
            tree = ast.parse(content)
            
            # Add file node
            self.dependency_graph.add_node(file_path)
            
            # Analyze imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        self._add_import_dependency(file_path, name.name)
                elif isinstance(node, ast.ImportFrom):
                    for name in node.names:
                        self._add_import_dependency(file_path, f"{node.module}.{name.name}")
                        
    def _analyze_import_dependencies(self) -> Dict[str, List[str]]:
        """Analyze import dependencies between files."""
        import_deps = {}
        
        for file_path in self.dependency_graph.nodes():
            import_deps[file_path] = [
                dep for dep in self.dependency_graph.successors(file_path)
                if self.dependency_graph[file_path][dep]["type"] == "import"
            ]
            
        return import_deps
        
    def _analyze_function_dependencies(self) -> Dict[str, List[str]]:
        """Analyze function call dependencies between files."""
        function_deps = {}
        
        for file_path in self.dependency_graph.nodes():
            function_deps[file_path] = [
                dep for dep in self.dependency_graph.successors(file_path)
                if self.dependency_graph[file_path][dep]["type"] == "function_call"
            ]
            
        return function_deps
        
    def _analyze_class_dependencies(self) -> Dict[str, List[str]]:
        """Analyze class inheritance dependencies between files."""
        class_deps = {}
        
        for file_path in self.dependency_graph.nodes():
            class_deps[file_path] = [
                dep for dep in self.dependency_graph.successors(file_path)
                if self.dependency_graph[file_path][dep]["type"] == "class_inheritance"
            ]
            
        return class_deps
        
    def _calculate_dependency_metrics(self) -> Dict[str, float]:
        """Calculate dependency-related metrics."""
        metrics = {
            "average_dependencies": 0.0,
            "max_dependencies": 0,
            "circular_dependencies": 0,
            "dependency_depth": 0
        }
        
        # Calculate average dependencies per file
        deps_per_file = [len(list(self.dependency_graph.successors(node))) 
                        for node in self.dependency_graph.nodes()]
        metrics["average_dependencies"] = sum(deps_per_file) / len(deps_per_file)
        
        # Calculate maximum dependencies
        metrics["max_dependencies"] = max(deps_per_file)
        
        # Count circular dependencies
        metrics["circular_dependencies"] = len(list(nx.simple_cycles(self.dependency_graph)))
        
        # Calculate maximum dependency depth
        metrics["dependency_depth"] = self._calculate_max_depth()
        
        return metrics

class ImpactAnalyzer:
    """Analyzer for real-time code impact analysis."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze_impact(self, changes: List[Dict[str, Any]], 
                      codebase: Dict[str, str]) -> Dict[str, Any]:
        """Analyze the impact of code changes."""
        # Analyze direct impact
        direct_impact = self._analyze_direct_impact(changes, codebase)
        
        # Analyze indirect impact
        indirect_impact = self._analyze_indirect_impact(changes, codebase)
        
        # Analyze test impact
        test_impact = self._analyze_test_impact(changes, codebase)
        
        # Calculate risk assessment
        risk_assessment = self._assess_risk(direct_impact, indirect_impact, test_impact)
        
        return {
            "direct_impact": direct_impact,
            "indirect_impact": indirect_impact,
            "test_impact": test_impact,
            "risk_assessment": risk_assessment
        }
        
    def _analyze_direct_impact(self, changes: List[Dict[str, Any]], 
                             codebase: Dict[str, str]) -> Dict[str, Any]:
        """Analyze direct impact of code changes."""
        direct_impact = {
            "modified_files": [],
            "affected_functions": [],
            "affected_classes": [],
            "breaking_changes": []
        }
        
        for change in changes:
            file_path = change["file_path"]
            content = codebase.get(file_path, "")
            
            # Parse file content
            tree = ast.parse(content)
            
            # Analyze modified code
            modified_code = self._get_modified_code(change, content)
            modified_tree = ast.parse(modified_code)
            
            # Compare ASTs to identify changes
            changes = self._compare_asts(tree, modified_tree)
            
            # Update impact information
            direct_impact["modified_files"].append(file_path)
            direct_impact["affected_functions"].extend(changes["modified_functions"])
            direct_impact["affected_classes"].extend(changes["modified_classes"])
            direct_impact["breaking_changes"].extend(changes["breaking_changes"])
            
        return direct_impact
        
    def _analyze_indirect_impact(self, changes: List[Dict[str, Any]], 
                               codebase: Dict[str, str]) -> Dict[str, Any]:
        """Analyze indirect impact of code changes."""
        indirect_impact = {
            "dependent_files": [],
            "affected_tests": [],
            "performance_impact": [],
            "security_impact": []
        }
        
        # Build dependency graph
        dependency_graph = self._build_dependency_graph(codebase)
        
        # Find dependent files
        for change in changes:
            file_path = change["file_path"]
            dependent_files = self._find_dependent_files(file_path, dependency_graph)
            indirect_impact["dependent_files"].extend(dependent_files)
            
        # Analyze test impact
        test_files = self._find_test_files(codebase)
        for test_file in test_files:
            if self._is_test_affected(test_file, changes, codebase):
                indirect_impact["affected_tests"].append(test_file)
                
        # Analyze performance impact
        performance_impact = self._analyze_performance_impact(changes, codebase)
        indirect_impact["performance_impact"] = performance_impact
        
        # Analyze security impact
        security_impact = self._analyze_security_impact(changes, codebase)
        indirect_impact["security_impact"] = security_impact
        
        return indirect_impact
        
    def _analyze_test_impact(self, changes: List[Dict[str, Any]], 
                           codebase: Dict[str, str]) -> Dict[str, Any]:
        """Analyze impact on test coverage and quality."""
        test_impact = {
            "affected_tests": [],
            "coverage_changes": {},
            "test_quality_impact": {},
            "regression_risk": {}
        }
        
        # Find affected tests
        test_files = self._find_test_files(codebase)
        for test_file in test_files:
            if self._is_test_affected(test_file, changes, codebase):
                test_impact["affected_tests"].append(test_file)
                
                # Analyze test coverage changes
                coverage_changes = self._analyze_test_coverage(test_file, changes, codebase)
                test_impact["coverage_changes"][test_file] = coverage_changes
                
                # Analyze test quality impact
                quality_impact = self._analyze_test_quality(test_file, changes, codebase)
                test_impact["test_quality_impact"][test_file] = quality_impact
                
                # Assess regression risk
                regression_risk = self._assess_regression_risk(test_file, changes, codebase)
                test_impact["regression_risk"][test_file] = regression_risk
                
        return test_impact
        
    def _assess_risk(self, direct_impact: Dict[str, Any], 
                    indirect_impact: Dict[str, Any], 
                    test_impact: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall risk of changes."""
        risk_assessment = {
            "risk_level": "",
            "risk_factors": [],
            "mitigation_suggestions": [],
            "confidence_score": 0.0
        }
        
        # Calculate risk level
        risk_factors = []
        
        # Breaking changes
        if direct_impact["breaking_changes"]:
            risk_factors.append({
                "factor": "breaking_changes",
                "severity": "high",
                "description": f"Found {len(direct_impact['breaking_changes'])} breaking changes"
            })
            
        # Dependent files
        if indirect_impact["dependent_files"]:
            risk_factors.append({
                "factor": "dependent_files",
                "severity": "medium",
                "description": f"Affects {len(indirect_impact['dependent_files'])} dependent files"
            })
            
        # Test coverage
        for test_file, coverage in test_impact["coverage_changes"].items():
            if coverage["decrease"] > 0.1:  # More than 10% decrease
                risk_factors.append({
                    "factor": "test_coverage",
                    "severity": "high",
                    "description": f"Test coverage decreased by {coverage['decrease']*100}% in {test_file}"
                })
                
        # Determine overall risk level
        if any(f["severity"] == "high" for f in risk_factors):
            risk_assessment["risk_level"] = "high"
        elif any(f["severity"] == "medium" for f in risk_factors):
            risk_assessment["risk_level"] = "medium"
        else:
            risk_assessment["risk_level"] = "low"
            
        risk_assessment["risk_factors"] = risk_factors
        
        # Generate mitigation suggestions
        risk_assessment["mitigation_suggestions"] = self._generate_mitigation_suggestions(risk_factors)
        
        # Calculate confidence score
        risk_assessment["confidence_score"] = self._calculate_confidence_score(
            direct_impact, indirect_impact, test_impact
        )
        
        return risk_assessment

class CodeQualityAnalyzer:
    """Analyzer for code quality metrics."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze_quality(self, code: str, file_path: str) -> Dict[str, Any]:
        """Analyze code quality metrics."""
        # Calculate complexity metrics
        complexity_metrics = self._calculate_complexity_metrics(code)
        
        # Calculate maintainability metrics
        maintainability_metrics = self._calculate_maintainability_metrics(code)
        
        # Calculate documentation metrics
        documentation_metrics = self._calculate_documentation_metrics(code)
        
        # Calculate security metrics
        security_metrics = self._calculate_security_metrics(code)
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(code)
        
        # Generate quality score
        quality_score = self._generate_quality_score(
            complexity_metrics,
            maintainability_metrics,
            documentation_metrics,
            security_metrics,
            performance_metrics
        )
        
        return {
            "complexity_metrics": complexity_metrics,
            "maintainability_metrics": maintainability_metrics,
            "documentation_metrics": documentation_metrics,
            "security_metrics": security_metrics,
            "performance_metrics": performance_metrics,
            "quality_score": quality_score
        }
        
    def _calculate_complexity_metrics(self, code: str) -> Dict[str, float]:
        """Calculate code complexity metrics."""
        metrics = {
            "cyclomatic_complexity": 0.0,
            "cognitive_complexity": 0.0,
            "halstead_complexity": 0.0,
            "maintainability_index": 0.0
        }
        
        # Calculate cyclomatic complexity
        metrics["cyclomatic_complexity"] = radon_complexity.cc_visit(code)
        
        # Calculate cognitive complexity
        metrics["cognitive_complexity"] = self._calculate_cognitive_complexity(code)
        
        # Calculate Halstead complexity
        metrics["halstead_complexity"] = radon_metrics.h_visit(code)
        
        # Calculate maintainability index
        metrics["maintainability_index"] = radon_metrics.mi_visit(code)
        
        return metrics
        
    def _calculate_maintainability_metrics(self, code: str) -> Dict[str, float]:
        """Calculate code maintainability metrics."""
        metrics = {
            "lines_of_code": 0,
            "comment_ratio": 0.0,
            "function_length": 0.0,
            "class_length": 0.0,
            "nesting_depth": 0.0
        }
        
        # Parse code into AST
        tree = ast.parse(code)
        
        # Calculate lines of code
        metrics["lines_of_code"] = len(code.splitlines())
        
        # Calculate comment ratio
        metrics["comment_ratio"] = self._calculate_comment_ratio(code)
        
        # Calculate function and class lengths
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                metrics["function_length"] = max(
                    metrics["function_length"],
                    node.end_lineno - node.lineno + 1
                )
            elif isinstance(node, ast.ClassDef):
                metrics["class_length"] = max(
                    metrics["class_length"],
                    node.end_lineno - node.lineno + 1
                )
                
        # Calculate nesting depth
        metrics["nesting_depth"] = self._calculate_nesting_depth(tree)
        
        return metrics
        
    def _calculate_documentation_metrics(self, code: str) -> Dict[str, float]:
        """Calculate code documentation metrics."""
        metrics = {
            "docstring_coverage": 0.0,
            "comment_coverage": 0.0,
            "documentation_quality": 0.0
        }
        
        # Parse code into AST
        tree = ast.parse(code)
        
        # Calculate docstring coverage
        total_items = 0
        documented_items = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                total_items += 1
                if ast.get_docstring(node):
                    documented_items += 1
                    
        metrics["docstring_coverage"] = documented_items / total_items if total_items > 0 else 0
        
        # Calculate comment coverage
        lines = code.splitlines()
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        metrics["comment_coverage"] = comment_lines / len(lines) if lines else 0
        
        # Calculate documentation quality
        metrics["documentation_quality"] = self._assess_documentation_quality(code)
        
        return metrics
        
    def _calculate_security_metrics(self, code: str) -> Dict[str, float]:
        """Calculate code security metrics."""
        metrics = {
            "security_score": 0.0,
            "vulnerability_count": 0,
            "secure_coding_practices": 0.0
        }
        
        # Analyze security patterns
        security_patterns = self._analyze_security_patterns(code)
        
        # Count vulnerabilities
        metrics["vulnerability_count"] = len(security_patterns["vulnerabilities"])
        
        # Calculate security score
        metrics["security_score"] = self._calculate_security_score(security_patterns)
        
        # Assess secure coding practices
        metrics["secure_coding_practices"] = self._assess_secure_coding_practices(code)
        
        return metrics
        
    def _calculate_performance_metrics(self, code: str) -> Dict[str, float]:
        """Calculate code performance metrics."""
        metrics = {
            "performance_score": 0.0,
            "algorithmic_complexity": 0.0,
            "resource_usage": 0.0
        }
        
        # Analyze performance patterns
        performance_patterns = self._analyze_performance_patterns(code)
        
        # Calculate algorithmic complexity
        metrics["algorithmic_complexity"] = self._calculate_algorithmic_complexity(code)
        
        # Assess resource usage
        metrics["resource_usage"] = self._assess_resource_usage(code)
        
        # Calculate overall performance score
        metrics["performance_score"] = self._calculate_performance_score(performance_patterns)
        
        return metrics
        
    def _generate_quality_score(self, complexity_metrics: Dict[str, float],
                              maintainability_metrics: Dict[str, float],
                              documentation_metrics: Dict[str, float],
                              security_metrics: Dict[str, float],
                              performance_metrics: Dict[str, float]) -> float:
        """Generate overall code quality score."""
        # Weight different metric categories
        weights = {
            "complexity": 0.2,
            "maintainability": 0.3,
            "documentation": 0.2,
            "security": 0.15,
            "performance": 0.15
        }
        
        # Calculate weighted scores
        complexity_score = self._normalize_complexity_score(complexity_metrics)
        maintainability_score = self._normalize_maintainability_score(maintainability_metrics)
        documentation_score = self._normalize_documentation_score(documentation_metrics)
        security_score = security_metrics["security_score"]
        performance_score = performance_metrics["performance_score"]
        
        # Calculate weighted average
        quality_score = (
            weights["complexity"] * complexity_score +
            weights["maintainability"] * maintainability_score +
            weights["documentation"] * documentation_score +
            weights["security"] * security_score +
            weights["performance"] * performance_score
        )
        
        return quality_score 