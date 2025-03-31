from typing import Dict, Any, List, Optional
import ast
import linecache
import sqlparse
import re
from datetime import datetime
from ...config.logging_config import logger

class LanguageOptimizer:
    """Enhanced language-specific performance optimizer"""
    
    def __init__(self):
        self.python_patterns = {
            'list_comprehension': r'for\s+\w+\s+in\s+range',
            'generator_expression': r'\(.*for.*in.*\)',
            'dictionary_comprehension': r'\{.*for.*in.*\}',
            'set_comprehension': r'\{.*for.*in.*\}',
            'nested_loops': r'for.*for',
            'global_variable': r'global\s+\w+',
            'class_method': r'@classmethod',
            'staticmethod': r'@staticmethod',
            'property': r'@property'
        }
        
        self.javascript_patterns = {
            'var_declaration': r'var\s+\w+',
            'let_declaration': r'let\s+\w+',
            'const_declaration': r'const\s+\w+',
            'arrow_function': r'\(\s*.*\s*\)\s*=>',
            'async_function': r'async\s+function',
            'promise': r'new\s+Promise',
            'setTimeout': r'setTimeout',
            'setInterval': r'setInterval',
            'document_query': r'document\.querySelector',
            'jquery_selector': r'\$\([\'"].*[\'"]\)'
        }
        
        self.sql_patterns = {
            'select_star': r'SELECT\s+\*',
            'where_clause': r'WHERE\s+.*',
            'join_clause': r'JOIN\s+.*',
            'order_by': r'ORDER\s+BY\s+.*',
            'group_by': r'GROUP\s+BY\s+.*',
            'having_clause': r'HAVING\s+.*',
            'subquery': r'\(SELECT\s+.*\)',
            'union': r'UNION\s+.*',
            'distinct': r'DISTINCT\s+.*'
        }
        
    def analyze_python_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python code for performance optimizations"""
        try:
            tree = ast.parse(code)
            optimizations = []
            complexity_score = 0
            
            # Analyze code structure
            for node in ast.walk(tree):
                # Check for nested loops
                if isinstance(node, ast.For) and any(isinstance(parent, ast.For) for parent in ast.walk(node)):
                    complexity_score += 2
                    optimizations.append({
                        "type": "complexity",
                        "message": "Nested loops detected. Consider using list comprehension or itertools",
                        "line": node.lineno,
                        "severity": "high"
                    })
                    
                # Check for global variables
                if isinstance(node, ast.Global):
                    complexity_score += 1
                    optimizations.append({
                        "type": "scope",
                        "message": "Global variables detected. Consider using class attributes or dependency injection",
                        "line": node.lineno,
                        "severity": "medium"
                    })
                    
                # Check for large functions
                if isinstance(node, ast.FunctionDef):
                    if len(node.body) > 20:
                        complexity_score += 1
                        optimizations.append({
                            "type": "function_size",
                            "message": "Large function detected. Consider breaking it into smaller functions",
                            "line": node.lineno,
                            "severity": "medium"
                        })
                        
                # Check for inefficient data structures
                if isinstance(node, ast.List):
                    if len(node.elts) > 1000:
                        optimizations.append({
                            "type": "data_structure",
                            "message": "Large list detected. Consider using numpy arrays or pandas DataFrames",
                            "line": node.lineno,
                            "severity": "medium"
                        })
                        
            # Pattern-based analysis
            for pattern_name, pattern in self.python_patterns.items():
                matches = re.finditer(pattern, code)
                for match in matches:
                    if pattern_name == 'list_comprehension':
                        optimizations.append({
                            "type": "optimization",
                            "message": "Consider using list comprehension for better performance",
                            "line": code[:match.start()].count('\n') + 1,
                            "severity": "low"
                        })
                    elif pattern_name == 'nested_loops':
                        complexity_score += 1
                        optimizations.append({
                            "type": "complexity",
                            "message": "Nested loops detected. Consider using itertools or vectorized operations",
                            "line": code[:match.start()].count('\n') + 1,
                            "severity": "high"
                        })
                        
            return {
                "optimizations": optimizations,
                "complexity_score": complexity_score,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing Python code: {str(e)}")
            return {}
            
    def analyze_javascript_code(self, code: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript code for performance optimizations"""
        try:
            optimizations = []
            complexity_score = 0
            
            # Pattern-based analysis
            for pattern_name, pattern in self.javascript_patterns.items():
                matches = re.finditer(pattern, code)
                for match in matches:
                    if pattern_name == 'var_declaration':
                        optimizations.append({
                            "type": "scope",
                            "message": "Use const or let instead of var for better scoping",
                            "line": code[:match.start()].count('\n') + 1,
                            "severity": "low"
                        })
                    elif pattern_name == 'document_query':
                        optimizations.append({
                            "type": "dom",
                            "message": "Cache DOM query results for better performance",
                            "line": code[:match.start()].count('\n') + 1,
                            "severity": "medium"
                        })
                    elif pattern_name == 'setTimeout':
                        complexity_score += 1
                        optimizations.append({
                            "type": "async",
                            "message": "Consider using requestAnimationFrame for animations",
                            "line": code[:match.start()].count('\n') + 1,
                            "severity": "medium"
                        })
                        
            # Check for event listener memory leaks
            if 'addEventListener' in code and 'removeEventListener' not in code:
                optimizations.append({
                    "type": "memory",
                    "message": "Event listeners detected without cleanup. Consider removing listeners when components unmount",
                    "severity": "high"
                })
                
            # Check for large objects
            if len(re.findall(r'\{[\s\S]*\}', code)) > 1000:
                optimizations.append({
                    "type": "data_structure",
                    "message": "Large object detected. Consider using Map or Set for better performance",
                    "severity": "medium"
                })
                
            return {
                "optimizations": optimizations,
                "complexity_score": complexity_score,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing JavaScript code: {str(e)}")
            return {}
            
    def analyze_sql_query(self, query: str) -> Dict[str, Any]:
        """Analyze SQL queries for performance optimizations"""
        try:
            optimizations = []
            complexity_score = 0
            parsed = sqlparse.parse(query)[0]
            
            # Pattern-based analysis
            for pattern_name, pattern in self.sql_patterns.items():
                matches = re.finditer(pattern, str(parsed), re.IGNORECASE)
                for match in matches:
                    if pattern_name == 'select_star':
                        optimizations.append({
                            "type": "query",
                            "message": "Avoid SELECT *. Specify required columns instead",
                            "line": query[:match.start()].count('\n') + 1,
                            "severity": "medium"
                        })
                    elif pattern_name == 'where_clause':
                        complexity_score += 1
                        optimizations.append({
                            "type": "index",
                            "message": "Ensure proper indexes exist on WHERE clause columns",
                            "line": query[:match.start()].count('\n') + 1,
                            "severity": "high"
                        })
                    elif pattern_name == 'join_clause':
                        complexity_score += 2
                        optimizations.append({
                            "type": "join",
                            "message": "Ensure proper indexes exist on join columns",
                            "line": query[:match.start()].count('\n') + 1,
                            "severity": "high"
                        })
                        
            # Check for subqueries
            if len(re.findall(r'\(SELECT\s+.*\)', str(parsed), re.IGNORECASE)) > 2:
                optimizations.append({
                    "type": "complexity",
                    "message": "Multiple subqueries detected. Consider using JOINs or CTEs",
                    "severity": "high"
                })
                
            # Check for ORDER BY without LIMIT
            if 'ORDER BY' in str(parsed) and 'LIMIT' not in str(parsed):
                optimizations.append({
                    "type": "query",
                    "message": "ORDER BY without LIMIT detected. Consider adding LIMIT clause",
                    "severity": "medium"
                })
                
            return {
                "optimizations": optimizations,
                "complexity_score": complexity_score,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing SQL query: {str(e)}")
            return {}
            
    def get_optimization_recommendations(self, language: str) -> Dict[str, Any]:
        """Get comprehensive optimization recommendations for a language"""
        recommendations = {
            'python': {
                'general': [
                    "Use list comprehensions instead of for loops when possible",
                    "Pre-allocate list sizes when known",
                    "Use appropriate data structures (set for lookups, deque for queues)",
                    "Profile code with cProfile or line_profiler",
                    "Use async/await for I/O-bound operations"
                ],
                'data_structures': [
                    "Use sets for unique value lookups",
                    "Use dictionaries for key-value mappings",
                    "Use deque for queue operations",
                    "Use numpy arrays for numerical computations",
                    "Use pandas DataFrames for tabular data"
                ],
                'performance': [
                    "Use generators for large datasets",
                    "Implement caching for expensive operations",
                    "Use multiprocessing for CPU-bound tasks",
                    "Use asyncio for I/O-bound tasks",
                    "Profile memory usage with memory_profiler"
                ]
            },
            'javascript': {
                'general': [
                    "Use const and let instead of var",
                    "Cache DOM elements and query results",
                    "Use requestAnimationFrame for animations",
                    "Implement debouncing for event handlers",
                    "Use Web Workers for CPU-intensive tasks"
                ],
                'performance': [
                    "Use event delegation for dynamic elements",
                    "Implement virtual scrolling for large lists",
                    "Use lazy loading for images and components",
                    "Minimize DOM manipulations",
                    "Use performance.now() for precise timing"
                ],
                'memory': [
                    "Clean up event listeners",
                    "Use WeakMap for object references",
                    "Implement proper garbage collection",
                    "Monitor memory leaks with Chrome DevTools",
                    "Use object pooling for frequently created objects"
                ]
            },
            'sql': {
                'general': [
                    "Create appropriate indexes on frequently queried columns",
                    "Avoid SELECT *",
                    "Use EXPLAIN to analyze query plans",
                    "Normalize database schema",
                    "Use appropriate data types"
                ],
                'performance': [
                    "Use covering indexes",
                    "Implement query caching",
                    "Use materialized views for complex queries",
                    "Partition large tables",
                    "Use connection pooling"
                ],
                'optimization': [
                    "Use EXISTS instead of IN for subqueries",
                    "Use UNION ALL instead of UNION when possible",
                    "Use appropriate join types",
                    "Implement proper indexing strategy",
                    "Use stored procedures for complex operations"
                ]
            }
        }
        
        return recommendations.get(language, {}) 