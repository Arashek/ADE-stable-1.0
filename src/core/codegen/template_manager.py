from typing import Dict, List, Optional, Set
import logging
from pathlib import Path
import json
import yaml
import jinja2
from dataclasses import dataclass
import re
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class TemplateMetadata:
    """Metadata for code generation templates"""
    name: str
    description: str
    language: str
    framework: Optional[str]
    category: str
    tags: List[str]
    dependencies: List[str]
    context_vars: List[str]
    examples: List[Dict]

class TemplateManager:
    """Manages code generation templates and their execution"""
    
    def __init__(self):
        self._load_config()
        self._setup_templates()
        self._template_cache = {}
        self._context_patterns = defaultdict(list)
        
    def _load_config(self) -> None:
        """Load template manager configuration"""
        try:
            config_path = Path("src/core/codegen/config/templates.yaml")
            if config_path.exists():
                with open(config_path, "r") as f:
                    self.config = yaml.safe_load(f)
            else:
                logger.warning("Template configuration not found")
                self.config = {}
                
        except Exception as e:
            logger.error(f"Error loading template configuration: {str(e)}")
            self.config = {}
            
    def _setup_templates(self) -> None:
        """Setup template environment and load templates"""
        try:
            # Create template loader
            template_dir = Path("src/core/codegen/templates")
            self.env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(template_dir),
                trim_blocks=True,
                lstrip_blocks=True
            )
            
            # Load template metadata
            self._load_template_metadata()
            
            # Setup context patterns
            self._setup_context_patterns()
            
        except Exception as e:
            logger.error(f"Error setting up templates: {str(e)}")
            
    def _load_template_metadata(self) -> None:
        """Load metadata for all templates"""
        try:
            metadata_dir = Path("src/core/codegen/templates/metadata")
            self.template_metadata = {}
            
            for metadata_file in metadata_dir.glob("*.yaml"):
                with open(metadata_file, "r") as f:
                    metadata = yaml.safe_load(f)
                    self.template_metadata[metadata["name"]] = TemplateMetadata(**metadata)
                    
        except Exception as e:
            logger.error(f"Error loading template metadata: {str(e)}")
            self.template_metadata = {}
            
    def _setup_context_patterns(self) -> None:
        """Setup patterns for context-aware suggestions"""
        try:
            patterns_dir = Path("src/core/codegen/patterns")
            
            for pattern_file in patterns_dir.glob("*.json"):
                with open(pattern_file, "r") as f:
                    patterns = json.load(f)
                    self._context_patterns[pattern_file.stem] = patterns
                    
        except Exception as e:
            logger.error(f"Error setting up context patterns: {str(e)}")
            
    def get_available_templates(self, language: Optional[str] = None, 
                              framework: Optional[str] = None) -> List[TemplateMetadata]:
        """Get available templates filtered by language and framework"""
        try:
            templates = list(self.template_metadata.values())
            
            if language:
                templates = [t for t in templates if t.language == language]
                
            if framework:
                templates = [t for t in templates if t.framework == framework]
                
            return templates
            
        except Exception as e:
            logger.error(f"Error getting available templates: {str(e)}")
            return []
            
    def generate_code(self, template_name: str, context: Dict) -> str:
        """Generate code from a template with given context"""
        try:
            # Get template metadata
            metadata = self.template_metadata.get(template_name)
            if not metadata:
                raise ValueError(f"Template {template_name} not found")
                
            # Validate context variables
            missing_vars = set(metadata.context_vars) - set(context.keys())
            if missing_vars:
                raise ValueError(f"Missing required context variables: {missing_vars}")
                
            # Get or load template
            if template_name not in self._template_cache:
                self._template_cache[template_name] = self.env.get_template(f"{template_name}.jinja2")
                
            template = self._template_cache[template_name]
            
            # Generate code
            return template.render(**context)
            
        except Exception as e:
            logger.error(f"Error generating code from template {template_name}: {str(e)}")
            raise
            
    def get_context_suggestions(self, code_context: str, language: str) -> List[Dict]:
        """Get context-aware code suggestions"""
        try:
            suggestions = []
            
            # Get patterns for language
            patterns = self._context_patterns.get(language, [])
            
            # Analyze code context
            for pattern in patterns:
                matches = re.finditer(pattern["regex"], code_context)
                for match in matches:
                    suggestion = {
                        "pattern": pattern["name"],
                        "description": pattern["description"],
                        "code": pattern["suggestion"],
                        "context": match.group(0),
                        "position": match.start()
                    }
                    suggestions.append(suggestion)
                    
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting context suggestions: {str(e)}")
            return []
            
    def learn_from_codebase(self, codebase_path: str) -> None:
        """Learn patterns from existing codebase"""
        try:
            codebase_dir = Path(codebase_path)
            
            # Analyze code files
            for file_path in codebase_dir.rglob("*"):
                if file_path.suffix in [".py", ".js", ".ts", ".java", ".cs", ".go", ".php"]:
                    with open(file_path, "r") as f:
                        code = f.read()
                        
                    # Extract patterns
                    language = file_path.suffix[1:]
                    patterns = self._extract_patterns(code, language)
                    
                    # Update context patterns
                    self._context_patterns[language].extend(patterns)
                    
            # Save updated patterns
            self._save_patterns()
            
        except Exception as e:
            logger.error(f"Error learning from codebase: {str(e)}")
            
    def _extract_patterns(self, code: str, language: str) -> List[Dict]:
        """Extract patterns from code"""
        try:
            patterns = []
            
            # Common patterns to look for
            common_patterns = [
                (r"class\s+(\w+)\s*:", "class_definition"),
                (r"def\s+(\w+)\s*\(", "function_definition"),
                (r"interface\s+(\w+)\s*{", "interface_definition"),
                (r"enum\s+(\w+)\s*{", "enum_definition"),
                (r"struct\s+(\w+)\s*{", "struct_definition"),
                (r"try\s*{", "try_block"),
                (r"catch\s*\([^)]+\)\s*{", "catch_block"),
                (r"finally\s*{", "finally_block"),
                (r"if\s*\([^)]+\)\s*{", "if_statement"),
                (r"for\s*\([^)]+\)\s*{", "for_loop"),
                (r"while\s*\([^)]+\)\s*{", "while_loop"),
                (r"switch\s*\([^)]+\)\s*{", "switch_statement"),
                (r"case\s+[^:]+:", "case_statement")
            ]
            
            for pattern, name in common_patterns:
                matches = re.finditer(pattern, code)
                for match in matches:
                    patterns.append({
                        "name": name,
                        "regex": pattern,
                        "description": f"Common {name} pattern",
                        "suggestion": match.group(0)
                    })
                    
            return patterns
            
        except Exception as e:
            logger.error(f"Error extracting patterns: {str(e)}")
            return []
            
    def _save_patterns(self) -> None:
        """Save learned patterns to files"""
        try:
            patterns_dir = Path("src/core/codegen/patterns")
            patterns_dir.mkdir(parents=True, exist_ok=True)
            
            for language, patterns in self._context_patterns.items():
                with open(patterns_dir / f"{language}.json", "w") as f:
                    json.dump(patterns, f, indent=2)
                    
        except Exception as e:
            logger.error(f"Error saving patterns: {str(e)}")
            
    def get_template_examples(self, template_name: str) -> List[Dict]:
        """Get example usages for a template"""
        try:
            metadata = self.template_metadata.get(template_name)
            if not metadata:
                return []
                
            return metadata.examples
            
        except Exception as e:
            logger.error(f"Error getting template examples: {str(e)}")
            return [] 