import ast
import random
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path
import json
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
import numpy as np
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze
from radon.visitors import ComplexityVisitor

@dataclass
class CodeQualityMetrics:
    """Metrics for code quality assessment."""
    cyclomatic_complexity: float
    maintainability_index: float
    lines_of_code: int
    comment_ratio: float
    function_count: int
    avg_function_length: float
    variable_count: int
    nesting_depth: int
    duplication_ratio: float
    naming_score: float

@dataclass
class RefactoringExample:
    """A single refactoring example with before/after code and explanations."""
    original_code: str
    refactored_code: str
    quality_before: CodeQualityMetrics
    quality_after: CodeQualityMetrics
    refactoring_steps: List[str]
    code_smells: List[str]
    benefits: List[str]
    difficulty: float
    category: str

class RefactoringTrainer:
    """Generates and evaluates code refactoring examples."""
    
    def __init__(self, output_dir: str = "data/refactoring"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Common code smells and their solutions
        self.code_smells = {
            "long_method": {
                "description": "Method is too long and does too many things",
                "solutions": [
                    "Extract method",
                    "Split into smaller methods",
                    "Use composition"
                ]
            },
            "complex_condition": {
                "description": "Complex conditional logic is hard to understand",
                "solutions": [
                    "Extract condition to method",
                    "Use guard clauses",
                    "Simplify boolean expressions"
                ]
            },
            "duplicate_code": {
                "description": "Same code appears in multiple places",
                "solutions": [
                    "Extract common code to method",
                    "Use inheritance",
                    "Create utility functions"
                ]
            },
            "large_class": {
                "description": "Class has too many responsibilities",
                "solutions": [
                    "Extract class",
                    "Use composition",
                    "Split into smaller classes"
                ]
            },
            "primitive_obsession": {
                "description": "Using primitive types instead of objects",
                "solutions": [
                    "Create value objects",
                    "Use enums",
                    "Encapsulate related data"
                ]
            },
            "switch_statement": {
                "description": "Complex switch/case statements",
                "solutions": [
                    "Use polymorphism",
                    "Create strategy pattern",
                    "Use dictionary mapping"
                ]
            },
            "data_clumps": {
                "description": "Groups of variables that always appear together",
                "solutions": [
                    "Create data class",
                    "Use record types",
                    "Encapsulate related data"
                ]
            },
            "feature_envy": {
                "description": "Method uses more data from another class than its own",
                "solutions": [
                    "Move method",
                    "Extract class",
                    "Use composition"
                ]
            },
            "shotgun_surgery": {
                "description": "Making changes in many places for a single feature",
                "solutions": [
                    "Move method",
                    "Inline class",
                    "Extract class"
                ]
            },
            "parallel_inheritance": {
                "description": "Two class hierarchies that grow together",
                "solutions": [
                    "Merge hierarchies",
                    "Extract superclass",
                    "Use composition"
                ]
            },
            "lazy_class": {
                "description": "Class that doesn't do enough to justify its existence",
                "solutions": [
                    "Inline class",
                    "Collapse hierarchy",
                    "Remove class"
                ]
            },
            "speculative_generality": {
                "description": "Code that's more general than needed",
                "solutions": [
                    "Collapse hierarchy",
                    "Remove parameter",
                    "Inline class"
                ]
            },
            "temporary_field": {
                "description": "Instance variable set only in certain cases",
                "solutions": [
                    "Extract class",
                    "Introduce null object",
                    "Remove field"
                ]
            },
            "message_chains": {
                "description": "Long chain of method calls",
                "solutions": [
                    "Hide delegate",
                    "Extract method",
                    "Introduce middle man"
                ]
            },
            "middle_man": {
                "description": "Class that only delegates to other classes",
                "solutions": [
                    "Remove middle man",
                    "Inline method",
                    "Replace delegation with inheritance"
                ]
            },
            "insider_trading": {
                "description": "Methods that take advantage of internal data structures",
                "solutions": [
                    "Move method",
                    "Extract method",
                    "Hide delegate"
                ]
            },
            "incomplete_library_class": {
                "description": "Library class that doesn't provide all needed functionality",
                "solutions": [
                    "Introduce foreign method",
                    "Introduce local extension",
                    "Extract class"
                ]
            }
        }
        
        # Refactoring patterns and their implementations
        self.refactoring_patterns = {
            "extract_method": self._extract_method,
            "extract_class": self._extract_class,
            "simplify_condition": self._simplify_condition,
            "remove_duplication": self._remove_duplication,
            "improve_naming": self._improve_naming,
            "use_composition": self._use_composition,
            "create_value_object": self._create_value_object,
            "use_polymorphism": self._use_polymorphism,
            "introduce_null_object": self._introduce_null_object,
            "replace_conditional_with_polymorphism": self._replace_conditional_with_polymorphism,
            "introduce_parameter_object": self._introduce_parameter_object,
            "remove_parameter": self._remove_parameter,
            "preserve_whole_object": self._preserve_whole_object,
            "replace_constructor_with_factory_method": self._replace_constructor_with_factory_method,
            "encapsulate_collection": self._encapsulate_collection,
            "replace_inheritance_with_delegation": self._replace_inheritance_with_delegation,
            "replace_delegation_with_inheritance": self._replace_delegation_with_inheritance,
            "introduce_assertion": self._introduce_assertion,
            "introduce_explaining_variable": self._introduce_explaining_variable,
            "split_temporary_variable": self._split_temporary_variable,
            "remove_assignments_to_parameters": self._remove_assignments_to_parameters,
            "replace_method_with_method_object": self._replace_method_with_method_object,
            "substitute_algorithm": self._substitute_algorithm,
            "move_method": self._move_method,
            "move_field": self._move_field,
            "extract_subclass": self._extract_subclass,
            "extract_superclass": self._extract_superclass,
            "extract_interface": self._extract_interface,
            "collapse_hierarchy": self._collapse_hierarchy,
            "form_template_method": self._form_template_method,
            "hide_delegate": self._hide_delegate,
            "remove_middle_man": self._remove_middle_man,
            "introduce_foreign_method": self._introduce_foreign_method,
            "introduce_local_extension": self._introduce_local_extension,
            "inline_class": self._inline_class,
            "inline_method": self._inline_method,
            "inline_temp": self._inline_temp,
            "extract_constant": self._extract_constant,
            "extract_variable": self._extract_variable,
            "replace_parameter_with_method_call": self._replace_parameter_with_method_call,
            "replace_parameter_with_explicit_methods": self._replace_parameter_with_explicit_methods,
            "rename_method": self._rename_method,
            "add_parameter": self._add_parameter,
            "separate_query_from_modifier": self._separate_query_from_modifier,
            "parameterize_method": self._parameterize_method
        }
    
    def generate_dataset(self, num_examples: int = 100) -> List[RefactoringExample]:
        """Generate a dataset of refactoring examples."""
        examples = []
        
        for _ in range(num_examples):
            # Generate a code example with intentional code smells
            original_code = self._generate_code_with_smells()
            
            # Analyze code quality before refactoring
            quality_before = self._analyze_code_quality(original_code)
            
            # Select code smells to address
            smells = self._identify_code_smells(original_code)
            
            # Apply refactoring patterns
            refactored_code, steps = self._apply_refactoring(original_code, smells)
            
            # Analyze code quality after refactoring
            quality_after = self._analyze_code_quality(refactored_code)
            
            # Generate benefits explanation
            benefits = self._generate_benefits(quality_before, quality_after)
            
            # Calculate difficulty
            difficulty = self._calculate_difficulty(original_code, refactored_code)
            
            # Create example
            example = RefactoringExample(
                original_code=original_code,
                refactored_code=refactored_code,
                quality_before=quality_before,
                quality_after=quality_after,
                refactoring_steps=steps,
                code_smells=smells,
                benefits=benefits,
                difficulty=difficulty,
                category=self._categorize_refactoring(smells)
            )
            
            examples.append(example)
        
        return examples
    
    def evaluate_refactoring(self, 
                           original_code: str, 
                           refactored_code: str) -> Dict[str, float]:
        """Evaluate the quality of a refactoring."""
        # Analyze code quality
        quality_before = self._analyze_code_quality(original_code)
        quality_after = self._analyze_code_quality(refactored_code)
        
        # Calculate improvement metrics
        improvement_metrics = self._calculate_improvement_metrics(
            quality_before, quality_after)
        
        # Check correctness
        correctness_metrics = self._check_correctness(original_code, refactored_code)
        
        # Evaluate refactoring relevance
        relevance_metrics = self._evaluate_relevance(
            original_code, refactored_code, quality_before, quality_after)
        
        return {
            "improvement": improvement_metrics,
            "correctness": correctness_metrics,
            "relevance": relevance_metrics
        }
    
    def _generate_code_with_smells(self) -> str:
        """Generate code examples with intentional code smells."""
        # Template for a class with multiple code smells
        template = """
class UserManager:
    def process_user_data(self, user_data):
        # Long method with complex logic
        if user_data.get('status') == 'active' and user_data.get('age') > 18 and user_data.get('country') in ['US', 'UK', 'CA']:
            if user_data.get('subscription') == 'premium' and user_data.get('payment_status') == 'paid':
                if user_data.get('last_login') > '2023-01-01' and user_data.get('login_count') > 5:
                    # Process user data
                    user_id = user_data.get('id')
                    user_name = user_data.get('name')
                    user_email = user_data.get('email')
                    user_phone = user_data.get('phone')
                    user_address = user_data.get('address')
                    
                    # Update user status
                    self.update_user_status(user_id, 'verified')
                    
                    # Send welcome email
                    self.send_welcome_email(user_email, user_name)
                    
                    # Create user profile
                    self.create_user_profile(user_id, user_name, user_email, user_phone, user_address)
                    
                    # Initialize user settings
                    self.initialize_user_settings(user_id)
                    
                    return True
        return False
    
    def update_user_status(self, user_id, status):
        # Duplicate code for status update
        if user_id and status:
            if status in ['active', 'inactive', 'suspended']:
                if self.validate_user_id(user_id):
                    self.db.update('users', {'status': status}, {'id': user_id})
                    return True
        return False
    
    def send_welcome_email(self, email, name):
        # Another duplicate code block
        if email and name:
            if self.validate_email(email):
                if self.validate_name(name):
                    self.email_service.send('welcome', email, {'name': name})
                    return True
        return False
    
    def create_user_profile(self, user_id, name, email, phone, address):
        # More duplicate code
        if user_id and name and email:
            if self.validate_user_id(user_id):
                if self.validate_email(email):
                    if self.validate_name(name):
                        self.db.insert('profiles', {
                            'user_id': user_id,
                            'name': name,
                            'email': email,
                            'phone': phone,
                            'address': address
                        })
                        return True
        return False
    
    def initialize_user_settings(self, user_id):
        # Yet more duplicate code
        if user_id:
            if self.validate_user_id(user_id):
                self.db.insert('settings', {
                    'user_id': user_id,
                    'theme': 'default',
                    'notifications': True,
                    'language': 'en'
                })
                return True
        return False
    
    def validate_user_id(self, user_id):
        return isinstance(user_id, int) and user_id > 0
    
    def validate_email(self, email):
        return isinstance(email, str) and '@' in email
    
    def validate_name(self, name):
        return isinstance(name, str) and len(name) > 0
"""
        return template
    
    def _analyze_code_quality(self, code: str) -> CodeQualityMetrics:
        """Analyze code quality metrics."""
        # Parse code into AST
        tree = ast.parse(code)
        
        # Calculate cyclomatic complexity
        complexity_results = cc_visit(code)
        avg_complexity = np.mean([item.complexity for item in complexity_results]) if complexity_results else 0
        
        # Calculate maintainability index
        maintainability = mi_visit(code, multi=True)
        
        # Calculate lines of code and comment ratio
        raw_metrics = analyze(code)
        loc = raw_metrics.loc
        comment_ratio = raw_metrics.comments / loc if loc > 0 else 0
        
        # Count functions and calculate average length
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        function_count = len(functions)
        avg_function_length = np.mean([len(node.body) for node in functions]) if functions else 0
        
        # Count variables
        variables = [node for node in ast.walk(tree) if isinstance(node, ast.Name)]
        variable_count = len(set(node.id for node in variables))
        
        # Calculate nesting depth
        nesting_depth = self._calculate_nesting_depth(tree)
        
        # Calculate code duplication ratio
        duplication_ratio = self._calculate_duplication_ratio(code)
        
        # Calculate naming score
        naming_score = self._calculate_naming_score(tree)
        
        return CodeQualityMetrics(
            cyclomatic_complexity=avg_complexity,
            maintainability_index=maintainability,
            lines_of_code=loc,
            comment_ratio=comment_ratio,
            function_count=function_count,
            avg_function_length=avg_function_length,
            variable_count=variable_count,
            nesting_depth=nesting_depth,
            duplication_ratio=duplication_ratio,
            naming_score=naming_score
        )
    
    def _identify_code_smells(self, code: str) -> List[str]:
        """Identify code smells in the code."""
        smells = []
        
        # Parse code into AST
        tree = ast.parse(code)
        
        # Check for long methods
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.body) > 10:  # Arbitrary threshold
                    smells.append("long_method")
        
        # Check for complex conditions
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                if len(ast.walk(node.test)) > 5:  # Arbitrary threshold
                    smells.append("complex_condition")
        
        # Check for duplicate code
        if self._calculate_duplication_ratio(code) > 0.3:  # Arbitrary threshold
            smells.append("duplicate_code")
        
        # Check for large class
        class_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        if class_nodes and len(class_nodes[0].body) > 10:  # Arbitrary threshold
            smells.append("large_class")
        
        # Check for primitive obsession
        if self._has_primitive_obsession(tree):
            smells.append("primitive_obsession")
        
        # Check for switch statements
        if self._has_switch_statement(tree):
            smells.append("switch_statement")
        
        # Check for data clumps
        if self._has_data_clumps(tree):
            smells.append("data_clumps")
        
        # Check for feature envy
        if self._has_feature_envy(tree):
            smells.append("feature_envy")
        
        return list(set(smells))  # Remove duplicates
    
    def _apply_refactoring(self, code: str, smells: List[str]) -> Tuple[str, List[str]]:
        """Apply appropriate refactoring patterns to address code smells."""
        steps = []
        refactored_code = code
        
        for smell in smells:
            if smell in self.refactoring_patterns:
                # Apply the refactoring pattern
                refactored_code, new_steps = self.refactoring_patterns[smell](refactored_code)
                steps.extend(new_steps)
        
        return refactored_code, steps
    
    def _generate_benefits(self, 
                          quality_before: CodeQualityMetrics, 
                          quality_after: CodeQualityMetrics) -> List[str]:
        """Generate explanations of refactoring benefits."""
        benefits = []
        
        # Compare metrics and generate benefits
        if quality_after.cyclomatic_complexity < quality_before.cyclomatic_complexity:
            benefits.append("Reduced code complexity, making it easier to understand and maintain")
        
        if quality_after.maintainability_index > quality_before.maintainability_index:
            benefits.append("Improved maintainability, making future changes easier")
        
        if quality_after.duplication_ratio < quality_before.duplication_ratio:
            benefits.append("Reduced code duplication, improving consistency and reducing maintenance effort")
        
        if quality_after.naming_score > quality_before.naming_score:
            benefits.append("Improved code readability through better naming conventions")
        
        if quality_after.nesting_depth < quality_before.nesting_depth:
            benefits.append("Reduced nesting depth, making the code flow clearer")
        
        return benefits
    
    def _calculate_difficulty(self, original_code: str, refactored_code: str) -> float:
        """Calculate the difficulty of the refactoring."""
        # Parse both code versions
        original_tree = ast.parse(original_code)
        refactored_tree = ast.parse(refactored_code)
        
        # Calculate various difficulty factors
        complexity_factor = self._calculate_complexity_factor(original_tree, refactored_tree)
        size_factor = self._calculate_size_factor(original_code, refactored_code)
        change_factor = self._calculate_change_factor(original_code, refactored_code)
        
        # Combine factors with weights
        difficulty = (
            0.4 * complexity_factor +
            0.3 * size_factor +
            0.3 * change_factor
        )
        
        return min(max(difficulty, 0.0), 1.0)  # Normalize to [0, 1]
    
    def _calculate_improvement_metrics(self, 
                                    quality_before: CodeQualityMetrics, 
                                    quality_after: CodeQualityMetrics) -> float:
        """Calculate improvement in code quality after refactoring."""
        # Calculate relative improvements for each metric
        improvements = [
            (quality_before.cyclomatic_complexity - quality_after.cyclomatic_complexity) / 
            max(quality_before.cyclomatic_complexity, 1),
            (quality_after.maintainability_index - quality_before.maintainability_index) / 
            max(quality_before.maintainability_index, 1),
            (quality_before.duplication_ratio - quality_after.duplication_ratio),
            (quality_after.naming_score - quality_before.naming_score),
            (quality_before.nesting_depth - quality_after.nesting_depth) / 
            max(quality_before.nesting_depth, 1)
        ]
        
        # Calculate weighted average improvement
        weights = [0.3, 0.2, 0.2, 0.15, 0.15]
        return sum(imp * weight for imp, weight in zip(improvements, weights))
    
    def _check_correctness(self, original_code: str, refactored_code: str) -> float:
        """Check if the refactored code maintains the original functionality."""
        try:
            # Parse both code versions
            original_tree = ast.parse(original_code)
            refactored_tree = ast.parse(refactored_code)
            
            # Compare function signatures
            original_funcs = self._get_function_signatures(original_tree)
            refactored_funcs = self._get_function_signatures(refactored_tree)
            
            # Compare class structures
            original_classes = self._get_class_structures(original_tree)
            refactored_classes = self._get_class_structures(refactored_tree)
            
            # Calculate similarity scores
            func_similarity = self._calculate_signature_similarity(original_funcs, refactored_funcs)
            class_similarity = self._calculate_structure_similarity(original_classes, refactored_classes)
            
            # Combine scores with weights
            return 0.6 * func_similarity + 0.4 * class_similarity
            
        except:
            return 0.0
    
    def _evaluate_relevance(self, 
                          original_code: str, 
                          refactored_code: str,
                          quality_before: CodeQualityMetrics,
                          quality_after: CodeQualityMetrics) -> float:
        """Evaluate the relevance of the refactoring suggestions."""
        # Calculate improvement ratio
        improvement_ratio = self._calculate_improvement_metrics(quality_before, quality_after)
        
        # Calculate code similarity
        code_similarity = SequenceMatcher(None, original_code, refactored_code).ratio()
        
        # Calculate effort ratio (how much code changed)
        effort_ratio = 1 - code_similarity
        
        # Combine metrics with weights
        return 0.5 * improvement_ratio + 0.3 * code_similarity + 0.2 * effort_ratio
    
    def _calculate_nesting_depth(self, tree: ast.AST) -> int:
        """Calculate the maximum nesting depth of the AST."""
        def visit(node: ast.AST, depth: int) -> int:
            if isinstance(node, (ast.If, ast.For, ast.While, ast.FunctionDef)):
                return max(depth + 1, max((visit(child, depth + 1) 
                                         for child in ast.iter_child_nodes(node)), 
                                        default=depth + 1))
            return max((visit(child, depth) 
                       for child in ast.iter_child_nodes(node)), 
                      default=depth)
        
        return visit(tree, 0)
    
    def _calculate_duplication_ratio(self, code: str) -> float:
        """Calculate the ratio of duplicated code."""
        # Split code into functions
        functions = []
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(ast.unparse(node))
        
        if not functions:
            return 0.0
        
        # Calculate similarity between functions
        similarities = []
        for i in range(len(functions)):
            for j in range(i + 1, len(functions)):
                similarity = SequenceMatcher(None, functions[i], functions[j]).ratio()
                if similarity > 0.7:  # Arbitrary threshold
                    similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.0
    
    def _calculate_naming_score(self, tree: ast.AST) -> float:
        """Calculate a score for variable and function naming."""
        naming_rules = {
            'function': lambda name: name.islower() and '_' in name,
            'class': lambda name: name[0].isupper() and name[1:].islower(),
            'variable': lambda name: name.islower() and '_' in name,
            'constant': lambda name: name.isupper() and '_' in name
        }
        
        scores = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                scores.append(1.0 if naming_rules['function'](node.name) else 0.0)
            elif isinstance(node, ast.ClassDef):
                scores.append(1.0 if naming_rules['class'](node.name) else 0.0)
            elif isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):  # Assignment
                    scores.append(1.0 if naming_rules['variable'](node.id) else 0.0)
                elif node.id.isupper():
                    scores.append(1.0 if naming_rules['constant'](node.id) else 0.0)
        
        return np.mean(scores) if scores else 1.0
    
    def _has_primitive_obsession(self, tree: ast.AST) -> bool:
        """Check for primitive obsession code smell."""
        # Look for groups of primitive variables that could be objects
        primitive_groups = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                primitive_vars = []
                for child in ast.walk(node):
                    if isinstance(child, ast.Name):
                        primitive_vars.append(child.id)
                if len(primitive_vars) > 3:  # Arbitrary threshold
                    primitive_groups.append(primitive_vars)
        
        return len(primitive_groups) > 0
    
    def _has_switch_statement(self, tree: ast.AST) -> bool:
        """Check for switch statement code smell."""
        # Look for long if-elif chains
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                if_chain = []
                current = node
                while isinstance(current, ast.If):
                    if_chain.append(current)
                    if current.orelse:
                        current = current.orelse[0]
                    else:
                        break
                if len(if_chain) > 3:  # Arbitrary threshold
                    return True
        return False
    
    def _has_data_clumps(self, tree: ast.AST) -> bool:
        """Check for data clumps code smell."""
        # Look for groups of variables that appear together
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                var_groups = []
                for child in ast.walk(node):
                    if isinstance(child, ast.Name):
                        var_groups.append(child.id)
                if len(var_groups) > 4:  # Arbitrary threshold
                    return True
        return False
    
    def _has_feature_envy(self, tree: ast.AST) -> bool:
        """Check for feature envy code smell."""
        # Look for methods that use more data from another class than their own
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self_vars = set()
                other_vars = set()
                for child in ast.walk(node):
                    if isinstance(child, ast.Name):
                        if isinstance(child.ctx, ast.Load):
                            if child.id.startswith('self.'):
                                self_vars.add(child.id)
                            else:
                                other_vars.add(child.id)
                if len(other_vars) > len(self_vars):  # Arbitrary threshold
                    return True
        return False
    
    def _calculate_complexity_factor(self, original_tree: ast.AST, refactored_tree: ast.AST) -> float:
        """Calculate complexity factor for difficulty estimation."""
        original_complexity = self._calculate_nesting_depth(original_tree)
        refactored_complexity = self._calculate_nesting_depth(refactored_tree)
        return 1.0 - (refactored_complexity / max(original_complexity, 1))
    
    def _calculate_size_factor(self, original_code: str, refactored_code: str) -> float:
        """Calculate size factor for difficulty estimation."""
        original_lines = len(original_code.split('\n'))
        refactored_lines = len(refactored_code.split('\n'))
        return 1.0 - (refactored_lines / max(original_lines, 1))
    
    def _calculate_change_factor(self, original_code: str, refactored_code: str) -> float:
        """Calculate change factor for difficulty estimation."""
        return 1.0 - SequenceMatcher(None, original_code, refactored_code).ratio()
    
    def _get_function_signatures(self, tree: ast.AST) -> List[str]:
        """Get function signatures from AST."""
        signatures = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                signature = f"{node.name}({', '.join(arg.arg for arg in node.args.args)})"
                signatures.append(signature)
        return signatures
    
    def _get_class_structures(self, tree: ast.AST) -> List[str]:
        """Get class structures from AST."""
        structures = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                structure = f"{node.name}:{','.join(base.id for base in node.bases)}"
                structures.append(structure)
        return structures
    
    def _calculate_signature_similarity(self, 
                                     original_sigs: List[str], 
                                     refactored_sigs: List[str]) -> float:
        """Calculate similarity between function signatures."""
        if not original_sigs or not refactored_sigs:
            return 0.0
        
        similarities = []
        for orig_sig in original_sigs:
            for ref_sig in refactored_sigs:
                similarity = SequenceMatcher(None, orig_sig, ref_sig).ratio()
                similarities.append(similarity)
        
        return max(similarities) if similarities else 0.0
    
    def _calculate_structure_similarity(self, 
                                     original_structs: List[str], 
                                     refactored_structs: List[str]) -> float:
        """Calculate similarity between class structures."""
        if not original_structs or not refactored_structs:
            return 0.0
        
        similarities = []
        for orig_struct in original_structs:
            for ref_struct in refactored_structs:
                similarity = SequenceMatcher(None, orig_struct, ref_struct).ratio()
                similarities.append(similarity)
        
        return max(similarities) if similarities else 0.0
    
    def _categorize_refactoring(self, smells: List[str]) -> str:
        """Categorize the refactoring based on code smells."""
        if "long_method" in smells or "complex_condition" in smells:
            return "method_refactoring"
        elif "large_class" in smells or "feature_envy" in smells:
            return "class_refactoring"
        elif "duplicate_code" in smells:
            return "duplication_refactoring"
        elif "primitive_obsession" in smells or "data_clumps" in smells:
            return "data_refactoring"
        elif "switch_statement" in smells:
            return "control_refactoring"
        else:
            return "general_refactoring"

def main():
    """Example usage of the RefactoringTrainer."""
    trainer = RefactoringTrainer()
    
    # Generate a dataset of refactoring examples
    examples = trainer.generate_dataset(num_examples=5)
    
    # Print examples
    for i, example in enumerate(examples, 1):
        print(f"\nExample {i}:")
        print("\nOriginal Code:")
        print(example.original_code)
        print("\nRefactored Code:")
        print(example.refactored_code)
        print("\nCode Smells:")
        for smell in example.code_smells:
            print(f"- {smell}")
        print("\nRefactoring Steps:")
        for step in example.refactoring_steps:
            print(f"- {step}")
        print("\nBenefits:")
        for benefit in example.benefits:
            print(f"- {benefit}")
        print(f"\nDifficulty: {example.difficulty:.2f}")
        print(f"Category: {example.category}")
        
        # Evaluate the refactoring
        metrics = trainer.evaluate_refactoring(
            example.original_code, example.refactored_code)
        print("\nEvaluation Metrics:")
        for category, score in metrics.items():
            print(f"- {category}: {score:.4f}")

if __name__ == "__main__":
    main() 