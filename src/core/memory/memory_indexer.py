from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime
import logging
from dataclasses import dataclass
from .knowledge_repository import KnowledgeEntry, KnowledgeRepository

@dataclass
class SearchResult:
    entry: KnowledgeEntry
    relevance_score: float
    context: Optional[str] = None

class MemoryIndexer:
    def __init__(self, repository: KnowledgeRepository):
        self.repository = repository
        self.logger = logging.getLogger(__name__)
        self._initialize_embeddings()

    def _initialize_embeddings(self):
        """Initialize or load the embeddings index."""
        self.embeddings_path = self.repository.storage_path / "embeddings.npz"
        if self.embeddings_path.exists():
            self.embeddings = np.load(self.embeddings_path)
        else:
            self.embeddings = {}

    def _save_embeddings(self):
        """Save the embeddings to disk."""
        np.savez(self.embeddings_path, **self.embeddings)

    def _compute_embedding(self, text: str) -> np.ndarray:
        """Compute embedding for a given text using a pre-trained model."""
        # TODO: Implement actual embedding computation using a model like BERT or SentenceTransformer
        # For now, return a dummy embedding
        return np.random.rand(768)

    def index_entry(self, entry: KnowledgeEntry) -> bool:
        """Index a knowledge entry with its embedding."""
        try:
            embedding = self._compute_embedding(entry.content)
            self.embeddings[entry.id] = embedding
            self._save_embeddings()
            return True
        except Exception as e:
            self.logger.error(f"Error indexing entry {entry.id}: {e}")
            return False

    def semantic_search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Perform semantic search using embeddings."""
        query_embedding = self._compute_embedding(query)
        results = []

        for entry_id, embedding in self.embeddings.items():
            entry = self.repository.get_entry(entry_id)
            if not entry:
                continue

            # Compute cosine similarity
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )

            # Apply importance score weighting
            weighted_score = similarity * entry.importance_score

            results.append(SearchResult(
                entry=entry,
                relevance_score=weighted_score
            ))

        # Sort by relevance score and return top results
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]

    def find_similar_entries(self, entry_id: str, limit: int = 5) -> List[SearchResult]:
        """Find entries similar to a given entry."""
        entry = self.repository.get_entry(entry_id)
        if not entry or entry_id not in self.embeddings:
            return []

        entry_embedding = self.embeddings[entry_id]
        results = []

        for other_id, embedding in self.embeddings.items():
            if other_id == entry_id:
                continue

            other_entry = self.repository.get_entry(other_id)
            if not other_entry:
                continue

            # Compute cosine similarity
            similarity = np.dot(entry_embedding, embedding) / (
                np.linalg.norm(entry_embedding) * np.linalg.norm(embedding)
            )

            # Apply importance score weighting
            weighted_score = similarity * other_entry.importance_score

            results.append(SearchResult(
                entry=other_entry,
                relevance_score=weighted_score
            ))

        # Sort by relevance score and return top results
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]

    def find_related_entries(self, entry_id: str, limit: int = 5) -> List[SearchResult]:
        """Find entries related to a given entry through tags and references."""
        entry = self.repository.get_entry(entry_id)
        if not entry:
            return []

        results = []
        related_ids = set()

        # Find entries with matching tags
        for tag in entry.tags:
            tag_entries = self.repository.search_by_tags([tag])
            for tag_entry in tag_entries:
                if tag_entry.id != entry_id:
                    related_ids.add(tag_entry.id)

        # Find entries referenced by the given entry
        for ref_id in entry.references:
            ref_entry = self.repository.get_entry(ref_id)
            if ref_entry:
                related_ids.add(ref_id)

        # Find entries that reference the given entry
        for other_id in self.repository.index["entries"]:
            other_entry = self.repository.get_entry(other_id)
            if other_entry and entry_id in other_entry.references:
                related_ids.add(other_id)

        # Compute relevance scores for related entries
        for related_id in related_ids:
            related_entry = self.repository.get_entry(related_id)
            if not related_entry:
                continue

            # Compute relevance score based on tag overlap and reference relationships
            tag_overlap = len(set(entry.tags) & set(related_entry.tags))
            reference_score = 1.0 if entry_id in related_entry.references or related_id in entry.references else 0.0
            
            relevance_score = (tag_overlap / max(len(entry.tags), len(related_entry.tags))) * 0.7 + reference_score * 0.3
            relevance_score *= related_entry.importance_score

            results.append(SearchResult(
                entry=related_entry,
                relevance_score=relevance_score
            ))

        # Sort by relevance score and return top results
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]

    def find_recent_entries(self, days: int = 7, limit: int = 10) -> List[KnowledgeEntry]:
        """Find recently added or updated entries."""
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        recent_entries = []

        for entry_id in self.repository.index["entries"]:
            entry = self.repository.get_entry(entry_id)
            if not entry:
                continue

            if entry.created_at.timestamp() > cutoff_date or entry.updated_at.timestamp() > cutoff_date:
                recent_entries.append(entry)

        # Sort by update time and return top results
        recent_entries.sort(key=lambda x: x.updated_at, reverse=True)
        return recent_entries[:limit]

    def find_important_entries(self, limit: int = 10) -> List[KnowledgeEntry]:
        """Find entries with high importance scores."""
        return self.repository.get_entries_by_importance(limit)

    def update_entry_embedding(self, entry_id: str) -> bool:
        """Update the embedding for a given entry."""
        entry = self.repository.get_entry(entry_id)
        if not entry:
            return False

        return self.index_entry(entry)

    def reindex_all(self) -> bool:
        """Reindex all entries in the repository."""
        try:
            for entry_id in self.repository.index["entries"]:
                entry = self.repository.get_entry(entry_id)
                if entry:
                    self.index_entry(entry)
            return True
        except Exception as e:
            self.logger.error(f"Error reindexing entries: {e}")
            return False

    def get_entry_context(self, entry_id: str, context_size: int = 3) -> List[KnowledgeEntry]:
        """Get contextual entries around a given entry."""
        entry = self.repository.get_entry(entry_id)
        if not entry:
            return []

        # Get related entries
        related = self.find_related_entries(entry_id, limit=context_size * 2)
        
        # Get similar entries
        similar = self.find_similar_entries(entry_id, limit=context_size * 2)

        # Combine and deduplicate entries
        context_entries = {}
        for result in related + similar:
            context_entries[result.entry.id] = result.entry

        # Sort by relevance score
        sorted_entries = sorted(
            context_entries.values(),
            key=lambda x: x.importance_score,
            reverse=True
        )

        return sorted_entries[:context_size] 