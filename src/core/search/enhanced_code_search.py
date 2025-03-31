from typing import Dict, List, Any, Optional, Set, Tuple
import logging
from dataclasses import dataclass
from enum import Enum
import tree_sitter
from pathlib import Path
import elasticsearch
from elasticsearch import Elasticsearch
import json
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel
import torch

logger = logging.getLogger(__name__)

class SymbolType(Enum):
    CLASS = "class"
    FUNCTION = "function"
    VARIABLE = "variable"
    METHOD = "method"
    PROPERTY = "property"
    INTERFACE = "interface"
    TYPE = "type"
    ENUM = "enum"
    CONSTANT = "constant"
    MODULE = "module"

@dataclass
class SearchResult:
    file_path: str
    line_number: int
    content: str
    context: str
    symbol_type: Optional[SymbolType]
    references: List[str]
    score: float
    type_info: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class EnhancedCodeSearch:
    """Advanced code search system with enhanced symbol search, cross-references, and type inference."""
    
    def __init__(self, elasticsearch_url: str = "http://localhost:9200"):
        """Initialize the enhanced code search system."""
        self.es = Elasticsearch([elasticsearch_url])
        self.index_name = "enhanced_code_search"
        self.vectorizer = TfidfVectorizer()
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        self.model = AutoModel.from_pretrained("microsoft/codebert-base")
        self._ensure_index_exists()
        
    def _ensure_index_exists(self):
        """Ensure the Elasticsearch index exists with proper mappings."""
        try:
            if not self.es.indices.exists(index=self.index_name):
                mappings = {
                    "mappings": {
                        "properties": {
                            "file_path": {"type": "keyword"},
                            "line_number": {"type": "integer"},
                            "content": {"type": "text", "analyzer": "code_analyzer"},
                            "context": {"type": "text"},
                            "symbol_type": {"type": "keyword"},
                            "symbol_name": {"type": "keyword"},
                            "references": {"type": "keyword"},
                            "type_info": {"type": "object"},
                            "metadata": {"type": "object"},
                            "vector": {
                                "type": "dense_vector",
                                "dims": 768,
                                "index": True,
                                "similarity": "cosine"
                            }
                        }
                    },
                    "settings": {
                        "analysis": {
                            "analyzer": {
                                "code_analyzer": {
                                    "type": "custom",
                                    "tokenizer": "standard",
                                    "filter": [
                                        "lowercase",
                                        "stop",
                                        "snowball"
                                    ]
                                }
                            }
                        }
                    }
                }
                self.es.indices.create(index=self.index_name, body=mappings)
                
        except Exception as e:
            logger.error(f"Error ensuring index exists: {e}")
            raise
            
    def index_code(self, file_path: str, content: str) -> None:
        """Index code with enhanced symbol and type information."""
        try:
            # Parse code
            tree = self._parse_code(file_path, content)
            
            # Extract symbols and their relationships
            symbols = self._extract_symbols(tree)
            
            # Analyze types
            type_info = self._analyze_types(tree)
            
            # Generate vector representations
            vectors = self._generate_vectors(content)
            
            # Index each symbol
            for symbol in symbols:
                # Get type information for this symbol
                symbol_type_info = type_info.get(symbol["name"], {})
                
                # Prepare document
                doc = {
                    "file_path": file_path,
                    "line_number": symbol["line_number"],
                    "content": symbol["content"],
                    "context": symbol["context"],
                    "symbol_type": symbol["type"].value,
                    "symbol_name": symbol["name"],
                    "references": symbol["references"],
                    "type_info": symbol_type_info,
                    "metadata": symbol.get("metadata", {}),
                    "vector": vectors.get(symbol["line_number"], [])
                }
                
                # Index document
                self.es.index(
                    index=self.index_name,
                    body=doc,
                    id=f"{file_path}:{symbol['line_number']}"
                )
                
        except Exception as e:
            logger.error(f"Error indexing code from {file_path}: {e}")
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
        
    def _extract_symbols(self, tree: tree_sitter.Tree) -> List[Dict[str, Any]]:
        """Extract symbols and their relationships from AST."""
        symbols = []
        
        def traverse(node: tree_sitter.Node):
            # Extract class definitions
            if node.type == "class_definition":
                class_name = node.child_by_field_name("name").text.decode("utf8")
                symbols.append({
                    "name": class_name,
                    "type": SymbolType.CLASS,
                    "line_number": node.start_point[0] + 1,
                    "content": node.text.decode("utf8"),
                    "context": self._get_context(node),
                    "references": self._extract_references(node),
                    "metadata": {
                        "bases": self._extract_bases(node),
                        "methods": self._extract_methods(node)
                    }
                })
                
            # Extract function definitions
            elif node.type == "function_definition":
                func_name = node.child_by_field_name("name").text.decode("utf8")
                symbols.append({
                    "name": func_name,
                    "type": SymbolType.FUNCTION,
                    "line_number": node.start_point[0] + 1,
                    "content": node.text.decode("utf8"),
                    "context": self._get_context(node),
                    "references": self._extract_references(node),
                    "metadata": {
                        "parameters": self._extract_parameters(node),
                        "return_type": self._extract_return_type(node)
                    }
                })
                
            # Extract variable declarations
            elif node.type in ["variable_declaration", "assignment"]:
                var_name = self._extract_variable_name(node)
                if var_name:
                    symbols.append({
                        "name": var_name,
                        "type": SymbolType.VARIABLE,
                        "line_number": node.start_point[0] + 1,
                        "content": node.text.decode("utf8"),
                        "context": self._get_context(node),
                        "references": self._extract_references(node),
                        "metadata": {
                            "type": self._extract_variable_type(node)
                        }
                    })
                    
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return symbols
        
    def _get_context(self, node: tree_sitter.Node, context_lines: int = 3) -> str:
        """Get context around a node."""
        start_line = max(0, node.start_point[0] - context_lines)
        end_line = node.end_point[0] + context_lines
        return "\n".join(node.text.decode("utf8").split("\n")[start_line:end_line])
        
    def _extract_references(self, node: tree_sitter.Node) -> List[str]:
        """Extract references from a node."""
        references = []
        
        def traverse(n: tree_sitter.Node):
            if n.type == "identifier":
                references.append(n.text.decode("utf8"))
            for child in n.children:
                traverse(child)
                
        traverse(node)
        return list(set(references))
        
    def _extract_bases(self, node: tree_sitter.Node) -> List[str]:
        """Extract base classes."""
        bases = []
        bases_node = node.child_by_field_name("superclasses")
        if bases_node:
            for base in bases_node.children:
                if base.type == "identifier":
                    bases.append(base.text.decode("utf8"))
        return bases
        
    def _extract_methods(self, node: tree_sitter.Node) -> List[str]:
        """Extract method names from a class."""
        methods = []
        for child in node.children:
            if child.type == "function_definition":
                name_node = child.child_by_field_name("name")
                if name_node:
                    methods.append(name_node.text.decode("utf8"))
        return methods
        
    def _extract_parameters(self, node: tree_sitter.Node) -> List[str]:
        """Extract function parameters."""
        parameters = []
        params_node = node.child_by_field_name("parameters")
        if params_node:
            for param in params_node.children:
                if param.type == "identifier":
                    parameters.append(param.text.decode("utf8"))
        return parameters
        
    def _extract_return_type(self, node: tree_sitter.Node) -> Optional[str]:
        """Extract function return type."""
        return_node = node.child_by_field_name("return_type")
        if return_node:
            return return_node.text.decode("utf8")
        return None
        
    def _extract_variable_name(self, node: tree_sitter.Node) -> Optional[str]:
        """Extract variable name."""
        if node.type == "variable_declaration":
            name_node = node.child_by_field_name("name")
        elif node.type == "assignment":
            name_node = node.child_by_field_name("left")
        else:
            return None
            
        if name_node and name_node.type == "identifier":
            return name_node.text.decode("utf8")
        return None
        
    def _extract_variable_type(self, node: tree_sitter.Node) -> Optional[str]:
        """Extract variable type."""
        type_node = node.child_by_field_name("type")
        if type_node:
            return type_node.text.decode("utf8")
        return None
        
    def _analyze_types(self, tree: tree_sitter.Tree) -> Dict[str, Dict[str, Any]]:
        """Analyze types in the code."""
        type_info = {}
        
        def traverse(node: tree_sitter.Node):
            # Analyze class types
            if node.type == "class_definition":
                class_name = node.child_by_field_name("name").text.decode("utf8")
                type_info[class_name] = {
                    "type": "class",
                    "bases": self._extract_bases(node),
                    "methods": self._extract_methods(node),
                    "properties": self._extract_properties(node)
                }
                
            # Analyze function types
            elif node.type == "function_definition":
                func_name = node.child_by_field_name("name").text.decode("utf8")
                type_info[func_name] = {
                    "type": "function",
                    "parameters": self._extract_parameters(node),
                    "return_type": self._extract_return_type(node)
                }
                
            # Analyze variable types
            elif node.type in ["variable_declaration", "assignment"]:
                var_name = self._extract_variable_name(node)
                if var_name:
                    type_info[var_name] = {
                        "type": "variable",
                        "type_annotation": self._extract_variable_type(node)
                    }
                    
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return type_info
        
    def _extract_properties(self, node: tree_sitter.Node) -> List[str]:
        """Extract property names from a class."""
        properties = []
        for child in node.children:
            if child.type == "expression_statement":
                # Check for property decorators
                if child.child_by_field_name("expression").type == "decorator":
                    properties.append(child.child_by_field_name("expression").text.decode("utf8"))
        return properties
        
    def _generate_vectors(self, content: str) -> Dict[int, List[float]]:
        """Generate vector representations for code lines."""
        vectors = {}
        
        # Split content into lines
        lines = content.split("\n")
        
        # Generate vectors for each line
        for i, line in enumerate(lines):
            if line.strip():
                # Tokenize line
                inputs = self.tokenizer(
                    line,
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
                vectors[i + 1] = embeddings.numpy()[0].tolist()
                
        return vectors
        
    def search_symbols(self, query: str, symbol_type: Optional[SymbolType] = None) -> List[SearchResult]:
        """Search for code symbols with enhanced type information."""
        try:
            # Build query
            search_query = {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["symbol_name^2", "content", "context"]
                            }
                        }
                    ]
                }
            }
            
            if symbol_type:
                search_query["bool"]["must"].append({
                    "term": {"symbol_type": symbol_type.value}
                })
                
            # Search in Elasticsearch
            response = self.es.search(
                index=self.index_name,
                body={
                    "query": search_query,
                    "highlight": {
                        "fields": {
                            "content": {},
                            "context": {}
                        }
                    }
                }
            )
            
            # Convert results
            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                results.append(SearchResult(
                    file_path=source["file_path"],
                    line_number=source["line_number"],
                    content=source["content"],
                    context=source["context"],
                    symbol_type=SymbolType(source["symbol_type"]),
                    references=source["references"],
                    score=hit["_score"],
                    type_info=source.get("type_info"),
                    metadata=source.get("metadata")
                ))
                
            return results
            
        except Exception as e:
            logger.error(f"Error searching symbols: {e}")
            return []
            
    def find_references(self, symbol_name: str) -> List[SearchResult]:
        """Find all references to a symbol with context."""
        try:
            # Search in Elasticsearch
            response = self.es.search(
                index=self.index_name,
                body={
                    "query": {
                        "term": {
                            "references": symbol_name
                        }
                    },
                    "highlight": {
                        "fields": {
                            "content": {},
                            "context": {}
                        }
                    }
                }
            )
            
            # Convert results
            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                results.append(SearchResult(
                    file_path=source["file_path"],
                    line_number=source["line_number"],
                    content=source["content"],
                    context=source["context"],
                    symbol_type=SymbolType(source["symbol_type"]),
                    references=source["references"],
                    score=hit["_score"],
                    type_info=source.get("type_info"),
                    metadata=source.get("metadata")
                ))
                
            return results
            
        except Exception as e:
            logger.error(f"Error finding references: {e}")
            return []
            
    def full_text_search(self, query: str, context_lines: int = 3) -> List[SearchResult]:
        """Perform full-text search with code context."""
        try:
            # Generate query vector
            query_vector = self._generate_vectors(query)[1]
            
            # Search in Elasticsearch
            response = self.es.search(
                index=self.index_name,
                body={
                    "size": 20,
                    "query": {
                        "script_score": {
                            "query": {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["content^2", "context"]
                                }
                            },
                            "script": {
                                "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                                "params": {"query_vector": query_vector}
                            }
                        }
                    },
                    "highlight": {
                        "fields": {
                            "content": {},
                            "context": {}
                        }
                    }
                }
            )
            
            # Convert results
            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                results.append(SearchResult(
                    file_path=source["file_path"],
                    line_number=source["line_number"],
                    content=source["content"],
                    context=source["context"],
                    symbol_type=SymbolType(source["symbol_type"]) if "symbol_type" in source else None,
                    references=source["references"],
                    score=hit["_score"],
                    type_info=source.get("type_info"),
                    metadata=source.get("metadata")
                ))
                
            return results
            
        except Exception as e:
            logger.error(f"Error performing full-text search: {e}")
            return []
            
    def infer_type(self, expression: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Infer the type of an expression with enhanced capabilities."""
        try:
            # Parse the expression
            tree = self._parse_code("temp.py", expression)
            
            # Analyze the expression
            type_info = self._analyze_expression_type(tree.root_node, context)
            
            return type_info
            
        except Exception as e:
            logger.error(f"Error inferring type: {e}")
            return None
            
    def _analyze_expression_type(self, node: tree_sitter.Node, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze an expression to infer its type."""
        if node.type == "identifier":
            # Check context for variable type
            if node.text.decode("utf8") in context:
                return context[node.text.decode("utf8")]
            # Check type registry
            return self._get_type_from_registry(node.text.decode("utf8"))
            
        elif node.type == "call":
            # Analyze function call
            if node.child_by_field_name("function").type == "identifier":
                func_name = node.child_by_field_name("function").text.decode("utf8")
                return self._get_function_return_type(func_name)
                
        elif node.type == "binary_operator":
            # Analyze binary operation
            left_type = self._analyze_expression_type(node.child_by_field_name("left"), context)
            right_type = self._analyze_expression_type(node.child_by_field_name("right"), context)
            if left_type and right_type:
                return self._resolve_binary_op_type(left_type, right_type, node.child_by_field_name("operator").text.decode("utf8"))
                
        return None
        
    def _get_type_from_registry(self, name: str) -> Optional[Dict[str, Any]]:
        """Get type information from the type registry."""
        # Search in Elasticsearch
        response = self.es.search(
            index=self.index_name,
            body={
                "query": {
                    "term": {
                        "symbol_name": name
                    }
                }
            }
        )
        
        if response["hits"]["hits"]:
            source = response["hits"]["hits"][0]["_source"]
            return source.get("type_info")
            
        return None
        
    def _get_function_return_type(self, func_name: str) -> Optional[Dict[str, Any]]:
        """Get function return type from the type registry."""
        type_info = self._get_type_from_registry(func_name)
        if type_info and "return_type" in type_info:
            return {"type": type_info["return_type"]}
        return None
        
    def _resolve_binary_op_type(self, left: Dict[str, Any], right: Dict[str, Any], operator: str) -> Optional[Dict[str, Any]]:
        """Resolve the type of a binary operation."""
        # Implement type resolution for binary operations
        # This is a simplified version - you would want to implement more sophisticated type resolution
        if operator in ["+", "-", "*", "/"]:
            if left["type"] == right["type"]:
                return {"type": left["type"]}
            return {"type": "any"}  # Fallback for type mismatch
        elif operator in ["==", "!=", "<", ">", "<=", ">="]:
            return {"type": "bool"}
        return None 