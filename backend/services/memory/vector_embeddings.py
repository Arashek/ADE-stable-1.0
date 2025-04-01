"""
Vector Embeddings Service

This module provides functions for generating and managing vector embeddings
using OpenAI's embeddings API, enabling semantic search and retrieval of
conversation history and project artifacts.
"""

import logging
import httpx
import json
from typing import List, Dict, Any, Optional, Union
from uuid import UUID
import numpy as np
from config.settings import settings
from .models.conversation_memory import VectorEmbedding, SemanticSearchResult

logger = logging.getLogger(__name__)

class VectorEmbeddingsService:
    """Service for generating and managing vector embeddings"""
    
    def __init__(self):
        """Initialize the vector embeddings service"""
        self.api_key = settings.OPENAI_API_KEY
        self.embedding_model = "text-embedding-ada-002"  # Default model
        self.embedding_dimension = 1536  # Dimension for text-embedding-ada-002
        self.embedding_endpoint = "https://api.openai.com/v1/embeddings"
        
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate a vector embedding for the given text using OpenAI's API"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "input": text,
                "model": self.embedding_model
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.embedding_endpoint,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Error generating embedding: {response.text}")
                    raise Exception(f"Error generating embedding: {response.status_code}")
                
                result = response.json()
                embedding = result["data"][0]["embedding"]
                
                return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
            
    async def create_embedding(
        self,
        project_id: UUID,
        content_id: UUID,
        content_type: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> VectorEmbedding:
        """Create a vector embedding for the given content"""
        try:
            # Generate embedding
            embedding = await self.generate_embedding(text)
            
            # Create embedding object
            vector_embedding = VectorEmbedding(
                project_id=project_id,
                content_id=content_id,
                content_type=content_type,
                embedding=embedding,
                text=text,
                metadata=metadata or {}
            )
            
            return vector_embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            raise
            
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            similarity = dot_product / (norm1 * norm2)
            
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            raise
            
    async def search_similar(
        self,
        query_text: str,
        embeddings: List[VectorEmbedding],
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[SemanticSearchResult]:
        """Search for similar content based on semantic similarity"""
        try:
            # Generate embedding for query
            query_embedding = await self.generate_embedding(query_text)
            
            # Calculate similarity scores
            results = []
            for embedding_obj in embeddings:
                similarity = self.calculate_similarity(query_embedding, embedding_obj.embedding)
                
                if similarity >= similarity_threshold:
                    result = SemanticSearchResult(
                        content_id=embedding_obj.content_id,
                        content_type=embedding_obj.content_type,
                        text=embedding_obj.text,
                        similarity_score=similarity,
                        metadata=embedding_obj.metadata
                    )
                    results.append(result)
            
            # Sort by similarity score (descending)
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            
            # Return top k results
            return results[:top_k]
        except Exception as e:
            logger.error(f"Error searching similar content: {str(e)}")
            raise

# Create a global instance of the vector embeddings service
vector_embeddings_service = VectorEmbeddingsService()
