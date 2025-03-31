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

logger = logging.getLogger(__name__)

class SearchResult:
    """Represents a code search result."""
    def __init__(
        self,
        file_path: str,
        line_number: int,
        content: str,
        context: str,
        score: float,
        symbol_type: Optional[str] = None,
        references: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.file_path = file_path
        self.line_number = line_number
        self.content = content
        self.context = context
        self.score = score
        self.symbol_type = symbol_type
        self.references = references or []
        self.metadata = metadata or {}

class CodeSearch:
    """Advanced code search system with semantic search capabilities."""
    
    def __init__(self, elasticsearch_url: str = "http://localhost:9200"):
        """Initialize the code search system."""
        self.es = Elasticsearch([elasticsearch_url])
        self.index_name = "code_search"
        self.vectorizer = TfidfVectorizer()
        self._ensure_index_exists()
        
    def _ensure_index_exists(self):
        """Ensure the Elasticsearch index exists with proper mappings."""
        try:
            if not self.es.indices.exists(index=self.index_name):
                # Define index mappings
                mappings = {
                    "mappings": {
                        "properties": {
                            "file_path": {"type": "keyword"},
                            "line_number": {"type": "integer"},
                            "content": {"type": "text"},
                            "context": {"type": "text"},
                            "symbol_type": {"type": "keyword"},
                            "references": {"type": "keyword"},
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
                        "number_of_shards": 1,
                        "number_of_replicas": 0
                    }
                }
                
                # Create index
                self.es.indices.create(index=self.index_name, body=mappings)
                
        except Exception as e:
            logger.error(f"Error ensuring index exists: {e}")
            raise
            
    def index_code(self, file_path: str, content: str) -> None:
        """Index code from a file."""
        try:
            # Parse the code
            tree = self._parse_code(file_path, content)
            
            # Extract code segments
            segments = self._extract_code_segments(tree)
            
            # Index each segment
            for segment in segments:
                # Generate vector representation
                vector = self._generate_vector(segment["content"])
                
                # Prepare document
                doc = {
                    "file_path": file_path,
                    "line_number": segment["line_number"],
                    "content": segment["content"],
                    "context": segment["context"],
                    "symbol_type": segment.get("symbol_type"),
                    "references": segment.get("references", []),
                    "metadata": segment.get("metadata", {}),
                    "vector": vector
                }
                
                # Index document
                self.es.index(
                    index=self.index_name,
                    body=doc,
                    id=f"{file_path}:{segment['line_number']}"
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
        
    def _extract_code_segments(self, tree: tree_sitter.Tree) -> List[Dict[str, Any]]:
        """Extract code segments from the AST."""
        segments = []
        
        def traverse(node: tree_sitter.Node):
            # Extract function definitions
            if node.type == "function_definition":
                segments.append({
                    "line_number": node.start_point[0] + 1,
                    "content": node.text.decode("utf8"),
                    "context": self._get_context(node),
                    "symbol_type": "function",
                    "metadata": {
                        "name": node.child_by_field_name("name").text.decode("utf8"),
                        "parameters": self._extract_parameters(node)
                    }
                })
                
            # Extract class definitions
            elif node.type == "class_definition":
                segments.append({
                    "line_number": node.start_point[0] + 1,
                    "content": node.text.decode("utf8"),
                    "context": self._get_context(node),
                    "symbol_type": "class",
                    "metadata": {
                        "name": node.child_by_field_name("name").text.decode("utf8"),
                        "bases": self._extract_bases(node)
                    }
                })
                
            # Extract variable declarations
            elif node.type in ["variable_declaration", "assignment"]:
                segments.append({
                    "line_number": node.start_point[0] + 1,
                    "content": node.text.decode("utf8"),
                    "context": self._get_context(node),
                    "symbol_type": "variable",
                    "metadata": {
                        "name": self._extract_variable_name(node)
                    }
                })
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return segments
        
    def _get_context(self, node: tree_sitter.Node, context_lines: int = 3) -> str:
        """Get context around a node."""
        start_line = max(0, node.start_point[0] - context_lines)
        end_line = node.end_point[0] + context_lines
        return "\n".join(node.text.decode("utf8").split("\n")[start_line:end_line])
        
    def _extract_parameters(self, node: tree_sitter.Node) -> List[str]:
        """Extract function parameters."""
        parameters = []
        params_node = node.child_by_field_name("parameters")
        if params_node:
            for param in params_node.children:
                if param.type == "identifier":
                    parameters.append(param.text.decode("utf8"))
        return parameters
        
    def _extract_bases(self, node: tree_sitter.Node) -> List[str]:
        """Extract base classes."""
        bases = []
        bases_node = node.child_by_field_name("superclasses")
        if bases_node:
            for base in bases_node.children:
                if base.type == "identifier":
                    bases.append(base.text.decode("utf8"))
        return bases
        
    def _extract_variable_name(self, node: tree_sitter.Node) -> Optional[str]:
        """Extract variable name from declaration or assignment."""
        if node.type == "variable_declaration":
            name_node = node.child_by_field_name("name")
        elif node.type == "assignment":
            name_node = node.child_by_field_name("left")
        else:
            return None
            
        if name_node and name_node.type == "identifier":
            return name_node.text.decode("utf8")
        return None
        
    def _generate_vector(self, text: str) -> List[float]:
        """Generate vector representation of text."""
        # Use TF-IDF vectorization
        vector = self.vectorizer.fit_transform([text]).toarray()[0]
        
        # Normalize vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector.tolist()
        
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Search for code using semantic search."""
        try:
            # Generate query vector
            query_vector = self._generate_vector(query)
            
            # Search in Elasticsearch
            response = self.es.search(
                index=self.index_name,
                body={
                    "size": limit,
                    "query": {
                        "script_score": {
                            "query": {"match_all": {}},
                            "script": {
                                "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                                "params": {"query_vector": query_vector}
                            }
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
                    score=hit["_score"],
                    symbol_type=source.get("symbol_type"),
                    references=source.get("references", []),
                    metadata=source.get("metadata", {})
                ))
                
            return results
            
        except Exception as e:
            logger.error(f"Error searching code: {e}")
            return []
            
    def search_symbols(self, symbol_name: str, symbol_type: Optional[str] = None) -> List[SearchResult]:
        """Search for code symbols."""
        try:
            # Build query
            query = {
                "bool": {
                    "must": [
                        {"term": {"content": symbol_name}}
                    ]
                }
            }
            
            if symbol_type:
                query["bool"]["must"].append({"term": {"symbol_type": symbol_type}})
                
            # Search in Elasticsearch
            response = self.es.search(
                index=self.index_name,
                body={
                    "query": query
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
                    score=hit["_score"],
                    symbol_type=source.get("symbol_type"),
                    references=source.get("references", []),
                    metadata=source.get("metadata", {})
                ))
                
            return results
            
        except Exception as e:
            logger.error(f"Error searching symbols: {e}")
            return []
            
    def find_references(self, symbol_name: str) -> List[SearchResult]:
        """Find all references to a symbol."""
        try:
            # Search in Elasticsearch
            response = self.es.search(
                index=self.index_name,
                body={
                    "query": {
                        "term": {
                            "references": symbol_name
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
                    score=hit["_score"],
                    symbol_type=source.get("symbol_type"),
                    references=source.get("references", []),
                    metadata=source.get("metadata", {})
                ))
                
            return results
            
        except Exception as e:
            logger.error(f"Error finding references: {e}")
            return []
            
    def analyze_code(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze code for various metrics and patterns."""
        try:
            # Parse the code
            tree = self._parse_code(file_path, content)
            
            # Extract metrics
            metrics = {
                "total_lines": len(content.split("\n")),
                "function_count": 0,
                "class_count": 0,
                "variable_count": 0,
                "complexity": 0,
                "dependencies": []
            }
            
            def traverse(node: tree_sitter.Node):
                # Count functions
                if node.type == "function_definition":
                    metrics["function_count"] += 1
                    
                # Count classes
                elif node.type == "class_definition":
                    metrics["class_count"] += 1
                    
                # Count variables
                elif node.type in ["variable_declaration", "assignment"]:
                    metrics["variable_count"] += 1
                    
                # Calculate complexity
                if node.type in ["if_statement", "for_statement", "while_statement", "match_statement"]:
                    metrics["complexity"] += 1
                    
                # Extract dependencies
                if node.type == "import_statement":
                    metrics["dependencies"].append(node.text.decode("utf8"))
                    
                for child in node.children:
                    traverse(child)
                    
            traverse(tree.root_node)
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing code: {e}")
            return {} 