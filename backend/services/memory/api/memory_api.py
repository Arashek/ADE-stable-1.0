"""
Memory API

This module implements the API endpoints for accessing and managing memory data,
enabling agents to retrieve relevant context and maintain a comprehensive
understanding of each project.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

from memory.api.models.conversation_memory import Conversation, Message, ConversationSummary
from memory.api.models.knowledge_graph import (
    Entity, Relationship, EntityType, RelationshipType,
    KnowledgeGraphQuery, ProjectOntology
)
from memory.api.models.decision_memory import (
    Decision, TechnicalDebt, DecisionCategory, 
    DecisionStatus, DecisionImpact, DecisionQuery
)
from memory.api.repositories.conversation_repository import conversation_repository
from memory.api.repositories.knowledge_graph_repository import knowledge_graph_repository
from memory.api.repositories.decision_repository import decision_repository

# Create router
router = APIRouter(
    prefix="/memory",
    tags=["memory"],
    responses={404: {"description": "Not found"}},
)

# Conversation Memory API

@router.post("/conversations", response_model=Conversation)
async def create_conversation(conversation: Conversation):
    """Create a new conversation"""
    try:
        return await conversation_repository.create_conversation(conversation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating conversation: {str(e)}")

@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: UUID):
    """Get a conversation by ID"""
    try:
        conversation = await conversation_repository.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail=f"Conversation with ID {conversation_id} not found")
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting conversation: {str(e)}")

@router.put("/conversations/{conversation_id}", response_model=Conversation)
async def update_conversation(conversation_id: UUID, conversation: Conversation):
    """Update an existing conversation"""
    try:
        if str(conversation_id) != str(conversation.id):
            raise HTTPException(status_code=400, detail="Conversation ID in path does not match ID in body")
        
        # Check if conversation exists
        existing = await conversation_repository.get_conversation(conversation_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Conversation with ID {conversation_id} not found")
        
        return await conversation_repository.update_conversation(conversation)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating conversation: {str(e)}")

@router.delete("/conversations/{conversation_id}", response_model=bool)
async def delete_conversation(conversation_id: UUID):
    """Delete a conversation by ID"""
    try:
        # Check if conversation exists
        existing = await conversation_repository.get_conversation(conversation_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Conversation with ID {conversation_id} not found")
        
        return await conversation_repository.delete_conversation(conversation_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting conversation: {str(e)}")

@router.post("/conversations/{conversation_id}/messages", response_model=Conversation)
async def add_message(conversation_id: UUID, message: Message):
    """Add a message to a conversation"""
    try:
        return await conversation_repository.add_message(conversation_id, message)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding message: {str(e)}")

@router.get("/projects/{project_id}/conversations", response_model=List[ConversationSummary])
async def get_project_conversations(
    project_id: UUID,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get conversations for a project"""
    try:
        return await conversation_repository.get_project_conversations(project_id, limit, offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting project conversations: {str(e)}")

@router.get("/projects/{project_id}/conversations/search", response_model=List[dict])
async def search_conversations(
    project_id: UUID,
    query: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=20)
):
    """Search conversations using semantic search"""
    try:
        return await conversation_repository.search_conversations(project_id, query, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching conversations: {str(e)}")

# Knowledge Graph API

@router.post("/entities", response_model=Entity)
async def create_entity(entity: Entity):
    """Create a new entity"""
    try:
        return await knowledge_graph_repository.create_entity(entity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating entity: {str(e)}")

@router.get("/entities/{entity_id}", response_model=Entity)
async def get_entity(entity_id: UUID):
    """Get an entity by ID"""
    try:
        entity = await knowledge_graph_repository.get_entity(entity_id)
        if not entity:
            raise HTTPException(status_code=404, detail=f"Entity with ID {entity_id} not found")
        return entity
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting entity: {str(e)}")

@router.put("/entities/{entity_id}", response_model=Entity)
async def update_entity(entity_id: UUID, entity: Entity):
    """Update an existing entity"""
    try:
        if str(entity_id) != str(entity.id):
            raise HTTPException(status_code=400, detail="Entity ID in path does not match ID in body")
        
        # Check if entity exists
        existing = await knowledge_graph_repository.get_entity(entity_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Entity with ID {entity_id} not found")
        
        return await knowledge_graph_repository.update_entity(entity)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating entity: {str(e)}")

@router.delete("/entities/{entity_id}", response_model=bool)
async def delete_entity(entity_id: UUID):
    """Delete an entity by ID"""
    try:
        # Check if entity exists
        existing = await knowledge_graph_repository.get_entity(entity_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Entity with ID {entity_id} not found")
        
        return await knowledge_graph_repository.delete_entity(entity_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting entity: {str(e)}")

@router.post("/relationships", response_model=Relationship)
async def create_relationship(relationship: Relationship):
    """Create a new relationship"""
    try:
        return await knowledge_graph_repository.create_relationship(relationship)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating relationship: {str(e)}")

@router.get("/relationships/{relationship_id}", response_model=Relationship)
async def get_relationship(relationship_id: UUID):
    """Get a relationship by ID"""
    try:
        relationship = await knowledge_graph_repository.get_relationship(relationship_id)
        if not relationship:
            raise HTTPException(status_code=404, detail=f"Relationship with ID {relationship_id} not found")
        return relationship
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting relationship: {str(e)}")

@router.put("/relationships/{relationship_id}", response_model=Relationship)
async def update_relationship(relationship_id: UUID, relationship: Relationship):
    """Update an existing relationship"""
    try:
        if str(relationship_id) != str(relationship.id):
            raise HTTPException(status_code=400, detail="Relationship ID in path does not match ID in body")
        
        # Check if relationship exists
        existing = await knowledge_graph_repository.get_relationship(relationship_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Relationship with ID {relationship_id} not found")
        
        return await knowledge_graph_repository.update_relationship(relationship)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating relationship: {str(e)}")

@router.delete("/relationships/{relationship_id}", response_model=bool)
async def delete_relationship(relationship_id: UUID):
    """Delete a relationship by ID"""
    try:
        # Check if relationship exists
        existing = await knowledge_graph_repository.get_relationship(relationship_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Relationship with ID {relationship_id} not found")
        
        return await knowledge_graph_repository.delete_relationship(relationship_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting relationship: {str(e)}")

@router.post("/knowledge-graph/query", response_model=Dict[str, Any])
async def query_knowledge_graph(query: KnowledgeGraphQuery):
    """Query the knowledge graph based on the specified criteria"""
    try:
        return await knowledge_graph_repository.query_knowledge_graph(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying knowledge graph: {str(e)}")

@router.get("/entities/{entity_id}/relationships", response_model=Dict[str, Any])
async def get_entity_relationships(
    entity_id: UUID,
    direction: str = Query("both", regex="^(outgoing|incoming|both)$"),
    relationship_types: Optional[List[str]] = Query(None)
):
    """Get relationships and connected entities for an entity"""
    try:
        # Convert relationship types to enum values if provided
        enum_types = None
        if relationship_types:
            try:
                enum_types = [RelationshipType(t) for t in relationship_types]
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid relationship type: {str(e)}")
        
        relationships, entities = await knowledge_graph_repository.get_entity_relationships(
            entity_id, enum_types, direction
        )
        
        return {
            "relationships": [r.dict() for r in relationships],
            "entities": [e.dict() for e in entities]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting entity relationships: {str(e)}")

@router.post("/projects/{project_id}/ontology", response_model=ProjectOntology)
async def create_or_update_ontology(project_id: UUID, ontology: ProjectOntology):
    """Create or update a project ontology"""
    try:
        if str(project_id) != str(ontology.project_id):
            raise HTTPException(status_code=400, detail="Project ID in path does not match ID in body")
        
        return await knowledge_graph_repository.create_or_update_ontology(ontology)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating or updating ontology: {str(e)}")

@router.get("/projects/{project_id}/ontology", response_model=Optional[ProjectOntology])
async def get_project_ontology(project_id: UUID):
    """Get the ontology for a project"""
    try:
        return await knowledge_graph_repository.get_project_ontology(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting project ontology: {str(e)}")

# Decision Memory API

@router.post("/decisions", response_model=Decision)
async def create_decision(decision: Decision):
    """Create a new decision"""
    try:
        return await decision_repository.create_decision(decision)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating decision: {str(e)}")

@router.get("/decisions/{decision_id}", response_model=Decision)
async def get_decision(decision_id: UUID):
    """Get a decision by ID"""
    try:
        decision = await decision_repository.get_decision(decision_id)
        if not decision:
            raise HTTPException(status_code=404, detail=f"Decision with ID {decision_id} not found")
        return decision
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting decision: {str(e)}")

@router.put("/decisions/{decision_id}", response_model=Decision)
async def update_decision(decision_id: UUID, decision: Decision):
    """Update an existing decision"""
    try:
        if str(decision_id) != str(decision.id):
            raise HTTPException(status_code=400, detail="Decision ID in path does not match ID in body")
        
        # Check if decision exists
        existing = await decision_repository.get_decision(decision_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Decision with ID {decision_id} not found")
        
        return await decision_repository.update_decision(decision)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating decision: {str(e)}")

@router.delete("/decisions/{decision_id}", response_model=bool)
async def delete_decision(decision_id: UUID):
    """Delete a decision by ID"""
    try:
        # Check if decision exists
        existing = await decision_repository.get_decision(decision_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Decision with ID {decision_id} not found")
        
        return await decision_repository.delete_decision(decision_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting decision: {str(e)}")

@router.post("/technical-debt", response_model=TechnicalDebt)
async def create_technical_debt(debt: TechnicalDebt):
    """Create a new technical debt item"""
    try:
        return await decision_repository.create_technical_debt(debt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating technical debt: {str(e)}")

@router.get("/technical-debt/{debt_id}", response_model=TechnicalDebt)
async def get_technical_debt(debt_id: UUID):
    """Get a technical debt item by ID"""
    try:
        debt = await decision_repository.get_technical_debt(debt_id)
        if not debt:
            raise HTTPException(status_code=404, detail=f"Technical debt with ID {debt_id} not found")
        return debt
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting technical debt: {str(e)}")

@router.put("/technical-debt/{debt_id}", response_model=TechnicalDebt)
async def update_technical_debt(debt_id: UUID, debt: TechnicalDebt):
    """Update an existing technical debt item"""
    try:
        if str(debt_id) != str(debt.id):
            raise HTTPException(status_code=400, detail="Technical debt ID in path does not match ID in body")
        
        # Check if technical debt exists
        existing = await decision_repository.get_technical_debt(debt_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Technical debt with ID {debt_id} not found")
        
        return await decision_repository.update_technical_debt(debt)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating technical debt: {str(e)}")

@router.delete("/technical-debt/{debt_id}", response_model=bool)
async def delete_technical_debt(debt_id: UUID):
    """Delete a technical debt item by ID"""
    try:
        # Check if technical debt exists
        existing = await decision_repository.get_technical_debt(debt_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Technical debt with ID {debt_id} not found")
        
        return await decision_repository.delete_technical_debt(debt_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting technical debt: {str(e)}")

@router.post("/technical-debt/{debt_id}/resolve", response_model=TechnicalDebt)
async def resolve_technical_debt(debt_id: UUID):
    """Mark a technical debt item as resolved"""
    try:
        return await decision_repository.resolve_technical_debt(debt_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resolving technical debt: {str(e)}")

@router.post("/projects/{project_id}/decisions/query", response_model=List[Decision])
async def query_decisions(project_id: UUID, query: DecisionQuery):
    """Query decisions based on the specified criteria"""
    try:
        if str(project_id) != str(query.project_id):
            raise HTTPException(status_code=400, detail="Project ID in path does not match ID in body")
        
        return await decision_repository.query_decisions(query)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying decisions: {str(e)}")

@router.get("/projects/{project_id}/technical-debt", response_model=List[TechnicalDebt])
async def get_project_technical_debt(
    project_id: UUID,
    include_resolved: bool = Query(False)
):
    """Get technical debt items for a project"""
    try:
        return await decision_repository.get_project_technical_debt(project_id, include_resolved)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting project technical debt: {str(e)}")

@router.get("/projects/{project_id}/technical-debt/summary", response_model=Dict[str, Any])
async def get_technical_debt_summary(project_id: UUID):
    """Get a summary of technical debt for a project"""
    try:
        return await decision_repository.get_technical_debt_summary(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting technical debt summary: {str(e)}")
