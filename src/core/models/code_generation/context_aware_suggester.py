from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
import ast
import re
from datetime import datetime
import json

from ..llm_integration import LLMIntegration, LLMConfig

logger = logging.getLogger(__name__)

@dataclass
class CodeSuggestion:
    """Represents a code suggestion with metadata"""
    type: str
    description: str
    code: str
    location: Dict[str, Any]
    priority: int
    category: str
    impact: str
    created_at: datetime

class ContextAwareSuggester:
    """Context-aware code suggestion engine"""
    
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        self.llm = LLMIntegration(llm_config) if llm_config else None
        self.suggestion_history: List[CodeSuggestion] = []
        
        # Define suggestion categories
        self.categories = {
            "performance": ["optimization", "caching", "algorithm"],
            "security": ["authentication", "authorization", "validation"],
            "maintainability": ["refactoring", "documentation", "testing"],
            "best_practices": ["patterns", "style", "architecture"]
        }
        
    async def generate_suggestions(
        self,
        code: str,
        context: Dict[str, Any],
        max_suggestions: int = 5
    ) -> List[CodeSuggestion]:
        """Generate context-aware code suggestions"""
        try:
            # Analyze code structure
            structure = await self._analyze_code_structure(code)
            
            # Analyze code patterns
            patterns = await self._analyze_code_patterns(code)
            
            # Generate suggestions using LLM
            llm_suggestions = await self._generate_llm_suggestions(
                code,
                structure,
                patterns,
                context
            )
            
            # Generate suggestions using static analysis
            static_suggestions = await self._generate_static_suggestions(
                code,
                structure,
                patterns
            )
            
            # Combine and prioritize suggestions
            all_suggestions = llm_suggestions + static_suggestions
            prioritized_suggestions = self._prioritize_suggestions(
                all_suggestions,
                context
            )
            
            # Limit number of suggestions
            suggestions = prioritized_suggestions[:max_suggestions]
            
            # Update suggestion history
            self.suggestion_history.extend(suggestions)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return []
            
    async def _analyze_code_structure(self, code: str) -> Dict[str, Any]:
        """Analyze code structure"""
        try:
            tree = ast.parse(code)
            return self._extract_structure(tree)
        except:
            # Fallback to regex-based analysis for non-Python code
            return self._extract_structure_regex(code)
            
    def _extract_structure(self, tree: ast.AST) -> Dict[str, Any]:
        """Extract structure from AST"""
        structure = {
            "classes": [],
            "functions": [],
            "imports": [],
            "variables": [],
            "complexity": self._calculate_complexity(tree)
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                structure["classes"].append({
                    "name": node.name,
                    "bases": [base.id for base in node.bases],
                    "methods": [method.name for method in node.body if isinstance(method, ast.FunctionDef)]
                })
            elif isinstance(node, ast.FunctionDef):
                structure["functions"].append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "returns": self._get_return_type(node),
                    "complexity": self._calculate_complexity(node)
                })
            elif isinstance(node, ast.Import):
                structure["imports"].extend(alias.name for alias in node.names)
            elif isinstance(node, ast.Assign):
                structure["variables"].extend(target.id for target in node.targets)
                
        return structure
        
    def _extract_structure_regex(self, code: str) -> Dict[str, Any]:
        """Extract structure using regex for non-Python code"""
        structure = {
            "classes": [],
            "functions": [],
            "imports": [],
            "variables": [],
            "complexity": self._estimate_complexity_regex(code)
        }
        
        # Extract classes
        class_pattern = r"class\s+(\w+)(?:\s*\([^)]*\))?:"
        structure["classes"] = re.findall(class_pattern, code)
        
        # Extract functions
        function_pattern = r"def\s+(\w+)\s*\([^)]*\):"
        structure["functions"] = re.findall(function_pattern, code)
        
        # Extract imports
        import_pattern = r"import\s+(\w+(?:\.\w+)*)"
        structure["imports"] = re.findall(import_pattern, code)
        
        # Extract variables
        variable_pattern = r"(\w+)\s*=\s*[^=]"
        structure["variables"] = re.findall(variable_pattern, code)
        
        return structure
        
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a node"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
                
        return complexity
        
    def _estimate_complexity_regex(self, code: str) -> int:
        """Estimate complexity using regex for non-Python code"""
        complexity = 1  # Base complexity
        
        # Count control structures
        control_patterns = [
            r"if\s*\([^)]*\)",
            r"while\s*\([^)]*\)",
            r"for\s*\([^)]*\)",
            r"catch\s*\([^)]*\)",
            r"switch\s*\([^)]*\)"
        ]
        
        for pattern in control_patterns:
            complexity += len(re.findall(pattern, code))
            
        return complexity
        
    async def _analyze_code_patterns(self, code: str) -> Dict[str, Any]:
        """Analyze code patterns"""
        patterns = {
            "design_patterns": [],
            "anti_patterns": [],
            "code_smells": [],
            "best_practices": []
        }
        
        # Analyze design patterns
        patterns["design_patterns"] = await self._detect_design_patterns(code)
        
        # Analyze anti-patterns
        patterns["anti_patterns"] = await self._detect_anti_patterns(code)
        
        # Analyze code smells
        patterns["code_smells"] = await self._detect_code_smells(code)
        
        # Analyze best practices
        patterns["best_practices"] = await self._detect_best_practices(code)
        
        return patterns
        
    async def _generate_llm_suggestions(
        self,
        code: str,
        structure: Dict[str, Any],
        patterns: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[CodeSuggestion]:
        """Generate suggestions using LLM"""
        if not self.llm:
            return []
            
        prompt = f"""
        Analyze the following code and generate suggestions for improvement:
        
        Code: {code}
        Structure: {structure}
        Patterns: {patterns}
        Context: {context}
        
        Generate suggestions focusing on:
        1. Performance optimization
        2. Security improvements
        3. Code maintainability
        4. Best practices
        5. Design patterns
        
        For each suggestion, provide:
        1. Type of suggestion
        2. Description
        3. Code example
        4. Location in code
        5. Priority (1-5)
        6. Category
        7. Impact
        """
        
        response = await self.llm.generate(prompt)
        suggestions = self._parse_llm_suggestions(response)
        
        return suggestions
        
    async def _generate_static_suggestions(
        self,
        code: str,
        structure: Dict[str, Any],
        patterns: Dict[str, Any]
    ) -> List[CodeSuggestion]:
        """Generate suggestions using static analysis"""
        suggestions = []
        
        # Check complexity
        if structure["complexity"] > 10:
            suggestions.append(CodeSuggestion(
                type="refactoring",
                description="High cyclomatic complexity detected. Consider breaking down into smaller functions.",
                code="",
                location={"type": "file", "line": 1},
                priority=3,
                category="maintainability",
                impact="medium",
                created_at=datetime.now()
            ))
            
        # Check function length
        for func in structure["functions"]:
            if func["complexity"] > 5:
                suggestions.append(CodeSuggestion(
                    type="refactoring",
                    description=f"Function '{func['name']}' has high complexity. Consider refactoring.",
                    code="",
                    location={"type": "function", "name": func["name"]},
                    priority=2,
                    category="maintainability",
                    impact="low",
                    created_at=datetime.now()
                ))
                
        # Check for anti-patterns
        for anti_pattern in patterns["anti_patterns"]:
            suggestions.append(CodeSuggestion(
                type="anti_pattern",
                description=f"Anti-pattern detected: {anti_pattern['name']}",
                code=anti_pattern["example"],
                location=anti_pattern["location"],
                priority=4,
                category="best_practices",
                impact="high",
                created_at=datetime.now()
            ))
            
        return suggestions
        
    def _prioritize_suggestions(
        self,
        suggestions: List[CodeSuggestion],
        context: Dict[str, Any]
    ) -> List[CodeSuggestion]:
        """Prioritize suggestions based on context"""
        # Sort by priority and impact
        prioritized = sorted(
            suggestions,
            key=lambda x: (x.priority, self._get_impact_score(x.impact)),
            reverse=True
        )
        
        # Filter based on context
        if "focus" in context:
            prioritized = [
                s for s in prioritized
                if context["focus"] in s.category
            ]
            
        return prioritized
        
    def _get_impact_score(self, impact: str) -> int:
        """Convert impact string to score"""
        impact_scores = {
            "high": 3,
            "medium": 2,
            "low": 1
        }
        return impact_scores.get(impact.lower(), 0)
        
    def _parse_llm_suggestions(self, response: str) -> List[CodeSuggestion]:
        """Parse LLM response into CodeSuggestion objects"""
        suggestions = []
        
        try:
            # Parse response into structured data
            data = json.loads(response)
            
            for item in data:
                suggestion = CodeSuggestion(
                    type=item["type"],
                    description=item["description"],
                    code=item["code"],
                    location=item["location"],
                    priority=item["priority"],
                    category=item["category"],
                    impact=item["impact"],
                    created_at=datetime.now()
                )
                suggestions.append(suggestion)
                
        except Exception as e:
            logger.error(f"Error parsing LLM suggestions: {e}")
            
        return suggestions 