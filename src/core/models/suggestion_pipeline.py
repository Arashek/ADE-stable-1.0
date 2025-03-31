from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import os
from pathlib import Path
import numpy as np
from collections import defaultdict

from .llm_integration import LLMIntegration, LLMConfig, LLMProvider
from .code_context_manager import CodeContextManager
from .solution_generator import MultiSolutionGenerator
from .context_aware_fix import ContextAwareFixSystem
from .safe_code_modifier import SafeCodeModifier

logger = logging.getLogger(__name__)

class SuggestionType(Enum):
    CODE_QUALITY = "code_quality"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"
    TESTABILITY = "testability"
    DOCUMENTATION = "documentation"
    ARCHITECTURE = "architecture"
    BEST_PRACTICES = "best_practices"
    ACCESSIBILITY = "accessibility"
    INTERNATIONALIZATION = "internationalization"
    ERROR_HANDLING = "error_handling"
    API_DESIGN = "api_design"
    DATABASE = "database"
    CACHING = "caching"
    LOGGING = "logging"
    TESTING = "testing"

class SuggestionPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class CodeSuggestion:
    type: SuggestionType
    priority: SuggestionPriority
    file_path: str
    line_number: Optional[int]
    description: str
    suggestion: str
    impact: str
    effort: str
    confidence: float
    context: Dict[str, Any]
    created_at: datetime = datetime.now()
    metadata: Dict[str, Any] = None

@dataclass
class PatternCondition:
    type: str  # regex, keyword, ast, complexity, dependency, etc.
    value: Any  # The actual condition value
    description: str
    weight: float = 1.0

@dataclass
class CustomPattern:
    name: str
    description: str
    type: SuggestionType
    conditions: List[PatternCondition]
    suggestion: str
    priority: SuggestionPriority
    impact: str
    effort: str
    confidence: float
    metadata: Dict[str, Any] = None

class SuggestionPipeline:
    def __init__(self, llm_config: LLMConfig, context_manager: CodeContextManager):
        self.llm = LLMIntegration(llm_config)
        self.context_manager = context_manager
        self.suggestions: Dict[str, List[CodeSuggestion]] = {}
        self.patterns: Dict[SuggestionType, List[Dict[str, Any]]] = defaultdict(list)
        
        # Initialize new components
        self.solution_generator = MultiSolutionGenerator(context_manager.project_dir)
        self.context_aware_fix = ContextAwareFixSystem(context_manager.project_dir)
        self.safe_code_modifier = SafeCodeModifier(context_manager.project_dir)
        
    def _load_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load suggestion patterns from configuration"""
        patterns = defaultdict(list)
        try:
            pattern_file = Path("config/suggestion_patterns.json")
            if pattern_file.exists():
                with open(pattern_file) as f:
                    data = json.load(f)
                    for pattern_type, pattern_list in data.items():
                        patterns[SuggestionType(pattern_type)] = pattern_list
        except Exception as e:
            logger.error(f"Failed to load suggestion patterns: {e}")
        return patterns
        
    def add_custom_pattern(self, pattern: CustomPattern) -> bool:
        """Add a custom pattern to the pipeline"""
        try:
            self.custom_patterns[pattern.name] = pattern
            logger.info(f"Added custom pattern: {pattern.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add custom pattern: {e}")
            return False
            
    def remove_custom_pattern(self, pattern_name: str) -> bool:
        """Remove a custom pattern from the pipeline"""
        try:
            if pattern_name in self.custom_patterns:
                del self.custom_patterns[pattern_name]
                logger.info(f"Removed custom pattern: {pattern_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove custom pattern: {e}")
            return False
            
    def update_custom_pattern(self, pattern: CustomPattern) -> bool:
        """Update an existing custom pattern"""
        try:
            if pattern.name in self.custom_patterns:
                self.custom_patterns[pattern.name] = pattern
                logger.info(f"Updated custom pattern: {pattern.name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update custom pattern: {e}")
            return False
            
    def get_custom_patterns(self) -> List[CustomPattern]:
        """Get all custom patterns"""
        return list(self.custom_patterns.values())
        
    def _matches_custom_pattern(self, content: str, context: Any, pattern: CustomPattern) -> bool:
        """Check if content matches a custom pattern's conditions"""
        try:
            total_weight = 0
            matched_weight = 0
            
            for condition in pattern.conditions:
                total_weight += condition.weight
                
                if condition.type == "regex":
                    import re
                    if re.search(condition.value, content):
                        matched_weight += condition.weight
                elif condition.type == "keyword":
                    if all(keyword in content for keyword in condition.value):
                        matched_weight += condition.weight
                elif condition.type == "ast":
                    # Use tree-sitter or similar for AST-based matching
                    if self._matches_ast_condition(content, condition.value):
                        matched_weight += condition.weight
                elif condition.type == "complexity":
                    if self._matches_complexity_condition(content, condition.value):
                        matched_weight += condition.weight
                elif condition.type == "dependency":
                    if self._matches_dependency_condition(context, condition.value):
                        matched_weight += condition.weight
                        
            # Pattern matches if weighted conditions are met
            return matched_weight / total_weight >= 0.7
            
        except Exception as e:
            logger.error(f"Failed to match custom pattern: {e}")
            return False
            
    def _matches_ast_condition(self, content: str, condition: Dict[str, Any]) -> bool:
        """Check if content matches AST-based condition"""
        # Implementation would use tree-sitter or similar
        return False
        
    def _matches_complexity_condition(self, content: str, condition: Dict[str, Any]) -> bool:
        """Check if content matches complexity-based condition"""
        try:
            if "max_cyclomatic" in condition:
                complexity = self._calculate_cyclomatic_complexity(content)
                return complexity > condition["max_cyclomatic"]
            return False
        except Exception as e:
            logger.error(f"Failed to match complexity condition: {e}")
            return False
            
    def _matches_dependency_condition(self, context: Any, condition: Dict[str, Any]) -> bool:
        """Check if content matches dependency-based condition"""
        try:
            if "max_dependencies" in condition:
                return len(context.dependencies) > condition["max_dependencies"]
            return False
        except Exception as e:
            logger.error(f"Failed to match dependency condition: {e}")
            return False
            
    def _calculate_cyclomatic_complexity(self, content: str) -> int:
        """Calculate cyclomatic complexity of code"""
        complexity = 1  # Base complexity
        
        # Count control structures
        control_structures = [
            "if", "elif", "else", "for", "while", "except", "finally",
            "and", "or", "not", "&&", "||", "!", "?", ":"
        ]
        
        for structure in control_structures:
            complexity += content.count(structure)
            
        return complexity
        
    async def analyze_code(self, file_path: str, content: str) -> List[CodeSuggestion]:
        """Analyze code and generate suggestions using enhanced systems"""
        try:
            # Update code context
            await self.context_manager.update_context(file_path, content)
            
            # Get code context
            context = await self.context_manager.get_code_context(file_path)
            if not context:
                return []
                
            suggestions = []
            
            # Generate suggestions using LLM
            llm_suggestions = await self._generate_llm_suggestions(content, context)
            suggestions.extend(llm_suggestions)
            
            # Generate suggestions using predefined patterns
            pattern_suggestions = self._generate_pattern_suggestions(content, context)
            suggestions.extend(pattern_suggestions)
            
            # Generate suggestions using custom patterns
            custom_suggestions = self._generate_custom_pattern_suggestions(content, context)
            suggestions.extend(custom_suggestions)
            
            # Generate suggestions using solution generator
            solution_suggestions = await self._generate_solution_suggestions(content, context)
            suggestions.extend(solution_suggestions)
            
            # Filter and prioritize suggestions
            filtered_suggestions = self._filter_suggestions(suggestions)
            prioritized_suggestions = self._prioritize_suggestions(filtered_suggestions)
            
            # Store suggestions
            self.suggestions[file_path] = prioritized_suggestions
            
            return prioritized_suggestions
            
        except Exception as e:
            logger.error(f"Failed to analyze code: {e}")
            return []
            
    async def _generate_llm_suggestions(self, content: str, context: Any) -> List[CodeSuggestion]:
        """Generate suggestions using LLM"""
        suggestions = []
        
        try:
            # Analyze code quality
            quality_analysis = await self.llm.analyze_code(content, "code_quality")
            if quality_analysis:
                suggestions.extend(self._parse_llm_analysis(quality_analysis, SuggestionType.CODE_QUALITY))
                
            # Analyze performance
            perf_analysis = await self.llm.analyze_code(content, "performance")
            if perf_analysis:
                suggestions.extend(self._parse_llm_analysis(perf_analysis, SuggestionType.PERFORMANCE))
                
            # Analyze security
            security_analysis = await self.llm.analyze_code(content, "security")
            if security_analysis:
                suggestions.extend(self._parse_llm_analysis(security_analysis, SuggestionType.SECURITY))
                
            # Analyze maintainability
            maintainability_analysis = await self.llm.analyze_code(content, "maintainability")
            if maintainability_analysis:
                suggestions.extend(self._parse_llm_analysis(maintainability_analysis, SuggestionType.MAINTAINABILITY))
                
        except Exception as e:
            logger.error(f"Failed to generate LLM suggestions: {e}")
            
        return suggestions
        
    def _parse_llm_analysis(self, analysis: Dict[str, Any], suggestion_type: SuggestionType) -> List[CodeSuggestion]:
        """Parse LLM analysis into suggestions"""
        suggestions = []
        
        try:
            if "analysis" in analysis:
                analysis_text = analysis["analysis"]
                # Parse analysis text into structured suggestions
                # This is a simplified example - you would need more sophisticated parsing
                for line in analysis_text.split("\n"):
                    if line.strip():
                        suggestion = CodeSuggestion(
                            type=suggestion_type,
                            priority=self._determine_priority(line),
                            file_path="",  # Would be set by caller
                            line_number=None,  # Would be determined from context
                            description=line,
                            suggestion=self._generate_suggestion(line),
                            impact=self._determine_impact(line),
                            effort=self._determine_effort(line),
                            confidence=0.8,  # Default confidence
                            context={"source": "llm_analysis"}
                        )
                        suggestions.append(suggestion)
                        
        except Exception as e:
            logger.error(f"Failed to parse LLM analysis: {e}")
            
        return suggestions
        
    def _generate_pattern_suggestions(self, content: str, context: Any) -> List[CodeSuggestion]:
        """Generate suggestions using predefined patterns"""
        suggestions = []
        
        try:
            for pattern_type, patterns in self.patterns.items():
                for pattern in patterns:
                    if self._matches_pattern(content, pattern):
                        suggestion = CodeSuggestion(
                            type=pattern_type,
                            priority=SuggestionPriority(pattern.get("priority", 2)),
                            file_path=context.file_path,
                            line_number=self._find_line_number(content, pattern),
                            description=pattern["description"],
                            suggestion=pattern["suggestion"],
                            impact=pattern.get("impact", "medium"),
                            effort=pattern.get("effort", "medium"),
                            confidence=pattern.get("confidence", 0.8),
                            context={"pattern": pattern["name"]}
                        )
                        suggestions.append(suggestion)
                        
        except Exception as e:
            logger.error(f"Failed to generate pattern suggestions: {e}")
            
        return suggestions
        
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
            
    def _find_line_number(self, content: str, pattern: Dict[str, Any]) -> Optional[int]:
        """Find line number where pattern matches"""
        try:
            if "regex" in pattern:
                import re
                match = re.search(pattern["regex"], content)
                if match:
                    return content[:match.start()].count("\n") + 1
            return None
        except Exception as e:
            logger.error(f"Failed to find line number: {e}")
            return None
            
    def _filter_suggestions(self, suggestions: List[CodeSuggestion]) -> List[CodeSuggestion]:
        """Filter out duplicate or low-quality suggestions"""
        filtered = []
        seen = set()
        
        for suggestion in suggestions:
            # Create unique key for suggestion
            key = f"{suggestion.type}_{suggestion.file_path}_{suggestion.line_number}_{suggestion.description}"
            
            # Skip if we've seen this suggestion before
            if key in seen:
                continue
                
            # Skip low confidence suggestions
            if suggestion.confidence < 0.6:
                continue
                
            seen.add(key)
            filtered.append(suggestion)
            
        return filtered
        
    def _prioritize_suggestions(self, suggestions: List[CodeSuggestion]) -> List[CodeSuggestion]:
        """Prioritize suggestions based on multiple factors"""
        def get_priority_score(suggestion: CodeSuggestion) -> float:
            # Base score from priority enum
            score = suggestion.priority.value
            
            # Adjust based on type with more granular weights
            type_weights = {
                SuggestionType.SECURITY: 1.8,  # Security issues are critical
                SuggestionType.PERFORMANCE: 1.5,  # Performance impacts user experience
                SuggestionType.ERROR_HANDLING: 1.4,  # Error handling is crucial for reliability
                SuggestionType.API_DESIGN: 1.3,  # API design affects system architecture
                SuggestionType.DATABASE: 1.3,  # Database issues can be critical
                SuggestionType.CACHING: 1.2,  # Caching affects performance
                SuggestionType.ARCHITECTURE: 1.4,  # Architecture impacts maintainability
                SuggestionType.CODE_QUALITY: 1.2,  # Code quality affects maintainability
                SuggestionType.MAINTAINABILITY: 1.1,  # Maintainability is important but less urgent
                SuggestionType.TESTING: 1.2,  # Testing is crucial for reliability
                SuggestionType.LOGGING: 1.0,  # Logging is important for debugging
                SuggestionType.DOCUMENTATION: 0.9,  # Documentation is important but less urgent
                SuggestionType.ACCESSIBILITY: 1.3,  # Accessibility is important for user experience
                SuggestionType.INTERNATIONALIZATION: 1.1,  # i18n is important but less urgent
                SuggestionType.BEST_PRACTICES: 1.0,  # Best practices are important but less urgent
                SuggestionType.TESTABILITY: 1.1  # Testability affects maintainability
            }
            score *= type_weights.get(suggestion.type, 1.0)
            
            # Adjust based on impact with more granular weights
            impact_weights = {
                "critical": 2.0,  # Critical issues must be addressed immediately
                "high": 1.5,  # High impact issues should be addressed soon
                "medium": 1.0,  # Medium impact issues can be addressed in normal course
                "low": 0.5  # Low impact issues can be addressed when convenient
            }
            score *= impact_weights.get(suggestion.impact.lower(), 1.0)
            
            # Adjust based on effort (inverse) with more granular weights
            effort_weights = {
                "critical": 0.3,  # Critical effort should be weighted very low
                "high": 0.5,  # High effort should be weighted low
                "medium": 1.0,  # Medium effort is neutral
                "low": 1.5  # Low effort should be weighted high
            }
            score *= effort_weights.get(suggestion.effort.lower(), 1.0)
            
            # Adjust based on confidence
            score *= suggestion.confidence
            
            # Additional factors
            
            # 1. Time sensitivity (if metadata includes time-related info)
            if suggestion.metadata and "time_sensitive" in suggestion.metadata:
                if suggestion.metadata["time_sensitive"]:
                    score *= 1.2
                    
            # 2. Dependencies (if suggestion depends on other changes)
            if suggestion.metadata and "dependencies" in suggestion.metadata:
                if suggestion.metadata["dependencies"]:
                    score *= 0.8  # Reduce priority if there are dependencies
                    
            # 3. Risk level (if metadata includes risk assessment)
            if suggestion.metadata and "risk_level" in suggestion.metadata:
                risk_weights = {
                    "high": 1.3,
                    "medium": 1.0,
                    "low": 0.7
                }
                score *= risk_weights.get(suggestion.metadata["risk_level"], 1.0)
                
            # 4. Business impact (if metadata includes business impact)
            if suggestion.metadata and "business_impact" in suggestion.metadata:
                business_weights = {
                    "high": 1.4,
                    "medium": 1.0,
                    "low": 0.6
                }
                score *= business_weights.get(suggestion.metadata["business_impact"], 1.0)
                
            # 5. Technical debt (if metadata includes technical debt info)
            if suggestion.metadata and "technical_debt" in suggestion.metadata:
                if suggestion.metadata["technical_debt"]:
                    score *= 1.1  # Slightly increase priority for technical debt
                    
            # 6. User impact (if metadata includes user impact)
            if suggestion.metadata and "user_impact" in suggestion.metadata:
                user_weights = {
                    "high": 1.3,
                    "medium": 1.0,
                    "low": 0.7
                }
                score *= user_weights.get(suggestion.metadata["user_impact"], 1.0)
                
            # 7. Code coverage impact (if metadata includes coverage info)
            if suggestion.metadata and "coverage_impact" in suggestion.metadata:
                if suggestion.metadata["coverage_impact"]:
                    score *= 1.1  # Slightly increase priority for coverage improvements
                    
            # 8. Security vulnerability (if metadata includes security info)
            if suggestion.metadata and "security_vulnerability" in suggestion.metadata:
                if suggestion.metadata["security_vulnerability"]:
                    score *= 2.0  # Double priority for security vulnerabilities
                    
            # 9. Performance critical path (if metadata includes performance info)
            if suggestion.metadata and "performance_critical" in suggestion.metadata:
                if suggestion.metadata["performance_critical"]:
                    score *= 1.4  # Increase priority for performance-critical issues
                    
            # 10. Maintenance window (if metadata includes maintenance info)
            if suggestion.metadata and "maintenance_window" in suggestion.metadata:
                if suggestion.metadata["maintenance_window"]:
                    score *= 1.2  # Increase priority if there's a maintenance window
            
            return score
            
        # Sort suggestions by priority score
        return sorted(suggestions, key=get_priority_score, reverse=True)
        
    def _determine_priority(self, text: str) -> SuggestionPriority:
        """Determine suggestion priority from text"""
        text = text.lower()
        if any(word in text for word in ["critical", "urgent", "immediate"]):
            return SuggestionPriority.CRITICAL
        elif any(word in text for word in ["high", "important", "significant"]):
            return SuggestionPriority.HIGH
        elif any(word in text for word in ["medium", "moderate"]):
            return SuggestionPriority.MEDIUM
        else:
            return SuggestionPriority.LOW
            
    def _generate_suggestion(self, text: str) -> str:
        """Generate improvement suggestion from text"""
        # This is a simplified example - you would need more sophisticated generation
        return f"Consider improving: {text}"
        
    def _determine_impact(self, text: str) -> str:
        """Determine suggestion impact from text"""
        text = text.lower()
        if any(word in text for word in ["critical", "major", "significant"]):
            return "high"
        elif any(word in text for word in ["moderate", "medium"]):
            return "medium"
        else:
            return "low"
            
    def _determine_effort(self, text: str) -> str:
        """Determine suggestion effort from text"""
        text = text.lower()
        if any(word in text for word in ["complex", "difficult", "major"]):
            return "high"
        elif any(word in text for word in ["moderate", "medium"]):
            return "medium"
        else:
            return "low"
            
    async def get_suggestions(self, file_path: str) -> List[CodeSuggestion]:
        """Get suggestions for a file"""
        return self.suggestions.get(file_path, [])
        
    async def get_suggestions_by_type(self, suggestion_type: SuggestionType) -> List[CodeSuggestion]:
        """Get suggestions of a specific type"""
        all_suggestions = []
        for suggestions in self.suggestions.values():
            all_suggestions.extend(
                s for s in suggestions if s.type == suggestion_type
            )
        return all_suggestions
        
    async def get_suggestions_by_priority(self, priority: SuggestionPriority) -> List[CodeSuggestion]:
        """Get suggestions of a specific priority"""
        all_suggestions = []
        for suggestions in self.suggestions.values():
            all_suggestions.extend(
                s for s in suggestions if s.priority == priority
            )
        return all_suggestions
        
    def _generate_custom_pattern_suggestions(self, content: str, context: Any) -> List[CodeSuggestion]:
        """Generate suggestions using custom patterns"""
        suggestions = []
        
        try:
            for pattern in self.custom_patterns.values():
                if self._matches_custom_pattern(content, context, pattern):
                    suggestion = CodeSuggestion(
                        type=pattern.type,
                        priority=pattern.priority,
                        file_path=context.file_path,
                        line_number=self._find_line_number(content, pattern),
                        description=pattern.description,
                        suggestion=pattern.suggestion,
                        impact=pattern.impact,
                        effort=pattern.effort,
                        confidence=pattern.confidence,
                        context={"pattern": pattern.name},
                        metadata=pattern.metadata
                    )
                    suggestions.append(suggestion)
                    
        except Exception as e:
            logger.error(f"Failed to generate custom pattern suggestions: {e}")
            
        return suggestions
        
    async def _generate_solution_suggestions(self, content: str, context: Any) -> List[CodeSuggestion]:
        """Generate suggestions using the solution generator"""
        suggestions = []
        
        try:
            # Analyze code for potential improvements
            analysis_result = await self.solution_generator.generate_solutions(
                "Analyze code for potential improvements",
                context.file_path
            )
            
            for solution in analysis_result:
                # Convert solution to suggestion
                suggestion = CodeSuggestion(
                    type=self._map_solution_to_suggestion_type(solution.fix.category),
                    priority=self._determine_priority_from_scores(solution),
                    file_path=context.file_path,
                    line_number=solution.fix.line_numbers[0] if solution.fix.line_numbers else None,
                    description=solution.fix.description,
                    suggestion=solution.fix.fix_code,
                    impact=solution.fix.impact,
                    effort=solution.fix.effort,
                    confidence=solution.confidence,
                    context={
                        "solution_scores": {
                            "effectiveness": solution.effectiveness_score,
                            "impact": solution.impact_score,
                            "complexity": solution.complexity_score,
                            "maintainability": solution.maintainability_score
                        },
                        "solution_metadata": solution.metadata
                    }
                )
                suggestions.append(suggestion)
                
        except Exception as e:
            logger.error(f"Failed to generate solution suggestions: {e}")
            
        return suggestions
        
    def _map_solution_to_suggestion_type(self, category: FixCategory) -> SuggestionType:
        """Map solution category to suggestion type"""
        mapping = {
            FixCategory.BUG: SuggestionType.ERROR_HANDLING,
            FixCategory.PERFORMANCE: SuggestionType.PERFORMANCE,
            FixCategory.SECURITY: SuggestionType.SECURITY,
            FixCategory.STYLE: SuggestionType.CODE_QUALITY,
            FixCategory.DOCUMENTATION: SuggestionType.DOCUMENTATION,
            FixCategory.REFACTORING: SuggestionType.MAINTAINABILITY
        }
        return mapping.get(category, SuggestionType.CODE_QUALITY)
        
    def _determine_priority_from_scores(self, solution: SolutionVariant) -> SuggestionPriority:
        """Determine suggestion priority from solution scores"""
        # Calculate weighted score
        weighted_score = (
            solution.effectiveness_score * 0.4 +
            solution.impact_score * 0.3 +
            solution.complexity_score * 0.15 +
            solution.maintainability_score * 0.15
        )
        
        # Map score to priority
        if weighted_score >= 0.8:
            return SuggestionPriority.CRITICAL
        elif weighted_score >= 0.6:
            return SuggestionPriority.HIGH
        elif weighted_score >= 0.4:
            return SuggestionPriority.MEDIUM
        else:
            return SuggestionPriority.LOW 