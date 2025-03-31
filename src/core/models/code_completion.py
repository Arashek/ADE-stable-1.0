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
class CompletionContext:
    file_path: str
    content: str
    cursor_position: int
    line_number: int
    column: int
    current_line: str
    current_word: str
    current_function: Optional[str]
    current_class: Optional[str]
    imports: List[str]
    variables: List[str]
    functions: List[str]
    classes: List[str]
    recent_changes: List[Dict[str, Any]]
    coding_patterns: Dict[str, Any]

@dataclass
class CodeCompletion:
    text: str
    description: str
    confidence: float
    type: str  # function, block, snippet, etc.
    context: Dict[str, Any]
    metadata: Dict[str, Any] = None

class SmartCodeCompletion:
    def __init__(self, llm_config: LLMConfig, context_manager: CodeContextManager):
        self.llm = LLMIntegration(llm_config)
        self.context_manager = context_manager
        self.completion_patterns: Dict[str, List[Dict[str, Any]]] = self._load_patterns()
        self.recent_completions: Dict[str, List[CodeCompletion]] = defaultdict(list)
        
    def _load_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load code completion patterns from configuration"""
        patterns = defaultdict(list)
        try:
            pattern_file = Path("config/completion_patterns.json")
            if pattern_file.exists():
                with open(pattern_file) as f:
                    data = json.load(f)
                    for pattern_type, pattern_list in data.items():
                        patterns[pattern_type] = pattern_list
        except Exception as e:
            logger.error(f"Failed to load completion patterns: {e}")
        return patterns
        
    async def get_completions(self, context: CompletionContext) -> List[CodeCompletion]:
        """Get code completions based on current context"""
        try:
            completions = []
            
            # Get completions from patterns
            pattern_completions = self._get_pattern_completions(context)
            completions.extend(pattern_completions)
            
            # Get completions from LLM
            llm_completions = await self._get_llm_completions(context)
            completions.extend(llm_completions)
            
            # Get completions from recent changes
            recent_completions = self._get_recent_completions(context)
            completions.extend(recent_completions)
            
            # Filter and sort completions
            filtered_completions = self._filter_completions(completions)
            sorted_completions = self._sort_completions(filtered_completions)
            
            # Store recent completions
            self._store_recent_completions(context.file_path, sorted_completions)
            
            return sorted_completions
            
        except Exception as e:
            logger.error(f"Failed to get completions: {e}")
            return []
            
    def _get_pattern_completions(self, context: CompletionContext) -> List[CodeCompletion]:
        """Get completions based on predefined patterns"""
        completions = []
        
        try:
            # Check for function completion patterns
            if context.current_word and context.current_word.endswith("("):
                function_patterns = self.completion_patterns.get("function", [])
                for pattern in function_patterns:
                    if self._matches_pattern(context, pattern):
                        completion = CodeCompletion(
                            text=pattern["completion"],
                            description=pattern["description"],
                            confidence=pattern.get("confidence", 0.8),
                            type="function",
                            context={"pattern": pattern["name"]},
                            metadata=pattern.get("metadata", {})
                        )
                        completions.append(completion)
                        
            # Check for block completion patterns
            block_patterns = self.completion_patterns.get("block", [])
            for pattern in block_patterns:
                if self._matches_pattern(context, pattern):
                    completion = CodeCompletion(
                        text=pattern["completion"],
                        description=pattern["description"],
                        confidence=pattern.get("confidence", 0.8),
                        type="block",
                        context={"pattern": pattern["name"]},
                        metadata=pattern.get("metadata", {})
                    )
                    completions.append(completion)
                    
        except Exception as e:
            logger.error(f"Failed to get pattern completions: {e}")
            
        return completions
        
    async def _get_llm_completions(self, context: CompletionContext) -> List[CodeCompletion]:
        """Get completions using LLM"""
        completions = []
        
        try:
            # Prepare prompt for LLM
            prompt = self._prepare_llm_prompt(context)
            
            # Get completion from LLM
            response = await self.llm.generate_code(prompt)
            
            if response:
                # Parse LLM response into completions
                parsed_completions = self._parse_llm_response(response, context)
                completions.extend(parsed_completions)
                
        except Exception as e:
            logger.error(f"Failed to get LLM completions: {e}")
            
        return completions
        
    def _get_recent_completions(self, context: CompletionContext) -> List[CodeCompletion]:
        """Get completions based on recent changes"""
        completions = []
        
        try:
            # Get recent completions for this file
            recent = self.recent_completions.get(context.file_path, [])
            
            # Filter recent completions based on context
            for completion in recent:
                if self._is_relevant_completion(completion, context):
                    completions.append(completion)
                    
        except Exception as e:
            logger.error(f"Failed to get recent completions: {e}")
            
        return completions
        
    def _filter_completions(self, completions: List[CodeCompletion]) -> List[CodeCompletion]:
        """Filter out duplicate or low-quality completions"""
        filtered = []
        seen = set()
        
        for completion in completions:
            # Create unique key for completion
            key = f"{completion.type}_{completion.text}"
            
            # Skip if we've seen this completion before
            if key in seen:
                continue
                
            # Skip low confidence completions
            if completion.confidence < 0.6:
                continue
                
            seen.add(key)
            filtered.append(completion)
            
        return filtered
        
    def _sort_completions(self, completions: List[CodeCompletion]) -> List[CodeCompletion]:
        """Sort completions by relevance and confidence"""
        def get_completion_score(completion: CodeCompletion) -> float:
            score = completion.confidence
            
            # Adjust score based on type
            type_weights = {
                "function": 1.2,
                "block": 1.1,
                "snippet": 1.0
            }
            score *= type_weights.get(completion.type, 1.0)
            
            # Adjust score based on context relevance
            if completion.context.get("pattern"):
                score *= 1.1
                
            return score
            
        return sorted(completions, key=get_completion_score, reverse=True)
        
    def _store_recent_completions(self, file_path: str, completions: List[CodeCompletion]):
        """Store recent completions for future reference"""
        try:
            # Keep only the most recent 10 completions
            self.recent_completions[file_path] = completions[:10]
        except Exception as e:
            logger.error(f"Failed to store recent completions: {e}")
            
    def _matches_pattern(self, context: CompletionContext, pattern: Dict[str, Any]) -> bool:
        """Check if context matches a pattern"""
        try:
            if "regex" in pattern:
                import re
                return bool(re.search(pattern["regex"], context.current_line))
            elif "keywords" in pattern:
                return all(keyword in context.current_line for keyword in pattern["keywords"])
            return False
        except Exception as e:
            logger.error(f"Failed to match pattern: {e}")
            return False
            
    def _prepare_llm_prompt(self, context: CompletionContext) -> str:
        """Prepare prompt for LLM"""
        prompt = f"""Complete the code at position {context.cursor_position} in file {context.file_path}.
Current line: {context.current_line}
Current word: {context.current_word}
Current function: {context.current_function}
Current class: {context.current_class}

Available imports: {', '.join(context.imports)}
Available variables: {', '.join(context.variables)}
Available functions: {', '.join(context.functions)}
Available classes: {', '.join(context.classes)}

Recent changes:
{json.dumps(context.recent_changes, indent=2)}

Coding patterns:
{json.dumps(context.coding_patterns, indent=2)}

Please provide appropriate code completion suggestions."""
        return prompt
        
    def _parse_llm_response(self, response: Dict[str, Any], context: CompletionContext) -> List[CodeCompletion]:
        """Parse LLM response into completions"""
        completions = []
        
        try:
            if "completions" in response:
                for completion_data in response["completions"]:
                    completion = CodeCompletion(
                        text=completion_data["text"],
                        description=completion_data.get("description", ""),
                        confidence=completion_data.get("confidence", 0.8),
                        type=completion_data.get("type", "snippet"),
                        context={"source": "llm"},
                        metadata=completion_data.get("metadata", {})
                    )
                    completions.append(completion)
                    
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            
        return completions
        
    def _is_relevant_completion(self, completion: CodeCompletion, context: CompletionContext) -> bool:
        """Check if a completion is relevant to the current context"""
        try:
            # Check if completion matches current word
            if context.current_word and context.current_word in completion.text:
                return True
                
            # Check if completion matches current function/class
            if context.current_function and context.current_function in completion.text:
                return True
            if context.current_class and context.current_class in completion.text:
                return True
                
            # Check if completion uses available variables/functions
            if any(var in completion.text for var in context.variables):
                return True
            if any(func in completion.text for func in context.functions):
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Failed to check completion relevance: {e}")
            return False 