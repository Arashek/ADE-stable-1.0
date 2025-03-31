from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path
import logging
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import numpy as np
import ast
from difflib import SequenceMatcher
import re

class DebugEvaluator:
    """Evaluates the quality of debugging assistance."""
    
    def __init__(self, output_dir: str = "evaluation/debug"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Enhanced evaluation metrics
        self.metrics = {
            "error_identification": {
                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "error_category_accuracy": {},  # Per-category accuracy
                "error_pattern_recognition": 0.0  # Pattern matching accuracy
            },
            "debugging_steps": {
                "completeness": 0.0,
                "correctness": 0.0,
                "clarity": 0.0,
                "step_order": 0.0,  # Order correctness
                "step_dependency": 0.0,  # Dependency satisfaction
                "step_specificity": 0.0  # Action specificity
            },
            "fix_proposals": {
                "correctness": 0.0,
                "efficiency": 0.0,
                "readability": 0.0,
                "maintainability": 0.0,  # Code maintainability
                "robustness": 0.0,  # Error handling
                "style_compliance": 0.0  # Code style
            },
            "overall": {
                "comprehensive_score": 0.0,
                "learning_effectiveness": 0.0,
                "practical_utility": 0.0
            }
        }
    
    def evaluate_error_identification(self, 
                                   true_errors: List[str], 
                                   predicted_errors: List[str]) -> Dict[str, float]:
        """Evaluate the accuracy of error cause identification with enhanced metrics."""
        # Basic metrics
        y_true = [1 if true == pred else 0 for true, pred in zip(true_errors, predicted_errors)]
        y_pred = [1] * len(predicted_errors)
        
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)
        
        # Per-category accuracy
        error_categories = {}
        for true, pred in zip(true_errors, predicted_errors):
            if true not in error_categories:
                error_categories[true] = {"correct": 0, "total": 0}
            error_categories[true]["total"] += 1
            if true == pred:
                error_categories[true]["correct"] += 1
        
        category_accuracy = {
            category: stats["correct"] / stats["total"]
            for category, stats in error_categories.items()
        }
        
        # Error pattern recognition
        pattern_scores = []
        for true, pred in zip(true_errors, predicted_errors):
            # Check if the predicted error follows the pattern of the true error
            pattern_match = self._check_error_pattern(true, pred)
            pattern_scores.append(pattern_match)
        
        pattern_recognition = np.mean(pattern_scores)
        
        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "error_category_accuracy": category_accuracy,
            "error_pattern_recognition": pattern_recognition
        }
    
    def evaluate_debugging_steps(self, 
                               true_steps: List[List[str]], 
                               predicted_steps: List[List[str]]) -> Dict[str, float]:
        """Evaluate the quality of step-by-step debugging instructions with enhanced metrics."""
        completeness_scores = []
        correctness_scores = []
        clarity_scores = []
        order_scores = []
        dependency_scores = []
        specificity_scores = []
        
        for true, pred in zip(true_steps, predicted_steps):
            # Basic metrics
            covered_steps = sum(1 for step in true if any(similar_step(step, p) for p in pred))
            completeness = covered_steps / len(true) if true else 0.0
            completeness_scores.append(completeness)
            
            correct_steps = sum(1 for step in pred if any(similar_step(step, t) for t in true))
            correctness = correct_steps / len(pred) if pred else 0.0
            correctness_scores.append(correctness)
            
            # Clarity with enhanced analysis
            clarity = self._evaluate_step_clarity(pred)
            clarity_scores.append(clarity)
            
            # Step order evaluation
            order_score = self._evaluate_step_order(true, pred)
            order_scores.append(order_score)
            
            # Dependency satisfaction
            dependency_score = self._evaluate_step_dependencies(true, pred)
            dependency_scores.append(dependency_score)
            
            # Action specificity
            specificity_score = self._evaluate_step_specificity(pred)
            specificity_scores.append(specificity_score)
        
        return {
            "completeness": np.mean(completeness_scores),
            "correctness": np.mean(correctness_scores),
            "clarity": np.mean(clarity_scores),
            "step_order": np.mean(order_scores),
            "step_dependency": np.mean(dependency_scores),
            "step_specificity": np.mean(specificity_scores)
        }
    
    def evaluate_fix_proposals(self, 
                             true_fixes: List[str], 
                             predicted_fixes: List[str]) -> Dict[str, float]:
        """Evaluate the quality of proposed fixes with enhanced metrics."""
        correctness_scores = []
        efficiency_scores = []
        readability_scores = []
        maintainability_scores = []
        robustness_scores = []
        style_scores = []
        
        for true, pred in zip(true_fixes, predicted_fixes):
            # Basic metrics
            correctness = 1.0 if similar_code(true, pred) else 0.0
            correctness_scores.append(correctness)
            
            # Efficiency with enhanced analysis
            efficiency = self._evaluate_code_efficiency(true, pred)
            efficiency_scores.append(efficiency)
            
            # Readability with enhanced analysis
            readability = self._evaluate_code_readability(pred)
            readability_scores.append(readability)
            
            # Maintainability
            maintainability = self._evaluate_code_maintainability(pred)
            maintainability_scores.append(maintainability)
            
            # Robustness
            robustness = self._evaluate_code_robustness(pred)
            robustness_scores.append(robustness)
            
            # Style compliance
            style = self._evaluate_code_style(pred)
            style_scores.append(style)
        
        return {
            "correctness": np.mean(correctness_scores),
            "efficiency": np.mean(efficiency_scores),
            "readability": np.mean(readability_scores),
            "maintainability": np.mean(maintainability_scores),
            "robustness": np.mean(robustness_scores),
            "style_compliance": np.mean(style_scores)
        }
    
    def evaluate(self, 
                test_data: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Evaluate all aspects of debugging assistance with enhanced metrics."""
        # Extract true and predicted values
        true_errors = [item["error_type"] for item in test_data]
        predicted_errors = [item["predicted_error"] for item in test_data]
        
        true_steps = [item["debugging_steps"] for item in test_data]
        predicted_steps = [item["predicted_steps"] for item in test_data]
        
        true_fixes = [item["fixed_code"] for item in test_data]
        predicted_fixes = [item["predicted_fix"] for item in test_data]
        
        # Calculate metrics
        self.metrics["error_identification"] = self.evaluate_error_identification(
            true_errors, predicted_errors)
        
        self.metrics["debugging_steps"] = self.evaluate_debugging_steps(
            true_steps, predicted_steps)
        
        self.metrics["fix_proposals"] = self.evaluate_fix_proposals(
            true_fixes, predicted_fixes)
        
        # Calculate overall metrics
        self.metrics["overall"] = self._calculate_overall_metrics()
        
        return self.metrics
    
    def _check_error_pattern(self, true_error: str, predicted_error: str) -> float:
        """Check if the predicted error follows the pattern of the true error."""
        # Extract error type and message
        true_type = true_error.split(':')[0] if ':' in true_error else true_error
        pred_type = predicted_error.split(':')[0] if ':' in predicted_error else predicted_error
        
        # Compare error types
        type_match = 1.0 if true_type == pred_type else 0.0
        
        # Compare error messages if available
        if ':' in true_error and ':' in predicted_error:
            true_msg = true_error.split(':', 1)[1].strip()
            pred_msg = predicted_error.split(':', 1)[1].strip()
            msg_similarity = SequenceMatcher(None, true_msg, pred_msg).ratio()
            return (type_match + msg_similarity) / 2
        
        return type_match
    
    def _evaluate_step_clarity(self, steps: List[str]) -> float:
        """Evaluate the clarity of debugging steps."""
        if not steps:
            return 0.0
        
        # Average word length
        word_lengths = [len(word) for step in steps for word in step.split()]
        avg_word_length = np.mean(word_lengths)
        
        # Step length variation
        step_lengths = [len(step.split()) for step in steps]
        length_variation = np.std(step_lengths)
        
        # Action verb presence
        action_verbs = {"check", "verify", "identify", "fix", "update", "modify", "test", "run"}
        verb_scores = [
            any(verb in step.lower() for verb in action_verbs)
            for step in steps
        ]
        verb_score = np.mean(verb_scores)
        
        # Combine metrics
        length_score = 1.0 / (1.0 + avg_word_length)
        variation_score = 1.0 / (1.0 + length_variation)
        
        return (length_score + variation_score + verb_score) / 3
    
    def _evaluate_step_order(self, true_steps: List[str], predicted_steps: List[str]) -> float:
        """Evaluate the order of debugging steps."""
        if not true_steps or not predicted_steps:
            return 0.0
        
        # Create step pairs
        true_pairs = list(zip(true_steps[:-1], true_steps[1:]))
        pred_pairs = list(zip(predicted_steps[:-1], predicted_steps[1:]))
        
        # Count matching pairs
        matching_pairs = sum(
            1 for true_pair in true_pairs
            if any(similar_step(true_pair[0], pred_pair[0]) and 
                  similar_step(true_pair[1], pred_pair[1])
                  for pred_pair in pred_pairs)
        )
        
        return matching_pairs / len(true_pairs) if true_pairs else 0.0
    
    def _evaluate_step_dependencies(self, true_steps: List[str], predicted_steps: List[str]) -> float:
        """Evaluate if step dependencies are satisfied."""
        if not predicted_steps:
            return 0.0
        
        # Define common dependencies
        dependencies = {
            "test": ["check", "verify"],
            "fix": ["identify", "check"],
            "verify": ["check", "test"],
            "update": ["check", "verify"]
        }
        
        # Check dependency satisfaction
        satisfied_deps = 0
        total_deps = 0
        
        for i, step in enumerate(predicted_steps):
            for action, deps in dependencies.items():
                if action in step.lower():
                    total_deps += len(deps)
                    for dep in deps:
                        if any(dep in prev_step.lower() for prev_step in predicted_steps[:i]):
                            satisfied_deps += 1
        
        return satisfied_deps / total_deps if total_deps > 0 else 1.0
    
    def _evaluate_step_specificity(self, steps: List[str]) -> float:
        """Evaluate the specificity of debugging steps."""
        if not steps:
            return 0.0
        
        # Check for specific details
        specific_indicators = {
            "variable": r'\b\w+\b',  # Variable names
            "value": r'\d+',  # Numeric values
            "function": r'\b\w+\s*\(',  # Function calls
            "line": r'line \d+',  # Line numbers
            "file": r'file "[^"]+"'  # File paths
        }
        
        specificity_scores = []
        for step in steps:
            step_score = 0
            for indicator, pattern in specific_indicators.items():
                if re.search(pattern, step):
                    step_score += 1
            specificity_scores.append(step_score / len(specific_indicators))
        
        return np.mean(specificity_scores)
    
    def _evaluate_code_efficiency(self, true_code: str, pred_code: str) -> float:
        """Evaluate code efficiency."""
        try:
            true_tree = ast.parse(true_code)
            pred_tree = ast.parse(pred_code)
            
            # Compare number of operations
            true_ops = len(list(ast.walk(true_tree)))
            pred_ops = len(list(ast.walk(pred_tree)))
            
            # Compare code length
            true_lines = len(true_code.split('\n'))
            pred_lines = len(pred_code.split('\n'))
            
            # Calculate efficiency score
            op_efficiency = 1.0 / (1.0 + abs(true_ops - pred_ops))
            line_efficiency = 1.0 / (1.0 + abs(true_lines - pred_lines))
            
            return (op_efficiency + line_efficiency) / 2
        except:
            return 0.0
    
    def _evaluate_code_readability(self, code: str) -> float:
        """Evaluate code readability with enhanced metrics."""
        try:
            # Parse code into AST
            tree = ast.parse(code)
            
            # Calculate metrics
            lines = code.split('\n')
            avg_line_length = np.mean([len(line) for line in lines])
            num_lines = len(lines)
            
            # Complexity metrics
            complexity = len(list(ast.walk(tree)))
            nesting_depth = self._calculate_nesting_depth(tree)
            
            # Variable naming
            variable_names = [
                node.id for node in ast.walk(tree)
                if isinstance(node, ast.Name)
            ]
            naming_score = self._evaluate_variable_naming(variable_names)
            
            # Combine metrics
            length_score = 1.0 / (1.0 + avg_line_length)
            lines_score = 1.0 / (1.0 + num_lines)
            complexity_score = 1.0 / (1.0 + complexity)
            nesting_score = 1.0 / (1.0 + nesting_depth)
            
            return (length_score + lines_score + complexity_score + 
                   nesting_score + naming_score) / 5
        except:
            return 0.0
    
    def _evaluate_code_maintainability(self, code: str) -> float:
        """Evaluate code maintainability."""
        try:
            tree = ast.parse(code)
            
            # Function length
            function_lengths = [
                len(node.body) for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef)
            ]
            avg_function_length = np.mean(function_lengths) if function_lengths else 0
            
            # Comment ratio
            comment_lines = sum(1 for line in code.split('\n') 
                              if line.strip().startswith('#'))
            total_lines = len(code.split('\n'))
            comment_ratio = comment_lines / total_lines if total_lines > 0 else 0
            
            # Variable scope
            global_vars = sum(1 for node in ast.walk(tree)
                            if isinstance(node, ast.Global))
            
            # Calculate maintainability score
            length_score = 1.0 / (1.0 + avg_function_length)
            comment_score = min(comment_ratio, 0.3) / 0.3  # Normalize to [0, 1]
            scope_score = 1.0 / (1.0 + global_vars)
            
            return (length_score + comment_score + scope_score) / 3
        except:
            return 0.0
    
    def _evaluate_code_robustness(self, code: str) -> float:
        """Evaluate code robustness."""
        try:
            tree = ast.parse(code)
            
            # Error handling
            try_except_blocks = sum(1 for node in ast.walk(tree)
                                  if isinstance(node, ast.Try))
            
            # Input validation
            validation_checks = sum(1 for node in ast.walk(tree)
                                  if isinstance(node, ast.If) and
                                  any(isinstance(cond, ast.Compare) for cond in ast.walk(node)))
            
            # Type checking
            type_checks = sum(1 for node in ast.walk(tree)
                            if isinstance(node, ast.Call) and
                            isinstance(node.func, ast.Name) and
                            node.func.id in {'isinstance', 'type'})
            
            # Calculate robustness score
            error_handling_score = min(try_except_blocks, 3) / 3  # Normalize to [0, 1]
            validation_score = min(validation_checks, 5) / 5
            type_check_score = min(type_checks, 3) / 3
            
            return (error_handling_score + validation_score + type_check_score) / 3
        except:
            return 0.0
    
    def _evaluate_code_style(self, code: str) -> float:
        """Evaluate code style compliance."""
        try:
            # Check indentation
            indentation_consistent = all(
                len(line) - len(line.lstrip()) in {0, 4}
                for line in code.split('\n')
            )
            
            # Check line length
            long_lines = sum(1 for line in code.split('\n')
                           if len(line) > 79)
            line_length_score = 1.0 / (1.0 + long_lines)
            
            # Check spacing
            spacing_consistent = all(
                not re.search(r'[^ ]{2,}', line)  # No multiple spaces
                for line in code.split('\n')
            )
            
            # Check naming conventions
            tree = ast.parse(code)
            naming_score = self._evaluate_naming_conventions(tree)
            
            # Combine scores
            style_score = (
                (1.0 if indentation_consistent else 0.0) +
                line_length_score +
                (1.0 if spacing_consistent else 0.0) +
                naming_score
            ) / 4
            
            return style_score
        except:
            return 0.0
    
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
    
    def _evaluate_variable_naming(self, variable_names: List[str]) -> float:
        """Evaluate variable naming conventions."""
        if not variable_names:
            return 1.0
        
        # Check for descriptive names
        descriptive_score = sum(
            1 for name in variable_names
            if len(name) > 2 and not name.isupper()
        ) / len(variable_names)
        
        # Check for consistent case
        case_consistent = all(
            name.islower() or name[0].isupper()
            for name in variable_names
        )
        
        return (descriptive_score + (1.0 if case_consistent else 0.0)) / 2
    
    def _evaluate_naming_conventions(self, tree: ast.AST) -> float:
        """Evaluate naming convention compliance."""
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
    
    def _calculate_overall_metrics(self) -> Dict[str, float]:
        """Calculate overall evaluation metrics."""
        # Weight the different components
        weights = {
            "error_identification": 0.3,
            "debugging_steps": 0.3,
            "fix_proposals": 0.4
        }
        
        # Calculate comprehensive score
        comprehensive_score = (
            weights["error_identification"] * np.mean(list(self.metrics["error_identification"].values())) +
            weights["debugging_steps"] * np.mean(list(self.metrics["debugging_steps"].values())) +
            weights["fix_proposals"] * np.mean(list(self.metrics["fix_proposals"].values()))
        )
        
        # Calculate learning effectiveness
        learning_effectiveness = (
            self.metrics["debugging_steps"]["step_specificity"] * 0.4 +
            self.metrics["debugging_steps"]["step_order"] * 0.3 +
            self.metrics["debugging_steps"]["step_dependency"] * 0.3
        )
        
        # Calculate practical utility
        practical_utility = (
            self.metrics["fix_proposals"]["maintainability"] * 0.3 +
            self.metrics["fix_proposals"]["robustness"] * 0.3 +
            self.metrics["fix_proposals"]["style_compliance"] * 0.2 +
            self.metrics["error_identification"]["error_pattern_recognition"] * 0.2
        )
        
        return {
            "comprehensive_score": comprehensive_score,
            "learning_effectiveness": learning_effectiveness,
            "practical_utility": practical_utility
        }

def similar_step(step1: str, step2: str) -> bool:
    """Check if two debugging steps are similar."""
    # Enhanced similarity check using word overlap and semantic similarity
    words1 = set(step1.lower().split())
    words2 = set(step2.lower().split())
    overlap = len(words1.intersection(words2))
    
    # Calculate word overlap ratio
    overlap_ratio = overlap / max(len(words1), len(words2))
    
    # Check for semantic similarity using common action verbs
    action_verbs = {"check", "verify", "identify", "fix", "update", "modify", "test", "run"}
    verbs1 = {word for word in words1 if word in action_verbs}
    verbs2 = {word for word in words2 if word in action_verbs}
    verb_overlap = len(verbs1.intersection(verbs2))
    
    # Combine metrics
    return overlap_ratio > 0.5 or (verb_overlap > 0 and overlap_ratio > 0.3)

def similar_code(code1: str, code2: str) -> bool:
    """Check if two code snippets are similar."""
    try:
        # Parse both code snippets
        tree1 = ast.parse(code1)
        tree2 = ast.parse(code2)
        
        # Compare AST structure
        def get_structure(node: ast.AST) -> str:
            return f"{type(node).__name__}:{','.join(get_structure(child) for child in ast.iter_child_nodes(node))}"
        
        structure1 = get_structure(tree1)
        structure2 = get_structure(tree2)
        
        # Calculate structure similarity
        structure_similarity = SequenceMatcher(None, structure1, structure2).ratio()
        
        # Compare code lines
        lines1 = set(code1.split('\n'))
        lines2 = set(code2.split('\n'))
        line_overlap = len(lines1.intersection(lines2))
        line_similarity = line_overlap / max(len(lines1), len(lines2))
        
        # Combine metrics
        return structure_similarity > 0.7 or line_similarity > 0.7
    except:
        # Fallback to simple line comparison
        lines1 = set(code1.split('\n'))
        lines2 = set(code2.split('\n'))
        overlap = len(lines1.intersection(lines2))
        return overlap / max(len(lines1), len(lines2)) > 0.7

def calculate_readability(code: str) -> float:
    """Calculate a basic readability score for code."""
    try:
        # Parse code into AST
        tree = ast.parse(code)
        
        # Calculate metrics
        lines = code.split('\n')
        avg_line_length = np.mean([len(line) for line in lines])
        num_lines = len(lines)
        
        # Complexity metrics
        complexity = len(list(ast.walk(tree)))
        nesting_depth = max(
            (len(node.col_offset // 4 for node in ast.walk(tree)
              if isinstance(node, (ast.If, ast.For, ast.While, ast.FunctionDef))),
            default=0
        )
        
        # Combine metrics
        length_score = 1.0 / (1.0 + avg_line_length)
        lines_score = 1.0 / (1.0 + num_lines)
        complexity_score = 1.0 / (1.0 + complexity)
        nesting_score = 1.0 / (1.0 + nesting_depth)
        
        return (length_score + lines_score + complexity_score + nesting_score) / 4
    except:
        # Fallback to basic metrics
        lines = code.split('\n')
        avg_line_length = np.mean([len(line) for line in lines])
        num_lines = len(lines)
        
        length_score = 1.0 / (1.0 + avg_line_length)
        lines_score = 1.0 / (1.0 + num_lines)
        
        return (length_score + lines_score) / 2

def main():
    """Example usage of the DebugEvaluator."""
    evaluator = DebugEvaluator()
    
    # Example test data
    test_data = [
        {
            "error_type": "type_error",
            "predicted_error": "type_error",
            "debugging_steps": [
                "Identify the type mismatch",
                "Convert the string to integer",
                "Perform the operation"
            ],
            "predicted_steps": [
                "Check the variable types",
                "Convert string to number",
                "Fix the operation"
            ],
            "fixed_code": "result = int('5') + 3",
            "predicted_fix": "result = int('5') + 3"
        }
    ]
    
    # Run evaluation
    metrics = evaluator.evaluate(test_data)
    
    # Print results
    print("\nEvaluation Results:")
    for category, scores in metrics.items():
        print(f"\n{category}:")
        if isinstance(scores, dict):
            for metric, value in scores.items():
                print(f"- {metric}: {value:.4f}")
        else:
            print(f"- {scores:.4f}")
    
    # Save results
    evaluator.save_evaluation(metrics)

if __name__ == "__main__":
    main() 