from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import numpy as np
from collections import defaultdict

from .llm_integration import LLMIntegration, LLMConfig
from .code_context_manager import CodeContextManager

logger = logging.getLogger(__name__)

@dataclass
class RefactoringSuggestion:
    type: str  # optimization, simplification, maintainability, etc.
    file_path: str
    line_numbers: List[int]
    description: str
    suggestion: str
    impact: str
    effort: str
    confidence: float
    context: Dict[str, Any]
    created_at: datetime = datetime.now()
    metadata: Dict[str, Any] = None

class CodeRefactoring:
    def __init__(self, llm_config: LLMConfig, context_manager: CodeContextManager):
        self.llm = LLMIntegration(llm_config)
        self.context_manager = context_manager
        self.refactoring_patterns: Dict[str, List[Dict[str, Any]]] = self._load_patterns()
        self.recent_suggestions: Dict[str, List[RefactoringSuggestion]] = defaultdict(list)
        
    def _load_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load refactoring patterns from configuration"""
        patterns = defaultdict(list)
        try:
            pattern_file = Path("config/refactoring_patterns.json")
            if pattern_file.exists():
                with open(pattern_file) as f:
                    data = json.load(f)
                    for pattern_type, pattern_list in data.items():
                        patterns[pattern_type] = pattern_list
        except Exception as e:
            logger.error(f"Failed to load refactoring patterns: {e}")
        return patterns
        
    async def analyze_code(self, file_path: str, content: str) -> List[RefactoringSuggestion]:
        """Analyze code and generate refactoring suggestions"""
        try:
            # Update code context
            await self.context_manager.update_context(file_path, content)
            
            # Get code context
            context = await self.context_manager.get_code_context(file_path)
            if not context:
                return []
                
            suggestions = []
            
            # Generate suggestions from patterns
            pattern_suggestions = self._get_pattern_suggestions(content, context)
            suggestions.extend(pattern_suggestions)
            
            # Generate suggestions from LLM
            llm_suggestions = await self._get_llm_suggestions(content, context)
            suggestions.extend(llm_suggestions)
            
            # Filter and sort suggestions
            filtered_suggestions = self._filter_suggestions(suggestions)
            sorted_suggestions = self._sort_suggestions(filtered_suggestions)
            
            # Store recent suggestions
            self._store_recent_suggestions(file_path, sorted_suggestions)
            
            return sorted_suggestions
            
        except Exception as e:
            logger.error(f"Failed to analyze code: {e}")
            return []
            
    def _get_pattern_suggestions(self, content: str, context: Any) -> List[RefactoringSuggestion]:
        """Get refactoring suggestions based on patterns"""
        suggestions = []
        
        try:
            for pattern_type, patterns in self.refactoring_patterns.items():
                for pattern in patterns:
                    if self._matches_pattern(content, pattern):
                        suggestion = RefactoringSuggestion(
                            type=pattern_type,
                            file_path=context.file_path,
                            line_numbers=self._find_line_numbers(content, pattern),
                            description=pattern["description"],
                            suggestion=pattern["suggestion"],
                            impact=pattern.get("impact", "medium"),
                            effort=pattern.get("effort", "medium"),
                            confidence=pattern.get("confidence", 0.8),
                            context={"pattern": pattern["name"]},
                            metadata=pattern.get("metadata", {})
                        )
                        suggestions.append(suggestion)
                        
        except Exception as e:
            logger.error(f"Failed to get pattern suggestions: {e}")
            
        return suggestions
        
    async def _get_llm_suggestions(self, content: str, context: Any) -> List[RefactoringSuggestion]:
        """Get refactoring suggestions using LLM"""
        suggestions = []
        
        try:
            # Prepare prompt for LLM
            prompt = self._prepare_llm_prompt(content, context)
            
            # Get suggestions from LLM
            response = await self.llm.analyze_code(content, "refactoring")
            
            if response:
                # Parse LLM response into suggestions
                parsed_suggestions = self._parse_llm_response(response, context)
                suggestions.extend(parsed_suggestions)
                
        except Exception as e:
            logger.error(f"Failed to get LLM suggestions: {e}")
            
        return suggestions
        
    def _filter_suggestions(self, suggestions: List[RefactoringSuggestion]) -> List[RefactoringSuggestion]:
        """Filter out duplicate or low-quality suggestions"""
        filtered = []
        seen = set()
        
        for suggestion in suggestions:
            # Create unique key for suggestion
            key = f"{suggestion.type}_{suggestion.file_path}_{suggestion.line_numbers}_{suggestion.description}"
            
            # Skip if we've seen this suggestion before
            if key in seen:
                continue
                
            # Skip low confidence suggestions
            if suggestion.confidence < 0.6:
                continue
                
            seen.add(key)
            filtered.append(suggestion)
            
        return filtered
        
    def _sort_suggestions(self, suggestions: List[RefactoringSuggestion]) -> List[RefactoringSuggestion]:
        """Sort suggestions by impact and effort"""
        def get_suggestion_score(suggestion: RefactoringSuggestion) -> float:
            score = suggestion.confidence
            
            # Adjust score based on type
            type_weights = {
                "optimization": 1.3,
                "simplification": 1.2,
                "maintainability": 1.1,
                "readability": 1.0
            }
            score *= type_weights.get(suggestion.type, 1.0)
            
            # Adjust score based on impact
            impact_weights = {
                "high": 1.5,
                "medium": 1.0,
                "low": 0.5
            }
            score *= impact_weights.get(suggestion.impact.lower(), 1.0)
            
            # Adjust score based on effort (inverse)
            effort_weights = {
                "high": 0.5,
                "medium": 1.0,
                "low": 1.5
            }
            score *= effort_weights.get(suggestion.effort.lower(), 1.0)
            
            return score
            
        return sorted(suggestions, key=get_suggestion_score, reverse=True)
        
    def _store_recent_suggestions(self, file_path: str, suggestions: List[RefactoringSuggestion]):
        """Store recent suggestions for future reference"""
        try:
            # Keep only the most recent 10 suggestions
            self.recent_suggestions[file_path] = suggestions[:10]
        except Exception as e:
            logger.error(f"Failed to store recent suggestions: {e}")
            
    def _matches_pattern(self, content: str, pattern: Dict[str, Any]) -> bool:
        """Check if content matches a pattern"""
        try:
            if "regex" in pattern:
                import re
                return bool(re.search(pattern["regex"], content))
            elif "keywords" in pattern:
                return all(keyword in content for keyword in pattern["keywords"])
            return False
        except Exception as e:
            logger.error(f"Failed to match pattern: {e}")
            return False
            
    def _find_line_numbers(self, content: str, pattern: Dict[str, Any]) -> List[int]:
        """Find line numbers where pattern matches"""
        line_numbers = []
        
        try:
            if "regex" in pattern:
                import re
                for match in re.finditer(pattern["regex"], content):
                    line_number = content[:match.start()].count("\n") + 1
                    line_numbers.append(line_number)
            return line_numbers
        except Exception as e:
            logger.error(f"Failed to find line numbers: {e}")
            return []
            
    def _prepare_llm_prompt(self, content: str, context: Any) -> str:
        """Prepare prompt for LLM"""
        prompt = f"""Analyze the following code for potential refactoring opportunities:

File: {context.file_path}
Content:
{content}

Consider:
1. Code optimization opportunities
2. Simplification possibilities
3. Maintainability improvements
4. Readability enhancements
5. Performance bottlenecks
6. Code duplication
7. Complex logic that could be simplified
8. Design patterns that could be applied
9. Error handling improvements
10. Documentation needs

Please provide specific suggestions with line numbers and explanations."""
        return prompt
        
    def _parse_llm_response(self, response: Dict[str, Any], context: Any) -> List[RefactoringSuggestion]:
        """Parse LLM response into suggestions"""
        suggestions = []
        
        try:
            if "suggestions" in response:
                for suggestion_data in response["suggestions"]:
                    suggestion = RefactoringSuggestion(
                        type=suggestion_data.get("type", "general"),
                        file_path=context.file_path,
                        line_numbers=suggestion_data.get("line_numbers", []),
                        description=suggestion_data.get("description", ""),
                        suggestion=suggestion_data.get("suggestion", ""),
                        impact=suggestion_data.get("impact", "medium"),
                        effort=suggestion_data.get("effort", "medium"),
                        confidence=suggestion_data.get("confidence", 0.8),
                        context={"source": "llm"},
                        metadata=suggestion_data.get("metadata", {})
                    )
                    suggestions.append(suggestion)
                    
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            
        return suggestions 