from typing import Dict, Any, List, Optional
import ast
import linecache
import sqlparse
from datetime import datetime
import json
from ...config.logging_config import logger
from ...database.redis_client import redis_client

class LanguageAnalyzer:
    """Analyzer for language-specific performance optimizations"""
    
    def __init__(self):
        self.python_optimizations = []
        self.javascript_optimizations = []
        self.sql_optimizations = []
        
    def analyze_python_code(self, code: str) -> List[Dict[str, Any]]:
        """Analyze Python code for performance optimizations"""
        try:
            optimizations = []
            tree = ast.parse(code)
            
            # Analyze imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        if name.name in ['numpy', 'pandas']:
                            optimizations.append({
                                "type": "import_optimization",
                                "message": f"Consider using {name.name} for better performance",
                                "line": node.lineno,
                                "severity": "medium"
                            })
                            
                # Analyze loops
                elif isinstance(node, ast.For):
                    if isinstance(node.iter, ast.Call):
                        if isinstance(node.iter.func, ast.Name):
                            if node.iter.func.id == 'range':
                                optimizations.append({
                                    "type": "loop_optimization",
                                    "message": "Consider using list comprehension for better performance",
                                    "line": node.lineno,
                                    "severity": "low"
                                })
                                
                # Analyze function calls
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['append', 'extend']:
                            optimizations.append({
                                "type": "list_operation_optimization",
                                "message": "Consider pre-allocating list size for better performance",
                                "line": node.lineno,
                                "severity": "medium"
                            })
                            
            return optimizations
            
        except Exception as e:
            logger.error(f"Error analyzing Python code: {str(e)}")
            return []
            
    def analyze_javascript_code(self, code: str) -> List[Dict[str, Any]]:
        """Analyze JavaScript/TypeScript code for performance optimizations"""
        try:
            optimizations = []
            
            # Basic JavaScript optimizations
            if 'for (var' in code or 'for (let' in code:
                optimizations.append({
                    "type": "loop_optimization",
                    "message": "Consider using forEach or map for better readability and performance",
                    "severity": "low"
                })
                
            if 'document.getElementById' in code:
                optimizations.append({
                    "type": "dom_optimization",
                    "message": "Consider caching DOM elements for better performance",
                    "severity": "medium"
                })
                
            if 'setTimeout' in code:
                optimizations.append({
                    "type": "async_optimization",
                    "message": "Consider using requestAnimationFrame for animations",
                    "severity": "medium"
                })
                
            return optimizations
            
        except Exception as e:
            logger.error(f"Error analyzing JavaScript code: {str(e)}")
            return []
            
    def analyze_sql_query(self, query: str) -> List[Dict[str, Any]]:
        """Analyze SQL queries for performance optimizations"""
        try:
            optimizations = []
            parsed = sqlparse.parse(query)[0]
            
            # Check for missing indexes
            if 'WHERE' in str(parsed):
                where_clause = str(parsed).split('WHERE')[1].split('ORDER BY')[0]
                if any(col in where_clause for col in ['created_at', 'updated_at']):
                    optimizations.append({
                        "type": "index_optimization",
                        "message": "Consider adding an index on timestamp columns used in WHERE clause",
                        "severity": "high"
                    })
                    
            # Check for SELECT *
            if 'SELECT *' in str(parsed):
                optimizations.append({
                    "type": "select_optimization",
                    "message": "Avoid using SELECT *, specify required columns instead",
                    "severity": "medium"
                })
                
            # Check for JOIN operations
            if 'JOIN' in str(parsed):
                optimizations.append({
                    "type": "join_optimization",
                    "message": "Ensure proper indexes exist on join columns",
                    "severity": "high"
                })
                
            return optimizations
            
        except Exception as e:
            logger.error(f"Error analyzing SQL query: {str(e)}")
            return []
            
    async def store_optimizations(self, language: str, optimizations: List[Dict[str, Any]]):
        """Store code optimizations in Redis"""
        try:
            key = f"code_optimizations:{language}:{datetime.utcnow().strftime('%Y%m%d')}"
            await redis_client.set(key, optimizations, expire=30 * 24 * 60 * 60)  # 30 days TTL
        except Exception as e:
            logger.error(f"Error storing optimizations: {str(e)}")
            
    def generate_optimization_report(self, language: str, code: str) -> Dict[str, Any]:
        """Generate a comprehensive optimization report"""
        try:
            optimizations = []
            
            if language == 'python':
                optimizations = self.analyze_python_code(code)
            elif language in ['javascript', 'typescript']:
                optimizations = self.analyze_javascript_code(code)
            elif language == 'sql':
                optimizations = self.analyze_sql_query(code)
                
            return {
                "language": language,
                "optimizations": optimizations,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating optimization report: {str(e)}")
            return {}
            
    def get_optimization_recommendations(self, language: str) -> List[str]:
        """Get general optimization recommendations for a language"""
        recommendations = {
            'python': [
                "Use list comprehensions instead of for loops when possible",
                "Pre-allocate list sizes when known",
                "Use appropriate data structures (set for lookups, deque for queues)",
                "Profile code with cProfile or line_profiler",
                "Use async/await for I/O-bound operations"
            ],
            'javascript': [
                "Use const and let instead of var",
                "Cache DOM elements and query results",
                "Use requestAnimationFrame for animations",
                "Implement debouncing for event handlers",
                "Use Web Workers for CPU-intensive tasks"
            ],
            'sql': [
                "Create appropriate indexes on frequently queried columns",
                "Avoid SELECT *",
                "Use EXPLAIN to analyze query plans",
                "Normalize database schema",
                "Use appropriate data types"
            ]
        }
        
        return recommendations.get(language, []) 