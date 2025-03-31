from typing import Dict, Any, List, Optional, Tuple
import logging
from dataclasses import dataclass
from datetime import datetime
import json

from .memory_manager import MemoryManager, MemoryType, MemoryEntry

logger = logging.getLogger(__name__)

@dataclass
class RAGContext:
    """Represents retrieved context for RAG"""
    memories: List[MemoryEntry]
    relevance_scores: List[float]
    metadata: Dict[str, Any]
    timestamp: str = datetime.now().isoformat()

class RAGSystem:
    """Handles retrieval-augmented generation for context-aware AI interactions"""
    
    def __init__(
        self,
        memory_manager: MemoryManager,
        max_context_size: int = 5,
        min_relevance_threshold: float = 0.7
    ):
        self.memory_manager = memory_manager
        self.max_context_size = max_context_size
        self.min_relevance_threshold = min_relevance_threshold
    
    async def process_input(
        self,
        input_text: str,
        project_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        memory_types: Optional[List[MemoryType]] = None
    ) -> Tuple[str, RAGContext]:
        """Process input and retrieve relevant context
        
        Args:
            input_text: Input text to process
            project_id: Optional project ID for context filtering
            agent_id: Optional agent ID for context filtering
            session_id: Optional session ID for context filtering
            memory_types: Optional list of memory types to consider
            
        Returns:
            Tuple of (augmented prompt, retrieved context)
        """
        try:
            # Retrieve relevant context
            context = await self._retrieve_context(
                input_text,
                project_id=project_id,
                agent_id=agent_id,
                session_id=session_id,
                memory_types=memory_types
            )
            
            # Augment prompt with context
            augmented_prompt = await self._augment_prompt(input_text, context)
            
            return augmented_prompt, context
            
        except Exception as e:
            logger.error(f"Failed to process input: {str(e)}")
            raise
    
    async def _retrieve_context(
        self,
        input_text: str,
        project_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        memory_types: Optional[List[MemoryType]] = None
    ) -> RAGContext:
        """Retrieve relevant context for input
        
        Args:
            input_text: Input text to find context for
            project_id: Optional project ID filter
            agent_id: Optional agent ID filter
            session_id: Optional session ID filter
            memory_types: Optional list of memory types to consider
            
        Returns:
            Retrieved context
        """
        try:
            # Retrieve memories
            memories = await self.memory_manager.retrieve_memories(
                query=input_text,
                project_id=project_id,
                limit=self.max_context_size
            )
            
            # Filter by memory types if specified
            if memory_types:
                memories = [
                    memory for memory in memories
                    if memory.type in memory_types
                ]
            
            # Filter by relevance threshold
            memories = [
                memory for memory in memories
                if memory.relevance_score >= self.min_relevance_threshold
            ]
            
            # Extract relevance scores
            relevance_scores = [memory.relevance_score for memory in memories]
            
            # Create context metadata
            metadata = {
                "input_text": input_text,
                "project_id": project_id,
                "agent_id": agent_id,
                "session_id": session_id,
                "memory_types": [t.value for t in memory_types] if memory_types else None,
                "num_memories": len(memories),
                "avg_relevance": sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
            }
            
            return RAGContext(
                memories=memories,
                relevance_scores=relevance_scores,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to retrieve context: {str(e)}")
            raise
    
    async def _augment_prompt(
        self,
        input_text: str,
        context: RAGContext
    ) -> str:
        """Augment prompt with retrieved context
        
        Args:
            input_text: Original input text
            context: Retrieved context
            
        Returns:
            Augmented prompt
        """
        try:
            # Format context from memories
            context_text = self._format_context(context.memories)
            
            # Create augmented prompt
            augmented_prompt = f"""Context from previous interactions:
{context_text}

Current input:
{input_text}

Please consider the above context when responding to the current input."""
            
            return augmented_prompt
            
        except Exception as e:
            logger.error(f"Failed to augment prompt: {str(e)}")
            raise
    
    def _format_context(self, memories: List[MemoryEntry]) -> str:
        """Format memories into context text
        
        Args:
            memories: List of memory entries
            
        Returns:
            Formatted context text
        """
        context_parts = []
        
        for memory in memories:
            # Format memory content based on type
            if memory.type == MemoryType.EPISODIC:
                context_parts.append(
                    f"Previous interaction: {memory.content.get('summary', '')}"
                )
            elif memory.type == MemoryType.SEMANTIC:
                context_parts.append(
                    f"Related knowledge: {memory.content.get('knowledge', '')}"
                )
            else:
                context_parts.append(
                    f"Context: {memory.content.get('text', '')}"
                )
            
            # Add metadata if available
            if memory.metadata:
                context_parts.append(
                    f"Metadata: {json.dumps(memory.metadata, indent=2)}"
                )
        
        return "\n\n".join(context_parts)
    
    async def store_interaction(
        self,
        input_text: str,
        response: str,
        context: RAGContext,
        project_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> None:
        """Store interaction in memory system
        
        Args:
            input_text: Original input text
            response: Generated response
            context: Retrieved context
            project_id: Optional project ID
            agent_id: Optional agent ID
            session_id: Optional session ID
        """
        try:
            # Store episodic memory of the interaction
            await self.memory_manager.store_memory(
                content={
                    "input": input_text,
                    "response": response,
                    "context_metadata": context.metadata,
                    "relevance_scores": context.relevance_scores
                },
                memory_type=MemoryType.EPISODIC,
                project_id=project_id,
                agent_id=agent_id,
                session_id=session_id,
                tags=["interaction", "rag"]
            )
            
            # Store semantic memory of any new knowledge
            if response:
                await self.memory_manager.store_memory(
                    content={
                        "knowledge": response,
                        "source_input": input_text,
                        "context_metadata": context.metadata
                    },
                    memory_type=MemoryType.SEMANTIC,
                    project_id=project_id,
                    agent_id=agent_id,
                    session_id=session_id,
                    tags=["knowledge", "rag"]
                )
            
        except Exception as e:
            logger.error(f"Failed to store interaction: {str(e)}")
            raise 