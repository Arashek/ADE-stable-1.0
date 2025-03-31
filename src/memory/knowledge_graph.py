from typing import Dict, List, Any, Optional, Tuple
import networkx as nx
import logging
from datetime import datetime
import json
import os

from .memory_manager import MemoryEntry, MemoryType

logger = logging.getLogger(__name__)

class KnowledgeGraph:
    def __init__(self):
        """Initialize knowledge graph"""
        self.graph = nx.DiGraph()
        self.edge_types = {
            "related_to": "RELATED_TO",
            "depends_on": "DEPENDS_ON",
            "similar_to": "SIMILAR_TO",
            "contradicts": "CONTRADICTS",
            "supports": "SUPPORTS"
        }
        
    def add_memory(self, memory: MemoryEntry) -> None:
        """Add a memory node to the graph
        
        Args:
            memory: Memory entry to add
        """
        try:
            # Add node with memory attributes
            self.graph.add_node(
                memory.id,
                type=memory.type.value,
                content=memory.content,
                created_at=memory.created_at,
                project_id=memory.project_id,
                agent_id=memory.agent_id,
                tags=memory.tags
            )
            
            # Analyze relationships with existing memories
            self._analyze_relationships(memory)
            
        except Exception as e:
            logger.error(f"Failed to add memory to knowledge graph: {str(e)}")
            raise
            
    def update_memory(self, memory: MemoryEntry) -> None:
        """Update a memory node in the graph
        
        Args:
            memory: Updated memory entry
        """
        try:
            if not self.graph.has_node(memory.id):
                raise ValueError(f"Memory not found in graph: {memory.id}")
                
            # Update node attributes
            self.graph.nodes[memory.id].update({
                "type": memory.type.value,
                "content": memory.content,
                "project_id": memory.project_id,
                "agent_id": memory.agent_id,
                "tags": memory.tags
            })
            
            # Re-analyze relationships
            self._analyze_relationships(memory)
            
        except Exception as e:
            logger.error(f"Failed to update memory in knowledge graph: {str(e)}")
            raise
            
    def delete_memory(self, memory_id: str) -> None:
        """Delete a memory node from the graph
        
        Args:
            memory_id: ID of memory to delete
        """
        try:
            if self.graph.has_node(memory_id):
                self.graph.remove_node(memory_id)
                
        except Exception as e:
            logger.error(f"Failed to delete memory from knowledge graph: {str(e)}")
            raise
            
    def get_related_memories(
        self,
        memory_id: str,
        relationship_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Tuple[str, str, Dict[str, Any]]]:
        """Get memories related to a given memory
        
        Args:
            memory_id: ID of memory to find relations for
            relationship_type: Optional type of relationship to filter by
            limit: Maximum number of results
            
        Returns:
            List of (source_id, target_id, edge_data) tuples
        """
        try:
            if not self.graph.has_node(memory_id):
                return []
                
            # Get all edges connected to the memory
            edges = []
            for edge in self.graph.edges(memory_id, data=True):
                if relationship_type is None or edge[2].get("type") == relationship_type:
                    edges.append(edge)
                    
            # Sort by relationship strength
            edges.sort(key=lambda x: x[2].get("strength", 0), reverse=True)
            
            return edges[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get related memories: {str(e)}")
            raise
            
    def get_memory_path(
        self,
        source_id: str,
        target_id: str,
        max_length: int = 3
    ) -> Optional[List[Tuple[str, str, Dict[str, Any]]]]:
        """Find a path between two memories
        
        Args:
            source_id: ID of source memory
            target_id: ID of target memory
            max_length: Maximum path length
            
        Returns:
            List of (source_id, target_id, edge_data) tuples if path exists
        """
        try:
            if not self.graph.has_node(source_id) or not self.graph.has_node(target_id):
                return None
                
            # Find shortest path
            path = nx.shortest_path(
                self.graph,
                source=source_id,
                target=target_id
            )
            
            if len(path) > max_length:
                return None
                
            # Get edges along the path
            edges = []
            for i in range(len(path) - 1):
                edge_data = self.graph.get_edge_data(path[i], path[i + 1])
                edges.append((path[i], path[i + 1], edge_data))
                
            return edges
            
        except nx.NetworkXNoPath:
            return None
        except Exception as e:
            logger.error(f"Failed to find memory path: {str(e)}")
            raise
            
    def get_memory_cluster(
        self,
        memory_id: str,
        max_distance: float = 0.7
    ) -> List[str]:
        """Get cluster of related memories
        
        Args:
            memory_id: ID of memory to find cluster for
            max_distance: Maximum distance for clustering
            
        Returns:
            List of memory IDs in the cluster
        """
        try:
            if not self.graph.has_node(memory_id):
                return []
                
            # Use community detection to find clusters
            communities = nx.community.louvain_communities(self.graph.to_undirected())
            
            # Find community containing the memory
            for community in communities:
                if memory_id in community:
                    return list(community)
                    
            return []
            
        except Exception as e:
            logger.error(f"Failed to get memory cluster: {str(e)}")
            raise
            
    def save(self, path: str) -> None:
        """Save the knowledge graph to disk
        
        Args:
            path: Path to save the graph
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(path, exist_ok=True)
            
            # Save graph data
            graph_data = nx.node_link_data(self.graph)
            with open(f"{path}/graph.json", "w") as f:
                json.dump(graph_data, f)
                
            # Save metadata
            metadata = {
                "edge_types": self.edge_types,
                "last_updated": datetime.now().isoformat()
            }
            with open(f"{path}/metadata.json", "w") as f:
                json.dump(metadata, f)
                
        except Exception as e:
            logger.error(f"Failed to save knowledge graph: {str(e)}")
            raise
            
    @classmethod
    def load(cls, path: str) -> "KnowledgeGraph":
        """Load the knowledge graph from disk
        
        Args:
            path: Path to load the graph from
            
        Returns:
            Loaded knowledge graph
        """
        try:
            # Create graph instance
            graph = cls()
            
            # Load graph data
            with open(f"{path}/graph.json", "r") as f:
                graph_data = json.load(f)
                graph.graph = nx.node_link_graph(graph_data)
                
            # Load metadata
            with open(f"{path}/metadata.json", "r") as f:
                metadata = json.load(f)
                graph.edge_types = metadata["edge_types"]
                
            return graph
            
        except Exception as e:
            logger.error(f"Failed to load knowledge graph: {str(e)}")
            raise
            
    def _analyze_relationships(self, memory: MemoryEntry) -> None:
        """Analyze relationships between memories
        
        Args:
            memory: Memory entry to analyze relationships for
        """
        try:
            # Get existing memories of the same type
            same_type_memories = [
                node for node, data in self.graph.nodes(data=True)
                if data.get("type") == memory.type.value
            ]
            
            # Analyze relationships with each memory
            for other_id in same_type_memories:
                if other_id == memory.id:
                    continue
                    
                # Calculate relationship strength based on content similarity
                strength = self._calculate_relationship_strength(
                    memory.content,
                    self.graph.nodes[other_id]["content"]
                )
                
                if strength > 0.5:  # Threshold for creating relationship
                    # Determine relationship type
                    rel_type = self._determine_relationship_type(
                        memory.content,
                        self.graph.nodes[other_id]["content"]
                    )
                    
                    # Add edge with relationship data
                    self.graph.add_edge(
                        memory.id,
                        other_id,
                        type=rel_type,
                        strength=strength,
                        created_at=datetime.now().isoformat()
                    )
                    
        except Exception as e:
            logger.error(f"Failed to analyze relationships: {str(e)}")
            raise
            
    def _calculate_relationship_strength(
        self,
        content1: Dict[str, Any],
        content2: Dict[str, Any]
    ) -> float:
        """Calculate relationship strength between two memories
        
        Args:
            content1: Content of first memory
            content2: Content of second memory
            
        Returns:
            Relationship strength (0.0 to 1.0)
        """
        # TODO: Implement more sophisticated similarity calculation
        # For now, using a simple text-based similarity
        text1 = str(content1).lower()
        text2 = str(content2).lower()
        
        # Calculate Jaccard similarity
        set1 = set(text1.split())
        set2 = set(text2.split())
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
        
    def _determine_relationship_type(
        self,
        content1: Dict[str, Any],
        content2: Dict[str, Any]
    ) -> str:
        """Determine the type of relationship between memories
        
        Args:
            content1: Content of first memory
            content2: Content of second memory
            
        Returns:
            Relationship type
        """
        # TODO: Implement more sophisticated relationship type determination
        # For now, using a simple heuristic
        strength = self._calculate_relationship_strength(content1, content2)
        
        if strength > 0.8:
            return self.edge_types["similar_to"]
        elif strength > 0.6:
            return self.edge_types["related_to"]
        else:
            return self.edge_types["depends_on"] 