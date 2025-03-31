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

class SemanticRelation(Enum):
    CALLS = "calls"
    USES = "uses"
    IMPLEMENTS = "implements"
    EXTENDS = "extends"
    IMPORTS = "imports"
    REFERENCES = "references"
    CONTAINS = "contains"
    MODIFIES = "modifies"
    RETURNS = "returns"
    THROWS = "throws"

@dataclass
class SemanticNode:
    id: str
    type: str
    name: str
    content: str
    location: str
    metadata: Dict[str, Any]
    vector: Optional[np.ndarray] = None

@dataclass
class SemanticRelation:
    source: str
    target: str
    type: SemanticRelation
    context: Dict[str, Any]
    confidence: float

class SemanticAnalyzer:
    """Advanced semantic code analysis system with neural network support."""
    
    def __init__(self, model_name: str = "microsoft/codebert-base"):
        """Initialize the semantic analyzer."""
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.vector_dim = self.model.config.hidden_size
        self.nodes: Dict[str, SemanticNode] = {}
        self.relations: List[SemanticRelation] = []
        
    def analyze_code(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze code for semantic relationships."""
        try:
            # Parse code
            tree = self._parse_code(file_path, content)
            
            # Extract semantic nodes
            self._extract_nodes(tree.root_node, file_path)
            
            # Analyze relationships
            self._analyze_relationships()
            
            # Generate vector representations
            self._generate_vectors()
            
            return {
                "nodes": self.nodes,
                "relations": self.relations
            }
            
        except Exception as e:
            logger.error(f"Error analyzing code: {e}")
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
        
    def _extract_nodes(self, node: tree_sitter.Node, file_path: str) -> None:
        """Extract semantic nodes from AST."""
        try:
            # Create node ID
            node_id = f"{file_path}:{node.start_point[0]}:{node.end_point[0]}"
            
            # Determine node type
            node_type = self._get_node_type(node)
            
            # Get node name
            name = self._get_node_name(node)
            
            # Get node content
            content = node.text.decode("utf8")
            
            # Get location
            location = f"{file_path}:{node.start_point[0] + 1}-{node.end_point[0] + 1}"
            
            # Build metadata
            metadata = self._build_metadata(node)
            
            # Create semantic node
            semantic_node = SemanticNode(
                id=node_id,
                type=node_type,
                name=name,
                content=content,
                location=location,
                metadata=metadata
            )
            
            # Store node
            self.nodes[node_id] = semantic_node
            
            # Process children
            for child in node.children:
                self._extract_nodes(child, file_path)
                
        except Exception as e:
            logger.error(f"Error extracting nodes: {e}")
            
    def _get_node_type(self, node: tree_sitter.Node) -> str:
        """Determine the type of a node."""
        type_map = {
            "module": "module",
            "class_definition": "class",
            "function_definition": "function",
            "variable_declaration": "variable",
            "import_statement": "import",
            "expression_statement": "statement",
            "expression": "expression",
            "comment": "comment",
            "string": "docstring"
        }
        return type_map.get(node.type, "unknown")
        
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
        
    def _analyze_relationships(self) -> None:
        """Analyze relationships between nodes."""
        try:
            # Clear existing relations
            self.relations.clear()
            
            # Analyze each node
            for node_id, node in self.nodes.items():
                # Function calls
                if node.type == "function":
                    self._analyze_function_calls(node)
                    
                # Class inheritance
                elif node.type == "class":
                    self._analyze_class_inheritance(node)
                    
                # Variable usage
                elif node.type == "variable":
                    self._analyze_variable_usage(node)
                    
                # Import relationships
                elif node.type == "import":
                    self._analyze_imports(node)
                    
        except Exception as e:
            logger.error(f"Error analyzing relationships: {e}")
            
    def _analyze_function_calls(self, node: SemanticNode) -> None:
        """Analyze function calls."""
        try:
            # Extract function calls from content
            call_pattern = r"\b(\w+)\s*\("
            calls = re.findall(call_pattern, node.content)
            
            for call in calls:
                # Find called function
                for target_id, target_node in self.nodes.items():
                    if target_node.type == "function" and target_node.name == call:
                        # Create relation
                        relation = SemanticRelation(
                            source=node.id,
                            target=target_id,
                            type=SemanticRelation.CALLS,
                            context={"call_site": node.location},
                            confidence=0.8
                        )
                        self.relations.append(relation)
                        
        except Exception as e:
            logger.error(f"Error analyzing function calls: {e}")
            
    def _analyze_class_inheritance(self, node: SemanticNode) -> None:
        """Analyze class inheritance."""
        try:
            if "base_classes" in node.metadata:
                for base_class in node.metadata["base_classes"]:
                    # Find base class
                    for target_id, target_node in self.nodes.items():
                        if target_node.type == "class" and target_node.name == base_class:
                            # Create relation
                            relation = SemanticRelation(
                                source=node.id,
                                target=target_id,
                                type=SemanticRelation.EXTENDS,
                                context={"inheritance_type": "extends"},
                                confidence=0.9
                            )
                            self.relations.append(relation)
                            
        except Exception as e:
            logger.error(f"Error analyzing class inheritance: {e}")
            
    def _analyze_variable_usage(self, node: SemanticNode) -> None:
        """Analyze variable usage."""
        try:
            # Extract variable references
            var_pattern = r"\b(\w+)\b"
            references = re.findall(var_pattern, node.content)
            
            for ref in references:
                # Find referenced variable
                for target_id, target_node in self.nodes.items():
                    if target_node.type == "variable" and target_node.name == ref:
                        # Create relation
                        relation = SemanticRelation(
                            source=node.id,
                            target=target_id,
                            type=SemanticRelation.USES,
                            context={"usage_site": node.location},
                            confidence=0.7
                        )
                        self.relations.append(relation)
                        
        except Exception as e:
            logger.error(f"Error analyzing variable usage: {e}")
            
    def _analyze_imports(self, node: SemanticNode) -> None:
        """Analyze import relationships."""
        try:
            # Extract imported module
            import_pattern = r"import\s+(\w+)"
            match = re.search(import_pattern, node.content)
            if match:
                module_name = match.group(1)
                
                # Find imported module
                for target_id, target_node in self.nodes.items():
                    if target_node.type == "module" and target_node.name == module_name:
                        # Create relation
                        relation = SemanticRelation(
                            source=node.id,
                            target=target_id,
                            type=SemanticRelation.IMPORTS,
                            context={"import_type": "direct"},
                            confidence=0.9
                        )
                        self.relations.append(relation)
                        
        except Exception as e:
            logger.error(f"Error analyzing imports: {e}")
            
    def _generate_vectors(self) -> None:
        """Generate vector representations for nodes."""
        try:
            for node in self.nodes.values():
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
                
        except Exception as e:
            logger.error(f"Error generating vectors: {e}")
            
    def compute_similarity(self, node1: SemanticNode, node2: SemanticNode) -> float:
        """Compute similarity between two nodes."""
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
            
    def find_similar_nodes(self, query_node: SemanticNode, threshold: float = 0.7) -> List[Tuple[SemanticNode, float]]:
        """Find nodes similar to a query node."""
        try:
            similarities = []
            for node in self.nodes.values():
                if node.id != query_node.id:
                    similarity = self.compute_similarity(query_node, node)
                    if similarity >= threshold:
                        similarities.append((node, similarity))
                        
            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return similarities
            
        except Exception as e:
            logger.error(f"Error finding similar nodes: {e}")
            return []
            
    def analyze_code_intent(self, node: SemanticNode) -> Dict[str, Any]:
        """Analyze the intent of code."""
        try:
            intent = {
                "primary_purpose": "",
                "secondary_purposes": [],
                "complexity": 0,
                "dependencies": [],
                "side_effects": []
            }
            
            # Analyze function intent
            if node.type == "function":
                # Extract docstring
                docstring = self._extract_docstring(node)
                if docstring:
                    intent["primary_purpose"] = self._extract_primary_purpose(docstring)
                    intent["secondary_purposes"] = self._extract_secondary_purposes(docstring)
                    
                # Analyze complexity
                intent["complexity"] = self._calculate_complexity(node)
                
                # Analyze dependencies
                intent["dependencies"] = self._extract_dependencies(node)
                
                # Analyze side effects
                intent["side_effects"] = self._analyze_side_effects(node)
                
            return intent
            
        except Exception as e:
            logger.error(f"Error analyzing code intent: {e}")
            return {}
            
    def _extract_docstring(self, node: SemanticNode) -> Optional[str]:
        """Extract docstring from node."""
        try:
            # Look for docstring in children
            for child in node.children:
                if child.type == "docstring":
                    return child.content
            return None
        except Exception as e:
            logger.error(f"Error extracting docstring: {e}")
            return None
            
    def _extract_primary_purpose(self, docstring: str) -> str:
        """Extract primary purpose from docstring."""
        try:
            # Split into lines
            lines = docstring.split("\n")
            
            # First line is usually the primary purpose
            if lines:
                return lines[0].strip()
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting primary purpose: {e}")
            return ""
            
    def _extract_secondary_purposes(self, docstring: str) -> List[str]:
        """Extract secondary purposes from docstring."""
        try:
            purposes = []
            lines = docstring.split("\n")
            
            # Skip first line (primary purpose)
            for line in lines[1:]:
                line = line.strip()
                if line and not line.startswith(("Args:", "Returns:", "Raises:")):
                    purposes.append(line)
                    
            return purposes
            
        except Exception as e:
            logger.error(f"Error extracting secondary purposes: {e}")
            return []
            
    def _calculate_complexity(self, node: SemanticNode) -> int:
        """Calculate code complexity."""
        try:
            complexity = 0
            
            # Count control structures
            control_patterns = [
                r"\bif\b",
                r"\bfor\b",
                r"\bwhile\b",
                r"\bswitch\b",
                r"\bcatch\b",
                r"\b&&\b",
                r"\b\|\|\b"
            ]
            
            for pattern in control_patterns:
                complexity += len(re.findall(pattern, node.content))
                
            return complexity
            
        except Exception as e:
            logger.error(f"Error calculating complexity: {e}")
            return 0
            
    def _extract_dependencies(self, node: SemanticNode) -> List[str]:
        """Extract dependencies from node."""
        try:
            dependencies = []
            
            # Get all relations where this node is the source
            for relation in self.relations:
                if relation.source == node.id:
                    target_node = self.nodes.get(relation.target)
                    if target_node:
                        dependencies.append(target_node.name)
                        
            return dependencies
            
        except Exception as e:
            logger.error(f"Error extracting dependencies: {e}")
            return []
            
    def _analyze_side_effects(self, node: SemanticNode) -> List[str]:
        """Analyze side effects of code."""
        try:
            side_effects = []
            
            # Look for global variable modifications
            global_pattern = r"global\s+(\w+)"
            globals = re.findall(global_pattern, node.content)
            if globals:
                side_effects.append(f"Modifies global variables: {', '.join(globals)}")
                
            # Look for file operations
            file_patterns = [
                r"open\s*\(",
                r"write\s*\(",
                r"read\s*\(",
                r"close\s*\("
            ]
            for pattern in file_patterns:
                if re.search(pattern, node.content):
                    side_effects.append("Performs file I/O operations")
                    break
                    
            # Look for network operations
            network_patterns = [
                r"socket\.",
                r"requests\.",
                r"http\.",
                r"https\."
            ]
            for pattern in network_patterns:
                if re.search(pattern, node.content):
                    side_effects.append("Performs network operations")
                    break
                    
            return side_effects
            
        except Exception as e:
            logger.error(f"Error analyzing side effects: {e}")
            return [] 