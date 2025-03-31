from typing import Dict, Any, List, Optional, Tuple
import ast
import random
from pathlib import Path
import json
from datetime import datetime
from ...config.logging_config import logger

class DebuggingDatasetGenerator:
    """Generator for debugging training datasets"""
    
    def __init__(self, output_dir: str = "data/debugging"):
        self.output_dir = Path(output_dir)
        self.error_types = {
            "syntax": [
                "missing_colon",
                "indentation",
                "unmatched_brackets",
                "invalid_operator",
                "missing_parentheses",
                "invalid_identifier"
            ],
            "runtime": [
                "type_error",
                "name_error",
                "index_error",
                "key_error",
                "attribute_error",
                "value_error",
                "zero_division_error",
                "import_error",
                "file_not_found_error"
            ],
            "logical": [
                "infinite_loop",
                "off_by_one",
                "wrong_condition",
                "missing_initialization",
                "race_condition",
                "deadlock",
                "memory_leak",
                "resource_leak"
            ],
            "concurrency": [
                "thread_safety",
                "deadlock",
                "race_condition",
                "starvation",
                "priority_inversion"
            ],
            "security": [
                "sql_injection",
                "xss_vulnerability",
                "buffer_overflow",
                "command_injection",
                "path_traversal"
            ]
        }
        
    def generate_dataset(self, num_examples: int = 10) -> List[Dict[str, Any]]:
        """Generate debugging training dataset"""
        try:
            dataset = []
            for _ in range(num_examples):
                example = self._generate_example()
                dataset.append(example)
            
            self._save_dataset(dataset)
            return dataset
            
        except Exception as e:
            logger.error(f"Error generating debugging dataset: {str(e)}")
            raise
            
    def _generate_example(self) -> Dict[str, Any]:
        """Generate a single debugging example"""
        try:
            error_type = random.choice(list(self.error_types.keys()))
            error_subtype = random.choice(self.error_types[error_type])
            
            if error_type == "syntax":
                return self._generate_syntax_error_example(error_subtype)
            elif error_type == "runtime":
                return self._generate_runtime_error_example(error_subtype)
            elif error_type == "logical":
                return self._generate_logical_error_example(error_subtype)
            elif error_type == "concurrency":
                return self._generate_concurrency_error_example(error_subtype)
            elif error_type == "security":
                return self._generate_security_error_example(error_subtype)
                
        except Exception as e:
            logger.error(f"Error generating example: {str(e)}")
            raise
            
    def _generate_syntax_error_example(self, error_subtype: str) -> Dict[str, Any]:
        """Generate syntax error example"""
        examples = {
            "missing_colon": {
                "buggy_code": """
def calculate_sum(a, b)
    return a + b
""",
                "fixed_code": """
def calculate_sum(a, b):
    return a + b
""",
                "error_message": "SyntaxError: invalid syntax",
                "explanation": "The function definition is missing a colon after the parameter list",
                "debugging_steps": [
                    "Check the function definition line",
                    "Notice the missing colon after the parameter list",
                    "Add the required colon",
                    "Verify the function syntax is correct"
                ]
            },
            "indentation": {
                "buggy_code": """
def process_data(data):
result = []
for item in data:
    result.append(item * 2)
return result
""",
                "fixed_code": """
def process_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result
""",
                "error_message": "IndentationError: expected an indented block",
                "explanation": "The code block inside the function is not properly indented",
                "debugging_steps": [
                    "Check the indentation of the function body",
                    "Notice that the code block is not indented",
                    "Add proper indentation to the function body",
                    "Verify all code blocks are properly indented"
                ]
            }
        }
        return examples.get(error_subtype, self._generate_default_example())
        
    def _generate_runtime_error_example(self, error_subtype: str) -> Dict[str, Any]:
        """Generate runtime error example"""
        examples = {
            "type_error": {
                "buggy_code": """
def add_numbers(a, b):
    return a + b

result = add_numbers("5", 3)
""",
                "fixed_code": """
def add_numbers(a, b):
    return a + b

result = add_numbers(5, 3)
""",
                "error_message": "TypeError: can only concatenate str (not \"int\") to str",
                "explanation": "The function is trying to concatenate a string and an integer",
                "debugging_steps": [
                    "Check the types of arguments being passed",
                    "Notice that '5' is a string and 3 is an integer",
                    "Convert the string to an integer using int()",
                    "Verify the types match before addition"
                ]
            },
            "name_error": {
                "buggy_code": """
def process_user(user_id):
    return user_name + " is active"

result = process_user(123)
""",
                "fixed_code": """
def process_user(user_id):
    user_name = get_user_name(user_id)
    return user_name + " is active"

result = process_user(123)
""",
                "error_message": "NameError: name 'user_name' is not defined",
                "explanation": "The variable user_name is used before being defined",
                "debugging_steps": [
                    "Check for undefined variables",
                    "Notice that user_name is used without being assigned",
                    "Add code to get the user name before using it",
                    "Verify all variables are properly defined"
                ]
            },
            "value_error": {
                "buggy_code": """
def convert_to_int(value):
    return int(value)

result = convert_to_int("not_a_number")
""",
                "fixed_code": """
def convert_to_int(value):
    try:
        return int(value)
    except ValueError:
        return None

result = convert_to_int("not_a_number")
""",
                "error_message": "ValueError: invalid literal for int() with base 10: 'not_a_number'",
                "explanation": "Attempting to convert a non-numeric string to an integer",
                "debugging_steps": [
                    "Check the input value type",
                    "Verify the string contains valid numeric characters",
                    "Add error handling for invalid inputs",
                    "Test with various input types"
                ]
            },
            "zero_division_error": {
                "buggy_code": """
def calculate_average(numbers):
    return sum(numbers) / len(numbers)

result = calculate_average([])
""",
                "fixed_code": """
def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

result = calculate_average([])
""",
                "error_message": "ZeroDivisionError: division by zero",
                "explanation": "Attempting to divide by zero when the input list is empty",
                "debugging_steps": [
                    "Check for empty input",
                    "Add validation for input length",
                    "Handle edge cases",
                    "Test with empty input"
                ]
            }
        }
        return examples.get(error_subtype, self._generate_default_example())
        
    def _generate_logical_error_example(self, error_subtype: str) -> Dict[str, Any]:
        """Generate logical error example"""
        examples = {
            "infinite_loop": {
                "buggy_code": """
def count_down(n):
    while n > 0:
        print(n)
        n = n + 1

count_down(5)
""",
                "fixed_code": """
def count_down(n):
    while n > 0:
        print(n)
        n = n - 1

count_down(5)
""",
                "error_message": "Program hangs indefinitely",
                "explanation": "The loop condition never becomes false because n is being increased instead of decreased",
                "debugging_steps": [
                    "Check the loop condition",
                    "Notice that n is being increased instead of decreased",
                    "Change the increment to a decrement",
                    "Verify the loop will terminate"
                ]
            },
            "off_by_one": {
                "buggy_code": """
def get_elements_up_to_index(lst, index):
    return lst[:index]

result = get_elements_up_to_index([1, 2, 3, 4, 5], 3)
""",
                "fixed_code": """
def get_elements_up_to_index(lst, index):
    return lst[:index + 1]

result = get_elements_up_to_index([1, 2, 3, 4, 5], 3)
""",
                "error_message": "Returns [1, 2, 3] instead of [1, 2, 3, 4]",
                "explanation": "The slice operation excludes the end index, causing one less element to be returned",
                "debugging_steps": [
                    "Check the slice operation",
                    "Notice that the end index is exclusive",
                    "Add 1 to the end index to include the desired element",
                    "Verify the correct number of elements is returned"
                ]
            }
        }
        return examples.get(error_subtype, self._generate_default_example())
        
    def _generate_concurrency_error_example(self, error_subtype: str) -> Dict[str, Any]:
        """Generate concurrency error example"""
        examples = {
            "thread_safety": {
                "buggy_code": """
import threading

class Counter:
    def __init__(self):
        self.count = 0
        
    def increment(self):
        self.count += 1

counter = Counter()
threads = []
for _ in range(100):
    t = threading.Thread(target=counter.increment)
    threads.append(t)
    t.start()
for t in threads:
    t.join()
print(counter.count)
""",
                "fixed_code": """
import threading

class Counter:
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()
        
    def increment(self):
        with self.lock:
            self.count += 1

counter = Counter()
threads = []
for _ in range(100):
    t = threading.Thread(target=counter.increment)
    threads.append(t)
    t.start()
for t in threads:
    t.join()
print(counter.count)
""",
                "error_message": "Race condition: count may not be 100",
                "explanation": "Multiple threads accessing shared resource without synchronization",
                "debugging_steps": [
                    "Identify shared resources",
                    "Add thread synchronization",
                    "Use locks or semaphores",
                    "Test with multiple threads"
                ]
            },
            "deadlock": {
                "buggy_code": """
import threading

lock1 = threading.Lock()
lock2 = threading.Lock()

def thread1():
    with lock1:
        with lock2:
            print("Thread 1")

def thread2():
    with lock2:
        with lock1:
            print("Thread 2")

t1 = threading.Thread(target=thread1)
t2 = threading.Thread(target=thread2)
t1.start()
t2.start()
""",
                "fixed_code": """
import threading

lock1 = threading.Lock()
lock2 = threading.Lock()

def thread1():
    with lock1:
        print("Thread 1: Got lock1")
        with lock2:
            print("Thread 1: Got lock2")

def thread2():
    with lock1:
        print("Thread 2: Got lock1")
        with lock2:
            print("Thread 2: Got lock2")

t1 = threading.Thread(target=thread1)
t2 = threading.Thread(target=thread2)
t1.start()
t2.start()
""",
                "error_message": "Program hangs due to deadlock",
                "explanation": "Circular dependency in lock acquisition order",
                "debugging_steps": [
                    "Identify lock acquisition order",
                    "Establish consistent lock ordering",
                    "Use timeout for locks",
                    "Test with different thread timings"
                ]
            }
        }
        return examples.get(error_subtype, self._generate_default_example())

    def _generate_security_error_example(self, error_subtype: str) -> Dict[str, Any]:
        """Generate security error example"""
        examples = {
            "sql_injection": {
                "buggy_code": """
def get_user_data(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)

result = get_user_data("1; DROP TABLE users;")
""",
                "fixed_code": """
def get_user_data(user_id):
    query = "SELECT * FROM users WHERE id = %s"
    return execute_query(query, (user_id,))

result = get_user_data("1; DROP TABLE users;")
""",
                "error_message": "SQL injection vulnerability",
                "explanation": "Unsanitized user input used in SQL query",
                "debugging_steps": [
                    "Identify user input points",
                    "Use parameterized queries",
                    "Validate input data",
                    "Test with malicious input"
                ]
            },
            "xss_vulnerability": {
                "buggy_code": """
def display_user_input(user_input):
    return f"<div>{user_input}</div>"

result = display_user_input("<script>alert('xss')</script>")
""",
                "fixed_code": """
import html

def display_user_input(user_input):
    escaped_input = html.escape(user_input)
    return f"<div>{escaped_input}</div>"

result = display_user_input("<script>alert('xss')</script>")
""",
                "error_message": "XSS vulnerability detected",
                "explanation": "Unescaped user input rendered in HTML",
                "debugging_steps": [
                    "Identify HTML output points",
                    "Escape user input",
                    "Use content security policy",
                    "Test with malicious scripts"
                ]
            }
        }
        return examples.get(error_subtype, self._generate_default_example())
        
    def _generate_default_example(self) -> Dict[str, Any]:
        """Generate a default example when error subtype is not found"""
        return {
            "buggy_code": """
def example_function():
    print("This is a default example")
""",
            "fixed_code": """
def example_function():
    print("This is a default example")
""",
            "error_message": "No specific error",
            "explanation": "This is a default example",
            "debugging_steps": [
                "Step 1",
                "Step 2",
                "Step 3"
            ]
        }
        
    def _save_dataset(self, dataset: List[Dict[str, Any]]):
        """Save the generated dataset"""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"debugging_dataset_{timestamp}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(dataset, f, indent=2)
                
            logger.info(f"Dataset saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving dataset: {str(e)}")
            raise
            
    def evaluate_example(self, example: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate a debugging example"""
        try:
            return {
                "error_identification": self._evaluate_error_identification(example),
                "debugging_steps": self._evaluate_debugging_steps(example),
                "fix_correctness": self._evaluate_fix_correctness(example)
            }
        except Exception as e:
            logger.error(f"Error evaluating example: {str(e)}")
            return {"error_identification": 0.0, "debugging_steps": 0.0, "fix_correctness": 0.0}
            
    def _evaluate_error_identification(self, example: Dict[str, Any]) -> float:
        """Evaluate the error identification quality"""
        try:
            score = 0.0
            
            # Check if error message is present
            if example.get("error_message"):
                score += 0.3
                
            # Check if explanation is clear
            if example.get("explanation") and len(example["explanation"]) > 20:
                score += 0.3
                
            # Check if error type matches the example
            if example.get("error_type"):
                score += 0.4
                
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error evaluating error identification: {str(e)}")
            return 0.0
            
    def _evaluate_debugging_steps(self, example: Dict[str, Any]) -> float:
        """Evaluate the debugging steps quality"""
        try:
            steps = example.get("debugging_steps", [])
            if not steps:
                return 0.0
                
            score = 0.0
            
            # Check number of steps
            if len(steps) >= 3:
                score += 0.3
                
            # Check step clarity
            clear_steps = sum(1 for step in steps if len(step) > 10)
            score += 0.3 * (clear_steps / len(steps))
            
            # Check step progression
            if len(steps) >= 2:
                score += 0.4
                
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error evaluating debugging steps: {str(e)}")
            return 0.0
            
    def _evaluate_fix_correctness(self, example: Dict[str, Any]) -> float:
        """Evaluate the fix correctness"""
        try:
            score = 0.0
            
            # Check if both buggy and fixed code are present
            if example.get("buggy_code") and example.get("fixed_code"):
                score += 0.4
                
            # Check if the fix addresses the error
            if example.get("error_message") and example.get("fixed_code"):
                score += 0.3
                
            # Check if the fix is minimal
            if example.get("buggy_code") and example.get("fixed_code"):
                buggy_lines = len(example["buggy_code"].splitlines())
                fixed_lines = len(example["fixed_code"].splitlines())
                if fixed_lines <= buggy_lines:
                    score += 0.3
                    
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error evaluating fix correctness: {str(e)}")
            return 0.0 