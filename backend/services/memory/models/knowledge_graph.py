"""
Knowledge Graph Models

This module defines the data models for storing and retrieving knowledge graph data,
enabling the platform to maintain a structured representation of project entities
and their relationships.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from enum import Enum

class EntityType(str, Enum):
    """Enumeration of entity types in the knowledge graph"""
    COMPONENT = "component"
    FEATURE = "feature"
    API = "api"
    DATABASE = "database"
    USER_STORY = "user_story"
    REQUIREMENT = "requirement"
    DECISION = "decision"
    TECHNOLOGY = "technology"
    FRAMEWORK = "framework"
    LIBRARY = "library"
    PATTERN = "pattern"
    CONCEPT = "concept"
    PERSON = "person"
    ORGANIZATION = "organization"
    DOCUMENT = "document"
    CODE = "code"
    FILE = "file"
    DIRECTORY = "directory"
    CUSTOM = "custom"

class RelationshipType(str, Enum):
    """Enumeration of relationship types in the knowledge graph"""
    DEPENDS_ON = "depends_on"
    IMPLEMENTS = "implements"
    CONTAINS = "contains"
    USES = "uses"
    REFERENCES = "references"
    CREATED_BY = "created_by"
    MODIFIED_BY = "modified_by"
    RELATED_TO = "related_to"
    DERIVED_FROM = "derived_from"
    PART_OF = "part_of"
    EXTENDS = "extends"
    INHERITS_FROM = "inherits_from"
    CALLS = "calls"
    IMPORTS = "imports"
    EXPORTS = "exports"
    CUSTOM = "custom"

class Entity(BaseModel):
    """Model for an entity in the knowledge graph"""
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    type: EntityType
    name: str
    description: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Relationship(BaseModel):
    """Model for a relationship between entities in the knowledge graph"""
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    source_id: UUID
    target_id: UUID
    type: RelationshipType
    name: Optional[str] = None
    description: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class KnowledgeGraphQuery(BaseModel):
    """Model for a query to the knowledge graph"""
    project_id: UUID
    entity_types: Optional[List[EntityType]] = None
    relationship_types: Optional[List[RelationshipType]] = None
    entity_ids: Optional[List[UUID]] = None
    max_depth: int = 2
    include_properties: bool = True
    include_metadata: bool = False

class ProjectOntology(BaseModel):
    """Model for a project ontology"""
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    name: str
    description: Optional[str] = None
    entity_types: List[EntityType]
    relationship_types: List[RelationshipType]
    custom_entity_types: Dict[str, str] = Field(default_factory=dict)
    custom_relationship_types: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
