"""
Conversation Repository

This module implements the repository for accessing and managing conversation memory data,
enabling the platform to maintain context across user interactions.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorCollection
from ..models.conversation_memory import Conversation, Message, ConversationSummary, VectorEmbedding
from ..mongodb_connection import mongodb_manager
from ..vector_embeddings import vector_embeddings_service

logger = logging.getLogger(__name__)

class ConversationRepository:
    """Repository for accessing and managing conversation memory data"""
    
    def __init__(self):
        """Initialize the conversation repository"""
        self.collection_name = "conversation_history"
        self.embedding_collection_name = "vector_embeddings"
        
    async def _get_collection(self) -> AsyncIOMotorCollection:
        """Get the MongoDB collection for conversation history"""
        return await mongodb_manager.get_collection(self.collection_name)
        
    async def _get_embedding_collection(self) -> AsyncIOMotorCollection:
        """Get the MongoDB collection for vector embeddings"""
        return await mongodb_manager.get_collection(self.embedding_collection_name)
        
    async def create_conversation(self, conversation: Conversation) -> Conversation:
        """Create a new conversation"""
        try:
            collection = await self._get_collection()
            
            # Convert to dict and insert
            conversation_dict = conversation.dict()
            result = await collection.insert_one(conversation_dict)
            
            # Update ID if necessary
            if result.inserted_id and str(result.inserted_id) != str(conversation.id):
                conversation.id = result.inserted_id
                
            return conversation
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise
            
    async def get_conversation(self, conversation_id: UUID) -> Optional[Conversation]:
        """Get a conversation by ID"""
        try:
            collection = await self._get_collection()
            
            # Find conversation
            conversation_dict = await collection.find_one({"id": str(conversation_id)})
            
            if not conversation_dict:
                return None
                
            # Convert to Conversation object
            return Conversation(**conversation_dict)
        except Exception as e:
            logger.error(f"Error getting conversation: {str(e)}")
            raise
            
    async def update_conversation(self, conversation: Conversation) -> Conversation:
        """Update an existing conversation"""
        try:
            collection = await self._get_collection()
            
            # Update timestamp
            conversation.updated_at = datetime.utcnow()
            
            # Convert to dict and update
            conversation_dict = conversation.dict()
            await collection.replace_one({"id": str(conversation.id)}, conversation_dict)
            
            return conversation
        except Exception as e:
            logger.error(f"Error updating conversation: {str(e)}")
            raise
            
    async def delete_conversation(self, conversation_id: UUID) -> bool:
        """Delete a conversation by ID"""
        try:
            collection = await self._get_collection()
            embedding_collection = await self._get_embedding_collection()
            
            # Delete conversation
            result = await collection.delete_one({"id": str(conversation_id)})
            
            # Delete associated embeddings
            await embedding_collection.delete_many({
                "content_type": "conversation",
                "content_id": str(conversation_id)
            })
            
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            raise
            
    async def add_message(self, conversation_id: UUID, message: Message) -> Conversation:
        """Add a message to a conversation"""
        try:
            # Get conversation
            conversation = await self.get_conversation(conversation_id)
            
            if not conversation:
                raise ValueError(f"Conversation with ID {conversation_id} not found")
                
            # Add message
            conversation.messages.append(message)
            conversation.updated_at = datetime.utcnow()
            
            # Update conversation
            await self.update_conversation(conversation)
            
            # Create embedding for message
            embedding = await vector_embeddings_service.create_embedding(
                project_id=conversation.project_id,
                content_id=message.id,
                content_type="message",
                text=message.content,
                metadata={
                    "conversation_id": str(conversation.id),
                    "sender": message.sender,
                    "timestamp": message.timestamp.isoformat()
                }
            )
            
            # Save embedding
            embedding_collection = await self._get_embedding_collection()
            await embedding_collection.insert_one(embedding.dict())
            
            return conversation
        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            raise
            
    async def get_project_conversations(
        self,
        project_id: UUID,
        limit: int = 10,
        offset: int = 0
    ) -> List[ConversationSummary]:
        """Get conversations for a project"""
        try:
            collection = await self._get_collection()
            
            # Find conversations
            cursor = collection.find({"project_id": str(project_id)})
            
            # Sort by updated_at (descending)
            cursor = cursor.sort("updated_at", -1)
            
            # Apply limit and offset
            cursor = cursor.skip(offset).limit(limit)
            
            # Convert to ConversationSummary objects
            conversations = []
            async for conv in cursor:
                summary = ConversationSummary(
                    id=conv["id"],
                    project_id=conv["project_id"],
                    user_id=conv["user_id"],
                    title=conv["title"],
                    created_at=conv["created_at"],
                    updated_at=conv["updated_at"],
                    message_count=len(conv["messages"]),
                    last_message_timestamp=conv["messages"][-1]["timestamp"] if conv["messages"] else conv["updated_at"],
                    tags=conv["tags"]
                )
                conversations.append(summary)
                
            return conversations
        except Exception as e:
            logger.error(f"Error getting project conversations: {str(e)}")
            raise
            
    async def search_conversations(
        self,
        project_id: UUID,
        query: str,
        limit: int = 5
    ) -> List[dict]:
        """Search conversations using semantic search"""
        try:
            embedding_collection = await self._get_embedding_collection()
            
            # Get all embeddings for the project
            cursor = embedding_collection.find({
                "project_id": str(project_id),
                "content_type": {"$in": ["message", "conversation"]}
            })
            
            embeddings = []
            async for emb in cursor:
                embeddings.append(VectorEmbedding(**emb))
                
            # Search for similar content
            results = await vector_embeddings_service.search_similar(
                query_text=query,
                embeddings=embeddings,
                top_k=limit
            )
            
            # Get conversation details for each result
            conversation_results = []
            for result in results:
                if result.content_type == "conversation":
                    # Get conversation
                    conversation = await self.get_conversation(UUID(result.content_id))
                    if conversation:
                        conversation_results.append({
                            "conversation_id": str(conversation.id),
                            "title": conversation.title,
                            "similarity_score": result.similarity_score,
                            "message_count": len(conversation.messages),
                            "updated_at": conversation.updated_at.isoformat(),
                            "text": result.text
                        })
                elif result.content_type == "message":
                    # Get conversation ID from metadata
                    conversation_id = result.metadata.get("conversation_id")
                    if conversation_id:
                        conversation = await self.get_conversation(UUID(conversation_id))
                        if conversation:
                            conversation_results.append({
                                "conversation_id": conversation_id,
                                "title": conversation.title,
                                "similarity_score": result.similarity_score,
                                "message": result.text,
                                "sender": result.metadata.get("sender"),
                                "timestamp": result.metadata.get("timestamp"),
                                "message_count": len(conversation.messages)
                            })
                            
            return conversation_results
        except Exception as e:
            logger.error(f"Error searching conversations: {str(e)}")
            raise

# Create a global instance of the conversation repository
conversation_repository = ConversationRepository()
