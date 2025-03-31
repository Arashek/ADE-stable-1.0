from typing import Dict, List, Any, Optional
import elasticsearch
from elasticsearch import Elasticsearch
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    file_path: str
    line_number: int
    content: str
    context: str
    symbol_type: str
    references: List[str]
    score: float

class CodeSearchService:
    """Service for code search and indexing using Elasticsearch."""
    
    def __init__(self, elasticsearch_url: str = "http://localhost:9200"):
        """Initialize the search service."""
        self.es = Elasticsearch([elasticsearch_url])
        self.index_name = "code_search"
        self._ensure_index_exists()
        
    def _ensure_index_exists(self):
        """Ensure the Elasticsearch index exists with proper mappings."""
        if not self.es.indices.exists(index=self.index_name):
            mapping = {
                "mappings": {
                    "properties": {
                        "file_path": {"type": "keyword"},
                        "line_number": {"type": "integer"},
                        "content": {"type": "text", "analyzer": "code_analyzer"},
                        "context": {"type": "text"},
                        "symbol_type": {"type": "keyword"},
                        "references": {"type": "keyword"},
                        "language": {"type": "keyword"},
                        "scope": {"type": "keyword"},
                        "last_modified": {"type": "date"},
                        "ast_path": {"type": "keyword"},
                        "type_info": {"type": "object"},
                        "dependencies": {"type": "keyword"}
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
            self.es.indices.create(index=self.index_name, body=mapping)
            
    def index_code(self, file_path: str, content: str, metadata: Dict[str, Any]):
        """Index a code file with its metadata."""
        try:
            # Parse and analyze the code
            ast_info = self._analyze_code(content)
            
            # Index each significant code element
            for element in ast_info["elements"]:
                doc = {
                    "file_path": file_path,
                    "line_number": element["line"],
                    "content": element["content"],
                    "context": element["context"],
                    "symbol_type": element["type"],
                    "references": element["references"],
                    "language": metadata.get("language", "unknown"),
                    "scope": element["scope"],
                    "last_modified": datetime.utcnow(),
                    "ast_path": element["ast_path"],
                    "type_info": element.get("type_info", {}),
                    "dependencies": metadata.get("dependencies", [])
                }
                
                self.es.index(
                    index=self.index_name,
                    body=doc,
                    id=f"{file_path}:{element['line']}"
                )
                
        except Exception as e:
            logger.error(f"Error indexing file {file_path}: {e}")
            raise
            
    def search_symbols(self, query: str, symbol_type: Optional[str] = None) -> List[SearchResult]:
        """Search for code symbols with optional type filtering."""
        search_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["content^2", "context"]
                            }
                        }
                    ]
                }
            },
            "highlight": {
                "fields": {
                    "content": {},
                    "context": {}
                }
            }
        }
        
        if symbol_type:
            search_query["query"]["bool"]["must"].append({
                "term": {"symbol_type": symbol_type}
            })
            
        try:
            response = self.es.search(
                index=self.index_name,
                body=search_query
            )
            
            return [
                SearchResult(
                    file_path=hit["_source"]["file_path"],
                    line_number=hit["_source"]["line_number"],
                    content=hit["_source"]["content"],
                    context=hit["_source"]["context"],
                    symbol_type=hit["_source"]["symbol_type"],
                    references=hit["_source"]["references"],
                    score=hit["_score"]
                )
                for hit in response["hits"]["hits"]
            ]
            
        except Exception as e:
            logger.error(f"Error searching symbols: {e}")
            raise
            
    def find_references(self, symbol: str) -> List[SearchResult]:
        """Find all references to a symbol."""
        search_query = {
            "query": {
                "term": {"references": symbol}
            }
        }
        
        try:
            response = self.es.search(
                index=self.index_name,
                body=search_query
            )
            
            return [
                SearchResult(
                    file_path=hit["_source"]["file_path"],
                    line_number=hit["_source"]["line_number"],
                    content=hit["_source"]["content"],
                    context=hit["_source"]["context"],
                    symbol_type=hit["_source"]["symbol_type"],
                    references=hit["_source"]["references"],
                    score=hit["_score"]
                )
                for hit in response["hits"]["hits"]
            ]
            
        except Exception as e:
            logger.error(f"Error finding references: {e}")
            raise
            
    def _analyze_code(self, content: str) -> Dict[str, Any]:
        """Analyze code to extract symbols and their relationships."""
        # This is a placeholder - implement actual code analysis
        # using your existing code analysis tools
        return {
            "elements": []
        } 