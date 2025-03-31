import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any, List

from production.src.core.memory.shared_knowledge import (
    SharedKnowledgeRepository,
    KnowledgeEntry,
    KnowledgeDomain
)
from production.src.core.agent import Agent

@pytest.fixture
def shared_knowledge():
    """Create a shared knowledge repository for testing."""
    return SharedKnowledgeRepository(db_path=":memory:")

@pytest.fixture
def agent():
    """Create an agent for testing."""
    return Agent(
        agent_id="test_agent",
        name="Test Agent",
        capabilities=["test_capability"]
    )

@pytest.mark.asyncio
async def test_add_knowledge(shared_knowledge):
    """Test adding knowledge to the repository."""
    entry = KnowledgeEntry(
        domain=KnowledgeDomain.FACT,
        content={
            "subject": "test",
            "predicate": "is",
            "object": "working"
        },
        created_by="test_agent",
        confidence=0.8,
        tags=["test", "fact"]
    )
    
    knowledge_id = shared_knowledge.add_knowledge(entry)
    assert knowledge_id is not None
    
    # Verify knowledge was stored
    knowledge = shared_knowledge.retrieve_knowledge(
        domain=KnowledgeDomain.FACT,
        tags=["test"],
        limit=1
    )
    assert len(knowledge) == 1
    assert knowledge[0].id == knowledge_id
    assert knowledge[0].content == entry.content

@pytest.mark.asyncio
async def test_update_knowledge(shared_knowledge):
    """Test updating knowledge in the repository."""
    # Add initial knowledge
    entry = KnowledgeEntry(
        domain=KnowledgeDomain.FACT,
        content={
            "subject": "test",
            "predicate": "is",
            "object": "working"
        },
        created_by="test_agent",
        confidence=0.8,
        tags=["test", "fact"]
    )
    knowledge_id = shared_knowledge.add_knowledge(entry)
    
    # Update knowledge
    updates = {
        "content": {
            "subject": "test",
            "predicate": "is",
            "object": "updated"
        },
        "confidence": 0.9
    }
    success = shared_knowledge.update_knowledge(knowledge_id, updates)
    assert success
    
    # Verify update
    knowledge = shared_knowledge.retrieve_knowledge(
        knowledge_id=knowledge_id,
        limit=1
    )
    assert len(knowledge) == 1
    assert knowledge[0].content["object"] == "updated"
    assert knowledge[0].confidence == 0.9
    assert knowledge[0].version == 2

@pytest.mark.asyncio
async def test_retrieve_knowledge(shared_knowledge):
    """Test retrieving knowledge from the repository."""
    # Add multiple knowledge entries
    entries = [
        KnowledgeEntry(
            domain=KnowledgeDomain.FACT,
            content={"subject": f"test_{i}", "predicate": "is", "object": f"value_{i}"},
            created_by="test_agent",
            confidence=0.8,
            tags=["test", "fact"]
        )
        for i in range(3)
    ]
    
    for entry in entries:
        shared_knowledge.add_knowledge(entry)
    
    # Test retrieval by domain
    knowledge = shared_knowledge.retrieve_knowledge(
        domain=KnowledgeDomain.FACT,
        limit=3
    )
    assert len(knowledge) == 3
    
    # Test retrieval by tags
    knowledge = shared_knowledge.retrieve_knowledge(
        tags=["test"],
        limit=3
    )
    assert len(knowledge) == 3
    
    # Test retrieval by confidence threshold
    knowledge = shared_knowledge.retrieve_knowledge(
        confidence_threshold=0.9,
        limit=3
    )
    assert len(knowledge) == 0

@pytest.mark.asyncio
async def test_conflict_detection(shared_knowledge):
    """Test conflict detection in the repository."""
    # Add initial fact
    entry1 = KnowledgeEntry(
        domain=KnowledgeDomain.FACT,
        content={
            "subject": "test",
            "predicate": "is",
            "object": "value1"
        },
        created_by="agent1",
        confidence=0.8,
        tags=["test", "fact"]
    )
    shared_knowledge.add_knowledge(entry1)
    
    # Add conflicting fact
    entry2 = KnowledgeEntry(
        domain=KnowledgeDomain.FACT,
        content={
            "subject": "test",
            "predicate": "is",
            "object": "value2"
        },
        created_by="agent2",
        confidence=0.7,
        tags=["test", "fact"]
    )
    knowledge_id = shared_knowledge.add_knowledge(entry2)
    
    # Verify conflict was detected
    knowledge = shared_knowledge.retrieve_knowledge(
        knowledge_id=knowledge_id,
        limit=1
    )
    assert len(knowledge) == 1
    assert len(knowledge[0].conflicts) > 0
    assert knowledge[0].conflicts[0]["type"] == "content_conflict"

@pytest.mark.asyncio
async def test_agent_knowledge_sharing(agent):
    """Test knowledge sharing between agents."""
    # Share knowledge
    knowledge_id = await agent.share_knowledge(
        domain=KnowledgeDomain.FACT,
        content={
            "subject": "test",
            "predicate": "is",
            "object": "shared"
        },
        confidence=0.8,
        tags=["test", "shared"]
    )
    assert knowledge_id is not None
    
    # Retrieve shared knowledge
    knowledge = await agent.retrieve_shared_knowledge(
        domain=KnowledgeDomain.FACT,
        tags=["shared"]
    )
    assert len(knowledge) == 1
    assert knowledge[0].content["object"] == "shared"
    
    # Update shared knowledge
    success = await agent.update_shared_knowledge(
        knowledge_id,
        {
            "content": {
                "subject": "test",
                "predicate": "is",
                "object": "updated"
            }
        }
    )
    assert success
    
    # Verify update
    knowledge = await agent.retrieve_shared_knowledge(
        knowledge_id=knowledge_id
    )
    assert len(knowledge) == 1
    assert knowledge[0].content["object"] == "updated"

@pytest.mark.asyncio
async def test_task_knowledge_integration(agent):
    """Test integration of task knowledge with shared knowledge."""
    # Handle task request
    task = {
        "task_id": "test_task",
        "description": "Test task",
        "requirements": ["test_requirement"]
    }
    
    await agent._handle_task_request(
        Message(
            category=MessageCategory.REQUEST,
            priority=MessagePriority.NORMAL,
            content=task
        )
    )
    
    # Verify task knowledge was shared
    knowledge = await agent.retrieve_shared_knowledge(
        domain=KnowledgeDomain.TASK,
        tags=["task", "accepted"]
    )
    assert len(knowledge) == 1
    assert knowledge[0].content["task_id"] == "test_task"
    
    # Complete task
    result = {"status": "success", "output": "test output"}
    await agent.complete_task("test_task", result)
    
    # Verify completion knowledge was shared
    knowledge = await agent.retrieve_shared_knowledge(
        domain=KnowledgeDomain.TASK,
        tags=["task", "completed"]
    )
    assert len(knowledge) == 1
    assert knowledge[0].content["task_id"] == "test_task"
    assert knowledge[0].content["status"] == "completed" 