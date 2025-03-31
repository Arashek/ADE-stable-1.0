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
class BugReport:
    type: str  # security, runtime, logic, etc.
    severity: str  # critical, high, medium, low
    file_path: str
    line_numbers: List[int]
    description: str
    impact: str
    suggestion: str
    confidence: float
    context: Dict[str, Any]
    created_at: datetime = datetime.now()
    metadata: Dict[str, Any] = None

class BugDetection:
    def __init__(self, llm_config: LLMConfig, context_manager: CodeContextManager):
        self.llm = LLMIntegration(llm_config)
        self.context_manager = context_manager
        self.bug_patterns: Dict[str, List[Dict[str, Any]]] = self._load_patterns()
        self.recent_bugs: Dict[str, List[BugReport]] = defaultdict(list)
        
    def _load_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load bug detection patterns from configuration"""
        patterns = defaultdict(list)
        try:
            pattern_file = Path("config/bug_patterns.json")
            if pattern_file.exists():
                with open(pattern_file) as f:
                    data = json.load(f)
                    for pattern_type, pattern_list in data.items():
                        patterns[pattern_type] = pattern_list
        except Exception as e:
            logger.error(f"Failed to load bug patterns: {e}")
        return patterns
        
    async def analyze_code(self, file_path: str, content: str) -> List[BugReport]:
        """Analyze code and detect potential bugs"""
        try:
            # Update code context
            await self.context_manager.update_context(file_path, content)
            
            # Get code context
            context = await self.context_manager.get_code_context(file_path)
            if not context:
                return []
                
            bugs = []
            
            # Detect bugs from patterns
            pattern_bugs = self._detect_pattern_bugs(content, context)
            bugs.extend(pattern_bugs)
            
            # Detect bugs using LLM
            llm_bugs = await self._detect_llm_bugs(content, context)
            bugs.extend(llm_bugs)
            
            # Filter and sort bugs
            filtered_bugs = self._filter_bugs(bugs)
            sorted_bugs = self._sort_bugs(filtered_bugs)
            
            # Store recent bugs
            self._store_recent_bugs(file_path, sorted_bugs)
            
            return sorted_bugs
            
        except Exception as e:
            logger.error(f"Failed to analyze code: {e}")
            return []
            
    def _detect_pattern_bugs(self, content: str, context: Any) -> List[BugReport]:
        """Detect bugs based on patterns"""
        bugs = []
        
        try:
            for pattern_type, patterns in self.bug_patterns.items():
                for pattern in patterns:
                    if self._matches_pattern(content, pattern):
                        bug = BugReport(
                            type=pattern_type,
                            severity=pattern.get("severity", "medium"),
                            file_path=context.file_path,
                            line_numbers=self._find_line_numbers(content, pattern),
                            description=pattern["description"],
                            impact=pattern.get("impact", "medium"),
                            suggestion=pattern["suggestion"],
                            confidence=pattern.get("confidence", 0.8),
                            context={"pattern": pattern["name"]},
                            metadata=pattern.get("metadata", {})
                        )
                        bugs.append(bug)
                        
        except Exception as e:
            logger.error(f"Failed to detect pattern bugs: {e}")
            
        return bugs
        
    async def _detect_llm_bugs(self, content: str, context: Any) -> List[BugReport]:
        """Detect bugs using LLM"""
        bugs = []
        
        try:
            # Prepare prompt for LLM
            prompt = self._prepare_llm_prompt(content, context)
            
            # Get bug detection from LLM
            response = await self.llm.analyze_code(content, "bug_detection")
            
            if response:
                # Parse LLM response into bugs
                parsed_bugs = self._parse_llm_response(response, context)
                bugs.extend(parsed_bugs)
                
        except Exception as e:
            logger.error(f"Failed to detect LLM bugs: {e}")
            
        return bugs
        
    def _filter_bugs(self, bugs: List[BugReport]) -> List[BugReport]:
        """Filter out duplicate or low-confidence bugs"""
        filtered = []
        seen = set()
        
        for bug in bugs:
            # Create unique key for bug
            key = f"{bug.type}_{bug.file_path}_{bug.line_numbers}_{bug.description}"
            
            # Skip if we've seen this bug before
            if key in seen:
                continue
                
            # Skip low confidence bugs
            if bug.confidence < 0.6:
                continue
                
            seen.add(key)
            filtered.append(bug)
            
        return filtered
        
    def _sort_bugs(self, bugs: List[BugReport]) -> List[BugReport]:
        """Sort bugs by severity and impact"""
        def get_bug_score(bug: BugReport) -> float:
            score = bug.confidence
            
            # Adjust score based on type
            type_weights = {
                "security": 2.0,
                "runtime": 1.5,
                "logic": 1.3,
                "performance": 1.2,
                "resource": 1.4
            }
            score *= type_weights.get(bug.type, 1.0)
            
            # Adjust score based on severity
            severity_weights = {
                "critical": 2.0,
                "high": 1.5,
                "medium": 1.0,
                "low": 0.5
            }
            score *= severity_weights.get(bug.severity.lower(), 1.0)
            
            # Adjust score based on impact
            impact_weights = {
                "critical": 1.5,
                "high": 1.2,
                "medium": 1.0,
                "low": 0.8
            }
            score *= impact_weights.get(bug.impact.lower(), 1.0)
            
            return score
            
        return sorted(bugs, key=get_bug_score, reverse=True)
        
    def _store_recent_bugs(self, file_path: str, bugs: List[BugReport]):
        """Store recent bugs for future reference"""
        try:
            # Keep only the most recent 10 bugs
            self.recent_bugs[file_path] = bugs[:10]
        except Exception as e:
            logger.error(f"Failed to store recent bugs: {e}")
            
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
        prompt = f"""Analyze the following code for potential bugs and vulnerabilities:

File: {context.file_path}
Content:
{content}

Consider:
1. Security vulnerabilities
2. Runtime errors
3. Logic bugs
4. Performance issues
5. Resource leaks
6. Race conditions
7. Memory issues
8. Input validation
9. Error handling
10. Edge cases

Please provide specific bug reports with line numbers and explanations."""
        return prompt
        
    def _parse_llm_response(self, response: Dict[str, Any], context: Any) -> List[BugReport]:
        """Parse LLM response into bugs"""
        bugs = []
        
        try:
            if "bugs" in response:
                for bug_data in response["bugs"]:
                    bug = BugReport(
                        type=bug_data.get("type", "general"),
                        severity=bug_data.get("severity", "medium"),
                        file_path=context.file_path,
                        line_numbers=bug_data.get("line_numbers", []),
                        description=bug_data.get("description", ""),
                        impact=bug_data.get("impact", "medium"),
                        suggestion=bug_data.get("suggestion", ""),
                        confidence=bug_data.get("confidence", 0.8),
                        context={"source": "llm"},
                        metadata=bug_data.get("metadata", {})
                    )
                    bugs.append(bug)
                    
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            
        return bugs 