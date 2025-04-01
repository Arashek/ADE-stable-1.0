"""
Memory Service

This module implements the main memory service for the ADE platform, providing
a unified interface for accessing and managing memory data across the platform.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from uuid import UUID
from datetime import datetime

from .mongodb_connection import mongodb_manager
from .vector_embeddings import vector_embeddings_service
from .repositories.conversation_repository import conversation_repository
from .repositories.knowledge_graph_repository import knowledge_graph_repository
from .repositories.decision_repository import decision_repository
from .models.conversation_memory import Conversation, Message, ConversationSummary
from .models.knowledge_graph import Entity, Relationship, KnowledgeGraphQuery
from .models.decision_memory import Decision, TechnicalDebt, DecisionQuery

logger = logging.getLogger(__name__)

class MemoryService:
    """Memory service for the ADE platform"""
    
    def __init__(self):
        """Initialize the memory service"""
        self.initialized = False
        
    async def initialize(self):
        """Initialize the memory service"""
        try:
            if self.initialized:
                return
                
            logger.info("Initializing memory service...")
            
            # Connect to MongoDB
            await mongodb_manager.connect()
            
            # Create indexes
            await mongodb_manager.create_indexes()
            
            self.initialized = True
            logger.info("Memory service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing memory service: {str(e)}")
            raise
            
    async def shutdown(self):
        """Shutdown the memory service"""
        try:
            if not self.initialized:
                return
                
            logger.info("Shutting down memory service...")
            
            # Disconnect from MongoDB
            await mongodb_manager.disconnect()
            
            self.initialized = False
            logger.info("Memory service shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down memory service: {str(e)}")
            raise
            
    # Conversation Memory Methods
    
    async def create_conversation(self, project_id: UUID, user_id: UUID, title: str, tags: Optional[List[str]] = None) -> Conversation:
        """Create a new conversation"""
        try:
            conversation = Conversation(
                project_id=project_id,
                user_id=user_id,
                title=title,
                tags=tags or []
            )
            
            return await conversation_repository.create_conversation(conversation)
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise
            
    async def add_message(self, conversation_id: UUID, sender: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Conversation:
        """Add a message to a conversation"""
        try:
            message = Message(
                sender=sender,
                content=content,
                metadata=metadata or {}
            )
            
            return await conversation_repository.add_message(conversation_id, message)
        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            raise
            
    async def get_conversation(self, conversation_id: UUID) -> Optional[Conversation]:
        """Get a conversation by ID"""
        try:
            return await conversation_repository.get_conversation(conversation_id)
        except Exception as e:
            logger.error(f"Error getting conversation: {str(e)}")
            raise
            
    async def get_project_conversations(self, project_id: UUID, limit: int = 10, offset: int = 0) -> List[ConversationSummary]:
        """Get conversations for a project"""
        try:
            return await conversation_repository.get_project_conversations(project_id, limit, offset)
        except Exception as e:
            logger.error(f"Error getting project conversations: {str(e)}")
            raise
            
    async def search_conversations(self, project_id: UUID, query: str, limit: int = 5) -> List[dict]:
        """Search conversations using semantic search"""
        try:
            return await conversation_repository.search_conversations(project_id, query, limit)
        except Exception as e:
            logger.error(f"Error searching conversations: {str(e)}")
            raise
            
    # Knowledge Graph Methods
    
    async def create_entity(self, entity: Entity) -> Entity:
        """Create a new entity"""
        try:
            return await knowledge_graph_repository.create_entity(entity)
        except Exception as e:
            logger.error(f"Error creating entity: {str(e)}")
            raise
            
    async def create_relationship(self, relationship: Relationship) -> Relationship:
        """Create a new relationship"""
        try:
            return await knowledge_graph_repository.create_relationship(relationship)
        except Exception as e:
            logger.error(f"Error creating relationship: {str(e)}")
            raise
            
    async def query_knowledge_graph(self, query: KnowledgeGraphQuery) -> Dict[str, Any]:
        """Query the knowledge graph based on the specified criteria"""
        try:
            return await knowledge_graph_repository.query_knowledge_graph(query)
        except Exception as e:
            logger.error(f"Error querying knowledge graph: {str(e)}")
            raise
            
    # Decision Memory Methods
    
    async def create_decision(self, decision: Decision) -> Decision:
        """Create a new decision"""
        try:
            return await decision_repository.create_decision(decision)
        except Exception as e:
            logger.error(f"Error creating decision: {str(e)}")
            raise
            
    async def create_technical_debt(self, debt: TechnicalDebt) -> TechnicalDebt:
        """Create a new technical debt item"""
        try:
            return await decision_repository.create_technical_debt(debt)
        except Exception as e:
            logger.error(f"Error creating technical debt: {str(e)}")
            raise
            
    async def query_decisions(self, query: DecisionQuery) -> List[Decision]:
        """Query decisions based on the specified criteria"""
        try:
            return await decision_repository.query_decisions(query)
        except Exception as e:
            logger.error(f"Error querying decisions: {str(e)}")
            raise
            
    async def get_project_technical_debt(self, project_id: UUID, include_resolved: bool = False) -> List[TechnicalDebt]:
        """Get technical debt items for a project"""
        try:
            return await decision_repository.get_project_technical_debt(project_id, include_resolved)
        except Exception as e:
            logger.error(f"Error getting project technical debt: {str(e)}")
            raise
            
    async def get_technical_debt_summary(self, project_id: UUID) -> Dict[str, Any]:
        """Get a summary of technical debt for a project"""
        try:
            return await decision_repository.get_technical_debt_summary(project_id)
        except Exception as e:
            logger.error(f"Error getting technical debt summary: {str(e)}")
            raise
            
    # Context Retrieval Methods
    
    async def retrieve_context(self, project_id: UUID, query: str, limit: int = 5) -> Dict[str, Any]:
        """Retrieve relevant context for a query"""
        try:
            # Search conversations
            conversation_results = await self.search_conversations(project_id, query, limit)
            
            # Query knowledge graph
            knowledge_query = KnowledgeGraphQuery(
                project_id=project_id,
                max_depth=1,
                include_properties=True
            )
            knowledge_results = await self.query_knowledge_graph(knowledge_query)
            
            # Query decisions
            decision_query = DecisionQuery(
                project_id=project_id
            )
            decision_results = await self.query_decisions(decision_query)
            
            # Combine results
            return {
                "conversations": conversation_results,
                "knowledge_graph": {
                    "entities": knowledge_results.get("entities", [])[:limit],
                    "relationships": knowledge_results.get("relationships", [])[:limit]
                },
                "decisions": decision_results[:limit]
            }
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            raise

# Create a global instance of the memory service
memory_service = MemoryService()
