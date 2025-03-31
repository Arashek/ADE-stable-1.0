from typing import Dict, Any, List, Optional, Tuple
import ast
import random
from pathlib import Path
import json
from datetime import datetime
from ...config.logging_config import logger

class BugIntroducer:
    """Class for introducing bugs into working code"""
    
    def __init__(self):
        self.bug_types = {
            "syntax": [
                self._introduce_missing_colon,
                self._introduce_indentation_error,
                self._introduce_unmatched_brackets
            ],
            "runtime": [
                self._introduce_type_error,
                self._introduce_name_error,
                self._introduce_index_error
            ],
            "logical": [
                self._introduce_infinite_loop,
                self._introduce_off_by_one,
                self._introduce_wrong_condition
            ]
        }
        
    def introduce_bugs(self, code: str, num_bugs: int = 1) -> List[Dict[str, Any]]:
        """Introduce bugs into working code"""
        try:
            results = []
            tree = ast.parse(code)
            
            for _ in range(num_bugs):
                bug_type = random.choice(list(self.bug_types.keys()))
                bug_introducer = random.choice(self.bug_types[bug_type])
                
                try:
                    buggy_code, error_message, explanation = bug_introducer(tree)
                    results.append({
                        "buggy_code": buggy_code,
                        "error_message": error_message,
                        "explanation": explanation,
                        "bug_type": bug_type
                    })
                except Exception as e:
                    logger.error(f"Error introducing bug: {str(e)}")
                    continue
                    
            return results
            
        except Exception as e:
            logger.error(f"Error introducing bugs: {str(e)}")
            raise
            
    def _introduce_missing_colon(self, tree: ast.AST) -> Tuple[str, str, str]:
        """Introduce a missing colon error"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Remove colon after function definition
                    source = ast.unparse(node)
                    buggy_code = source.replace(":", "")
                    return (
                        buggy_code,
                        "SyntaxError: invalid syntax",
                        "Missing colon after function definition"
                    )
            return "", "", ""
        except Exception as e:
            logger.error(f"Error introducing missing colon: {str(e)}")
            return "", "", ""
            
    def _introduce_indentation_error(self, tree: ast.AST) -> Tuple[str, str, str]:
        """Introduce an indentation error"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Remove indentation from function body
                    source = ast.unparse(node)
                    lines = source.split("\n")
                    buggy_code = lines[0] + "\n" + "\n".join(line.lstrip() for line in lines[1:])
                    return (
                        buggy_code,
                        "IndentationError: expected an indented block",
                        "Missing indentation in function body"
                    )
            return "", "", ""
        except Exception as e:
            logger.error(f"Error introducing indentation error: {str(e)}")
            return "", "", ""
            
    def _introduce_type_error(self, tree: ast.AST) -> Tuple[str, str, str]:
        """Introduce a type error"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.BinOp):
                    # Convert one operand to string
                    source = ast.unparse(node)
                    buggy_code = source.replace(node.left.id, f'"{node.left.id}"')
                    return (
                        buggy_code,
                        "TypeError: can only concatenate str (not \"int\") to str",
                        "Mixing string and integer types in operation"
                    )
            return "", "", ""
        except Exception as e:
            logger.error(f"Error introducing type error: {str(e)}")
            return "", "", ""
            
    def _introduce_name_error(self, tree: ast.AST) -> Tuple[str, str, str]:
        """Introduce a name error"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    # Use undefined variable
                    source = ast.unparse(tree)
                    buggy_code = source.replace(node.id, "undefined_variable")
                    return (
                        buggy_code,
                        "NameError: name 'undefined_variable' is not defined",
                        "Using undefined variable"
                    )
            return "", "", ""
        except Exception as e:
            logger.error(f"Error introducing name error: {str(e)}")
            return "", "", ""
            
    def _introduce_index_error(self, tree: ast.AST) -> Tuple[str, str, str]:
        """Introduce an index error"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.Subscript):
                    # Access index beyond list length
                    source = ast.unparse(tree)
                    buggy_code = source.replace(node.slice.value.n, "999")
                    return (
                        buggy_code,
                        "IndexError: list index out of range",
                        "Accessing index beyond list length"
                    )
            return "", "", ""
        except Exception as e:
            logger.error(f"Error introducing index error: {str(e)}")
            return "", "", ""
            
    def _introduce_infinite_loop(self, tree: ast.AST) -> Tuple[str, str, str]:
        """Introduce an infinite loop"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.While):
                    # Change decrement to increment
                    source = ast.unparse(node)
                    buggy_code = source.replace("-=", "+=")
                    return (
                        buggy_code,
                        "Program hangs indefinitely",
                        "Loop condition never becomes false"
                    )
            return "", "", ""
        except Exception as e:
            logger.error(f"Error introducing infinite loop: {str(e)}")
            return "", "", ""
            
    def _introduce_off_by_one(self, tree: ast.AST) -> Tuple[str, str, str]:
        """Introduce an off-by-one error"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.Slice):
                    # Remove +1 from slice end
                    source = ast.unparse(tree)
                    buggy_code = source.replace("+ 1", "")
                    return (
                        buggy_code,
                        "Returns one less element than expected",
                        "Slice end index is exclusive"
                    )
            return "", "", ""
        except Exception as e:
            logger.error(f"Error introducing off-by-one error: {str(e)}")
            return "", "", ""
            
    def _introduce_wrong_condition(self, tree: ast.AST) -> Tuple[str, str, str]:
        """Introduce a wrong condition error"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.Compare):
                    # Change comparison operator
                    source = ast.unparse(node)
                    buggy_code = source.replace("<", ">")
                    return (
                        buggy_code,
                        "Condition evaluates incorrectly",
                        "Wrong comparison operator used"
                    )
            return "", "", ""
        except Exception as e:
            logger.error(f"Error introducing wrong condition: {str(e)}")
            return "", "", ""
            
    def generate_examples(self, working_code: str, num_examples: int = 5) -> List[Dict[str, Any]]:
        """Generate examples of buggy code"""
        try:
            examples = []
            for _ in range(num_examples):
                bug_results = self.introduce_bugs(working_code)
                if bug_results:
                    example = {
                        "working_code": working_code,
                        "buggy_code": bug_results[0]["buggy_code"],
                        "error_message": bug_results[0]["error_message"],
                        "explanation": bug_results[0]["explanation"],
                        "bug_type": bug_results[0]["bug_type"],
                        "debugging_steps": self._generate_debugging_steps(bug_results[0])
                    }
                    examples.append(example)
            return examples
        except Exception as e:
            logger.error(f"Error generating examples: {str(e)}")
            return []
            
    def _generate_debugging_steps(self, bug_result: Dict[str, Any]) -> List[str]:
        """Generate debugging steps for a bug"""
        try:
            steps = []
            bug_type = bug_result["bug_type"]
            
            if bug_type == "syntax":
                steps = [
                    "Check for syntax errors in the code",
                    "Look for missing colons, brackets, or indentation",
                    "Verify the code structure is valid",
                    "Fix the syntax issue"
                ]
            elif bug_type == "runtime":
                steps = [
                    "Run the code and observe the error message",
                    "Check variable types and definitions",
                    "Verify array indices and dictionary keys",
                    "Fix the runtime error"
                ]
            else:  # logical
                steps = [
                    "Analyze the program logic",
                    "Check loop conditions and counters",
                    "Verify comparison operators",
                    "Fix the logical error"
                ]
                
            return steps
            
        except Exception as e:
            logger.error(f"Error generating debugging steps: {str(e)}")
            return [] 