from typing import Dict, Any, List, Optional
import os
import re
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
from .base import BaseDocumentationGenerator
from ...config.logging_config import logger

class KnowledgeDocumentationGenerator(BaseDocumentationGenerator):
    """Generator for knowledge base documentation"""
    
    def __init__(self, output_dir: str = "docs"):
        super().__init__(output_dir)
        self.sections = {
            "templates": [],
            "visualizations": [],
            "language_features": [],
            "system_docs": []
        }
        
    def generate_knowledge_docs(self, source_dir: str, config: Dict[str, Any] = None):
        """Generate knowledge base documentation"""
        try:
            self.create_output_dirs()
            source_path = Path(source_dir)
            config = config or {}
            
            # Generate documentation sections
            self._generate_template_docs()
            self._generate_visualization_docs()
            self._generate_language_feature_docs()
            self._generate_system_docs()
            
            # Generate navigation and index
            self._generate_knowledge_navigation()
            self._generate_knowledge_index()
            
            logger.info("Knowledge documentation generated successfully")
            
        except Exception as e:
            logger.error(f"Error generating knowledge documentation: {str(e)}")
            raise
            
    def _generate_template_docs(self):
        """Generate template documentation"""
        try:
            template = self.load_template("template_docs.md")
            content = template.render(
                version_info=self.generate_version_info(),
                templates=self._get_template_examples(),
                best_practices=self._get_template_best_practices()
            )
            self.save_file(content, "knowledge/templates.md")
            self.sections["templates"].append("templates.md")
            
        except Exception as e:
            logger.error(f"Error generating template documentation: {str(e)}")
            raise
            
    def _get_template_examples(self) -> List[Dict[str, Any]]:
        """Get template examples"""
        try:
            return [
                {
                    "name": "API Documentation",
                    "description": "Template for API endpoint documentation",
                    "example": """
```markdown
# {{ endpoint.name }}

## Description
{{ endpoint.description }}

## Parameters
{% for param in endpoint.parameters %}
- {{ param.name }} ({{ param.type }}): {{ param.description }}
{% endfor %}

## Response
{% for response in endpoint.responses %}
### {{ response.status_code }}
{{ response.description }}
{% endfor %}
```
"""
                },
                {
                    "name": "Code Documentation",
                    "description": "Template for code documentation",
                    "example": """
```markdown
# {{ class.name }}

## Description
{{ class.docstring }}

## Methods
{% for method in class.methods %}
### {{ method.name }}
{{ method.docstring }}
{% endfor %}
```
"""
                },
                {
                    "name": "Architecture Documentation",
                    "description": "Template for architecture documentation",
                    "example": """
```markdown
# {{ component.name }}

## Overview
{{ component.description }}

## Dependencies
{% for dep in component.dependencies %}
- {{ dep }}
{% endfor %}

## Data Flow
{% for flow in component.data_flows %}
### {{ flow.name }}
{{ flow.description }}
{% endfor %}
```
"""
                }
            ]
        except Exception as e:
            logger.error(f"Error getting template examples: {str(e)}")
            return []
            
    def _get_template_best_practices(self) -> List[Dict[str, Any]]:
        """Get template best practices"""
        try:
            return [
                {
                    "category": "Structure",
                    "practices": [
                        "Use clear and consistent headings",
                        "Include a table of contents",
                        "Organize content logically",
                        "Use appropriate heading levels"
                    ]
                },
                {
                    "category": "Content",
                    "practices": [
                        "Write clear and concise descriptions",
                        "Include code examples where appropriate",
                        "Use consistent terminology",
                        "Keep content up to date"
                    ]
                },
                {
                    "category": "Formatting",
                    "practices": [
                        "Use markdown formatting consistently",
                        "Include proper code block syntax highlighting",
                        "Use tables for structured data",
                        "Include diagrams and visualizations"
                    ]
                }
            ]
        except Exception as e:
            logger.error(f"Error getting template best practices: {str(e)}")
            return []
            
    def _generate_visualization_docs(self):
        """Generate visualization documentation"""
        try:
            template = self.load_template("visualization_docs.md")
            content = template.render(
                version_info=self.generate_version_info(),
                visualizations=self._get_visualization_examples(),
                tools=self._get_visualization_tools()
            )
            self.save_file(content, "knowledge/visualizations.md")
            self.sections["visualizations"].append("visualizations.md")
            
        except Exception as e:
            logger.error(f"Error generating visualization documentation: {str(e)}")
            raise
            
    def _get_visualization_examples(self) -> List[Dict[str, Any]]:
        """Get visualization examples"""
        try:
            return [
                {
                    "name": "Component Diagram",
                    "description": "Visualize system components and their relationships",
                    "code": """
```python
import networkx as nx
import matplotlib.pyplot as plt

def create_component_diagram(components, relationships):
    G = nx.DiGraph()
    
    # Add nodes
    for component in components:
        G.add_node(component.name, **component)
        
    # Add edges
    for rel in relationships:
        G.add_edge(rel.source, rel.target, **rel)
        
    # Draw diagram
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True)
    plt.savefig('component_diagram.png')
```
"""
                },
                {
                    "name": "Performance Metrics",
                    "description": "Visualize performance metrics over time",
                    "code": """
```python
import plotly.express as px

def create_performance_chart(metrics_data):
    df = pd.DataFrame(metrics_data)
    fig = px.line(df, x='timestamp', y=['cpu', 'memory', 'disk'],
                  title='System Performance Metrics')
    fig.write_html('performance_chart.html')
```
"""
                },
                {
                    "name": "Code Coverage",
                    "description": "Visualize code coverage statistics",
                    "code": """
```python
import plotly.graph_objects as go

def create_coverage_chart(coverage_data):
    fig = go.Figure(data=[
        go.Bar(name='Covered', x=coverage_data['files'], y=coverage_data['covered']),
        go.Bar(name='Uncovered', x=coverage_data['files'], y=coverage_data['uncovered'])
    ])
    fig.update_layout(title='Code Coverage by File')
    fig.write_html('coverage_chart.html')
```
"""
                }
            ]
        except Exception as e:
            logger.error(f"Error getting visualization examples: {str(e)}")
            return []
            
    def _get_visualization_tools(self) -> List[Dict[str, Any]]:
        """Get visualization tools"""
        try:
            return [
                {
                    "name": "Plotly",
                    "description": "Interactive visualization library",
                    "features": [
                        "Interactive charts",
                        "Multiple chart types",
                        "Export to HTML",
                        "Custom styling"
                    ]
                },
                {
                    "name": "NetworkX",
                    "description": "Graph visualization library",
                    "features": [
                        "Directed and undirected graphs",
                        "Layout algorithms",
                        "Node and edge attributes",
                        "Export to various formats"
                    ]
                },
                {
                    "name": "Matplotlib",
                    "description": "Static visualization library",
                    "features": [
                        "Basic plotting",
                        "Custom styling",
                        "Multiple backends",
                        "Export to various formats"
                    ]
                }
            ]
        except Exception as e:
            logger.error(f"Error getting visualization tools: {str(e)}")
            return []
            
    def _generate_language_feature_docs(self):
        """Generate language-specific feature documentation"""
        try:
            template = self.load_template("language_features.md")
            content = template.render(
                version_info=self.generate_version_info(),
                languages=self._get_language_features()
            )
            self.save_file(content, "knowledge/language_features.md")
            self.sections["language_features"].append("language_features.md")
            
        except Exception as e:
            logger.error(f"Error generating language feature documentation: {str(e)}")
            raise
            
    def _get_language_features(self) -> List[Dict[str, Any]]:
        """Get language-specific features"""
        try:
            return [
                {
                    "name": "Python",
                    "features": [
                        {
                            "name": "Type Hints",
                            "description": "Static type checking support",
                            "example": """
```python
def process_data(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    result = {}
    for item in data:
        result[item['id']] = item['value']
    return result
```
"""
                        },
                        {
                            "name": "Decorators",
                            "description": "Function and class decorators",
                            "example": """
```python
def cache_result(func):
    cache = {}
    def wrapper(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result
    return wrapper
```
"""
                        }
                    ]
                },
                {
                    "name": "JavaScript",
                    "features": [
                        {
                            "name": "Async/Await",
                            "description": "Asynchronous programming support",
                            "example": """
```javascript
async function fetchData() {
    try {
        const response = await fetch('api/data');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error:', error);
    }
}
```
"""
                        },
                        {
                            "name": "Classes",
                            "description": "Object-oriented programming support",
                            "example": """
```javascript
class User {
    constructor(name, email) {
        this.name = name;
        this.email = email;
    }
    
    getInfo() {
        return `${this.name} (${this.email})`;
    }
}
```
"""
                        }
                    ]
                }
            ]
        except Exception as e:
            logger.error(f"Error getting language features: {str(e)}")
            return []
            
    def _generate_system_docs(self):
        """Generate system documentation"""
        try:
            template = self.load_template("system_docs.md")
            content = template.render(
                version_info=self.generate_version_info(),
                architecture=self._get_system_architecture(),
                components=self._get_system_components(),
                workflows=self._get_system_workflows()
            )
            self.save_file(content, "knowledge/system.md")
            self.sections["system_docs"].append("system.md")
            
        except Exception as e:
            logger.error(f"Error generating system documentation: {str(e)}")
            raise
            
    def _get_system_architecture(self) -> Dict[str, Any]:
        """Get system architecture information"""
        try:
            return {
                "overview": "The documentation system consists of multiple generators for different types of documentation",
                "components": [
                    {
                        "name": "Base Generator",
                        "description": "Core functionality for all documentation generators",
                        "features": [
                            "Template management",
                            "File operations",
                            "Version control",
                            "Configuration handling"
                        ]
                    },
                    {
                        "name": "API Generator",
                        "description": "Generates API documentation",
                        "features": [
                            "OpenAPI/Swagger",
                            "Interactive documentation",
                            "Example generation",
                            "Version history"
                        ]
                    },
                    {
                        "name": "Code Generator",
                        "description": "Generates code documentation",
                        "features": [
                            "Multi-language support",
                            "Code analysis",
                            "Documentation extraction",
                            "Example generation"
                        ]
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Error getting system architecture: {str(e)}")
            return {}
            
    def _get_system_components(self) -> List[Dict[str, Any]]:
        """Get system components information"""
        try:
            return [
                {
                    "name": "Template Engine",
                    "description": "Jinja2-based template rendering",
                    "features": [
                        "Template inheritance",
                        "Macro support",
                        "Filter support",
                        "Auto-escaping"
                    ]
                },
                {
                    "name": "Code Analyzer",
                    "description": "Code analysis and documentation extraction",
                    "features": [
                        "AST parsing",
                        "Comment extraction",
                        "Type inference",
                        "Dependency analysis"
                    ]
                },
                {
                    "name": "Visualization Engine",
                    "description": "Documentation visualization tools",
                    "features": [
                        "Interactive charts",
                        "Component diagrams",
                        "Performance visualizations",
                        "Custom styling"
                    ]
                }
            ]
        except Exception as e:
            logger.error(f"Error getting system components: {str(e)}")
            return []
            
    def _get_system_workflows(self) -> List[Dict[str, Any]]:
        """Get system workflows"""
        try:
            return [
                {
                    "name": "Documentation Generation",
                    "steps": [
                        "Load configuration",
                        "Create output directories",
                        "Generate documentation",
                        "Validate output",
                        "Save files"
                    ]
                },
                {
                    "name": "Template Processing",
                    "steps": [
                        "Load template",
                        "Prepare context",
                        "Render template",
                        "Validate output",
                        "Save result"
                    ]
                },
                {
                    "name": "Code Analysis",
                    "steps": [
                        "Parse code",
                        "Extract information",
                        "Analyze dependencies",
                        "Generate documentation",
                        "Save results"
                    ]
                }
            ]
        except Exception as e:
            logger.error(f"Error getting system workflows: {str(e)}")
            return []
            
    def _generate_knowledge_navigation(self):
        """Generate navigation for knowledge documentation"""
        try:
            template = self.load_template("knowledge_navigation.md")
            content = template.render(
                sections=self.sections,
                version_info=self.generate_version_info()
            )
            self.save_file(content, "knowledge/navigation.md")
        except Exception as e:
            logger.error(f"Error generating knowledge navigation: {str(e)}")
            raise
            
    def _generate_knowledge_index(self):
        """Generate index for knowledge documentation"""
        try:
            template = self.load_template("knowledge_index.md")
            content = template.render(
                sections=self.sections,
                version_info=self.generate_version_info()
            )
            self.save_file(content, "knowledge/index.md")
        except Exception as e:
            logger.error(f"Error generating knowledge index: {str(e)}")
            raise 