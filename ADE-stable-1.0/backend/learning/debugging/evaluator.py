from typing import Dict, Any, List, Optional, Tuple
import ast
import difflib
from pathlib import Path
import json
from datetime import datetime
from ...config.logging_config import logger
import re

class DebuggingEvaluator:
    """Evaluator for debugging examples and solutions"""
    
    def __init__(self):
        self.metrics = {
            "error_identification": 0.0,
            "debugging_steps": 0.0,
            "fix_correctness": 0.0,
            "solution_quality": 0.0,
            "code_style": 0.0,
            "performance": 0.0,
            "security": 0.0,
            "maintainability": 0.0
        }
        
    def evaluate_solution(self, 
                         buggy_code: str, 
                         proposed_solution: str, 
                         correct_solution: str,
                         debugging_steps: List[str]) -> Dict[str, float]:
        """Evaluate a proposed debugging solution"""
        try:
            metrics = {
                "error_identification": self._evaluate_error_identification(buggy_code, proposed_solution),
                "debugging_steps": self._evaluate_debugging_steps(debugging_steps),
                "fix_correctness": self._evaluate_fix_correctness(proposed_solution, correct_solution),
                "solution_quality": self._evaluate_solution_quality(proposed_solution, correct_solution),
                "code_style": self._evaluate_code_style(proposed_solution),
                "performance": self._evaluate_performance(proposed_solution),
                "security": self._evaluate_security(proposed_solution),
                "maintainability": self._evaluate_maintainability(proposed_solution)
            }
            
            self.metrics = metrics
            return metrics
            
        except Exception as e:
            logger.error(f"Error evaluating solution: {str(e)}")
            return self.metrics
            
    def _evaluate_error_identification(self, buggy_code: str, proposed_solution: str) -> float:
        """Evaluate how well the error was identified"""
        try:
            score = 0.0
            
            # Parse both codes
            buggy_tree = ast.parse(buggy_code)
            solution_tree = ast.parse(proposed_solution)
            
            # Compare ASTs
            diff = difflib.ndiff(
                ast.dump(buggy_tree).splitlines(),
                ast.dump(solution_tree).splitlines()
            )
            
            # Count differences
            diff_count = sum(1 for line in diff if line.startswith('+') or line.startswith('-'))
            
            # Score based on number of changes
            if diff_count == 0:
                score = 0.0
            elif diff_count == 1:
                score = 0.8
            else:
                score = 0.4
                
            return score
            
        except Exception as e:
            logger.error(f"Error evaluating error identification: {str(e)}")
            return 0.0
            
    def _evaluate_debugging_steps(self, debugging_steps: List[str]) -> float:
        """Evaluate the quality of debugging steps"""
        try:
            if not debugging_steps:
                return 0.0
                
            score = 0.0
            
            # Check number of steps
            if len(debugging_steps) >= 3:
                score += 0.3
                
            # Check step clarity
            clear_steps = sum(1 for step in debugging_steps if len(step) > 10)
            score += 0.3 * (clear_steps / len(debugging_steps))
            
            # Check step progression
            if len(debugging_steps) >= 2:
                score += 0.4
                
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error evaluating debugging steps: {str(e)}")
            return 0.0
            
    def _evaluate_fix_correctness(self, proposed_solution: str, correct_solution: str) -> float:
        """Evaluate if the fix is correct"""
        try:
            score = 0.0
            
            # Parse both solutions
            proposed_tree = ast.parse(proposed_solution)
            correct_tree = ast.parse(correct_solution)
            
            # Compare ASTs
            diff = difflib.ndiff(
                ast.dump(proposed_tree).splitlines(),
                ast.dump(correct_tree).splitlines()
            )
            
            # Count differences
            diff_count = sum(1 for line in diff if line.startswith('+') or line.startswith('-'))
            
            # Score based on number of differences
            if diff_count == 0:
                score = 1.0
            elif diff_count == 1:
                score = 0.8
            elif diff_count == 2:
                score = 0.6
            else:
                score = 0.4
                
            return score
            
        except Exception as e:
            logger.error(f"Error evaluating fix correctness: {str(e)}")
            return 0.0
            
    def _evaluate_solution_quality(self, proposed_solution: str, correct_solution: str) -> float:
        """Evaluate the quality of the solution"""
        try:
            score = 0.0
            
            # Compare code length
            proposed_lines = len(proposed_solution.splitlines())
            correct_lines = len(correct_solution.splitlines())
            
            if proposed_lines <= correct_lines:
                score += 0.4
                
            # Compare code complexity
            proposed_complexity = self._calculate_complexity(proposed_solution)
            correct_complexity = self._calculate_complexity(correct_solution)
            
            if proposed_complexity <= correct_complexity:
                score += 0.3
                
            # Check for code style
            if self._check_code_style(proposed_solution):
                score += 0.3
                
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error evaluating solution quality: {str(e)}")
            return 0.0
            
    def _calculate_complexity(self, code: str) -> int:
        """Calculate code complexity"""
        try:
            tree = ast.parse(code)
            complexity = 0
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                    complexity += 1
                    
            return complexity
            
        except Exception as e:
            logger.error(f"Error calculating complexity: {str(e)}")
            return 0
            
    def _check_code_style(self, code: str) -> bool:
        """Check if code follows style guidelines"""
        try:
            # Check line length
            lines = code.splitlines()
            if any(len(line) > 79 for line in lines):
                return False
                
            # Check indentation
            if not all(line.startswith('    ') or not line.strip() for line in lines[1:]):
                return False
                
            # Check for proper spacing
            if not all(line.strip() for line in lines):
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error checking code style: {str(e)}")
            return False
            
    def generate_report(self, metrics: Dict[str, float]) -> str:
        """Generate an evaluation report"""
        try:
            report = [
                "Debugging Solution Evaluation Report",
                "=====================================",
                "",
                f"Error Identification Score: {metrics['error_identification']:.2f}",
                f"Debugging Steps Score: {metrics['debugging_steps']:.2f}",
                f"Fix Correctness Score: {metrics['fix_correctness']:.2f}",
                f"Solution Quality Score: {metrics['solution_quality']:.2f}",
                "",
                "Overall Assessment:",
                self._get_overall_assessment(metrics)
            ]
            
            return "\n".join(report)
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return "Error generating evaluation report"
            
    def _get_overall_assessment(self, metrics: Dict[str, float]) -> str:
        """Get overall assessment based on metrics"""
        try:
            avg_score = sum(metrics.values()) / len(metrics)
            
            if avg_score >= 0.9:
                return "Excellent solution with high quality in all aspects"
            elif avg_score >= 0.7:
                return "Good solution with minor areas for improvement"
            elif avg_score >= 0.5:
                return "Fair solution with several areas needing improvement"
            else:
                return "Poor solution requiring significant improvement"
                
        except Exception as e:
            logger.error(f"Error getting overall assessment: {str(e)}")
            return "Unable to assess solution quality"
            
    def save_evaluation(self, evaluation: Dict[str, Any], output_dir: str = "data/evaluations"):
        """Save evaluation results"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_path / f"evaluation_{timestamp}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(evaluation, f, indent=2)
                
            logger.info(f"Evaluation saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving evaluation: {str(e)}")
            raise 

    def _evaluate_code_style(self, code: str) -> float:
        """Evaluate code style compliance"""
        try:
            score = 0.0
            
            # Check line length
            lines = code.splitlines()
            if all(len(line) <= 79 for line in lines):
                score += 0.2
                
            # Check indentation
            if all(line.startswith('    ') or not line.strip() for line in lines[1:]):
                score += 0.2
                
            # Check for proper spacing
            if all(line.strip() for line in lines):
                score += 0.2
                
            # Check for docstrings
            if any('"""' in line or "'''" in line for line in lines):
                score += 0.2
                
            # Check for type hints
            if any(':' in line and '->' in line for line in lines):
                score += 0.2
                
            return score
            
        except Exception as e:
            logger.error(f"Error evaluating code style: {str(e)}")
            return 0.0
            
    def _evaluate_performance(self, code: str) -> float:
        """Evaluate code performance"""
        try:
            score = 0.0
            tree = ast.parse(code)
            
            # Check for inefficient loops
            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name):
                        if node.iter.func.id == 'range':
                            score += 0.2
                            
            # Check for unnecessary list comprehensions
            if not any(isinstance(node, ast.ListComp) for node in ast.walk(tree)):
                score += 0.2
                
            # Check for proper data structures
            if not any(isinstance(node, ast.Dict) for node in ast.walk(tree)):
                score += 0.2
                
            # Check for caching opportunities
            if any(isinstance(node, ast.FunctionDef) and len(node.body) > 5 for node in ast.walk(tree)):
                score += 0.2
                
            # Check for memory efficiency
            if not any(isinstance(node, ast.List) for node in ast.walk(tree)):
                score += 0.2
                
            return score
            
        except Exception as e:
            logger.error(f"Error evaluating performance: {str(e)}")
            return 0.0
            
    def _evaluate_security(self, code: str) -> float:
        """Evaluate code security"""
        try:
            score = 0.0
            
            # Check for SQL injection vulnerabilities
            if not any('f"' in line and 'SELECT' in line for line in code.splitlines()):
                score += 0.2
                
            # Check for XSS vulnerabilities
            if not any('f"' in line and '<div>' in line for line in code.splitlines()):
                score += 0.2
                
            # Check for command injection
            if not any('os.system' in line or 'subprocess.call' in line for line in code.splitlines()):
                score += 0.2
                
            # Check for proper input validation
            if any('isinstance' in line or 'try' in line for line in code.splitlines()):
                score += 0.2
                
            # Check for secure file operations
            if not any('open(' in line for line in code.splitlines()):
                score += 0.2
                
            return score
            
        except Exception as e:
            logger.error(f"Error evaluating security: {str(e)}")
            return 0.0
            
    def _evaluate_maintainability(self, code: str) -> float:
        """Evaluate code maintainability"""
        try:
            score = 0.0
            
            # Check for function length
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if len(node.body) <= 10:
                        score += 0.2
                        
            # Check for code duplication
            lines = code.splitlines()
            unique_lines = len(set(lines))
            if unique_lines / len(lines) > 0.8:
                score += 0.2
                
            # Check for meaningful variable names
            if all(len(name) > 2 for name in re.findall(r'\b[a-zA-Z_]\w*\b', code)):
                score += 0.2
                
            # Check for comments
            if any('#' in line for line in lines):
                score += 0.2
                
            # Check for modularity
            if len(tree.body) > 1:
                score += 0.2
                
            return score
            
        except Exception as e:
            logger.error(f"Error evaluating maintainability: {str(e)}")
            return 0.0 