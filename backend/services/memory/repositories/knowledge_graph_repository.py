"""
Knowledge Graph Repository

This module implements the repository for accessing and managing knowledge graph data,
enabling the platform to maintain a structured representation of project entities
and their relationships.
"""

import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorCollection
from memory.repositories.models.knowledge_graph import (
    Entity, Relationship, EntityType, RelationshipType,
    KnowledgeGraphQuery, ProjectOntology
)
from memory.repositories.mongodb_connection import mongodb_manager

logger = logging.getLogger(__name__)

class KnowledgeGraphRepository:
    """Repository for accessing and managing knowledge graph data"""
    
    def __init__(self):
        """Initialize the knowledge graph repository"""
        self.entity_collection_name = "knowledge_graph_entities"
        self.relationship_collection_name = "knowledge_graph_relationships"
        self.ontology_collection_name = "project_ontologies"
        
    async def _get_entity_collection(self) -> AsyncIOMotorCollection:
        """Get the MongoDB collection for entities"""
        return await mongodb_manager.get_collection(self.entity_collection_name)
        
    async def _get_relationship_collection(self) -> AsyncIOMotorCollection:
        """Get the MongoDB collection for relationships"""
        return await mongodb_manager.get_collection(self.relationship_collection_name)
        
    async def _get_ontology_collection(self) -> AsyncIOMotorCollection:
        """Get the MongoDB collection for project ontologies"""
        return await mongodb_manager.get_collection(self.ontology_collection_name)
        
    async def create_entity(self, entity: Entity) -> Entity:
        """Create a new entity"""
        try:
            collection = await self._get_entity_collection()
            
            # Convert to dict and insert
            entity_dict = entity.dict()
            result = await collection.insert_one(entity_dict)
            
            # Update ID if necessary
            if result.inserted_id and str(result.inserted_id) != str(entity.id):
                entity.id = result.inserted_id
                
            return entity
        except Exception as e:
            logger.error(f"Error creating entity: {str(e)}")
            raise
            
    async def get_entity(self, entity_id: UUID) -> Optional[Entity]:
        """Get an entity by ID"""
        try:
            collection = await self._get_entity_collection()
            
            # Find entity
            entity_dict = await collection.find_one({"id": str(entity_id)})
            
            if not entity_dict:
                return None
                
            # Convert to Entity object
            return Entity(**entity_dict)
        except Exception as e:
            logger.error(f"Error getting entity: {str(e)}")
            raise
            
    async def update_entity(self, entity: Entity) -> Entity:
        """Update an existing entity"""
        try:
            collection = await self._get_entity_collection()
            
            # Update timestamp
            entity.updated_at = datetime.utcnow()
            
            # Convert to dict and update
            entity_dict = entity.dict()
            await collection.replace_one({"id": str(entity.id)}, entity_dict)
            
            return entity
        except Exception as e:
            logger.error(f"Error updating entity: {str(e)}")
            raise
            
    async def delete_entity(self, entity_id: UUID) -> bool:
        """Delete an entity by ID"""
        try:
            entity_collection = await self._get_entity_collection()
            relationship_collection = await self._get_relationship_collection()
            
            # Delete entity
            result = await entity_collection.delete_one({"id": str(entity_id)})
            
            # Delete associated relationships
            await relationship_collection.delete_many({
                "$or": [
                    {"source_id": str(entity_id)},
                    {"target_id": str(entity_id)}
                ]
            })
            
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting entity: {str(e)}")
            raise
            
    async def create_relationship(self, relationship: Relationship) -> Relationship:
        """Create a new relationship"""
        try:
            collection = await self._get_relationship_collection()
            
            # Convert to dict and insert
            relationship_dict = relationship.dict()
            result = await collection.insert_one(relationship_dict)
            
            # Update ID if necessary
            if result.inserted_id and str(result.inserted_id) != str(relationship.id):
                relationship.id = result.inserted_id
                
            return relationship
        except Exception as e:
            logger.error(f"Error creating relationship: {str(e)}")
            raise
            
    async def get_relationship(self, relationship_id: UUID) -> Optional[Relationship]:
        """Get a relationship by ID"""
        try:
            collection = await self._get_relationship_collection()
            
            # Find relationship
            relationship_dict = await collection.find_one({"id": str(relationship_id)})
            
            if not relationship_dict:
                return None
                
            # Convert to Relationship object
            return Relationship(**relationship_dict)
        except Exception as e:
            logger.error(f"Error getting relationship: {str(e)}")
            raise
            
    async def update_relationship(self, relationship: Relationship) -> Relationship:
        """Update an existing relationship"""
        try:
            collection = await self._get_relationship_collection()
            
            # Update timestamp
            relationship.updated_at = datetime.utcnow()
            
            # Convert to dict and update
            relationship_dict = relationship.dict()
            await collection.replace_one({"id": str(relationship.id)}, relationship_dict)
            
            return relationship
        except Exception as e:
            logger.error(f"Error updating relationship: {str(e)}")
            raise
            
    async def delete_relationship(self, relationship_id: UUID) -> bool:
        """Delete a relationship by ID"""
        try:
            collection = await self._get_relationship_collection()
            
            # Delete relationship
            result = await collection.delete_one({"id": str(relationship_id)})
            
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting relationship: {str(e)}")
            raise
            
    async def get_entity_relationships(
        self,
        entity_id: UUID,
        relationship_types: Optional[List[RelationshipType]] = None,
        direction: str = "both"
    ) -> Tuple[List[Relationship], List[Entity]]:
        """Get relationships and connected entities for an entity"""
        try:
            relationship_collection = await self._get_relationship_collection()
            entity_collection = await self._get_entity_collection()
            
            # Build query
            query = {}
            if direction == "outgoing":
                query["source_id"] = str(entity_id)
            elif direction == "incoming":
                query["target_id"] = str(entity_id)
            else:  # both
                query["$or"] = [
                    {"source_id": str(entity_id)},
                    {"target_id": str(entity_id)}
                ]
                
            # Add relationship types if specified
            if relationship_types:
                query["type"] = {"$in": [t.value for t in relationship_types]}
                
            # Find relationships
            cursor = relationship_collection.find(query)
            relationships = [Relationship(**rel) async for rel in cursor]
            
            # Get connected entities
            connected_entity_ids = set()
            for rel in relationships:
                if str(rel.source_id) != str(entity_id):
                    connected_entity_ids.add(str(rel.source_id))
                if str(rel.target_id) != str(entity_id):
                    connected_entity_ids.add(str(rel.target_id))
                    
            # Find connected entities
            entities = []
            for eid in connected_entity_ids:
                entity_dict = await entity_collection.find_one({"id": eid})
                if entity_dict:
                    entities.append(Entity(**entity_dict))
                    
            return relationships, entities
        except Exception as e:
            logger.error(f"Error getting entity relationships: {str(e)}")
            raise
            
    async def query_knowledge_graph(self, query: KnowledgeGraphQuery) -> Dict[str, Any]:
        """Query the knowledge graph based on the specified criteria"""
        try:
            entity_collection = await self._get_entity_collection()
            relationship_collection = await self._get_relationship_collection()
            
            # Build entity query
            entity_query = {"project_id": str(query.project_id)}
            if query.entity_types:
                entity_query["type"] = {"$in": [t.value for t in query.entity_types]}
            if query.entity_ids:
                entity_query["id"] = {"$in": [str(eid) for eid in query.entity_ids]}
                
            # Find entities
            entity_cursor = entity_collection.find(entity_query)
            entities = [Entity(**entity) async for entity in entity_cursor]
            
            # If no specific entities requested, return all entities and relationships
            if not query.entity_ids and query.max_depth == 0:
                # Build relationship query
                relationship_query = {"project_id": str(query.project_id)}
                if query.relationship_types:
                    relationship_query["type"] = {"$in": [t.value for t in query.relationship_types]}
                    
                # Find relationships
                relationship_cursor = relationship_collection.find(relationship_query)
                relationships = [Relationship(**rel) async for rel in relationship_cursor]
                
                return {
                    "entities": [e.dict(include={"id", "type", "name", "description", "properties"} if query.include_properties else {"id", "type", "name", "description"}) for e in entities],
                    "relationships": [r.dict(include={"id", "source_id", "target_id", "type", "name", "description", "properties"} if query.include_properties else {"id", "source_id", "target_id", "type", "name", "description"}) for r in relationships]
                }
                
            # For specific entities with depth > 0, perform graph traversal
            visited_entities = {str(e.id): e for e in entities}
            visited_relationships = {}
            
            # Perform BFS traversal
            for _ in range(query.max_depth):
                # Get all entity IDs in the current frontier
                frontier_entity_ids = list(visited_entities.keys())
                
                # Find relationships connected to these entities
                relationship_query = {
                    "project_id": str(query.project_id),
                    "$or": [
                        {"source_id": {"$in": frontier_entity_ids}},
                        {"target_id": {"$in": frontier_entity_ids}}
                    ]
                }
                
                if query.relationship_types:
                    relationship_query["type"] = {"$in": [t.value for t in query.relationship_types]}
                    
                relationship_cursor = relationship_collection.find(relationship_query)
                
                # Collect new entities to visit
                new_entity_ids = set()
                
                async for rel_dict in relationship_cursor:
                    rel = Relationship(**rel_dict)
                    rel_id = str(rel.id)
                    
                    # Skip if already visited
                    if rel_id in visited_relationships:
                        continue
                        
                    visited_relationships[rel_id] = rel
                    
                    # Add connected entities to new frontier
                    if str(rel.source_id) not in visited_entities:
                        new_entity_ids.add(str(rel.source_id))
                    if str(rel.target_id) not in visited_entities:
                        new_entity_ids.add(str(rel.target_id))
                        
                # If no new entities to visit, break
                if not new_entity_ids:
                    break
                    
                # Find new entities
                for chunk in [list(new_entity_ids)[i:i+100] for i in range(0, len(new_entity_ids), 100)]:
                    entity_cursor = entity_collection.find({"id": {"$in": chunk}})
                    async for entity_dict in entity_cursor:
                        entity = Entity(**entity_dict)
                        visited_entities[str(entity.id)] = entity
                        
            return {
                "entities": [e.dict(include={"id", "type", "name", "description", "properties", "metadata"} if query.include_properties and query.include_metadata else 
                                   {"id", "type", "name", "description", "properties"} if query.include_properties else 
                                   {"id", "type", "name", "description", "metadata"} if query.include_metadata else 
                                   {"id", "type", "name", "description"}) 
                            for e in visited_entities.values()],
                "relationships": [r.dict(include={"id", "source_id", "target_id", "type", "name", "description", "properties", "metadata"} if query.include_properties and query.include_metadata else 
                                        {"id", "source_id", "target_id", "type", "name", "description", "properties"} if query.include_properties else 
                                        {"id", "source_id", "target_id", "type", "name", "description", "metadata"} if query.include_metadata else 
                                        {"id", "source_id", "target_id", "type", "name", "description"}) 
                                 for r in visited_relationships.values()]
            }
        except Exception as e:
            logger.error(f"Error querying knowledge graph: {str(e)}")
            raise
            
    async def create_or_update_ontology(self, ontology: ProjectOntology) -> ProjectOntology:
        """Create or update a project ontology"""
        try:
            collection = await self._get_ontology_collection()
            
            # Check if ontology exists
            existing = await collection.find_one({"project_id": str(ontology.project_id)})
            
            if existing:
                # Update timestamp
                ontology.updated_at = datetime.utcnow()
                
                # Convert to dict and update
                ontology_dict = ontology.dict()
                await collection.replace_one({"id": existing["id"]}, ontology_dict)
            else:
                # Convert to dict and insert
                ontology_dict = ontology.dict()
                result = await collection.insert_one(ontology_dict)
                
                # Update ID if necessary
                if result.inserted_id and str(result.inserted_id) != str(ontology.id):
                    ontology.id = result.inserted_id
                    
            return ontology
        except Exception as e:
            logger.error(f"Error creating or updating ontology: {str(e)}")
            raise
            
    async def get_project_ontology(self, project_id: UUID) -> Optional[ProjectOntology]:
        """Get the ontology for a project"""
        try:
            collection = await self._get_ontology_collection()
            
            # Find ontology
            ontology_dict = await collection.find_one({"project_id": str(project_id)})
            
            if not ontology_dict:
                return None
                
            # Convert to ProjectOntology object
            return ProjectOntology(**ontology_dict)
        except Exception as e:
            logger.error(f"Error getting project ontology: {str(e)}")
            raise

# Create a global instance of the knowledge graph repository
knowledge_graph_repository = KnowledgeGraphRepository()
