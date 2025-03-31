from typing import Dict, Any, List, Optional, Set, Tuple
import logging
from datetime import datetime
import json
from dataclasses import dataclass
from collections import defaultdict
import uuid

from .memory_manager import MemoryManager, MemoryType, MemoryEntry

logger = logging.getLogger(__name__)

@dataclass
class Pattern:
    """Represents a recognized pattern across projects"""
    id: str
    name: str
    description: str
    examples: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: str = datetime.now().isoformat()
    updated_at: str = datetime.now().isoformat()
    success_rate: float = 0.0
    usage_count: int = 0

@dataclass
class KnowledgeGraph:
    """Represents a knowledge graph of related concepts"""
    nodes: Dict[str, Dict[str, Any]]
    edges: Dict[str, List[Dict[str, Any]]]
    metadata: Dict[str, Any]
    created_at: str = datetime.now().isoformat()
    updated_at: str = datetime.now().isoformat()

class CrossProjectLearning:
    """Handles pattern recognition and knowledge transfer across projects"""
    
    def __init__(
        self,
        memory_manager: MemoryManager,
        min_pattern_confidence: float = 0.7,
        max_pattern_examples: int = 10
    ):
        self.memory_manager = memory_manager
        self.min_pattern_confidence = min_pattern_confidence
        self.max_pattern_examples = max_pattern_examples
        
        # Initialize pattern storage
        self.patterns: Dict[str, Pattern] = {}
        self.pattern_usage: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Initialize knowledge graph
        self.knowledge_graph = KnowledgeGraph(
            nodes={},
            edges={},
            metadata={
                "num_nodes": 0,
                "num_edges": 0,
                "last_updated": datetime.now().isoformat()
            }
        )
    
    async def analyze_project_patterns(self, project_id: str) -> List[Pattern]:
        """Analyze patterns in a specific project
        
        Args:
            project_id: Project ID to analyze
            
        Returns:
            List of identified patterns
        """
        try:
            # Retrieve project memories
            project_memories = await self.memory_manager.retrieve_memories(
                query={},
                project_id=project_id,
                limit=1000
            )
            
            # Analyze patterns
            patterns = await self._analyze_patterns(project_memories)
            
            # Store patterns
            for pattern in patterns:
                self.patterns[pattern.id] = pattern
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to analyze project patterns: {str(e)}")
            raise
    
    async def analyze_cross_project_patterns(self) -> List[Pattern]:
        """Analyze patterns across all projects
        
        Returns:
            List of identified patterns
        """
        try:
            # Retrieve all project memories
            all_memories = await self.memory_manager.retrieve_memories(
                query={},
                limit=10000
            )
            
            # Analyze patterns
            patterns = await self._analyze_cross_project_patterns(all_memories)
            
            # Store patterns
            for pattern in patterns:
                self.patterns[pattern.id] = pattern
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to analyze cross-project patterns: {str(e)}")
            raise
    
    async def update_knowledge_graph(
        self,
        memories: List[MemoryEntry]
    ) -> KnowledgeGraph:
        """Update knowledge graph with new memories
        
        Args:
            memories: List of memories to incorporate
            
        Returns:
            Updated knowledge graph
        """
        try:
            # Extract concepts from memories
            concepts = await self._extract_concepts(memories)
            
            # Update nodes
            for concept in concepts:
                if concept not in self.knowledge_graph.nodes:
                    self.knowledge_graph.nodes[concept] = {
                        "id": concept,
                        "type": "concept",
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                        "usage_count": 0
                    }
                else:
                    self.knowledge_graph.nodes[concept]["usage_count"] += 1
                    self.knowledge_graph.nodes[concept]["updated_at"] = datetime.now().isoformat()
            
            # Update edges
            for i, memory1 in enumerate(memories):
                for memory2 in memories[i+1:]:
                    edge_id = f"{memory1.id}_{memory2.id}"
                    if edge_id not in self.knowledge_graph.edges:
                        self.knowledge_graph.edges[edge_id] = []
                    
                    # Add relationship
                    relationship = await self._determine_relationship(memory1, memory2)
                    if relationship:
                        self.knowledge_graph.edges[edge_id].append({
                            "type": relationship,
                            "created_at": datetime.now().isoformat(),
                            "confidence": await self._calculate_relationship_confidence(
                                memory1, memory2, relationship
                            )
                        })
            
            # Update metadata
            self.knowledge_graph.metadata.update({
                "num_nodes": len(self.knowledge_graph.nodes),
                "num_edges": sum(len(edges) for edges in self.knowledge_graph.edges.values()),
                "last_updated": datetime.now().isoformat()
            })
            
            return self.knowledge_graph
            
        except Exception as e:
            logger.error(f"Failed to update knowledge graph: {str(e)}")
            raise
    
    async def get_relevant_patterns(
        self,
        query: str,
        project_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Pattern]:
        """Get patterns relevant to a query
        
        Args:
            query: Query to find relevant patterns for
            project_id: Optional project ID to filter by
            limit: Maximum number of patterns to return
            
        Returns:
            List of relevant patterns
        """
        try:
            # Generate query embedding
            query_embedding = await self.memory_manager._generate_embedding({"text": query})
            
            # Search for relevant memories
            memories = await self.memory_manager.retrieve_memories(
                query=query_embedding,
                project_id=project_id,
                limit=100
            )
            
            # Find patterns with high relevance
            relevant_patterns = []
            for pattern in self.patterns.values():
                relevance = await self._calculate_pattern_relevance(pattern, memories)
                if relevance >= self.min_pattern_confidence:
                    relevant_patterns.append((pattern, relevance))
            
            # Sort by relevance and limit
            relevant_patterns.sort(key=lambda x: x[1], reverse=True)
            return [pattern for pattern, _ in relevant_patterns[:limit]]
            
        except Exception as e:
            logger.error(f"Failed to get relevant patterns: {str(e)}")
            raise
    
    async def track_pattern_usage(
        self,
        pattern_id: str,
        project_id: str,
        success: bool
    ) -> None:
        """Track usage and success of a pattern
        
        Args:
            pattern_id: ID of the pattern
            project_id: Project where pattern was used
            success: Whether the pattern was successful
        """
        try:
            if pattern_id not in self.patterns:
                raise ValueError(f"Pattern not found: {pattern_id}")
            
            # Update usage count
            self.pattern_usage[pattern_id][project_id] += 1
            
            # Update pattern success rate
            pattern = self.patterns[pattern_id]
            pattern.usage_count += 1
            
            # Calculate new success rate
            current_success = pattern.success_rate * (pattern.usage_count - 1)
            new_success = current_success + (1 if success else 0)
            pattern.success_rate = new_success / pattern.usage_count
            
            pattern.updated_at = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Failed to track pattern usage: {str(e)}")
            raise
    
    async def _analyze_patterns(
        self,
        memories: List[MemoryEntry]
    ) -> List[Pattern]:
        """Analyze patterns in memories"""
        try:
            patterns = []
            
            # Group memories by type
            memories_by_type = defaultdict(list)
            for memory in memories:
                memories_by_type[memory.type].append(memory)
            
            # Analyze each type of memory
            for memory_type, type_memories in memories_by_type.items():
                # Find common patterns
                common_patterns = await self._find_common_patterns(type_memories)
                
                # Create pattern objects
                for pattern_data in common_patterns:
                    pattern = Pattern(
                        id=self._generate_pattern_id(),
                        name=pattern_data["name"],
                        description=pattern_data["description"],
                        examples=pattern_data["examples"],
                        metadata={
                            "memory_type": memory_type.value,
                            "confidence": pattern_data["confidence"],
                            "num_examples": len(pattern_data["examples"])
                        }
                    )
                    patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to analyze patterns: {str(e)}")
            raise
    
    async def _analyze_cross_project_patterns(
        self,
        memories: List[MemoryEntry]
    ) -> List[Pattern]:
        """Analyze patterns across projects"""
        try:
            patterns = []
            
            # Group memories by project
            memories_by_project = defaultdict(list)
            for memory in memories:
                if memory.project_id:
                    memories_by_project[memory.project_id].append(memory)
            
            # Find patterns that appear in multiple projects
            project_patterns = defaultdict(list)
            for project_id, project_memories in memories_by_project.items():
                project_patterns[project_id] = await self._analyze_patterns(project_memories)
            
            # Find common patterns across projects
            common_patterns = await self._find_cross_project_patterns(project_patterns)
            
            # Create pattern objects
            for pattern_data in common_patterns:
                pattern = Pattern(
                    id=self._generate_pattern_id(),
                    name=pattern_data["name"],
                    description=pattern_data["description"],
                    examples=pattern_data["examples"],
                    metadata={
                        "num_projects": pattern_data["num_projects"],
                        "confidence": pattern_data["confidence"],
                        "project_ids": pattern_data["project_ids"]
                    }
                )
                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to analyze cross-project patterns: {str(e)}")
            raise
    
    async def _extract_concepts(self, memories: List[MemoryEntry]) -> Set[str]:
        """Extract concepts from memories"""
        try:
            concepts = set()
            
            for memory in memories:
                # Extract concepts from content
                content_concepts = await self._extract_concepts_from_content(memory.content)
                concepts.update(content_concepts)
                
                # Extract concepts from metadata
                metadata_concepts = await self._extract_concepts_from_metadata(memory.metadata)
                concepts.update(metadata_concepts)
            
            return concepts
            
        except Exception as e:
            logger.error(f"Failed to extract concepts: {str(e)}")
            raise
    
    async def _extract_concepts_from_content(
        self,
        content: Dict[str, Any]
    ) -> Set[str]:
        """Extract concepts from content
        
        Args:
            content: Content dictionary to extract concepts from
            
        Returns:
            Set of extracted concepts
        """
        try:
            concepts = set()
            
            # Extract concepts from text fields
            text_fields = self._find_text_fields(content)
            for field, text in text_fields:
                # Extract key terms
                terms = self._extract_key_terms(text)
                concepts.update(terms)
                
                # Extract named entities
                entities = self._extract_named_entities(text)
                concepts.update(entities)
            
            # Extract concepts from structured fields
            structured_fields = self._find_structured_fields(content)
            for field, value in structured_fields:
                # Extract concepts from lists
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            concepts.add(item)
                        elif isinstance(item, dict):
                            concepts.update(self._extract_concepts_from_content(item))
                
                # Extract concepts from dictionaries
                elif isinstance(value, dict):
                    concepts.update(self._extract_concepts_from_content(value))
            
            return concepts
            
        except Exception as e:
            logger.error(f"Failed to extract concepts from content: {str(e)}")
            return set()
    
    async def _extract_concepts_from_metadata(
        self,
        metadata: Dict[str, Any]
    ) -> Set[str]:
        """Extract concepts from metadata
        
        Args:
            metadata: Metadata dictionary to extract concepts from
            
        Returns:
            Set of extracted concepts
        """
        try:
            concepts = set()
            
            # Extract concepts from key fields
            key_fields = {
                "type", "category", "tags", "labels", "keywords",
                "domain", "technology", "framework", "language"
            }
            
            for field in key_fields:
                if field in metadata:
                    value = metadata[field]
                    if isinstance(value, str):
                        concepts.add(value)
                    elif isinstance(value, list):
                        concepts.update(value)
            
            # Extract concepts from nested metadata
            for value in metadata.values():
                if isinstance(value, dict):
                    concepts.update(self._extract_concepts_from_metadata(value))
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            concepts.update(self._extract_concepts_from_metadata(item))
            
            return concepts
            
        except Exception as e:
            logger.error(f"Failed to extract concepts from metadata: {str(e)}")
            return set()
    
    def _find_text_fields(
        self,
        obj: Any,
        path: str = ""
    ) -> List[Tuple[str, str]]:
        """Find text fields in an object
        
        Args:
            obj: Object to search in
            path: Current path in the object
            
        Returns:
            List of (path, text) tuples
        """
        text_fields = []
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                if isinstance(value, str):
                    text_fields.append((new_path, value))
                else:
                    text_fields.extend(self._find_text_fields(value, new_path))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]"
                text_fields.extend(self._find_text_fields(item, new_path))
        
        return text_fields
    
    def _find_structured_fields(
        self,
        obj: Any,
        path: str = ""
    ) -> List[Tuple[str, Any]]:
        """Find structured fields in an object
        
        Args:
            obj: Object to search in
            path: Current path in the object
            
        Returns:
            List of (path, value) tuples
        """
        structured_fields = []
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                if isinstance(value, (list, dict)):
                    structured_fields.append((new_path, value))
                    structured_fields.extend(self._find_structured_fields(value, new_path))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]"
                if isinstance(item, (list, dict)):
                    structured_fields.append((new_path, item))
                    structured_fields.extend(self._find_structured_fields(item, new_path))
        
        return structured_fields
    
    def _extract_key_terms(self, text: str) -> Set[str]:
        """Extract key terms from text
        
        Args:
            text: Text to extract terms from
            
        Returns:
            Set of extracted terms
        """
        try:
            # TODO: Implement more sophisticated term extraction
            # For now, just split on whitespace and filter
            terms = set()
            
            # Split into words and filter
            words = text.lower().split()
            for word in words:
                # Filter out common words and short terms
                if len(word) > 2 and word not in self._get_stop_words():
                    terms.add(word)
            
            return terms
            
        except Exception as e:
            logger.error(f"Failed to extract key terms: {str(e)}")
            return set()
    
    def _extract_named_entities(self, text: str) -> Set[str]:
        """Extract named entities from text
        
        Args:
            text: Text to extract entities from
            
        Returns:
            Set of extracted entities
        """
        try:
            # TODO: Implement named entity recognition
            # For now, just look for capitalized phrases
            entities = set()
            
            # Split into sentences
            sentences = text.split('.')
            for sentence in sentences:
                # Look for capitalized phrases
                words = sentence.split()
                current_phrase = []
                
                for word in words:
                    if word and word[0].isupper():
                        current_phrase.append(word)
                    elif current_phrase:
                        if len(current_phrase) > 1:  # Only keep multi-word phrases
                            entities.add(' '.join(current_phrase))
                        current_phrase = []
                
                # Check last phrase
                if current_phrase and len(current_phrase) > 1:
                    entities.add(' '.join(current_phrase))
            
            return entities
            
        except Exception as e:
            logger.error(f"Failed to extract named entities: {str(e)}")
            return set()
    
    def _get_stop_words(self) -> Set[str]:
        """Get set of stop words to filter out
        
        Returns:
            Set of stop words
        """
        return {
            "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
            "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
            "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
            "or", "an", "will", "my", "one", "all", "would", "there", "their"
        }
    
    async def _determine_relationship(
        self,
        memory1: MemoryEntry,
        memory2: MemoryEntry
    ) -> Optional[str]:
        """Determine relationship between two memories"""
        try:
            # Calculate similarity
            similarity = await self._calculate_similarity(memory1, memory2)
            
            if similarity > 0.8:
                return "similar"
            elif similarity > 0.6:
                return "related"
            elif similarity > 0.4:
                return "weakly_related"
            else:
                return None
            
        except Exception as e:
            logger.error(f"Failed to determine relationship: {str(e)}")
            raise
    
    async def _calculate_relationship_confidence(
        self,
        memory1: MemoryEntry,
        memory2: MemoryEntry,
        relationship: str
    ) -> float:
        """Calculate confidence in relationship between memories"""
        try:
            # Calculate base confidence from similarity
            similarity = await self._calculate_similarity(memory1, memory2)
            
            # Adjust confidence based on relationship type
            if relationship == "similar":
                return similarity
            elif relationship == "related":
                return similarity * 0.8
            elif relationship == "weakly_related":
                return similarity * 0.6
            else:
                return 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate relationship confidence: {str(e)}")
            raise
    
    async def _calculate_pattern_relevance(
        self,
        pattern: Pattern,
        memories: List[MemoryEntry]
    ) -> float:
        """Calculate relevance of pattern to memories"""
        try:
            # Calculate average similarity to pattern examples
            similarities = []
            for example in pattern.examples:
                example_embedding = await self.memory_manager._generate_embedding(example)
                for memory in memories:
                    similarity = await self._calculate_similarity(
                        MemoryEntry(
                            id="example",
                            type=pattern.metadata.get("memory_type", MemoryType.SEMANTIC),
                            content=example,
                            metadata={}
                        ),
                        memory
                    )
                    similarities.append(similarity)
            
            if not similarities:
                return 0.0
            
            return sum(similarities) / len(similarities)
            
        except Exception as e:
            logger.error(f"Failed to calculate pattern relevance: {str(e)}")
            raise
    
    async def _calculate_similarity(
        self,
        memory1: MemoryEntry,
        memory2: MemoryEntry
    ) -> float:
        """Calculate similarity between two memories"""
        try:
            # Generate embeddings if not present
            if not memory1.embedding:
                memory1.embedding = await self.memory_manager._generate_embedding(memory1.content)
            if not memory2.embedding:
                memory2.embedding = await self.memory_manager._generate_embedding(memory2.content)
            
            # Calculate cosine similarity
            dot_product = sum(a * b for a, b in zip(memory1.embedding, memory2.embedding))
            norm1 = sum(a * a for a in memory1.embedding) ** 0.5
            norm2 = sum(a * a for a in memory2.embedding) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {str(e)}")
            raise
    
    def _generate_pattern_id(self) -> str:
        """Generate unique pattern ID"""
        return f"pattern_{uuid.uuid4().hex}"
    
    async def _find_common_patterns(
        self,
        memories: List[MemoryEntry]
    ) -> List[Dict[str, Any]]:
        """Find common patterns in memories
        
        Args:
            memories: List of memory entries to analyze
            
        Returns:
            List of identified patterns with their metadata
        """
        try:
            patterns = []
            
            # Group memories by content type
            content_types = defaultdict(list)
            for memory in memories:
                content_type = memory.content.get("type", "unknown")
                content_types[content_type].append(memory)
            
            # Analyze each content type group
            for content_type, type_memories in content_types.items():
                if len(type_memories) < 2:  # Need at least 2 examples for a pattern
                    continue
                
                # Find similar content structures
                content_structures = defaultdict(list)
                for memory in type_memories:
                    structure = self._extract_content_structure(memory.content)
                    content_structures[structure].append(memory)
                
                # Create patterns for common structures
                for structure, structure_memories in content_structures.items():
                    if len(structure_memories) >= 2:  # Need at least 2 examples
                        # Calculate pattern confidence
                        confidence = self._calculate_pattern_confidence(structure_memories)
                        
                        if confidence >= self.min_pattern_confidence:
                            # Extract common fields and values
                            common_fields = self._find_common_fields(structure_memories)
                            
                            # Create pattern examples
                            examples = []
                            for memory in structure_memories[:self.max_pattern_examples]:
                                examples.append({
                                    "content": memory.content,
                                    "metadata": memory.metadata,
                                    "timestamp": memory.created_at
                                })
                            
                            # Create pattern
                            pattern = {
                                "name": f"{content_type}_pattern_{len(patterns)}",
                                "description": f"Common pattern in {content_type} content with {len(structure_memories)} examples",
                                "examples": examples,
                                "confidence": confidence,
                                "metadata": {
                                    "content_type": content_type,
                                    "structure": structure,
                                    "common_fields": common_fields,
                                    "num_examples": len(structure_memories)
                                }
                            }
                            patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to find common patterns: {str(e)}")
            raise
    
    def _extract_content_structure(self, content: Dict[str, Any]) -> str:
        """Extract structure signature from content
        
        Args:
            content: Content dictionary
            
        Returns:
            String representation of content structure
        """
        def _get_type(value: Any) -> str:
            if isinstance(value, dict):
                return "dict"
            elif isinstance(value, list):
                return "list"
            elif isinstance(value, str):
                return "str"
            elif isinstance(value, (int, float)):
                return "num"
            else:
                return "other"
        
        def _structure_to_string(obj: Any, depth: int = 0) -> str:
            if isinstance(obj, dict):
                parts = []
                for key, value in sorted(obj.items()):
                    parts.append(f"{key}:{_structure_to_string(value, depth + 1)}")
                return f"{{{','.join(parts)}}}"
            elif isinstance(obj, list):
                if not obj:
                    return "[]"
                return f"[{_structure_to_string(obj[0], depth + 1)}]"
            else:
                return _get_type(obj)
        
        return _structure_to_string(content)
    
    def _calculate_pattern_confidence(
        self,
        memories: List[MemoryEntry]
    ) -> float:
        """Calculate confidence in pattern based on memory examples
        
        Args:
            memories: List of memory entries
            
        Returns:
            Confidence score between 0 and 1
        """
        try:
            if len(memories) < 2:
                return 0.0
            
            # Calculate average similarity between all pairs
            similarities = []
            for i in range(len(memories)):
                for j in range(i + 1, len(memories)):
                    similarity = self._calculate_content_similarity(
                        memories[i].content,
                        memories[j].content
                    )
                    similarities.append(similarity)
            
            if not similarities:
                return 0.0
            
            # Calculate confidence based on average similarity and number of examples
            avg_similarity = sum(similarities) / len(similarities)
            example_factor = min(len(memories) / 10, 1.0)  # Cap at 10 examples
            
            return avg_similarity * example_factor
            
        except Exception as e:
            logger.error(f"Failed to calculate pattern confidence: {str(e)}")
            return 0.0
    
    def _calculate_content_similarity(
        self,
        content1: Dict[str, Any],
        content2: Dict[str, Any]
    ) -> float:
        """Calculate similarity between two content dictionaries
        
        Args:
            content1: First content dictionary
            content2: Second content dictionary
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Extract common keys
            keys1 = set(content1.keys())
            keys2 = set(content2.keys())
            common_keys = keys1.intersection(keys2)
            
            if not common_keys:
                return 0.0
            
            # Calculate similarity for each common key
            similarities = []
            for key in common_keys:
                value1 = content1[key]
                value2 = content2[key]
                
                if isinstance(value1, dict) and isinstance(value2, dict):
                    similarities.append(
                        self._calculate_content_similarity(value1, value2)
                    )
                elif isinstance(value1, list) and isinstance(value2, list):
                    if not value1 or not value2:
                        continue
                    # Compare first elements as representatives
                    if isinstance(value1[0], dict) and isinstance(value2[0], dict):
                        similarities.append(
                            self._calculate_content_similarity(value1[0], value2[0])
                        )
                    else:
                        similarities.append(1.0 if value1[0] == value2[0] else 0.0)
                else:
                    similarities.append(1.0 if value1 == value2 else 0.0)
            
            if not similarities:
                return 0.0
            
            return sum(similarities) / len(similarities)
            
        except Exception as e:
            logger.error(f"Failed to calculate content similarity: {str(e)}")
            return 0.0
    
    def _find_common_fields(
        self,
        memories: List[MemoryEntry]
    ) -> Dict[str, Any]:
        """Find common fields and their values across memories
        
        Args:
            memories: List of memory entries
            
        Returns:
            Dictionary of common fields and their values
        """
        try:
            common_fields = {}
            
            # Get all unique keys across all memories
            all_keys = set()
            for memory in memories:
                all_keys.update(self._get_nested_keys(memory.content))
            
            # Analyze each key
            for key in all_keys:
                values = self._get_nested_values(memories, key)
                if values:
                    # Calculate value statistics
                    value_counts = defaultdict(int)
                    for value in values:
                        value_counts[str(value)] += 1
                    
                    # Find most common value
                    if value_counts:
                        most_common = max(value_counts.items(), key=lambda x: x[1])
                        common_fields[key] = {
                            "value": most_common[0],
                            "frequency": most_common[1] / len(memories),
                            "total_occurrences": most_common[1]
                        }
            
            return common_fields
            
        except Exception as e:
            logger.error(f"Failed to find common fields: {str(e)}")
            return {}
    
    def _get_nested_keys(self, obj: Any) -> Set[str]:
        """Get all nested keys from a dictionary or list
        
        Args:
            obj: Object to extract keys from
            
        Returns:
            Set of key paths
        """
        keys = set()
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                keys.add(key)
                keys.update(self._get_nested_keys(value))
        elif isinstance(obj, list):
            for item in obj:
                keys.update(self._get_nested_keys(item))
        
        return keys
    
    def _get_nested_values(
        self,
        memories: List[MemoryEntry],
        key: str
    ) -> List[Any]:
        """Get all values for a nested key across memories
        
        Args:
            memories: List of memory entries
            key: Key to find values for
            
        Returns:
            List of found values
        """
        values = []
        
        for memory in memories:
            value = self._get_nested_value(memory.content, key)
            if value is not None:
                values.append(value)
        
        return values
    
    def _get_nested_value(self, obj: Any, key: str) -> Optional[Any]:
        """Get value for a nested key from an object
        
        Args:
            obj: Object to search in
            key: Key to find
            
        Returns:
            Found value or None
        """
        if isinstance(obj, dict):
            if key in obj:
                return obj[key]
            for value in obj.values():
                result = self._get_nested_value(value, key)
                if result is not None:
                    return result
        elif isinstance(obj, list):
            for item in obj:
                result = self._get_nested_value(item, key)
                if result is not None:
                    return result
        
        return None
    
    async def _find_cross_project_patterns(
        self,
        project_patterns: Dict[str, List[Pattern]]
    ) -> List[Dict[str, Any]]:
        """Find patterns common across projects
        
        Args:
            project_patterns: Dictionary mapping project IDs to their patterns
            
        Returns:
            List of cross-project patterns with metadata
        """
        try:
            cross_project_patterns = []
            
            # Group patterns by content type
            patterns_by_type = defaultdict(list)
            for project_id, patterns in project_patterns.items():
                for pattern in patterns:
                    content_type = pattern.metadata.get("content_type", "unknown")
                    patterns_by_type[content_type].append((project_id, pattern))
            
            # Analyze each content type group
            for content_type, type_patterns in patterns_by_type.items():
                if len(type_patterns) < 2:  # Need at least 2 projects
                    continue
                
                # Group patterns by structure
                structure_groups = defaultdict(list)
                for project_id, pattern in type_patterns:
                    structure = pattern.metadata.get("structure", "")
                    structure_groups[structure].append((project_id, pattern))
                
                # Find patterns that appear in multiple projects
                for structure, structure_patterns in structure_groups.items():
                    if len(structure_patterns) < 2:  # Need at least 2 projects
                        continue
                    
                    # Get unique project IDs
                    project_ids = {pid for pid, _ in structure_patterns}
                    
                    # Calculate cross-project confidence
                    confidence = self._calculate_cross_project_confidence(structure_patterns)
                    
                    if confidence >= self.min_pattern_confidence:
                        # Merge examples from different projects
                        examples = []
                        for _, pattern in structure_patterns:
                            examples.extend(pattern.examples[:self.max_pattern_examples // len(structure_patterns)])
                        
                        # Find common fields across projects
                        common_fields = self._find_cross_project_common_fields(structure_patterns)
                        
                        # Create cross-project pattern
                        pattern = {
                            "name": f"cross_project_{content_type}_pattern_{len(cross_project_patterns)}",
                            "description": f"Pattern found in {len(project_ids)} projects for {content_type} content",
                            "examples": examples[:self.max_pattern_examples],
                            "confidence": confidence,
                            "metadata": {
                                "content_type": content_type,
                                "structure": structure,
                                "project_ids": list(project_ids),
                                "num_projects": len(project_ids),
                                "common_fields": common_fields,
                                "num_examples": len(examples)
                            }
                        }
                        cross_project_patterns.append(pattern)
            
            return cross_project_patterns
            
        except Exception as e:
            logger.error(f"Failed to find cross-project patterns: {str(e)}")
            raise
    
    def _calculate_cross_project_confidence(
        self,
        structure_patterns: List[Tuple[str, Pattern]]
    ) -> float:
        """Calculate confidence in cross-project pattern
        
        Args:
            structure_patterns: List of (project_id, pattern) tuples
            
        Returns:
            Confidence score between 0 and 1
        """
        try:
            if len(structure_patterns) < 2:
                return 0.0
            
            # Calculate average pattern confidence
            pattern_confidences = [pattern.confidence for _, pattern in structure_patterns]
            avg_confidence = sum(pattern_confidences) / len(pattern_confidences)
            
            # Calculate project coverage factor
            num_projects = len({pid for pid, _ in structure_patterns})
            project_factor = min(num_projects / 5, 1.0)  # Cap at 5 projects
            
            # Calculate example diversity factor
            examples = []
            for _, pattern in structure_patterns:
                examples.extend(pattern.examples)
            diversity_factor = self._calculate_example_diversity(examples)
            
            # Combine factors
            return avg_confidence * project_factor * diversity_factor
            
        except Exception as e:
            logger.error(f"Failed to calculate cross-project confidence: {str(e)}")
            return 0.0
    
    def _calculate_example_diversity(self, examples: List[Dict[str, Any]]) -> float:
        """Calculate diversity of examples
        
        Args:
            examples: List of example dictionaries
            
        Returns:
            Diversity score between 0 and 1
        """
        try:
            if not examples:
                return 0.0
            
            # Calculate average similarity between examples
            similarities = []
            for i in range(len(examples)):
                for j in range(i + 1, len(examples)):
                    similarity = self._calculate_content_similarity(
                        examples[i]["content"],
                        examples[j]["content"]
                    )
                    similarities.append(similarity)
            
            if not similarities:
                return 1.0
            
            # Convert average similarity to diversity (1 - similarity)
            avg_similarity = sum(similarities) / len(similarities)
            return 1.0 - avg_similarity
            
        except Exception as e:
            logger.error(f"Failed to calculate example diversity: {str(e)}")
            return 0.0
    
    def _find_cross_project_common_fields(
        self,
        structure_patterns: List[Tuple[str, Pattern]]
    ) -> Dict[str, Any]:
        """Find common fields across project patterns
        
        Args:
            structure_patterns: List of (project_id, pattern) tuples
            
        Returns:
            Dictionary of common fields and their statistics
        """
        try:
            common_fields = {}
            
            # Get all unique fields across all patterns
            all_fields = set()
            for _, pattern in structure_patterns:
                all_fields.update(pattern.metadata.get("common_fields", {}).keys())
            
            # Analyze each field
            for field in all_fields:
                field_stats = defaultdict(int)
                field_values = defaultdict(int)
                
                for _, pattern in structure_patterns:
                    pattern_fields = pattern.metadata.get("common_fields", {})
                    if field in pattern_fields:
                        field_stats["occurrences"] += 1
                        value = pattern_fields[field]["value"]
                        field_values[value] += pattern_fields[field]["total_occurrences"]
                
                if field_stats["occurrences"] > 0:
                    # Calculate field statistics
                    occurrence_rate = field_stats["occurrences"] / len(structure_patterns)
                    
                    # Find most common value
                    if field_values:
                        most_common = max(field_values.items(), key=lambda x: x[1])
                        common_fields[field] = {
                            "value": most_common[0],
                            "occurrence_rate": occurrence_rate,
                            "total_occurrences": most_common[1],
                            "num_unique_values": len(field_values)
                        }
            
            return common_fields
            
        except Exception as e:
            logger.error(f"Failed to find cross-project common fields: {str(e)}")
            return {} 