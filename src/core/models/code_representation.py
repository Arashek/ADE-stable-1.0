from typing import Dict, List, Any, Optional, Set, Tuple
import logging
from dataclasses import dataclass
from enum import Enum
import tree_sitter
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel
import json
import re

logger = logging.getLogger(__name__)

class CodeNodeType(Enum):
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    VARIABLE = "variable"
    IMPORT = "import"
    STATEMENT = "statement"
    EXPRESSION = "expression"
    COMMENT = "comment"
    DOCSTRING = "docstring"

@dataclass
class CodeNode:
    type: CodeNodeType
    name: str
    content: str
    start_line: int
    end_line: int
    children: List["CodeNode"]
    metadata: Dict[str, Any]
    vector: Optional[np.ndarray] = None

class CodeRepresentationModel:
    """Advanced code representation model with neural network support."""
    
    def __init__(self, model_name: str = "microsoft/codebert-base"):
        """Initialize the code representation model."""
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.vector_dim = self.model.config.hidden_size
        
    def parse_code(self, file_path: str, content: str) -> CodeNode:
        """Parse code into a hierarchical representation."""
        try:
            # Parse code using tree-sitter
            tree = self._parse_code(file_path, content)
            
            # Build code tree
            root = self._build_code_tree(tree.root_node)
            
            # Generate vector representations
            self._generate_vectors(root)
            
            return root
            
        except Exception as e:
            logger.error(f"Error parsing code: {e}")
            raise
            
    def _parse_code(self, file_path: str, content: str) -> tree_sitter.Tree:
        """Parse code using tree-sitter."""
        language = self._detect_language(file_path)
        parser = tree_sitter.Parser()
        parser.set_language(tree_sitter.Language(f"build/{language}.so", language))
        return parser.parse(bytes(content, "utf8"))
        
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = Path(file_path).suffix.lower()
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".go": "go",
            ".rs": "rust"
        }
        return language_map.get(ext, "python")
        
    def _build_code_tree(self, node: tree_sitter.Node) -> CodeNode:
        """Build a hierarchical code tree from AST."""
        # Determine node type
        node_type = self._get_node_type(node)
        
        # Get node name
        name = self._get_node_name(node)
        
        # Get node content
        content = node.text.decode("utf8")
        
        # Build metadata
        metadata = self._build_metadata(node)
        
        # Process children
        children = []
        for child in node.children:
            child_node = self._build_code_tree(child)
            if child_node:
                children.append(child_node)
                
        return CodeNode(
            type=node_type,
            name=name,
            content=content,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            children=children,
            metadata=metadata
        )
        
    def _get_node_type(self, node: tree_sitter.Node) -> CodeNodeType:
        """Determine the type of a node."""
        type_map = {
            "module": CodeNodeType.MODULE,
            "class_definition": CodeNodeType.CLASS,
            "function_definition": CodeNodeType.FUNCTION,
            "variable_declaration": CodeNodeType.VARIABLE,
            "import_statement": CodeNodeType.IMPORT,
            "expression_statement": CodeNodeType.STATEMENT,
            "expression": CodeNodeType.EXPRESSION,
            "comment": CodeNodeType.COMMENT,
            "string": CodeNodeType.DOCSTRING
        }
        return type_map.get(node.type, CodeNodeType.STATEMENT)
        
    def _get_node_name(self, node: tree_sitter.Node) -> str:
        """Get the name of a node."""
        if node.type in ["class_definition", "function_definition"]:
            name_node = node.child_by_field_name("name")
            if name_node:
                return name_node.text.decode("utf8")
        elif node.type == "variable_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                return name_node.text.decode("utf8")
        return node.type
        
    def _build_metadata(self, node: tree_sitter.Node) -> Dict[str, Any]:
        """Build metadata for a node."""
        metadata = {}
        
        if node.type == "function_definition":
            # Extract parameters
            params_node = node.child_by_field_name("parameters")
            if params_node:
                metadata["parameters"] = [
                    param.text.decode("utf8")
                    for param in params_node.children
                    if param.type == "identifier"
                ]
                
            # Extract return type
            return_node = node.child_by_field_name("return_type")
            if return_node:
                metadata["return_type"] = return_node.text.decode("utf8")
                
        elif node.type == "class_definition":
            # Extract base classes
            bases_node = node.child_by_field_name("superclasses")
            if bases_node:
                metadata["base_classes"] = [
                    base.text.decode("utf8")
                    for base in bases_node.children
                    if base.type == "identifier"
                ]
                
        elif node.type == "variable_declaration":
            # Extract variable type
            type_node = node.child_by_field_name("type")
            if type_node:
                metadata["variable_type"] = type_node.text.decode("utf8")
                
        return metadata
        
    def _generate_vectors(self, node: CodeNode) -> None:
        """Generate vector representations for code nodes."""
        try:
            # Tokenize content
            inputs = self.tokenizer(
                node.content,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )
            
            # Generate embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)
                
            # Store vector
            node.vector = embeddings.numpy()[0]
            
            # Process children
            for child in node.children:
                self._generate_vectors(child)
                
        except Exception as e:
            logger.error(f"Error generating vectors: {e}")
            
    def compute_similarity(self, node1: CodeNode, node2: CodeNode) -> float:
        """Compute similarity between two code nodes."""
        try:
            if node1.vector is None or node2.vector is None:
                return 0.0
                
            # Compute cosine similarity
            similarity = np.dot(node1.vector, node2.vector) / (
                np.linalg.norm(node1.vector) * np.linalg.norm(node2.vector)
            )
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0
            
    def find_similar_nodes(self, query_node: CodeNode, nodes: List[CodeNode], threshold: float = 0.7) -> List[Tuple[CodeNode, float]]:
        """Find nodes similar to a query node."""
        try:
            similarities = []
            for node in nodes:
                similarity = self.compute_similarity(query_node, node)
                if similarity >= threshold:
                    similarities.append((node, similarity))
                    
            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return similarities
            
        except Exception as e:
            logger.error(f"Error finding similar nodes: {e}")
            return []
            
    def analyze_code_structure(self, node: CodeNode) -> Dict[str, Any]:
        """Analyze the structure of code."""
        try:
            structure = {
                "total_nodes": 0,
                "node_types": {},
                "depth": 0,
                "complexity": 0,
                "metrics": {
                    "classes": 0,
                    "functions": 0,
                    "variables": 0,
                    "imports": 0
                }
            }
            
            def traverse(n: CodeNode, current_depth: int):
                # Update counts
                structure["total_nodes"] += 1
                structure["node_types"][n.type.value] = structure["node_types"].get(n.type.value, 0) + 1
                structure["depth"] = max(structure["depth"], current_depth)
                
                # Update metrics
                if n.type == CodeNodeType.CLASS:
                    structure["metrics"]["classes"] += 1
                elif n.type == CodeNodeType.FUNCTION:
                    structure["metrics"]["functions"] += 1
                elif n.type == CodeNodeType.VARIABLE:
                    structure["metrics"]["variables"] += 1
                elif n.type == CodeNodeType.IMPORT:
                    structure["metrics"]["imports"] += 1
                    
                # Calculate complexity
                if n.type in [CodeNodeType.CLASS, CodeNodeType.FUNCTION]:
                    structure["complexity"] += len(n.children)
                    
                # Process children
                for child in n.children:
                    traverse(child, current_depth + 1)
                    
            traverse(node, 0)
            return structure
            
        except Exception as e:
            logger.error(f"Error analyzing code structure: {e}")
            return {}
            
    def extract_code_features(self, node: CodeNode) -> Dict[str, Any]:
        """Extract features from code."""
        try:
            features = {
                "syntax_features": self._extract_syntax_features(node),
                "semantic_features": self._extract_semantic_features(node),
                "structural_features": self._extract_structural_features(node)
            }
            return features
            
        except Exception as e:
            logger.error(f"Error extracting code features: {e}")
            return {}
            
    def _extract_syntax_features(self, node: CodeNode) -> Dict[str, Any]:
        """Extract syntax-related features."""
        features = {
            "keywords": [],
            "operators": [],
            "delimiters": [],
            "identifiers": []
        }
        
        # Extract keywords
        keyword_pattern = r"\b(if|else|for|while|return|class|def|import|from|as|try|except|finally|raise|with|in|is|not|and|or)\b"
        keywords = re.findall(keyword_pattern, node.content)
        features["keywords"] = list(set(keywords))
        
        # Extract operators
        operator_pattern = r"[+\-*/=<>!&|^%]"
        operators = re.findall(operator_pattern, node.content)
        features["operators"] = list(set(operators))
        
        # Extract delimiters
        delimiter_pattern = r"[(){}\[\].,;:]"
        delimiters = re.findall(delimiter_pattern, node.content)
        features["delimiters"] = list(set(delimiters))
        
        # Extract identifiers
        identifier_pattern = r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"
        identifiers = re.findall(identifier_pattern, node.content)
        features["identifiers"] = list(set(identifiers))
        
        return features
        
    def _extract_semantic_features(self, node: CodeNode) -> Dict[str, Any]:
        """Extract semantic features."""
        features = {
            "type_info": {},
            "scope_info": {},
            "dependencies": []
        }
        
        if node.type == CodeNodeType.FUNCTION:
            # Extract parameter types
            if "parameters" in node.metadata:
                features["type_info"]["parameters"] = node.metadata["parameters"]
                
            # Extract return type
            if "return_type" in node.metadata:
                features["type_info"]["return_type"] = node.metadata["return_type"]
                
        elif node.type == CodeNodeType.CLASS:
            # Extract base classes
            if "base_classes" in node.metadata:
                features["type_info"]["base_classes"] = node.metadata["base_classes"]
                
        # Extract dependencies
        for child in node.children:
            if child.type == CodeNodeType.IMPORT:
                features["dependencies"].append(child.content)
                
        return features
        
    def _extract_structural_features(self, node: CodeNode) -> Dict[str, Any]:
        """Extract structural features."""
        features = {
            "nesting_level": 0,
            "branching_factor": 0,
            "size": 0
        }
        
        def traverse(n: CodeNode, level: int):
            features["nesting_level"] = max(features["nesting_level"], level)
            features["branching_factor"] = max(features["branching_factor"], len(n.children))
            features["size"] += 1
            
            for child in n.children:
                traverse(child, level + 1)
                
        traverse(node, 0)
        return features 