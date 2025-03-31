from typing import Dict, List, Optional, Any, Tuple, Set
import numpy as np
from sentence_transformers import SentenceTransformer
import logging
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from fuzzywuzzy import fuzz
from collections import defaultdict
import concurrent.futures
from tqdm import tqdm

@dataclass
class SearchResult:
    """Represents a search result with similarity score."""
    item_id: str
    item_type: str  # 'pattern' or 'solution'
    similarity_score: float
    metadata: Dict[str, Any]
    context_similarity: float = 0.0
    fuzzy_score: float = 0.0

class SimilaritySearch:
    """Performs similarity search on error patterns and solutions using embeddings."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: str = "data/embeddings",
                 max_workers: int = 4, fuzzy_threshold: float = 0.8):
        self.logger = logging.getLogger(__name__)
        self.model = SentenceTransformer(model_name)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers
        self.fuzzy_threshold = fuzzy_threshold
        
        # Initialize caches
        self.pattern_embeddings: Dict[str, np.ndarray] = {}
        self.solution_embeddings: Dict[str, np.ndarray] = {}
        self.pattern_texts: Dict[str, str] = {}
        self.solution_texts: Dict[str, str] = {}
        self.pattern_contexts: Dict[str, Set[str]] = defaultdict(set)
        self.solution_contexts: Dict[str, Set[str]] = defaultdict(set)
        
        # Load cached embeddings
        self._load_cached_embeddings()
    
    def _load_cached_embeddings(self):
        """Load cached embeddings from disk."""
        try:
            # Load pattern embeddings
            pattern_cache = self.cache_dir / "pattern_embeddings.json"
            if pattern_cache.exists():
                with open(pattern_cache, 'r') as f:
                    data = json.load(f)
                    for pattern_id, embedding_data in data.items():
                        self.pattern_embeddings[pattern_id] = np.array(embedding_data["embedding"])
                        self.pattern_texts[pattern_id] = embedding_data["text"]
                        self.pattern_contexts[pattern_id] = set(embedding_data.get("contexts", []))
            
            # Load solution embeddings
            solution_cache = self.cache_dir / "solution_embeddings.json"
            if solution_cache.exists():
                with open(solution_cache, 'r') as f:
                    data = json.load(f)
                    for solution_id, embedding_data in data.items():
                        self.solution_embeddings[solution_id] = np.array(embedding_data["embedding"])
                        self.solution_texts[solution_id] = embedding_data["text"]
                        self.solution_contexts[solution_id] = set(embedding_data.get("contexts", []))
        except Exception as e:
            self.logger.error(f"Error loading cached embeddings: {str(e)}")
    
    def _save_cached_embeddings(self):
        """Save embeddings to disk cache."""
        try:
            # Save pattern embeddings
            pattern_cache = self.cache_dir / "pattern_embeddings.json"
            pattern_data = {
                pattern_id: {
                    "embedding": embedding.tolist(),
                    "text": text,
                    "contexts": list(contexts)
                }
                for pattern_id, embedding in self.pattern_embeddings.items()
                for text in [self.pattern_texts.get(pattern_id, "")]
                for contexts in [self.pattern_contexts.get(pattern_id, set())]
            }
            with open(pattern_cache, 'w') as f:
                json.dump(pattern_data, f)
            
            # Save solution embeddings
            solution_cache = self.cache_dir / "solution_embeddings.json"
            solution_data = {
                solution_id: {
                    "embedding": embedding.tolist(),
                    "text": text,
                    "contexts": list(contexts)
                }
                for solution_id, embedding in self.solution_embeddings.items()
                for text in [self.solution_texts.get(solution_id, "")]
                for contexts in [self.solution_contexts.get(solution_id, set())]
            }
            with open(solution_cache, 'w') as f:
                json.dump(solution_data, f)
        except Exception as e:
            self.logger.error(f"Error saving cached embeddings: {str(e)}")
    
    def _compute_embedding(self, text: str) -> np.ndarray:
        """Compute embedding for a text using the model."""
        return self.model.encode(text, convert_to_numpy=True)
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two embeddings."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def _compute_fuzzy_similarity(self, text1: str, text2: str) -> float:
        """Compute fuzzy string similarity between two texts."""
        return fuzz.ratio(text1.lower(), text2.lower()) / 100.0
    
    def _compute_context_similarity(self, contexts1: Set[str], contexts2: Set[str]) -> float:
        """Compute similarity between two sets of contexts."""
        if not contexts1 or not contexts2:
            return 0.0
        intersection = len(contexts1.intersection(contexts2))
        union = len(contexts1.union(contexts2))
        return intersection / union if union > 0 else 0.0
    
    def add_pattern(self, pattern_id: str, pattern_text: str, contexts: Optional[List[str]] = None):
        """Add a pattern to the search index with optional contexts."""
        try:
            # Compute and store embedding
            embedding = self._compute_embedding(pattern_text)
            self.pattern_embeddings[pattern_id] = embedding
            self.pattern_texts[pattern_id] = pattern_text
            
            # Store contexts
            if contexts:
                self.pattern_contexts[pattern_id].update(contexts)
            
            # Update cache
            self._save_cached_embeddings()
        except Exception as e:
            self.logger.error(f"Error adding pattern: {str(e)}")
    
    def add_solution(self, solution_id: str, solution_text: str, contexts: Optional[List[str]] = None):
        """Add a solution to the search index with optional contexts."""
        try:
            # Compute and store embedding
            embedding = self._compute_embedding(solution_text)
            self.solution_embeddings[solution_id] = embedding
            self.solution_texts[solution_id] = solution_text
            
            # Store contexts
            if contexts:
                self.solution_contexts[solution_id].update(contexts)
            
            # Update cache
            self._save_cached_embeddings()
        except Exception as e:
            self.logger.error(f"Error adding solution: {str(e)}")
    
    def _process_search_batch(self, query_embedding: np.ndarray, items: List[Tuple[str, str, np.ndarray, str, Set[str]]]) -> List[SearchResult]:
        """Process a batch of items for search."""
        results = []
        for item_id, item_type, embedding, text, contexts in items:
            # Compute similarities
            semantic_similarity = self._cosine_similarity(query_embedding, embedding)
            fuzzy_similarity = self._compute_fuzzy_similarity(query_embedding, text)
            
            # Create result
            result = SearchResult(
                item_id=item_id,
                item_type=item_type,
                similarity_score=float(semantic_similarity),
                metadata={"text": text},
                fuzzy_score=float(fuzzy_similarity)
            )
            results.append(result)
        return results
    
    def search(self, query: str, top_k: int = 5, 
               search_patterns: bool = True, search_solutions: bool = True,
               use_fuzzy: bool = True, use_context: bool = True,
               context_weight: float = 0.3) -> List[SearchResult]:
        """Search for similar patterns and solutions with enhanced features."""
        try:
            # Compute query embedding
            query_embedding = self._compute_embedding(query)
            results = []
            
            # Prepare items for batch processing
            items = []
            if search_patterns:
                items.extend([
                    (pid, "pattern", emb, self.pattern_texts[pid], self.pattern_contexts[pid])
                    for pid, emb in self.pattern_embeddings.items()
                ])
            if search_solutions:
                items.extend([
                    (sid, "solution", emb, self.solution_texts[sid], self.solution_contexts[sid])
                    for sid, emb in self.solution_embeddings.items()
                ])
            
            # Process items in batches
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                batch_size = max(1, len(items) // (self.max_workers * 4))
                futures = []
                
                for i in range(0, len(items), batch_size):
                    batch = items[i:i + batch_size]
                    futures.append(
                        executor.submit(self._process_search_batch, query_embedding, batch)
                    )
                
                # Collect results
                for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
                    results.extend(future.result())
            
            # Combine similarity scores
            for result in results:
                if use_fuzzy and use_context:
                    # Combine semantic, fuzzy, and context similarities
                    result.similarity_score = (
                        result.similarity_score * (1 - context_weight) +
                        result.fuzzy_score * context_weight
                    )
                elif use_fuzzy:
                    # Combine semantic and fuzzy similarities
                    result.similarity_score = (
                        result.similarity_score * 0.7 +
                        result.fuzzy_score * 0.3
                    )
            
            # Sort by similarity score and return top k results
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            return results[:top_k]
            
        except Exception as e:
            self.logger.error(f"Error performing search: {str(e)}")
            return []
    
    def find_similar_patterns(self, pattern_id: str, top_k: int = 5,
                            use_fuzzy: bool = True, use_context: bool = True) -> List[SearchResult]:
        """Find patterns similar to a given pattern with enhanced features."""
        if pattern_id not in self.pattern_embeddings:
            return []
        
        pattern_embedding = self.pattern_embeddings[pattern_id]
        pattern_text = self.pattern_texts[pattern_id]
        pattern_contexts = self.pattern_contexts[pattern_id]
        
        results = []
        for other_id, embedding in self.pattern_embeddings.items():
            if other_id != pattern_id:
                # Compute similarities
                semantic_similarity = self._cosine_similarity(pattern_embedding, embedding)
                fuzzy_similarity = self._compute_fuzzy_similarity(pattern_text, self.pattern_texts[other_id])
                context_similarity = self._compute_context_similarity(
                    pattern_contexts,
                    self.pattern_contexts[other_id]
                )
                
                # Create result
                result = SearchResult(
                    item_id=other_id,
                    item_type="pattern",
                    similarity_score=float(semantic_similarity),
                    metadata={"text": self.pattern_texts[other_id]},
                    fuzzy_score=float(fuzzy_similarity),
                    context_similarity=float(context_similarity)
                )
                
                # Combine similarity scores
                if use_fuzzy and use_context:
                    result.similarity_score = (
                        result.similarity_score * 0.5 +
                        result.fuzzy_score * 0.3 +
                        result.context_similarity * 0.2
                    )
                elif use_fuzzy:
                    result.similarity_score = (
                        result.similarity_score * 0.7 +
                        result.fuzzy_score * 0.3
                    )
                
                results.append(result)
        
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:top_k]
    
    def find_similar_solutions(self, solution_id: str, top_k: int = 5,
                             use_fuzzy: bool = True, use_context: bool = True) -> List[SearchResult]:
        """Find solutions similar to a given solution with enhanced features."""
        if solution_id not in self.solution_embeddings:
            return []
        
        solution_embedding = self.solution_embeddings[solution_id]
        solution_text = self.solution_texts[solution_id]
        solution_contexts = self.solution_contexts[solution_id]
        
        results = []
        for other_id, embedding in self.solution_embeddings.items():
            if other_id != solution_id:
                # Compute similarities
                semantic_similarity = self._cosine_similarity(solution_embedding, embedding)
                fuzzy_similarity = self._compute_fuzzy_similarity(solution_text, self.solution_texts[other_id])
                context_similarity = self._compute_context_similarity(
                    solution_contexts,
                    self.solution_contexts[other_id]
                )
                
                # Create result
                result = SearchResult(
                    item_id=other_id,
                    item_type="solution",
                    similarity_score=float(semantic_similarity),
                    metadata={"text": self.solution_texts[other_id]},
                    fuzzy_score=float(fuzzy_similarity),
                    context_similarity=float(context_similarity)
                )
                
                # Combine similarity scores
                if use_fuzzy and use_context:
                    result.similarity_score = (
                        result.similarity_score * 0.5 +
                        result.fuzzy_score * 0.3 +
                        result.context_similarity * 0.2
                    )
                elif use_fuzzy:
                    result.similarity_score = (
                        result.similarity_score * 0.7 +
                        result.fuzzy_score * 0.3
                    )
                
                results.append(result)
        
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:top_k]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the search index."""
        return {
            "total_patterns": len(self.pattern_embeddings),
            "total_solutions": len(self.solution_embeddings),
            "embedding_dimension": self.model.get_sentence_embedding_dimension(),
            "model_name": self.model.__class__.__name__,
            "patterns_with_context": sum(1 for c in self.pattern_contexts.values() if c),
            "solutions_with_context": sum(1 for c in self.solution_contexts.values() if c),
            "average_contexts_per_pattern": np.mean([len(c) for c in self.pattern_contexts.values()]),
            "average_contexts_per_solution": np.mean([len(c) for c in self.solution_contexts.values()])
        } 