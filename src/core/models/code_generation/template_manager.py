from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import os
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template

logger = logging.getLogger(__name__)

@dataclass
class CodeTemplate:
    """Template for code generation"""
    name: str
    description: str
    content: str
    parameters: Dict[str, Any]
    tags: List[str]
    language: str
    category: str
    version: str
    author: str
    created_at: datetime
    updated_at: datetime

class TemplateManager:
    """Manager for code generation templates"""
    
    def __init__(self, templates_dir: str):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize template environment
        self.template_env = Environment(
            loader=FileSystemLoader(templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Load templates
        self.templates: Dict[str, CodeTemplate] = {}
        self._load_templates()
        
    def _load_templates(self) -> None:
        """Load all templates from the templates directory"""
        try:
            for template_file in self.templates_dir.glob("**/*.yaml"):
                with open(template_file) as f:
                    template_data = yaml.safe_load(f)
                    
                template = CodeTemplate(
                    name=template_data["name"],
                    description=template_data["description"],
                    content=template_data["content"],
                    parameters=template_data["parameters"],
                    tags=template_data["tags"],
                    language=template_data["language"],
                    category=template_data["category"],
                    version=template_data["version"],
                    author=template_data["author"],
                    created_at=datetime.fromisoformat(template_data["created_at"]),
                    updated_at=datetime.fromisoformat(template_data["updated_at"])
                )
                
                self.templates[template.name] = template
                
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
            
    async def select_template(
        self,
        requirements: str,
        analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> CodeTemplate:
        """Select appropriate template based on requirements and context"""
        # Filter templates by language and category
        language = context["language"]
        project_type = context.get("project_type")
        
        candidates = [
            template for template in self.templates.values()
            if template.language == language
            and (not project_type or project_type in template.tags)
        ]
        
        if not candidates:
            raise ValueError(f"No templates found for language: {language}")
            
        # Score candidates based on requirements and analysis
        scored_candidates = []
        for template in candidates:
            score = await self._score_template(
                template,
                requirements,
                analysis,
                context
            )
            scored_candidates.append((template, score))
            
        # Select best template
        best_template = max(scored_candidates, key=lambda x: x[1])[0]
        return best_template
        
    async def _score_template(
        self,
        template: CodeTemplate,
        requirements: str,
        analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """Score a template based on requirements and context"""
        score = 0.0
        
        # Check if template parameters match requirements
        required_params = set(analysis.get("components", []))
        template_params = set(template.parameters.keys())
        param_match = len(required_params.intersection(template_params)) / len(required_params)
        score += param_match * 0.4
        
        # Check if template patterns match analysis
        required_patterns = set(analysis.get("patterns", []))
        template_patterns = set(template.tags)
        pattern_match = len(required_patterns.intersection(template_patterns)) / len(required_patterns)
        score += pattern_match * 0.3
        
        # Check if template matches project type
        if context.get("project_type") in template.tags:
            score += 0.2
            
        # Check if template matches architecture
        if context.get("architecture") in template.tags:
            score += 0.1
            
        return score
        
    async def generate_code(
        self,
        template: CodeTemplate,
        parameters: Dict[str, Any]
    ) -> str:
        """Generate code using a template"""
        try:
            # Create template from content
            template_obj = self.template_env.from_string(template.content)
            
            # Validate parameters
            self._validate_parameters(template, parameters)
            
            # Generate code
            code = template_obj.render(**parameters)
            
            return code
            
        except Exception as e:
            logger.error(f"Failed to generate code from template: {e}")
            raise
            
    def _validate_parameters(
        self,
        template: CodeTemplate,
        parameters: Dict[str, Any]
    ) -> None:
        """Validate template parameters"""
        required_params = {
            name for name, param in template.parameters.items()
            if param.get("required", True)
        }
        
        missing_params = required_params - set(parameters.keys())
        if missing_params:
            raise ValueError(f"Missing required parameters: {missing_params}")
            
    async def create_template(
        self,
        name: str,
        description: str,
        content: str,
        parameters: Dict[str, Any],
        tags: List[str],
        language: str,
        category: str,
        author: str
    ) -> CodeTemplate:
        """Create a new template"""
        template = CodeTemplate(
            name=name,
            description=description,
            content=content,
            parameters=parameters,
            tags=tags,
            language=language,
            category=category,
            version="1.0.0",
            author=author,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save template
        template_file = self.templates_dir / f"{name}.yaml"
        with open(template_file, 'w') as f:
            yaml.dump(
                {
                    "name": template.name,
                    "description": template.description,
                    "content": template.content,
                    "parameters": template.parameters,
                    "tags": template.tags,
                    "language": template.language,
                    "category": template.category,
                    "version": template.version,
                    "author": template.author,
                    "created_at": template.created_at.isoformat(),
                    "updated_at": template.updated_at.isoformat()
                },
                f,
                indent=2
            )
            
        self.templates[name] = template
        return template
        
    async def update_template(
        self,
        name: str,
        updates: Dict[str, Any]
    ) -> CodeTemplate:
        """Update an existing template"""
        if name not in self.templates:
            raise ValueError(f"Template not found: {name}")
            
        template = self.templates[name]
        
        # Update template fields
        for field, value in updates.items():
            if hasattr(template, field):
                setattr(template, field, value)
                
        template.updated_at = datetime.now()
        
        # Save updated template
        template_file = self.templates_dir / f"{name}.yaml"
        with open(template_file, 'w') as f:
            yaml.dump(
                {
                    "name": template.name,
                    "description": template.description,
                    "content": template.content,
                    "parameters": template.parameters,
                    "tags": template.tags,
                    "language": template.language,
                    "category": template.category,
                    "version": template.version,
                    "author": template.author,
                    "created_at": template.created_at.isoformat(),
                    "updated_at": template.updated_at.isoformat()
                },
                f,
                indent=2
            )
            
        return template
        
    async def delete_template(self, name: str) -> None:
        """Delete a template"""
        if name not in self.templates:
            raise ValueError(f"Template not found: {name}")
            
        # Delete template file
        template_file = self.templates_dir / f"{name}.yaml"
        if template_file.exists():
            template_file.unlink()
            
        # Remove from templates dict
        del self.templates[name] 