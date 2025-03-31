from typing import Dict, Any, List, Optional
import os
import json
import yaml
import re
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from ...config.logging_config import logger

class BaseDocumentationGenerator:
    """Base class for all documentation generators"""
    
    def __init__(self, output_dir: str = "docs"):
        self.output_dir = Path(output_dir)
        self.template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True
        )
        self.version = "1.0.0"
        self.last_updated = datetime.utcnow().isoformat()
        
    def create_output_dirs(self):
        """Create necessary output directories"""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            (self.output_dir / "api").mkdir(exist_ok=True)
            (self.output_dir / "code").mkdir(exist_ok=True)
            (self.output_dir / "architecture").mkdir(exist_ok=True)
            (self.output_dir / "user").mkdir(exist_ok=True)
            (self.output_dir / "knowledge").mkdir(exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating output directories: {str(e)}")
            raise
            
    def load_template(self, template_name: str) -> str:
        """Load a template file"""
        try:
            return self.env.get_template(template_name)
        except Exception as e:
            logger.error(f"Error loading template {template_name}: {str(e)}")
            raise
            
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with context"""
        try:
            template = self.load_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {str(e)}")
            raise
            
    def save_file(self, content: str, filepath: str):
        """Save content to a file"""
        try:
            filepath = self.output_dir / filepath
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Saved documentation to {filepath}")
        except Exception as e:
            logger.error(f"Error saving file {filepath}: {str(e)}")
            raise
            
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config {config_path}: {str(e)}")
            raise
            
    def save_config(self, config: Dict[str, Any], config_path: str):
        """Save configuration to YAML file"""
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Error saving config {config_path}: {str(e)}")
            raise
            
    def extract_code_comments(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract code comments from a file"""
        try:
            comments = []
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines):
                # Check for single-line comments
                if '#' in line:
                    comment = line[line.index('#'):].strip()
                    if comment:
                        comments.append({
                            "line": i + 1,
                            "type": "single",
                            "content": comment
                        })
                        
                # Check for multi-line comments
                if '"""' in line or "'''" in line:
                    comment_lines = []
                    j = i + 1
                    while j < len(lines) and ('"""' not in lines[j] and "'''" not in lines[j]):
                        comment_lines.append(lines[j].strip())
                        j += 1
                    if comment_lines:
                        comments.append({
                            "line": i + 1,
                            "type": "multi",
                            "content": "\n".join(comment_lines)
                        })
                        
            return comments
        except Exception as e:
            logger.error(f"Error extracting comments from {file_path}: {str(e)}")
            return []
            
    def generate_version_info(self) -> Dict[str, Any]:
        """Generate version information"""
        return {
            "version": self.version,
            "last_updated": self.last_updated,
            "generator": self.__class__.__name__,
            "environment": {
                "python_version": os.sys.version,
                "platform": os.sys.platform
            }
        }
        
    def validate_documentation(self, content: str, doc_type: str) -> bool:
        """Validate generated documentation"""
        try:
            # Basic validation rules
            if not content or len(content.strip()) == 0:
                logger.error(f"Empty documentation generated for {doc_type}")
                return False
                
            # Check for required sections based on doc_type
            required_sections = {
                "api": ["endpoints", "parameters", "responses"],
                "code": ["classes", "functions", "examples"],
                "architecture": ["components", "relationships", "data_flow"],
                "user": ["installation", "usage", "troubleshooting"],
                "knowledge": ["snippets", "best_practices", "patterns"]
            }
            
            if doc_type in required_sections:
                for section in required_sections[doc_type]:
                    if section not in content.lower():
                        logger.warning(f"Missing required section '{section}' in {doc_type} documentation")
                        
            return True
        except Exception as e:
            logger.error(f"Error validating documentation: {str(e)}")
            return False
            
    def update_documentation(self, content: str, doc_type: str, filepath: str):
        """Update documentation with version control"""
        try:
            # Create backup of existing documentation
            if os.path.exists(filepath):
                backup_path = f"{filepath}.{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.bak"
                os.rename(filepath, backup_path)
                
            # Save new documentation
            self.save_file(content, filepath)
            
            # Update version history
            version_history = self.load_version_history(doc_type)
            version_history.append({
                "version": self.version,
                "timestamp": self.last_updated,
                "filepath": filepath
            })
            self.save_version_history(doc_type, version_history)
            
        except Exception as e:
            logger.error(f"Error updating documentation: {str(e)}")
            raise
            
    def load_version_history(self, doc_type: str) -> List[Dict[str, Any]]:
        """Load version history for documentation type"""
        try:
            history_file = self.output_dir / f"{doc_type}_version_history.json"
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading version history: {str(e)}")
            return []
            
    def save_version_history(self, doc_type: str, history: List[Dict[str, Any]]):
        """Save version history for documentation type"""
        try:
            history_file = self.output_dir / f"{doc_type}_version_history.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving version history: {str(e)}")
            raise 