from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import numpy as np
from collections import defaultdict
import ast
import inspect

from .llm_integration import LLMIntegration, LLMConfig
from .code_context_manager import CodeContextManager

logger = logging.getLogger(__name__)

@dataclass
class Documentation:
    type: str  # function, class, module, etc.
    file_path: str
    line_numbers: List[int]
    content: str
    description: str
    parameters: List[Dict[str, str]]
    returns: Optional[str]
    examples: List[str]
    references: List[str]
    confidence: float
    context: Dict[str, Any]
    created_at: datetime = datetime.now()
    metadata: Dict[str, Any] = None

class DocumentationGenerator:
    def __init__(self, llm_config: LLMConfig, context_manager: CodeContextManager):
        self.llm = LLMIntegration(llm_config)
        self.context_manager = context_manager
        self.doc_patterns: Dict[str, List[Dict[str, Any]]] = self._load_patterns()
        self.recent_docs: Dict[str, List[Documentation]] = defaultdict(list)
        
    def _load_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load documentation patterns from configuration"""
        patterns = defaultdict(list)
        try:
            pattern_file = Path("config/documentation_patterns.json")
            if pattern_file.exists():
                with open(pattern_file) as f:
                    data = json.load(f)
                    for pattern_type, pattern_list in data.items():
                        patterns[pattern_type] = pattern_list
        except Exception as e:
            logger.error(f"Failed to load documentation patterns: {e}")
        return patterns
        
    async def generate_documentation(self, file_path: str, content: str) -> List[Documentation]:
        """Generate documentation for code"""
        try:
            # Update code context
            await self.context_manager.update_context(file_path, content)
            
            # Get code context
            context = await self.context_manager.get_code_context(file_path)
            if not context:
                return []
                
            docs = []
            
            # Parse code to identify documentation targets
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                    # Generate documentation for each target
                    doc = await self._generate_doc_for_node(node, content, context)
                    if doc:
                        docs.append(doc)
            
            # Filter and sort documentation
            filtered_docs = self._filter_documentation(docs)
            sorted_docs = self._sort_documentation(filtered_docs)
            
            # Store recent documentation
            self._store_recent_docs(file_path, sorted_docs)
            
            return sorted_docs
            
        except Exception as e:
            logger.error(f"Failed to generate documentation: {e}")
            return []
            
    async def _generate_doc_for_node(self, node: ast.AST, content: str, context: Any) -> Optional[Documentation]:
        """Generate documentation for a specific AST node"""
        try:
            # Get node type and name
            node_type = type(node).__name__.lower()
            node_name = getattr(node, 'name', 'module')
            
            # Get node content and line numbers
            node_content = ast.get_source_segment(content, node)
            line_numbers = list(range(node.lineno, node.end_lineno + 1))
            
            # Prepare prompt for LLM
            prompt = self._prepare_llm_prompt(node_type, node_name, node_content, context)
            
            # Get documentation from LLM
            response = await self.llm.generate_documentation(prompt)
            
            if response:
                # Parse LLM response into documentation
                doc = self._parse_llm_response(response, node_type, node_name, line_numbers, context)
                return doc
                
        except Exception as e:
            logger.error(f"Failed to generate documentation for node: {e}")
            
        return None
        
    def _filter_documentation(self, docs: List[Documentation]) -> List[Documentation]:
        """Filter out duplicate or low-quality documentation"""
        filtered = []
        seen = set()
        
        for doc in docs:
            # Create unique key for documentation
            key = f"{doc.type}_{doc.file_path}_{doc.line_numbers}_{doc.description}"
            
            # Skip if we've seen this documentation before
            if key in seen:
                continue
                
            # Skip low confidence documentation
            if doc.confidence < 0.6:
                continue
                
            seen.add(key)
            filtered.append(doc)
            
        return filtered
        
    def _sort_documentation(self, docs: List[Documentation]) -> List[Documentation]:
        """Sort documentation by type and confidence"""
        def get_doc_score(doc: Documentation) -> float:
            score = doc.confidence
            
            # Adjust score based on type
            type_weights = {
                "class": 1.3,
                "function": 1.2,
                "module": 1.1,
                "method": 1.0
            }
            score *= type_weights.get(doc.type, 1.0)
            
            # Adjust score based on completeness
            if doc.parameters and doc.returns and doc.examples:
                score *= 1.2
                
            return score
            
        return sorted(docs, key=get_doc_score, reverse=True)
        
    def _store_recent_docs(self, file_path: str, docs: List[Documentation]):
        """Store recent documentation for future reference"""
        try:
            # Keep only the most recent 10 docs
            self.recent_docs[file_path] = docs[:10]
        except Exception as e:
            logger.error(f"Failed to store recent documentation: {e}")
            
    def _prepare_llm_prompt(self, node_type: str, node_name: str, content: str, context: Any) -> str:
        """Prepare prompt for LLM"""
        prompt = f"""Generate comprehensive documentation for the following {node_type}:

Name: {node_name}
Content:
{content}

File: {context.file_path}

Please provide:
1. A clear description of the {node_type}'s purpose
2. Parameter descriptions (if applicable)
3. Return value description (if applicable)
4. Usage examples
5. Related references or dependencies
6. Any important notes or warnings

Format the documentation in a clear, concise manner following standard documentation conventions."""
        return prompt
        
    def _parse_llm_response(self, response: Dict[str, Any], node_type: str, node_name: str, 
                          line_numbers: List[int], context: Any) -> Optional[Documentation]:
        """Parse LLM response into documentation"""
        try:
            if "documentation" in response:
                doc_data = response["documentation"]
                doc = Documentation(
                    type=node_type,
                    file_path=context.file_path,
                    line_numbers=line_numbers,
                    content=doc_data.get("content", ""),
                    description=doc_data.get("description", ""),
                    parameters=doc_data.get("parameters", []),
                    returns=doc_data.get("returns"),
                    examples=doc_data.get("examples", []),
                    references=doc_data.get("references", []),
                    confidence=doc_data.get("confidence", 0.8),
                    context={"source": "llm"},
                    metadata=doc_data.get("metadata", {})
                )
                return doc
                
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            
        return None 