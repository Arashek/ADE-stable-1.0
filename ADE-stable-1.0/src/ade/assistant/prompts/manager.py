from typing import Dict, Optional, List, Any, Union
from dataclasses import dataclass
from datetime import datetime
from .system import SystemPromptTemplate

@dataclass
class PromptContext:
    """Context information for prompt generation."""
    project_type: str
    programming_language: str
    current_task: str
    previous_interactions: List[str]
    available_tools: List[str]
    code_context: Optional[Dict[str, str]] = None
    developer_expertise: Optional[str] = None
    project_phase: Optional[str] = None
    performance_requirements: Optional[Dict[str, Any]] = None
    security_requirements: Optional[Dict[str, Any]] = None
    custom_instructions: Optional[Dict[str, str]] = None
    domain: Optional[str] = None
    timestamp: Optional[datetime] = None
    session_id: Optional[str] = None
    user_preferences: Optional[Dict[str, Any]] = None
    project_metadata: Optional[Dict[str, Any]] = None
    tool_configurations: Optional[Dict[str, Dict[str, Any]]] = None
    error_history: Optional[List[Dict[str, Any]]] = None
    success_metrics: Optional[Dict[str, Any]] = None

class PromptManager:
    """Manages the application of prompts during training and inference."""
    
    def __init__(self):
        self.template = SystemPromptTemplate()
        self.context: Optional[PromptContext] = None
        self.custom_scenarios: Dict[str, str] = {}
        self.context_history: List[PromptContext] = []
        self.formatting_options: Dict[str, Any] = {
            "include_timestamps": True,
            "include_session_id": True,
            "include_metrics": True,
            "include_error_history": True,
            "include_tool_configs": True,
            "format_code_blocks": True,
            "highlight_important": True,
            "use_sections": True,
            "include_summary": True
        }
        
    def set_context(self, context: PromptContext):
        """Set the current context and maintain history."""
        if not context.timestamp:
            context.timestamp = datetime.now()
        self.context_history.append(self.context)
        self.context = context
        
    def set_formatting_options(self, options: Dict[str, Any]):
        """Set formatting options for prompt generation."""
        self.formatting_options.update(options)
        
    def add_custom_scenario(self, name: str, instructions: str):
        """Add a custom training or inference scenario."""
        self.custom_scenarios[name] = instructions
        
    def get_training_prompt(self, scenario: Optional[str] = None) -> str:
        """Get the training prompt with context-specific modifications."""
        base_prompt = self.template.get_training_prompt(
            scenario=scenario,
            domain=self.context.domain if self.context else None
        )
        if not self.context:
            return base_prompt
            
        # Add context-specific modifications
        context_prompt = self._generate_context_prompt()
        
        # Add custom instructions if provided
        custom_prompt = self._generate_custom_instructions()
        
        # Add formatting and metadata
        metadata_prompt = self._generate_metadata_prompt()
        
        return f"{base_prompt}\n\n{context_prompt}\n\n{custom_prompt}\n\n{metadata_prompt}"
        
    def get_inference_prompt(self, scenario: Optional[str] = None) -> str:
        """Get the inference prompt with context-specific modifications."""
        base_prompt = self.template.get_inference_prompt(
            scenario=scenario,
            domain=self.context.domain if self.context else None
        )
        if not self.context:
            return base_prompt
            
        # Add context-specific modifications
        context_prompt = self._generate_context_prompt()
        
        # Add custom instructions if provided
        custom_prompt = self._generate_custom_instructions()
        
        # Add formatting and metadata
        metadata_prompt = self._generate_metadata_prompt()
        
        return f"{base_prompt}\n\n{context_prompt}\n\n{custom_prompt}\n\n{metadata_prompt}"
        
    def get_task_specific_prompt(self, task_type: str) -> str:
        """Get a prompt specialized for a specific task type."""
        task_prompt = self.template.SPECIALIZED_SCENARIOS.get(task_type, "")
        if not task_prompt:
            task_prompt = self.custom_scenarios.get(task_type, "")
            
        if not task_prompt:
            return self.get_inference_prompt()
            
        return f"{self.get_inference_prompt()}\n\n{task_prompt}"
        
    def _generate_context_prompt(self) -> str:
        """Generate context-specific prompt modifications."""
        if not self.context:
            return ""
            
        context_parts = [
            f"Context-Specific Guidelines:",
            f"Project Type: {self.context.project_type}",
            f"Programming Language: {self.context.programming_language}",
            f"Current Task: {self.context.current_task}",
        ]
        
        if self.context.developer_expertise:
            context_parts.append(f"Developer Expertise: {self.context.developer_expertise}")
            
        if self.context.project_phase:
            context_parts.append(f"Project Phase: {self.context.project_phase}")
            
        if self.context.performance_requirements:
            context_parts.append("\nPerformance Requirements:")
            for key, value in self.context.performance_requirements.items():
                context_parts.append(f"- {key}: {value}")
                
        if self.context.security_requirements:
            context_parts.append("\nSecurity Requirements:")
            for key, value in self.context.security_requirements.items():
                context_parts.append(f"- {key}: {value}")
                
        if self.context.project_metadata:
            context_parts.append("\nProject Metadata:")
            for key, value in self.context.project_metadata.items():
                context_parts.append(f"- {key}: {value}")
                
        context_parts.extend([
            "\nAvailable Tools:",
            self._format_tools(self.context.available_tools),
            "\nCode Context:",
            self._format_code_context(self.context.code_context),
            "\nPrevious Interactions:",
            self._format_interactions(self.context.previous_interactions)
        ])
        
        return "\n".join(context_parts)
        
    def _generate_custom_instructions(self) -> str:
        """Generate custom instruction modifications."""
        if not self.context or not self.context.custom_instructions:
            return ""
            
        custom_parts = ["Custom Instructions:"]
        for key, value in self.context.custom_instructions.items():
            custom_parts.append(f"{key}:")
            custom_parts.append(value)
            
        return "\n".join(custom_parts)
        
    def _generate_metadata_prompt(self) -> str:
        """Generate metadata and formatting information."""
        if not self.context:
            return ""
            
        metadata_parts = []
        
        if self.formatting_options["include_timestamps"] and self.context.timestamp:
            metadata_parts.append(f"Timestamp: {self.context.timestamp}")
            
        if self.formatting_options["include_session_id"] and self.context.session_id:
            metadata_parts.append(f"Session ID: {self.context.session_id}")
            
        if self.formatting_options["include_metrics"] and self.context.success_metrics:
            metadata_parts.append("\nSuccess Metrics:")
            for key, value in self.context.success_metrics.items():
                metadata_parts.append(f"- {key}: {value}")
                
        if self.formatting_options["include_error_history"] and self.context.error_history:
            metadata_parts.append("\nError History:")
            for error in self.context.error_history:
                metadata_parts.append(f"- {error.get('type', 'Unknown')}: {error.get('message', 'No message')}")
                
        if self.formatting_options["include_tool_configs"] and self.context.tool_configurations:
            metadata_parts.append("\nTool Configurations:")
            for tool, config in self.context.tool_configurations.items():
                metadata_parts.append(f"- {tool}:")
                for key, value in config.items():
                    metadata_parts.append(f"  {key}: {value}")
                    
        if self.formatting_options["include_summary"]:
            metadata_parts.append("\nSession Summary:")
            metadata_parts.append(f"- Total Interactions: {len(self.context.previous_interactions)}")
            metadata_parts.append(f"- Current Task: {self.context.current_task}")
            metadata_parts.append(f"- Project Phase: {self.context.project_phase or 'Not specified'}")
            
        return "\n".join(metadata_parts)
        
    def _format_tools(self, tools: List[str]) -> str:
        """Format the list of available tools."""
        if not tools:
            return "No tools available"
        return "\n".join(f"- {tool}" for tool in tools)
        
    def _format_code_context(self, context: Optional[Dict[str, str]]) -> str:
        """Format the code context information."""
        if not context:
            return "No code context available"
        return "\n".join(f"- {key}: {value}" for key, value in context.items())
        
    def _format_interactions(self, interactions: List[str]) -> str:
        """Format the previous interactions."""
        if not interactions:
            return "No previous interactions"
        return "\n".join(f"- {interaction}" for interaction in interactions)
        
    def get_context_history(self) -> List[PromptContext]:
        """Get the history of contexts."""
        return self.context_history
        
    def clear_context_history(self):
        """Clear the context history."""
        self.context_history = []
        
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session."""
        if not self.context:
            return {}
            
        return {
            "session_id": self.context.session_id,
            "start_time": self.context.timestamp,
            "project_type": self.context.project_type,
            "programming_language": self.context.programming_language,
            "current_task": self.context.current_task,
            "total_interactions": len(self.context.previous_interactions),
            "success_metrics": self.context.success_metrics,
            "error_count": len(self.context.error_history) if self.context.error_history else 0
        } 