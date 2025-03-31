from typing import Dict, Any, List, Optional
import difflib
import ast
import re
from ...config.logging_config import logger

class RewardSystem:
    """Sophisticated reward system for code completion"""
    
    def __init__(self):
        self.reward_weights = {
            'exact_match': 1.0,
            'partial_match': 0.5,
            'syntax_correct': 0.3,
            'type_correct': 0.2,
            'context_relevant': 0.2,
            'length_appropriate': 0.1,
            'style_consistent': 0.1
        }
        
    def calculate_reward(self, action: str, actual_completion: str, context: Dict[str, Any]) -> float:
        """Calculate comprehensive reward for an action"""
        try:
            rewards = {
                'exact_match': self._reward_exact_match(action, actual_completion),
                'partial_match': self._reward_partial_match(action, actual_completion),
                'syntax_correct': self._reward_syntax_correct(action, context),
                'type_correct': self._reward_type_correct(action, context),
                'context_relevant': self._reward_context_relevant(action, context),
                'length_appropriate': self._reward_length_appropriate(action, actual_completion),
                'style_consistent': self._reward_style_consistent(action, context)
            }
            
            # Calculate weighted sum
            total_reward = sum(
                reward * self.reward_weights[metric]
                for metric, reward in rewards.items()
            )
            
            return total_reward
            
        except Exception as e:
            logger.error(f"Error calculating reward: {str(e)}")
            return 0.0
            
    def _reward_exact_match(self, action: str, actual_completion: str) -> float:
        """Reward for exact match"""
        return 1.0 if action == actual_completion else 0.0
        
    def _reward_partial_match(self, action: str, actual_completion: str) -> float:
        """Reward for partial match using string similarity"""
        matcher = difflib.SequenceMatcher(None, action, actual_completion)
        return matcher.ratio()
        
    def _reward_syntax_correct(self, action: str, context: Dict[str, Any]) -> float:
        """Reward for syntactically correct completion"""
        try:
            # Try to parse the completion in context
            code = context['context'] + action
            ast.parse(code)
            return 1.0
        except SyntaxError:
            return 0.0
            
    def _reward_type_correct(self, action: str, context: Dict[str, Any]) -> float:
        """Reward for type-correct completion"""
        try:
            # Get type information from context
            types = context.get('metadata', {}).get('types', {})
            
            # Check if completion matches expected type
            if 'expected_type' in types:
                return 1.0 if self._check_type_match(action, types['expected_type']) else 0.0
                
            return 0.5  # Neutral reward if type info not available
            
        except Exception:
            return 0.0
            
    def _reward_context_relevant(self, action: str, context: Dict[str, Any]) -> float:
        """Reward for contextually relevant completion"""
        try:
            # Get relevant terms from context
            context_text = context['context']
            relevant_terms = self._extract_relevant_terms(context_text)
            
            # Check if completion contains relevant terms
            matches = sum(1 for term in relevant_terms if term in action)
            return matches / len(relevant_terms) if relevant_terms else 0.5
            
        except Exception:
            return 0.0
            
    def _reward_length_appropriate(self, action: str, actual_completion: str) -> float:
        """Reward for appropriate completion length"""
        try:
            # Calculate length ratio
            ratio = len(action) / len(actual_completion) if actual_completion else 0
            
            # Reward for reasonable length ratio (0.5 to 2.0)
            if 0.5 <= ratio <= 2.0:
                return 1.0 - abs(1.0 - ratio)  # Higher reward for closer to 1.0
            return 0.0
            
        except Exception:
            return 0.0
            
    def _reward_style_consistent(self, action: str, context: Dict[str, Any]) -> float:
        """Reward for style consistency"""
        try:
            # Get style patterns from context
            context_text = context['context']
            style_patterns = self._extract_style_patterns(context_text)
            
            # Check if completion follows style patterns
            matches = sum(1 for pattern in style_patterns if pattern in action)
            return matches / len(style_patterns) if style_patterns else 0.5
            
        except Exception:
            return 0.0
            
    def _extract_relevant_terms(self, context: str) -> List[str]:
        """Extract relevant terms from context"""
        try:
            # Parse context
            tree = ast.parse(context)
            
            # Extract variable names, function names, and types
            terms = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    terms.append(node.id)
                elif isinstance(node, ast.FunctionDef):
                    terms.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    terms.append(node.name)
                    
            return list(set(terms))  # Remove duplicates
            
        except Exception:
            return []
            
    def _extract_style_patterns(self, context: str) -> List[str]:
        """Extract coding style patterns from context"""
        try:
            patterns = []
            
            # Check indentation style
            lines = context.split('\n')
            if lines:
                indentation = re.match(r'^\s*', lines[0]).group()
                patterns.append(indentation)
                
            # Check naming conventions
            for line in lines:
                # Variable naming
                var_matches = re.findall(r'\b[a-z_][a-z0-9_]*\b', line)
                patterns.extend(var_matches)
                
                # Function naming
                func_matches = re.findall(r'\bdef\s+([a-z_][a-z0-9_]*)\b', line)
                patterns.extend(func_matches)
                
            return list(set(patterns))  # Remove duplicates
            
        except Exception:
            return []
            
    def _check_type_match(self, action: str, expected_type: str) -> bool:
        """Check if completion matches expected type"""
        try:
            # Simple type checking
            type_patterns = {
                'int': r'^\d+$',
                'float': r'^\d*\.\d+$',
                'str': r'^[\'"].*[\'"]$',
                'bool': r'^(True|False)$',
                'list': r'^\[.*\]$',
                'dict': r'^\{.*\}$',
                'set': r'^\{.*\}$',
                'tuple': r'^\(.*\)$'
            }
            
            if expected_type in type_patterns:
                return bool(re.match(type_patterns[expected_type], action))
                
            return True  # Default to True for complex types
            
        except Exception:
            return False 