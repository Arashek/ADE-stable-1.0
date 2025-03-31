from typing import Dict, List, Any, Optional
import numpy as np
import faiss
import json
import logging
from datetime import datetime

from .memory_manager import MemoryEntry, MemoryType

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, dimension: int = 768):
        """Initialize vector store with FAISS index
        
        Args:
            dimension: Dimension of the vectors (default: 768 for BERT embeddings)
        """
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.memory_map: Dict[int, str] = {}  # Maps FAISS index to memory ID
        self.next_id = 0
        
    def add_memory(self, memory: MemoryEntry) -> None:
        """Add a memory entry to the vector store
        
        Args:
            memory: Memory entry to add
        """
        if not memory.embedding:
            raise ValueError("Memory must have an embedding")
            
        # Add to FAISS index
        embedding_array = np.array([memory.embedding], dtype=np.float32)
        self.index.add(embedding_array)
        
        # Map index to memory ID
        self.memory_map[self.next_id] = memory.id
        self.next_id += 1
        
    def search(
        self,
        query_embedding: List[float],
        k: int = 10,
        memory_type: Optional[MemoryType] = None
    ) -> List[tuple[str, float]]:
        """Search for similar memories
        
        Args:
            query_embedding: Query vector
            k: Number of results to return
            memory_type: Optional memory type filter
            
        Returns:
            List of (memory_id, distance) tuples
        """
        # Convert query to numpy array
        query_array = np.array([query_embedding], dtype=np.float32)
        
        # Search in FAISS index
        distances, indices = self.index.search(query_array, k)
        
        # Convert distances to similarity scores (1 / (1 + distance))
        similarities = 1 / (1 + distances[0])
        
        # Get memory IDs and create results
        results = []
        for idx, (memory_idx, similarity) in enumerate(zip(indices[0], similarities)):
            if memory_idx == -1:  # FAISS returns -1 for empty slots
                continue
                
            memory_id = self.memory_map.get(memory_idx)
            if memory_id:
                results.append((memory_id, float(similarity)))
                
        return results
        
    def update_memory(self, memory: MemoryEntry) -> None:
        """Update a memory entry in the vector store
        
        Args:
            memory: Updated memory entry
        """
        if not memory.embedding:
            raise ValueError("Memory must have an embedding")
            
        # Find the index of the memory
        memory_idx = None
        for idx, mem_id in self.memory_map.items():
            if mem_id == memory.id:
                memory_idx = idx
                break
                
        if memory_idx is None:
            raise ValueError(f"Memory not found: {memory.id}")
            
        # Update the vector in FAISS
        embedding_array = np.array([memory.embedding], dtype=np.float32)
        self.index.remove_ids(np.array([memory_idx]))
        self.index.add(embedding_array)
        
    def delete_memory(self, memory_id: str) -> None:
        """Delete a memory entry from the vector store
        
        Args:
            memory_id: ID of memory to delete
        """
        # Find the index of the memory
        memory_idx = None
        for idx, mem_id in self.memory_map.items():
            if mem_id == memory_id:
                memory_idx = idx
                break
                
        if memory_idx is not None:
            # Remove from FAISS index
            self.index.remove_ids(np.array([memory_idx]))
            
            # Remove from memory map
            del self.memory_map[memory_idx]
            
    def save(self, path: str) -> None:
        """Save the vector store to disk
        
        Args:
            path: Path to save the store
        """
        # Save FAISS index
        faiss.write_index(self.index, f"{path}/index.faiss")
        
        # Save memory map
        with open(f"{path}/memory_map.json", "w") as f:
            json.dump(self.memory_map, f)
            
        # Save metadata
        metadata = {
            "dimension": self.dimension,
            "next_id": self.next_id,
            "last_updated": datetime.now().isoformat()
        }
        with open(f"{path}/metadata.json", "w") as f:
            json.dump(metadata, f)
            
    @classmethod
    def load(cls, path: str) -> "VectorStore":
        """Load the vector store from disk
        
        Args:
            path: Path to load the store from
            
        Returns:
            Loaded vector store
        """
        # Load metadata
        with open(f"{path}/metadata.json", "r") as f:
            metadata = json.load(f)
            
        # Create store instance
        store = cls(dimension=metadata["dimension"])
        store.next_id = metadata["next_id"]
        
        # Load FAISS index
        store.index = faiss.read_index(f"{path}/index.faiss")
        
        # Load memory map
        with open(f"{path}/memory_map.json", "r") as f:
            store.memory_map = json.load(f)
            
        return store 