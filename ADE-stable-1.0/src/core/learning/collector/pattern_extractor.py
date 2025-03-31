from typing import Dict, List, Optional, Set, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import logging
from collections import defaultdict
import re
import difflib
from pathlib import Path

from ...utils.logging import get_logger
from ...config import Config
from ..models.pattern import (
    BasePattern, SolutionPattern, ErrorRecoveryPattern,
    WorkflowPattern, ToolUsagePattern, PatternType
)
from ..models.privacy_settings import PrivacySettings
from ..anonymization.anonymizer import Anonymizer, AnonymizationContext

logger = get_logger(__name__)

class TaskType(str, Enum):
    """Types of development tasks"""
    BUG_FIX = "bug_fix"
    FEATURE_ADD = "feature_add"
    REFACTOR = "refactor"
    OPTIMIZATION = "optimization"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    OTHER = "other"

class ProblemClass(str, Enum):
    """Classes of development problems"""
    SYNTAX_ERROR = "syntax_error"
    RUNTIME_ERROR = "runtime_error"
    LOGIC_ERROR = "logic_error"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPATIBILITY = "compatibility"
    ARCHITECTURE = "architecture"
    OTHER = "other"

@dataclass
class PatternCharacteristics:
    """Characteristics of an extracted pattern"""
    task_type: TaskType
    problem_class: ProblemClass
    complexity: float  # 0.0 to 1.0
    success_rate: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    tags: Set[str]
    metadata: Dict[str, Any]

class PatternExtractor:
    """Component for extracting reusable patterns from development activity"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the pattern extractor.
        
        Args:
            config: Optional configuration object
        """
        self.config = config or Config()
        self.anonymizer = Anonymizer(config)
        self._initialize_pattern_characteristics()
        self._initialize_pattern_rules()
        
    def _initialize_pattern_rules(self) -> None:
        """Initialize pattern extraction rules and heuristics"""
        self.code_patterns = {
            "bug_fix": [
                r"fix.*bug",
                r"resolve.*issue",
                r"correct.*error",
                r"patch.*problem"
            ],
            "feature_add": [
                r"add.*feature",
                r"implement.*functionality",
                r"create.*component",
                r"introduce.*capability"
            ],
            "refactor": [
                r"refactor.*code",
                r"restructure.*component",
                r"reorganize.*module",
                r"improve.*structure"
            ]
        }
        
        self.error_patterns = {
            "syntax_error": [
                r"SyntaxError",
                r"IndentationError",
                r"NameError",
                r"TypeError"
            ],
            "runtime_error": [
                r"RuntimeError",
                r"ValueError",
                r"KeyError",
                r"IndexError"
            ],
            "logic_error": [
                r"LogicError",
                r"AssertionError",
                r"ValidationError"
            ]
        }
        
        self.tool_patterns = {
            "git": ["commit", "push", "pull", "branch", "merge"],
            "docker": ["build", "run", "compose", "container"],
            "test": ["pytest", "unittest", "coverage", "assert"]
        }
    
    def _initialize_pattern_characteristics(self) -> None:
        """Initialize pattern characteristics tracking"""
        self.pattern_characteristics: Dict[str, PatternCharacteristics] = {}
        self.pattern_occurrences: Dict[str, int] = defaultdict(int)
        self.pattern_successes: Dict[str, int] = defaultdict(int)
    
    def extract_patterns(
        self,
        activities: List[Dict[str, Any]],
        privacy_settings: PrivacySettings
    ) -> List[BasePattern]:
        """
        Extract patterns from development activities.
        
        Args:
            activities: List of development activities
            privacy_settings: Privacy settings for pattern extraction
            
        Returns:
            List[BasePattern]: List of extracted patterns
        """
        patterns = []
        
        try:
            # Group activities by type
            activity_groups = self._group_activities(activities)
            
            # Extract patterns from each group
            for activity_type, group in activity_groups.items():
                if activity_type == "code_edit":
                    patterns.extend(self._extract_solution_patterns(group))
                elif activity_type == "debug":
                    patterns.extend(self._extract_error_patterns(group))
                elif activity_type == "sequence":
                    patterns.extend(self._extract_workflow_patterns(group))
                elif activity_type == "tool":
                    patterns.extend(self._extract_tool_patterns(group))
            
            # Anonymize patterns
            context = AnonymizationContext(
                privacy_settings=privacy_settings,
                timestamp=datetime.utcnow(),
                instance_id=self.config.instance_id
            )
            patterns = self.anonymizer.anonymize_patterns(patterns, context)
            
            # Update pattern characteristics
            self._update_pattern_characteristics(patterns)
            
            logger.info(f"Extracted {len(patterns)} patterns from {len(activities)} activities")
            return patterns
            
        except Exception as e:
            logger.error(f"Error extracting patterns: {str(e)}")
            raise
    
    def _group_activities(self, activities: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group activities by type for pattern extraction.
        
        Args:
            activities: List of development activities
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Grouped activities
        """
        groups = defaultdict(list)
        
        for activity in activities:
            activity_type = activity.get("type", "unknown")
            if activity_type in ["code_edit", "debug", "sequence", "tool"]:
                groups[activity_type].append(activity)
            else:
                groups["other"].append(activity)
        
        return dict(groups)
    
    def _extract_solution_patterns(
        self,
        activities: List[Dict[str, Any]]
    ) -> List[SolutionPattern]:
        """
        Extract solution patterns from code editing activities.
        
        Args:
            activities: List of code editing activities
            
        Returns:
            List[SolutionPattern]: List of extracted solution patterns
        """
        patterns = []
        
        for activity in activities:
            # Analyze code changes
            changes = activity.get("changes", [])
            if not changes:
                continue
                
            # Identify solution characteristics
            characteristics = self._analyze_solution_characteristics(changes)
            
            # Create solution pattern
            pattern = SolutionPattern(
                pattern_type=PatternType.SOLUTION,
                name=self._generate_pattern_name(activity, characteristics),
                description=self._generate_pattern_description(activity, characteristics),
                steps=self._extract_solution_steps(changes),
                prerequisites=self._extract_prerequisites(changes),
                alternatives=self._extract_alternatives(changes),
                validation_rules=self._extract_validation_rules(changes),
                estimated_duration=self._estimate_duration(activity),
                context=self._extract_context(activity),
                privacy=self._create_privacy_metadata(),
                effectiveness=self._create_effectiveness_metrics(characteristics)
            )
            
            patterns.append(pattern)
        
        return patterns
    
    def _extract_error_patterns(
        self,
        activities: List[Dict[str, Any]]
    ) -> List[ErrorRecoveryPattern]:
        """
        Extract error recovery patterns from debugging activities.
        
        Args:
            activities: List of debugging activities
            
        Returns:
            List[ErrorRecoveryPattern]: List of extracted error patterns
        """
        patterns = []
        
        for activity in activities:
            # Analyze error information
            error_info = activity.get("error", {})
            if not error_info:
                continue
                
            # Identify error characteristics
            characteristics = self._analyze_error_characteristics(error_info)
            
            # Create error pattern
            pattern = ErrorRecoveryPattern(
                pattern_type=PatternType.ERROR_RECOVERY,
                name=self._generate_pattern_name(activity, characteristics),
                description=self._generate_pattern_description(activity, characteristics),
                error_type=error_info.get("type", "unknown"),
                error_signature=self._generate_error_signature(error_info),
                recovery_steps=self._extract_recovery_steps(activity),
                prevention_measures=self._extract_prevention_measures(activity),
                error_context=self._extract_error_context(error_info),
                severity_level=self._determine_severity(error_info),
                context=self._extract_context(activity),
                privacy=self._create_privacy_metadata(),
                effectiveness=self._create_effectiveness_metrics(characteristics)
            )
            
            patterns.append(pattern)
        
        return patterns
    
    def _extract_workflow_patterns(
        self,
        activities: List[Dict[str, Any]]
    ) -> List[WorkflowPattern]:
        """
        Extract workflow patterns from activity sequences.
        
        Args:
            activities: List of sequential activities
            
        Returns:
            List[WorkflowPattern]: List of extracted workflow patterns
        """
        patterns = []
        
        # Group activities into sequences
        sequences = self._identify_sequences(activities)
        
        for sequence in sequences:
            # Analyze sequence characteristics
            characteristics = self._analyze_workflow_characteristics(sequence)
            
            # Create workflow pattern
            pattern = WorkflowPattern(
                pattern_type=PatternType.WORKFLOW,
                name=self._generate_pattern_name(sequence, characteristics),
                description=self._generate_pattern_description(sequence, characteristics),
                sequence=self._extract_sequence(sequence),
                dependencies=self._extract_dependencies(sequence),
                checkpoints=self._extract_checkpoints(sequence),
                rollback_steps=self._extract_rollback_steps(sequence),
                parallel_actions=self._extract_parallel_actions(sequence),
                context=self._extract_context(sequence),
                privacy=self._create_privacy_metadata(),
                effectiveness=self._create_effectiveness_metrics(characteristics)
            )
            
            patterns.append(pattern)
        
        return patterns
    
    def _extract_tool_patterns(
        self,
        activities: List[Dict[str, Any]]
    ) -> List[ToolUsagePattern]:
        """
        Extract tool usage patterns from tool interactions.
        
        Args:
            activities: List of tool interaction activities
            
        Returns:
            List[ToolUsagePattern]: List of extracted tool patterns
        """
        patterns = []
        
        for activity in activities:
            # Analyze tool interaction
            tool_info = activity.get("tool", {})
            if not tool_info:
                continue
                
            # Identify tool characteristics
            characteristics = self._analyze_tool_characteristics(tool_info)
            
            # Create tool pattern
            pattern = ToolUsagePattern(
                pattern_type=PatternType.TOOL_USAGE,
                name=self._generate_pattern_name(activity, characteristics),
                description=self._generate_pattern_description(activity, characteristics),
                tool_name=tool_info.get("name", "unknown"),
                command_sequence=self._extract_command_sequence(activity),
                parameters=self._extract_tool_parameters(activity),
                output_format=self._extract_output_format(activity),
                common_issues=self._extract_common_issues(activity),
                optimization_tips=self._extract_optimization_tips(activity),
                context=self._extract_context(activity),
                privacy=self._create_privacy_metadata(),
                effectiveness=self._create_effectiveness_metrics(characteristics)
            )
            
            patterns.append(pattern)
        
        return patterns
    
    def _analyze_solution_characteristics(
        self,
        changes: List[Dict[str, Any]]
    ) -> PatternCharacteristics:
        """
        Analyze characteristics of code changes.
        
        Args:
            changes: List of code changes
            
        Returns:
            PatternCharacteristics: Characteristics of the solution
        """
        # Analyze change patterns
        change_types = defaultdict(int)
        file_types = defaultdict(int)
        complexity_score = 0.0
        
        for change in changes:
            # Count change types
            change_type = change.get("type", "unknown")
            change_types[change_type] += 1
            
            # Count file types
            file_path = change.get("file_path", "")
            file_ext = Path(file_path).suffix
            file_types[file_ext] += 1
            
            # Calculate complexity based on change size and type
            change_size = len(change.get("content", ""))
            complexity_score += self._calculate_change_complexity(change_type, change_size)
        
        # Normalize complexity score
        complexity_score = min(1.0, complexity_score / (len(changes) * 100))
        
        # Determine task type based on change patterns
        task_type = self._determine_task_type_from_changes(change_types)
        
        # Determine problem class based on file types and changes
        problem_class = self._determine_problem_class_from_changes(file_types, change_types)
        
        # Extract tags based on changes
        tags = self._extract_tags_from_changes(changes)
        
        # Calculate success rate based on validation results
        success_rate = self._calculate_success_rate(changes)
        
        # Calculate confidence based on pattern matching
        confidence = self._calculate_confidence(changes)
        
        return PatternCharacteristics(
            task_type=task_type,
            problem_class=problem_class,
            complexity=complexity_score,
            success_rate=success_rate,
            confidence=confidence,
            tags=tags,
            metadata={
                "change_types": dict(change_types),
                "file_types": dict(file_types),
                "total_changes": len(changes)
            }
        )
    
    def _analyze_error_characteristics(
        self,
        error_info: Dict[str, Any]
    ) -> PatternCharacteristics:
        """
        Analyze characteristics of error information.
        
        Args:
            error_info: Error information dictionary
            
        Returns:
            PatternCharacteristics: Characteristics of the error pattern
        """
        # Extract error type and message
        error_type = error_info.get("type", "unknown")
        error_message = error_info.get("message", "")
        
        # Determine problem class based on error type
        problem_class = self._determine_problem_class_from_error(error_type, error_message)
        
        # Calculate complexity based on error context
        complexity = self._calculate_error_complexity(error_info)
        
        # Extract tags from error information
        tags = self._extract_tags_from_error(error_info)
        
        # Calculate success rate based on recovery attempts
        success_rate = self._calculate_error_success_rate(error_info)
        
        # Calculate confidence based on error pattern matching
        confidence = self._calculate_error_confidence(error_info)
        
        return PatternCharacteristics(
            task_type=TaskType.BUG_FIX,
            problem_class=problem_class,
            complexity=complexity,
            success_rate=success_rate,
            confidence=confidence,
            tags=tags,
            metadata={
                "error_type": error_type,
                "error_message": error_message,
                "stack_trace": error_info.get("stack_trace", []),
                "context": error_info.get("context", {})
            }
        )
    
    def _analyze_workflow_characteristics(
        self,
        sequence: List[Dict[str, Any]]
    ) -> PatternCharacteristics:
        """
        Analyze characteristics of activity sequences.
        
        Args:
            sequence: List of sequential activities
            
        Returns:
            PatternCharacteristics: Characteristics of the workflow pattern
        """
        # Analyze sequence structure
        activity_types = defaultdict(int)
        dependencies = defaultdict(list)
        checkpoints = []
        
        for i, activity in enumerate(sequence):
            # Count activity types
            activity_type = activity.get("type", "unknown")
            activity_types[activity_type] += 1
            
            # Identify dependencies
            if "depends_on" in activity:
                dependencies[activity_type].extend(activity["depends_on"])
            
            # Identify checkpoints
            if activity.get("is_checkpoint", False):
                checkpoints.append(i)
        
        # Calculate complexity based on sequence structure
        complexity = self._calculate_workflow_complexity(sequence, dependencies)
        
        # Determine task type based on activity types
        task_type = self._determine_task_type_from_sequence(activity_types)
        
        # Determine problem class based on sequence characteristics
        problem_class = self._determine_problem_class_from_sequence(sequence)
        
        # Extract tags from sequence
        tags = self._extract_tags_from_sequence(sequence)
        
        # Calculate success rate based on sequence completion
        success_rate = self._calculate_workflow_success_rate(sequence)
        
        # Calculate confidence based on pattern matching
        confidence = self._calculate_workflow_confidence(sequence)
        
        return PatternCharacteristics(
            task_type=task_type,
            problem_class=problem_class,
            complexity=complexity,
            success_rate=success_rate,
            confidence=confidence,
            tags=tags,
            metadata={
                "activity_types": dict(activity_types),
                "dependencies": dict(dependencies),
                "checkpoints": checkpoints,
                "sequence_length": len(sequence)
            }
        )
    
    def _analyze_tool_characteristics(
        self,
        tool_info: Dict[str, Any]
    ) -> PatternCharacteristics:
        """
        Analyze characteristics of tool interactions.
        
        Args:
            tool_info: Tool interaction information
            
        Returns:
            PatternCharacteristics: Characteristics of the tool pattern
        """
        # Extract tool information
        tool_name = tool_info.get("name", "unknown")
        commands = tool_info.get("commands", [])
        parameters = tool_info.get("parameters", {})
        
        # Calculate complexity based on tool usage
        complexity = self._calculate_tool_complexity(tool_info)
        
        # Determine task type based on tool usage
        task_type = self._determine_task_type_from_tool(tool_name, commands)
        
        # Determine problem class based on tool interaction
        problem_class = self._determine_problem_class_from_tool(tool_info)
        
        # Extract tags from tool usage
        tags = self._extract_tags_from_tool(tool_info)
        
        # Calculate success rate based on tool execution
        success_rate = self._calculate_tool_success_rate(tool_info)
        
        # Calculate confidence based on pattern matching
        confidence = self._calculate_tool_confidence(tool_info)
        
        return PatternCharacteristics(
            task_type=task_type,
            problem_class=problem_class,
            complexity=complexity,
            success_rate=success_rate,
            confidence=confidence,
            tags=tags,
            metadata={
                "tool_name": tool_name,
                "command_count": len(commands),
                "parameter_count": len(parameters),
                "execution_time": tool_info.get("execution_time", 0)
            }
        )
    
    def _generate_pattern_name(
        self,
        activity: Dict[str, Any],
        characteristics: PatternCharacteristics
    ) -> str:
        """
        Generate a descriptive name for a pattern.
        
        Args:
            activity: Activity information
            characteristics: Pattern characteristics
            
        Returns:
            str: Generated pattern name
        """
        # Extract key information
        activity_type = activity.get("type", "unknown")
        task_type = characteristics.task_type.value
        problem_class = characteristics.problem_class.value
        
        # Generate name based on pattern type
        if activity_type == "code_edit":
            return f"{task_type.title()} for {problem_class.replace('_', ' ').title()}"
        elif activity_type == "debug":
            return f"Recovery for {problem_class.replace('_', ' ').title()}"
        elif activity_type == "sequence":
            return f"Workflow for {task_type.title()}"
        elif activity_type == "tool":
            tool_name = activity.get("tool", {}).get("name", "unknown")
            return f"{tool_name.title()} Usage Pattern"
        else:
            return f"Pattern for {activity_type.title()}"
    
    def _generate_pattern_description(
        self,
        activity: Dict[str, Any],
        characteristics: PatternCharacteristics
    ) -> str:
        """
        Generate a detailed description for a pattern.
        
        Args:
            activity: Activity information
            characteristics: Pattern characteristics
            
        Returns:
            str: Generated pattern description
        """
        # Extract key information
        activity_type = activity.get("type", "unknown")
        task_type = characteristics.task_type.value
        problem_class = characteristics.problem_class.value
        tags = characteristics.tags
        
        # Generate description based on pattern type
        description = f"This pattern addresses {problem_class.replace('_', ' ')} "
        description += f"in the context of {task_type.replace('_', ' ')}. "
        
        if activity_type == "code_edit":
            description += "It provides a systematic approach to code modification "
            description += "with clear steps and validation rules."
        elif activity_type == "debug":
            description += "It offers a proven method for error recovery "
            description += "with prevention measures and rollback procedures."
        elif activity_type == "sequence":
            description += "It defines a structured workflow with dependencies "
            description += "and checkpoints for reliable execution."
        elif activity_type == "tool":
            description += "It outlines effective tool usage patterns "
            description += "with parameter optimization and common issue handling."
        
        # Add tags if available
        if tags:
            description += f"\n\nKey aspects: {', '.join(tags)}"
        
        return description
    
    def _extract_context(self, activity: Dict[str, Any]) -> Any:
        """
        Extract context information from activity.
        
        Args:
            activity: Activity information
            
        Returns:
            Any: Extracted context information
        """
        context = {
            "timestamp": activity.get("timestamp", datetime.utcnow()),
            "environment": activity.get("environment", {}),
            "project": activity.get("project", {}),
            "user": activity.get("user", {}),
            "system": activity.get("system", {})
        }
        
        # Add type-specific context
        activity_type = activity.get("type", "unknown")
        if activity_type == "code_edit":
            context["code_context"] = {
                "language": activity.get("language", "unknown"),
                "framework": activity.get("framework", "unknown"),
                "file_path": activity.get("file_path", "unknown")
            }
        elif activity_type == "debug":
            context["error_context"] = {
                "error_type": activity.get("error", {}).get("type", "unknown"),
                "error_message": activity.get("error", {}).get("message", ""),
                "stack_trace": activity.get("error", {}).get("stack_trace", [])
            }
        elif activity_type == "sequence":
            context["sequence_context"] = {
                "sequence_type": activity.get("sequence_type", "unknown"),
                "dependencies": activity.get("dependencies", []),
                "checkpoints": activity.get("checkpoints", [])
            }
        elif activity_type == "tool":
            context["tool_context"] = {
                "tool_name": activity.get("tool", {}).get("name", "unknown"),
                "commands": activity.get("tool", {}).get("commands", []),
                "parameters": activity.get("tool", {}).get("parameters", {})
            }
        
        return context
    
    def _create_privacy_metadata(self) -> Any:
        """
        Create privacy metadata for a pattern.
        
        Returns:
            Any: Privacy metadata
        """
        return {
            "created_at": datetime.utcnow(),
            "last_updated": datetime.utcnow(),
            "version": "1.0",
            "privacy_level": "medium",
            "data_retention": "30d",
            "sharing_policy": "aggregated_only"
        }
    
    def _create_effectiveness_metrics(
        self,
        characteristics: PatternCharacteristics
    ) -> Any:
        """
        Create effectiveness metrics for a pattern.
        
        Args:
            characteristics: Pattern characteristics
            
        Returns:
            Any: Effectiveness metrics
        """
        return {
            "success_rate": characteristics.success_rate,
            "confidence_score": characteristics.confidence,
            "complexity_score": characteristics.complexity,
            "reusability_score": self._calculate_reusability(characteristics),
            "maintainability_score": self._calculate_maintainability(characteristics),
            "last_used": datetime.utcnow(),
            "usage_count": 0,
            "feedback_score": 0.0
        }
    
    def _calculate_change_complexity(
        self,
        change_type: str,
        change_size: int
    ) -> float:
        """Calculate complexity score for a code change"""
        base_complexity = {
            "add": 1.0,
            "modify": 1.5,
            "delete": 0.5,
            "rename": 0.8,
            "move": 1.2
        }.get(change_type, 1.0)
        
        # Scale by change size
        return base_complexity * (1 + min(1.0, change_size / 1000))
    
    def _calculate_error_complexity(
        self,
        error_info: Dict[str, Any]
    ) -> float:
        """Calculate complexity score for an error"""
        # Base complexity on error type
        base_complexity = {
            "syntax_error": 0.5,
            "runtime_error": 0.8,
            "logic_error": 1.0,
            "performance": 1.2,
            "security": 1.5
        }.get(error_info.get("type", "unknown"), 1.0)
        
        # Scale by stack trace depth
        stack_depth = len(error_info.get("stack_trace", []))
        return base_complexity * (1 + min(1.0, stack_depth / 10))
    
    def _calculate_workflow_complexity(
        self,
        sequence: List[Dict[str, Any]],
        dependencies: Dict[str, List[str]]
    ) -> float:
        """Calculate complexity score for a workflow"""
        # Base complexity on sequence length
        base_complexity = min(1.0, len(sequence) / 10)
        
        # Scale by dependency complexity
        dep_complexity = sum(len(deps) for deps in dependencies.values())
        return base_complexity * (1 + min(1.0, dep_complexity / 20))
    
    def _calculate_tool_complexity(
        self,
        tool_info: Dict[str, Any]
    ) -> float:
        """Calculate complexity score for tool usage"""
        # Base complexity on command count
        base_complexity = min(1.0, len(tool_info.get("commands", [])) / 5)
        
        # Scale by parameter complexity
        param_count = len(tool_info.get("parameters", {}))
        return base_complexity * (1 + min(1.0, param_count / 10))
    
    def _calculate_reusability(
        self,
        characteristics: PatternCharacteristics
    ) -> float:
        """Calculate reusability score for a pattern"""
        # Base reusability on problem class
        base_reusability = {
            ProblemClass.SYNTAX_ERROR: 0.9,
            ProblemClass.RUNTIME_ERROR: 0.8,
            ProblemClass.LOGIC_ERROR: 0.7,
            ProblemClass.PERFORMANCE: 0.6,
            ProblemClass.SECURITY: 0.5,
            ProblemClass.COMPATIBILITY: 0.4,
            ProblemClass.ARCHITECTURE: 0.3,
            ProblemClass.OTHER: 0.5
        }.get(characteristics.problem_class, 0.5)
        
        # Scale by complexity (lower complexity = higher reusability)
        return base_reusability * (1 - characteristics.complexity * 0.5)
    
    def _calculate_maintainability(
        self,
        characteristics: PatternCharacteristics
    ) -> float:
        """Calculate maintainability score for a pattern"""
        # Base maintainability on task type
        base_maintainability = {
            TaskType.BUG_FIX: 0.9,
            TaskType.FEATURE_ADD: 0.8,
            TaskType.REFACTOR: 0.7,
            TaskType.OPTIMIZATION: 0.6,
            TaskType.DOCUMENTATION: 0.9,
            TaskType.TESTING: 0.8,
            TaskType.DEPLOYMENT: 0.7,
            TaskType.OTHER: 0.5
        }.get(characteristics.task_type, 0.5)
        
        # Scale by confidence (higher confidence = higher maintainability)
        return base_maintainability * (0.5 + characteristics.confidence * 0.5)
    
    def _determine_task_type_from_changes(
        self,
        change_types: Dict[str, int]
    ) -> TaskType:
        """Determine task type from code changes"""
        # Analyze change patterns
        if change_types.get("delete", 0) > change_types.get("add", 0):
            return TaskType.REFACTOR
        elif change_types.get("add", 0) > change_types.get("modify", 0):
            return TaskType.FEATURE_ADD
        else:
            return TaskType.BUG_FIX
    
    def _determine_problem_class_from_changes(
        self,
        file_types: Dict[str, int],
        change_types: Dict[str, int]
    ) -> ProblemClass:
        """Determine problem class from code changes"""
        # Analyze file types and changes
        if ".test." in file_types:
            return ProblemClass.TESTING
        elif ".security." in file_types:
            return ProblemClass.SECURITY
        elif change_types.get("modify", 0) > change_types.get("add", 0):
            return ProblemClass.PERFORMANCE
        else:
            return ProblemClass.ARCHITECTURE
    
    def _determine_task_type_from_sequence(
        self,
        activity_types: Dict[str, int]
    ) -> TaskType:
        """Determine task type from activity sequence"""
        # Analyze activity patterns
        if "test" in activity_types:
            return TaskType.TESTING
        elif "deploy" in activity_types:
            return TaskType.DEPLOYMENT
        elif "build" in activity_types:
            return TaskType.FEATURE_ADD
        else:
            return TaskType.OTHER
    
    def _determine_problem_class_from_sequence(
        self,
        sequence: List[Dict[str, Any]]
    ) -> ProblemClass:
        """Determine problem class from activity sequence"""
        # Analyze sequence characteristics
        if any("test" in activity.get("type", "") for activity in sequence):
            return ProblemClass.TESTING
        elif any("security" in activity.get("type", "") for activity in sequence):
            return ProblemClass.SECURITY
        elif any("performance" in activity.get("type", "") for activity in sequence):
            return ProblemClass.PERFORMANCE
        else:
            return ProblemClass.ARCHITECTURE
    
    def _determine_task_type_from_tool(
        self,
        tool_name: str,
        commands: List[str]
    ) -> TaskType:
        """Determine task type from tool usage"""
        # Analyze tool and command patterns
        if tool_name == "git":
            if "commit" in commands:
                return TaskType.FEATURE_ADD
            elif "merge" in commands:
                return TaskType.REFACTOR
        elif tool_name == "docker":
            if "build" in commands:
                return TaskType.DEPLOYMENT
            elif "compose" in commands:
                return TaskType.FEATURE_ADD
        elif tool_name == "test":
            return TaskType.TESTING
        
        return TaskType.OTHER
    
    def _determine_problem_class_from_tool(
        self,
        tool_info: Dict[str, Any]
    ) -> ProblemClass:
        """Determine problem class from tool usage"""
        # Analyze tool interaction patterns
        if "security" in tool_info.get("name", "").lower():
            return ProblemClass.SECURITY
        elif "test" in tool_info.get("name", "").lower():
            return ProblemClass.TESTING
        elif "performance" in tool_info.get("name", "").lower():
            return ProblemClass.PERFORMANCE
        else:
            return ProblemClass.OTHER
    
    def _extract_tags_from_changes(
        self,
        changes: List[Dict[str, Any]]
    ) -> Set[str]:
        """Extract tags from code changes"""
        tags = set()
        
        for change in changes:
            # Add language-specific tags
            if "language" in change:
                tags.add(f"lang:{change['language']}")
            
            # Add framework-specific tags
            if "framework" in change:
                tags.add(f"framework:{change['framework']}")
            
            # Add change-specific tags
            if "type" in change:
                tags.add(f"change:{change['type']}")
        
        return tags
    
    def _extract_tags_from_error(
        self,
        error_info: Dict[str, Any]
    ) -> Set[str]:
        """Extract tags from error information"""
        tags = set()
        
        # Add error type tags
        if "type" in error_info:
            tags.add(f"error:{error_info['type']}")
        
        # Add severity tags
        if "severity" in error_info:
            tags.add(f"severity:{error_info['severity']}")
        
        # Add context tags
        if "context" in error_info:
            for key, value in error_info["context"].items():
                tags.add(f"context:{key}")
        
        return tags
    
    def _extract_tags_from_sequence(
        self,
        sequence: List[Dict[str, Any]]
    ) -> Set[str]:
        """Extract tags from activity sequence"""
        tags = set()
        
        for activity in sequence:
            # Add activity type tags
            if "type" in activity:
                tags.add(f"activity:{activity['type']}")
            
            # Add tool tags
            if "tool" in activity:
                tags.add(f"tool:{activity['tool'].get('name', 'unknown')}")
            
            # Add environment tags
            if "environment" in activity:
                tags.add(f"env:{activity['environment'].get('type', 'unknown')}")
        
        return tags
    
    def _extract_tags_from_tool(
        self,
        tool_info: Dict[str, Any]
    ) -> Set[str]:
        """Extract tags from tool usage"""
        tags = set()
        
        # Add tool name tag
        if "name" in tool_info:
            tags.add(f"tool:{tool_info['name']}")
        
        # Add command tags
        for cmd in tool_info.get("commands", []):
            tags.add(f"cmd:{cmd}")
        
        # Add parameter tags
        for param in tool_info.get("parameters", {}):
            tags.add(f"param:{param}")
        
        return tags
    
    def _calculate_success_rate(
        self,
        changes: List[Dict[str, Any]]
    ) -> float:
        """Calculate success rate for code changes"""
        if not changes:
            return 0.0
        
        successful_changes = sum(
            1 for change in changes
            if change.get("validation", {}).get("success", False)
        )
        
        return successful_changes / len(changes)
    
    def _calculate_error_success_rate(
        self,
        error_info: Dict[str, Any]
    ) -> float:
        """Calculate success rate for error recovery"""
        recovery_attempts = error_info.get("recovery_attempts", [])
        if not recovery_attempts:
            return 0.0
        
        successful_recoveries = sum(
            1 for attempt in recovery_attempts
            if attempt.get("success", False)
        )
        
        return successful_recoveries / len(recovery_attempts)
    
    def _calculate_workflow_success_rate(
        self,
        sequence: List[Dict[str, Any]]
    ) -> float:
        """Calculate success rate for workflow sequence"""
        if not sequence:
            return 0.0
        
        successful_steps = sum(
            1 for activity in sequence
            if activity.get("status", "") == "success"
        )
        
        return successful_steps / len(sequence)
    
    def _calculate_tool_success_rate(
        self,
        tool_info: Dict[str, Any]
    ) -> float:
        """Calculate success rate for tool usage"""
        executions = tool_info.get("executions", [])
        if not executions:
            return 0.0
        
        successful_executions = sum(
            1 for execution in executions
            if execution.get("status", "") == "success"
        )
        
        return successful_executions / len(executions)
    
    def _calculate_confidence(
        self,
        changes: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for code changes"""
        if not changes:
            return 0.0
        
        # Base confidence on validation results
        validation_scores = [
            change.get("validation", {}).get("confidence", 0.0)
            for change in changes
        ]
        
        # Average validation scores
        return sum(validation_scores) / len(validation_scores)
    
    def _calculate_error_confidence(
        self,
        error_info: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for error recovery"""
        recovery_attempts = error_info.get("recovery_attempts", [])
        if not recovery_attempts:
            return 0.0
        
        # Base confidence on recovery success and pattern matching
        confidence_scores = [
            attempt.get("confidence", 0.0)
            for attempt in recovery_attempts
            if attempt.get("success", False)
        ]
        
        return sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
    
    def _calculate_workflow_confidence(
        self,
        sequence: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for workflow sequence"""
        if not sequence:
            return 0.0
        
        # Base confidence on step success and dependencies
        confidence_scores = [
            activity.get("confidence", 0.0)
            for activity in sequence
            if activity.get("status", "") == "success"
        ]
        
        return sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
    
    def _calculate_tool_confidence(
        self,
        tool_info: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for tool usage"""
        executions = tool_info.get("executions", [])
        if not executions:
            return 0.0
        
        # Base confidence on execution success and parameter matching
        confidence_scores = [
            execution.get("confidence", 0.0)
            for execution in executions
            if execution.get("status", "") == "success"
        ]
        
        return sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
    
    def _update_pattern_characteristics(
        self,
        patterns: List[BasePattern]
    ) -> None:
        """
        Update pattern characteristics tracking.
        
        Args:
            patterns: List of patterns to update
        """
        for pattern in patterns:
            # Update occurrence count
            self.pattern_occurrences[pattern.pattern_id] += 1
            
            # Update success count if pattern was successful
            if pattern.effectiveness.success_rate > 0.7:
                self.pattern_successes[pattern.pattern_id] += 1
            
            # Update characteristics
            characteristics = PatternCharacteristics(
                task_type=self._determine_task_type(pattern),
                problem_class=self._determine_problem_class(pattern),
                complexity=self._calculate_complexity(pattern),
                success_rate=pattern.effectiveness.success_rate,
                confidence=pattern.effectiveness.confidence_score,
                tags=self._extract_tags(pattern),
                metadata=self._extract_metadata(pattern)
            )
            
            self.pattern_characteristics[pattern.pattern_id] = characteristics
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about extracted patterns.
        
        Returns:
            Dict[str, Any]: Pattern statistics
        """
        return {
            "total_patterns": len(self.pattern_characteristics),
            "patterns_by_type": self._count_patterns_by_type(),
            "success_rate": self._calculate_overall_success_rate(),
            "average_confidence": self._calculate_average_confidence(),
            "pattern_characteristics": {
                pid: {
                    "task_type": char.task_type,
                    "problem_class": char.problem_class,
                    "complexity": char.complexity,
                    "success_rate": char.success_rate,
                    "confidence": char.confidence,
                    "tags": list(char.tags)
                }
                for pid, char in self.pattern_characteristics.items()
            }
        }
    
    def _count_patterns_by_type(self) -> Dict[PatternType, int]:
        """Count patterns by type"""
        counts = defaultdict(int)
        for pattern_id in self.pattern_characteristics:
            pattern_type = self._get_pattern_type(pattern_id)
            counts[pattern_type] += 1
        return dict(counts)
    
    def _calculate_overall_success_rate(self) -> float:
        """Calculate overall success rate of patterns"""
        if not self.pattern_occurrences:
            return 0.0
        total_successes = sum(self.pattern_successes.values())
        total_occurrences = sum(self.pattern_occurrences.values())
        return total_successes / total_occurrences if total_occurrences > 0 else 0.0
    
    def _calculate_average_confidence(self) -> float:
        """Calculate average confidence score of patterns"""
        if not self.pattern_characteristics:
            return 0.0
        confidences = [char.confidence for char in self.pattern_characteristics.values()]
        return sum(confidences) / len(confidences) 