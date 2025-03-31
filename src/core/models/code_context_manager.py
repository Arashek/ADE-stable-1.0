from typing import Dict, List, Any, Optional, Set
import logging
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import hashlib
from collections import defaultdict
import networkx as nx
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from elasticsearch import AsyncElasticsearch

logger = logging.getLogger(__name__)

@dataclass
class CodeContext:
    file_path: str
    content: str
    language: str
    imports: List[str]
    exports: List[str]
    classes: List[str]
    functions: List[str]
    variables: List[str]
    dependencies: List[str]
    last_modified: datetime
    embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = None

class CodeContextManager:
    def __init__(self, workspace_root: str, es_host: str = "localhost", es_port: int = 9200):
        self.workspace_root = Path(workspace_root)
        self.contexts: Dict[str, CodeContext] = {}
        self.dependency_graph = nx.DiGraph()
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        self.model = AutoModel.from_pretrained("microsoft/codebert-base")
        self.es = AsyncElasticsearch([f"http://{es_host}:{es_port}"])
        self.index_name = "code_contexts"
        
    async def initialize(self):
        """Initialize the context manager"""
        try:
            # Create Elasticsearch index if it doesn't exist
            if not await self.es.indices.exists(index=self.index_name):
                await self.es.indices.create(
                    index=self.index_name,
                    body={
                        "mappings": {
                            "properties": {
                                "file_path": {"type": "keyword"},
                                "content": {"type": "text"},
                                "language": {"type": "keyword"},
                                "imports": {"type": "keyword"},
                                "exports": {"type": "keyword"},
                                "classes": {"type": "keyword"},
                                "functions": {"type": "keyword"},
                                "variables": {"type": "keyword"},
                                "dependencies": {"type": "keyword"},
                                "last_modified": {"type": "date"},
                                "embedding": {
                                    "type": "dense_vector",
                                    "dims": 768,
                                    "index": True,
                                    "similarity": "cosine"
                                }
                            }
                        }
                    }
                )
                
            # Load existing contexts
            await self._load_contexts()
            
        except Exception as e:
            logger.error(f"Failed to initialize context manager: {e}")
            raise
            
    async def _load_contexts(self):
        """Load existing contexts from Elasticsearch"""
        try:
            result = await self.es.search(
                index=self.index_name,
                body={"query": {"match_all": {}}}
            )
            
            for hit in result["hits"]["hits"]:
                source = hit["_source"]
                context = CodeContext(
                    file_path=source["file_path"],
                    content=source["content"],
                    language=source["language"],
                    imports=source["imports"],
                    exports=source["exports"],
                    classes=source["classes"],
                    functions=source["functions"],
                    variables=source["variables"],
                    dependencies=source["dependencies"],
                    last_modified=datetime.fromisoformat(source["last_modified"]),
                    embedding=np.array(source["embedding"]),
                    metadata=source.get("metadata", {})
                )
                self.contexts[context.file_path] = context
                
        except Exception as e:
            logger.error(f"Failed to load contexts: {e}")
            
    async def update_context(self, file_path: str, content: str) -> None:
        """Update or create context for a file"""
        try:
            # Parse code to extract information
            language = self._detect_language(file_path)
            imports = self._extract_imports(content, language)
            exports = self._extract_exports(content, language)
            classes = self._extract_classes(content, language)
            functions = self._extract_functions(content, language)
            variables = self._extract_variables(content, language)
            dependencies = self._extract_dependencies(content, language)
            
            # Generate embedding
            embedding = self._generate_embedding(content)
            
            # Create context
            context = CodeContext(
                file_path=file_path,
                content=content,
                language=language,
                imports=imports,
                exports=exports,
                classes=classes,
                functions=functions,
                variables=variables,
                dependencies=dependencies,
                last_modified=datetime.now(),
                embedding=embedding,
                metadata=self._extract_metadata(content)
            )
            
            # Update in-memory cache
            self.contexts[file_path] = context
            
            # Update dependency graph
            self._update_dependency_graph(context)
            
            # Store in Elasticsearch
            await self._store_context(context)
            
        except Exception as e:
            logger.error(f"Failed to update context for {file_path}: {e}")
            
    async def _store_context(self, context: CodeContext) -> None:
        """Store context in Elasticsearch"""
        try:
            await self.es.index(
                index=self.index_name,
                id=context.file_path,
                body={
                    "file_path": context.file_path,
                    "content": context.content,
                    "language": context.language,
                    "imports": context.imports,
                    "exports": context.exports,
                    "classes": context.classes,
                    "functions": context.functions,
                    "variables": context.variables,
                    "dependencies": context.dependencies,
                    "last_modified": context.last_modified.isoformat(),
                    "embedding": context.embedding.tolist(),
                    "metadata": context.metadata
                }
            )
        except Exception as e:
            logger.error(f"Failed to store context in Elasticsearch: {e}")
            
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".h": "cpp",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".dart": "dart"
        }
        return language_map.get(ext, "unknown")
        
    def _extract_imports(self, content: str, language: str) -> List[str]:
        """Extract import statements based on language"""
        imports = []
        if language == "python":
            for line in content.split("\n"):
                if line.startswith(("import ", "from ")):
                    imports.append(line.strip())
        elif language in ["javascript", "typescript"]:
            for line in content.split("\n"):
                if line.startswith(("import ", "require(")):
                    imports.append(line.strip())
        return imports
        
    def _extract_exports(self, content: str, language: str) -> List[str]:
        """Extract export statements based on language"""
        exports = []
        if language in ["javascript", "typescript"]:
            for line in content.split("\n"):
                if line.startswith(("export ", "module.exports")):
                    exports.append(line.strip())
        return exports
        
    def _extract_classes(self, content: str, language: str) -> List[str]:
        """Extract class definitions based on language"""
        classes = []
        if language == "python":
            for line in content.split("\n"):
                if line.startswith("class "):
                    classes.append(line.strip())
        elif language in ["javascript", "typescript", "java", "cpp"]:
            for line in content.split("\n"):
                if "class " in line:
                    classes.append(line.strip())
        return classes
        
    def _extract_functions(self, content: str, language: str) -> List[str]:
        """Extract function definitions based on language"""
        functions = []
        if language == "python":
            for line in content.split("\n"):
                if line.startswith("def "):
                    functions.append(line.strip())
        elif language in ["javascript", "typescript"]:
            for line in content.split("\n"):
                if line.startswith("function ") or "=>" in line:
                    functions.append(line.strip())
        return functions
        
    def _extract_variables(self, content: str, language: str) -> List[str]:
        """Extract variable declarations based on language"""
        variables = []
        if language == "python":
            for line in content.split("\n"):
                if "=" in line and not line.startswith(("def ", "class ", "import ")):
                    variables.append(line.strip())
        elif language in ["javascript", "typescript"]:
            for line in content.split("\n"):
                if line.startswith(("let ", "const ", "var ")):
                    variables.append(line.strip())
        return variables
        
    def _extract_dependencies(self, content: str, language: str) -> List[str]:
        """Extract dependencies based on language"""
        dependencies = []
        if language == "python":
            for line in content.split("\n"):
                if line.startswith(("import ", "from ")):
                    module = line.split()[1].split(".")[0]
                    dependencies.append(module)
        elif language in ["javascript", "typescript"]:
            for line in content.split("\n"):
                if line.startswith(("import ", "require(")):
                    module = line.split()[1].strip("'\"")
                    dependencies.append(module)
        return dependencies
        
    def _generate_embedding(self, content: str) -> np.ndarray:
        """Generate embedding for code content"""
        try:
            inputs = self.tokenizer(content, return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs)
            return outputs.last_hidden_state.mean(dim=1).numpy()[0]
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return np.zeros(768)
            
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from code content"""
        return {
            "line_count": len(content.split("\n")),
            "char_count": len(content),
            "hash": hashlib.md5(content.encode()).hexdigest()
        }
        
    def _update_dependency_graph(self, context: CodeContext) -> None:
        """Update dependency graph with new context"""
        self.dependency_graph.add_node(context.file_path)
        for dep in context.dependencies:
            self.dependency_graph.add_edge(context.file_path, dep)
            
    async def search_similar_code(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar code using semantic search"""
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # Search in Elasticsearch
            result = await self.es.search(
                index=self.index_name,
                body={
                    "query": {
                        "script_score": {
                            "query": {"match_all": {}},
                            "script": {
                                "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                "params": {"query_vector": query_embedding.tolist()}
                            }
                        }
                    },
                    "size": limit
                }
            )
            
            # Format results
            results = []
            for hit in result["hits"]["hits"]:
                source = hit["_source"]
                results.append({
                    "file_path": source["file_path"],
                    "score": hit["_score"],
                    "content": source["content"],
                    "language": source["language"]
                })
                
            return results
            
        except Exception as e:
            logger.error(f"Failed to search similar code: {e}")
            return []
            
    async def get_file_dependencies(self, file_path: str) -> Dict[str, List[str]]:
        """Get direct and indirect dependencies for a file"""
        try:
            if file_path not in self.dependency_graph:
                return {"direct": [], "indirect": []}
                
            direct_deps = list(self.dependency_graph.successors(file_path))
            indirect_deps = []
            
            # Get indirect dependencies
            for dep in direct_deps:
                if dep in self.dependency_graph:
                    indirect_deps.extend(list(self.dependency_graph.successors(dep)))
                    
            return {
                "direct": direct_deps,
                "indirect": list(set(indirect_deps))
            }
            
        except Exception as e:
            logger.error(f"Failed to get dependencies for {file_path}: {e}")
            return {"direct": [], "indirect": []}
            
    async def get_related_files(self, file_path: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get related files based on content similarity"""
        try:
            if file_path not in self.contexts:
                return []
                
            context = self.contexts[file_path]
            
            # Search for similar files
            result = await self.es.search(
                index=self.index_name,
                body={
                    "query": {
                        "script_score": {
                            "query": {
                                "bool": {
                                    "must_not": [{"term": {"file_path": file_path}}]
                                }
                            },
                            "script": {
                                "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                "params": {"query_vector": context.embedding.tolist()}
                            }
                        }
                    },
                    "size": limit
                }
            )
            
            # Format results
            results = []
            for hit in result["hits"]["hits"]:
                source = hit["_source"]
                results.append({
                    "file_path": source["file_path"],
                    "similarity": hit["_score"],
                    "language": source["language"]
                })
                
            return results
            
        except Exception as e:
            logger.error(f"Failed to get related files for {file_path}: {e}")
            return []
            
    async def get_code_context(self, file_path: str) -> Optional[CodeContext]:
        """Get code context for a file"""
        return self.contexts.get(file_path)
        
    async def cleanup(self):
        """Clean up resources"""
        try:
            await self.es.close()
        except Exception as e:
            logger.error(f"Failed to cleanup: {e}") 