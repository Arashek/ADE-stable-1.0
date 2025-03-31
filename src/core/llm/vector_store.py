from typing import Dict, List, Optional, Any
import numpy as np
from dataclasses import dataclass
import logging
from pathlib import Path
import json
import faiss
import pickle
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class ErrorEmbedding:
    """Container for error embedding and metadata."""
    error_id: str
    embedding: np.ndarray
    metadata: Dict[str, Any]
    timestamp: datetime

class VectorStore:
    """Vector store for error embeddings using FAISS."""
    
    def __init__(self, index_path: Optional[str] = None):
        """
        Initialize the vector store.
        
        Args:
            index_path: Path to save/load the FAISS index
        """
        self.index_path = index_path
        self.dimension = 1536  # OpenAI embedding dimension
        self.index = self._initialize_index()
        self.metadata_store = {}
        
    def _initialize_index(self) -> faiss.Index:
        """Initialize or load FAISS index."""
        if self.index_path and Path(self.index_path).exists():
            return self._load_index()
        return faiss.IndexFlatL2(self.dimension)
    
    def _load_index(self) -> faiss.Index:
        """Load FAISS index from file."""
        try:
            index = faiss.read_index(self.index_path)
            metadata_path = Path(self.index_path).with_suffix('.meta')
            if metadata_path.exists():
                with open(metadata_path, 'rb') as f:
                    self.metadata_store = pickle.load(f)
            return index
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return faiss.IndexFlatL2(self.dimension)
    
    def save_index(self) -> None:
        """Save FAISS index and metadata to file."""
        if self.index_path:
            try:
                faiss.write_index(self.index, self.index_path)
                metadata_path = Path(self.index_path).with_suffix('.meta')
                with open(metadata_path, 'wb') as f:
                    pickle.dump(self.metadata_store, f)
            except Exception as e:
                logger.error(f"Failed to save index: {e}")
    
    def add_error(
        self,
        error_id: str,
        embedding: np.ndarray,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Add an error embedding to the store.
        
        Args:
            error_id: Unique identifier for the error
            embedding: Vector embedding of the error
            metadata: Additional error metadata
        """
        try:
            # Add embedding to FAISS index
            self.index.add(np.array([embedding], dtype=np.float32))
            
            # Store metadata
            self.metadata_store[error_id] = ErrorEmbedding(
                error_id=error_id,
                embedding=embedding,
                metadata=metadata,
                timestamp=datetime.utcnow()
            )
            
            # Save index periodically
            if len(self.metadata_store) % 100 == 0:
                self.save_index()
                
        except Exception as e:
            logger.error(f"Failed to add error to vector store: {e}")
            raise
    
    def find_similar_errors(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
        threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Find similar errors using vector similarity.
        
        Args:
            query_embedding: Query vector
            k: Number of results to return
            threshold: Similarity threshold
            
        Returns:
            List of similar errors with metadata
        """
        try:
            # Search in FAISS index
            distances, indices = self.index.search(
                np.array([query_embedding], dtype=np.float32),
                k
            )
            
            # Convert distances to similarities
            similarities = 1 / (1 + distances[0])
            
            # Get results above threshold
            results = []
            for i, (idx, similarity) in enumerate(zip(indices[0], similarities)):
                if similarity >= threshold:
                    error_id = list(self.metadata_store.keys())[idx]
                    error_data = self.metadata_store[error_id]
                    results.append({
                        "error_id": error_id,
                        "similarity": float(similarity),
                        "metadata": error_data.metadata,
                        "timestamp": error_data.timestamp
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to find similar errors: {e}")
            raise
    
    def get_error(self, error_id: str) -> Optional[ErrorEmbedding]:
        """
        Retrieve error data by ID.
        
        Args:
            error_id: Error identifier
            
        Returns:
            ErrorEmbedding if found, None otherwise
        """
        return self.metadata_store.get(error_id)
    
    def update_error(
        self,
        error_id: str,
        embedding: Optional[np.ndarray] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update error data in the store.
        
        Args:
            error_id: Error identifier
            embedding: New embedding (optional)
            metadata: New metadata (optional)
        """
        if error_id not in self.metadata_store:
            raise ValueError(f"Error {error_id} not found")
            
        current_data = self.metadata_store[error_id]
        
        if embedding is not None:
            current_data.embedding = embedding
            
        if metadata is not None:
            current_data.metadata.update(metadata)
            
        current_data.timestamp = datetime.utcnow()
    
    def delete_error(self, error_id: str) -> None:
        """
        Delete error from the store.
        
        Args:
            error_id: Error identifier
        """
        if error_id not in self.metadata_store:
            raise ValueError(f"Error {error_id} not found")
            
        # Remove from metadata store
        del self.metadata_store[error_id]
        
        # Rebuild index without the deleted error
        self._rebuild_index()
    
    def _rebuild_index(self) -> None:
        """Rebuild FAISS index from current metadata."""
        try:
            # Create new index
            self.index = faiss.IndexFlatL2(self.dimension)
            
            # Add all embeddings
            embeddings = np.array([
                data.embedding for data in self.metadata_store.values()
            ], dtype=np.float32)
            
            if len(embeddings) > 0:
                self.index.add(embeddings)
                
            # Save updated index
            self.save_index()
            
        except Exception as e:
            logger.error(f"Failed to rebuild index: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            "total_errors": len(self.metadata_store),
            "index_size": self.index.ntotal,
            "dimension": self.dimension,
            "last_updated": max(
                (data.timestamp for data in self.metadata_store.values()),
                default=None
            )
        }

    def cluster_errors(
        self,
        n_clusters: int = 5,
        min_cluster_size: int = 2
    ) -> Dict[str, Any]:
        """
        Cluster similar errors using K-means.
        
        Args:
            n_clusters: Number of clusters to create
            min_cluster_size: Minimum size for a valid cluster
            
        Returns:
            Dict containing cluster information and statistics
        """
        try:
            if len(self.metadata_store) < n_clusters:
                raise ValueError("Not enough errors for clustering")
                
            # Extract embeddings
            embeddings = np.array([
                data.embedding for data in self.metadata_store.values()
            ], dtype=np.float32)
            
            # Perform K-means clustering
            kmeans = faiss.Kmeans(self.dimension, n_clusters)
            kmeans.train(embeddings)
            
            # Get cluster assignments
            _, labels = kmeans.index.search(embeddings, 1)
            
            # Group errors by cluster
            clusters = {}
            for i, label in enumerate(labels):
                cluster_id = int(label[0])
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                error_id = list(self.metadata_store.keys())[i]
                clusters[cluster_id].append(error_id)
            
            # Filter small clusters
            valid_clusters = {
                k: v for k, v in clusters.items()
                if len(v) >= min_cluster_size
            }
            
            # Calculate cluster statistics
            stats = {
                "total_clusters": len(valid_clusters),
                "total_errors": len(self.metadata_store),
                "cluster_sizes": {
                    k: len(v) for k, v in valid_clusters.items()
                },
                "cluster_centroids": kmeans.centroids.tolist()
            }
            
            return {
                "clusters": valid_clusters,
                "statistics": stats
            }
            
        except Exception as e:
            logger.error(f"Failed to cluster errors: {e}")
            raise

    def analyze_error_trends(
        self,
        time_window: int = 7  # days
    ) -> Dict[str, Any]:
        """
        Analyze error trends over time.
        
        Args:
            time_window: Time window in days
            
        Returns:
            Dict containing trend analysis results
        """
        try:
            # Get current time
            now = datetime.utcnow()
            window_start = now - timedelta(days=time_window)
            
            # Filter errors within time window
            recent_errors = {
                k: v for k, v in self.metadata_store.items()
                if v.timestamp >= window_start
            }
            
            # Group errors by type
            error_types = {}
            for error_data in recent_errors.values():
                error_type = error_data.metadata.get("error_type", "unknown")
                if error_type not in error_types:
                    error_types[error_type] = []
                error_types[error_type].append(error_data)
            
            # Calculate trends
            trends = {}
            for error_type, errors in error_types.items():
                # Sort errors by timestamp
                sorted_errors = sorted(errors, key=lambda x: x.timestamp)
                
                # Calculate frequency
                frequency = len(errors) / time_window
                
                # Calculate severity (if available)
                severities = [
                    error.metadata.get("severity", 0)
                    for error in errors
                ]
                avg_severity = sum(severities) / len(severities) if severities else 0
                
                trends[error_type] = {
                    "count": len(errors),
                    "frequency": frequency,
                    "average_severity": avg_severity,
                    "first_occurrence": sorted_errors[0].timestamp,
                    "last_occurrence": sorted_errors[-1].timestamp
                }
            
            return {
                "time_window": time_window,
                "total_errors": len(recent_errors),
                "error_types": len(error_types),
                "trends": trends
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze error trends: {e}")
            raise

    def filter_by_metadata(
        self,
        criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Filter errors by metadata criteria.
        
        Args:
            criteria: Dictionary of metadata criteria
            
        Returns:
            List of matching errors
        """
        try:
            matches = []
            for error_id, error_data in self.metadata_store.items():
                # Check if error matches all criteria
                matches_all = True
                for key, value in criteria.items():
                    if key not in error_data.metadata or error_data.metadata[key] != value:
                        matches_all = False
                        break
                
                if matches_all:
                    matches.append({
                        "error_id": error_id,
                        "metadata": error_data.metadata,
                        "timestamp": error_data.timestamp,
                        "embedding": error_data.embedding
                    })
            
            return matches
            
        except Exception as e:
            logger.error(f"Failed to filter errors: {e}")
            raise

    def get_error_statistics(
        self,
        group_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get detailed error statistics.
        
        Args:
            group_by: Optional field to group statistics by
            
        Returns:
            Dict containing error statistics
        """
        try:
            stats = {
                "total_errors": len(self.metadata_store),
                "error_types": {},
                "severity_distribution": {},
                "timestamp_range": {
                    "earliest": None,
                    "latest": None
                }
            }
            
            # Calculate basic statistics
            timestamps = []
            for error_data in self.metadata_store.values():
                # Count error types
                error_type = error_data.metadata.get("error_type", "unknown")
                stats["error_types"][error_type] = stats["error_types"].get(error_type, 0) + 1
                
                # Count severity levels
                severity = error_data.metadata.get("severity", 0)
                stats["severity_distribution"][severity] = stats["severity_distribution"].get(severity, 0) + 1
                
                # Track timestamps
                timestamps.append(error_data.timestamp)
            
            # Set timestamp range
            if timestamps:
                stats["timestamp_range"]["earliest"] = min(timestamps)
                stats["timestamp_range"]["latest"] = max(timestamps)
            
            # Group statistics if requested
            if group_by and group_by in ["error_type", "severity", "location"]:
                grouped_stats = {}
                for error_data in self.metadata_store.values():
                    group_value = error_data.metadata.get(group_by, "unknown")
                    if group_value not in grouped_stats:
                        grouped_stats[group_value] = {
                            "count": 0,
                            "error_types": {},
                            "severity_distribution": {}
                        }
                    
                    grouped_stats[group_value]["count"] += 1
                    
                    # Group error types
                    error_type = error_data.metadata.get("error_type", "unknown")
                    grouped_stats[group_value]["error_types"][error_type] = \
                        grouped_stats[group_value]["error_types"].get(error_type, 0) + 1
                    
                    # Group severity levels
                    severity = error_data.metadata.get("severity", 0)
                    grouped_stats[group_value]["severity_distribution"][severity] = \
                        grouped_stats[group_value]["severity_distribution"].get(severity, 0) + 1
                
                stats["grouped_statistics"] = grouped_stats
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to calculate error statistics: {e}")
            raise 