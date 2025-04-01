"""
Memory Service Test Script

This script tests the memory service functionality, including conversation memory,
knowledge graph, and decision memory components. It can be run standalone to verify
that the memory infrastructure is working correctly.
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any

from memory_service import memory_service
from models.conversation_memory import Conversation, Message
from models.knowledge_graph import Entity, Relationship, EntityType, RelationshipType
from models.decision_memory import Decision, TechnicalDebt, DecisionCategory, DecisionStatus, DecisionImpact

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_conversation_memory():
    """Test conversation memory functionality"""
    logger.info("Testing conversation memory...")
    
    # Create a new project ID
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    # Create a new conversation
    conversation = await memory_service.create_conversation(
        project_id=project_id,
        user_id=user_id,
        title="Test Conversation",
        tags=["test", "memory"]
    )
    logger.info(f"Created conversation: {conversation.id}")
    
    # Add messages to the conversation
    await memory_service.add_message(
        conversation_id=conversation.id,
        sender="user",
        content="Hello, I need help with my project",
        metadata={"client_timestamp": datetime.now().isoformat()}
    )
    
    await memory_service.add_message(
        conversation_id=conversation.id,
        sender="assistant",
        content="I'd be happy to help! What kind of project are you working on?",
        metadata={"model": "gpt-4"}
    )
    
    await memory_service.add_message(
        conversation_id=conversation.id,
        sender="user",
        content="I'm building a web application with React and FastAPI",
        metadata={"client_timestamp": datetime.now().isoformat()}
    )
    
    # Get the conversation
    updated_conversation = await memory_service.get_conversation(conversation.id)
    logger.info(f"Retrieved conversation with {len(updated_conversation.messages)} messages")
    
    # Search conversations
    search_results = await memory_service.search_conversations(
        project_id=project_id,
        query="web application React",
        limit=5
    )
    logger.info(f"Found {len(search_results)} relevant conversation snippets")
    
    return updated_conversation

async def test_knowledge_graph():
    """Test knowledge graph functionality"""
    logger.info("Testing knowledge graph...")
    
    # Create a new project ID
    project_id = uuid.uuid4()
    
    # Create entities
    project_entity = await memory_service.create_entity(Entity(
        name="Test Project",
        entity_type=EntityType.PROJECT,
        project_id=project_id,
        properties={
            "description": "A test project for the memory service",
            "created_at": datetime.now().isoformat()
        }
    ))
    logger.info(f"Created project entity: {project_entity.id}")
    
    component_entity = await memory_service.create_entity(Entity(
        name="Frontend",
        entity_type=EntityType.COMPONENT,
        project_id=project_id,
        properties={
            "technology": "React",
            "version": "18.0.0"
        }
    ))
    logger.info(f"Created component entity: {component_entity.id}")
    
    api_entity = await memory_service.create_entity(Entity(
        name="API",
        entity_type=EntityType.COMPONENT,
        project_id=project_id,
        properties={
            "technology": "FastAPI",
            "version": "0.95.0"
        }
    ))
    logger.info(f"Created API entity: {api_entity.id}")
    
    # Create relationships
    contains_relationship = await memory_service.create_relationship(Relationship(
        source_id=project_entity.id,
        target_id=component_entity.id,
        relationship_type=RelationshipType.CONTAINS,
        project_id=project_id,
        properties={
            "created_at": datetime.now().isoformat()
        }
    ))
    logger.info(f"Created contains relationship: {contains_relationship.id}")
    
    depends_on_relationship = await memory_service.create_relationship(Relationship(
        source_id=component_entity.id,
        target_id=api_entity.id,
        relationship_type=RelationshipType.DEPENDS_ON,
        project_id=project_id,
        properties={
            "created_at": datetime.now().isoformat()
        }
    ))
    logger.info(f"Created depends_on relationship: {depends_on_relationship.id}")
    
    # Query knowledge graph
    from models.knowledge_graph import KnowledgeGraphQuery
    query_result = await memory_service.query_knowledge_graph(KnowledgeGraphQuery(
        project_id=project_id,
        entity_types=[EntityType.COMPONENT],
        max_depth=2,
        include_properties=True
    ))
    
    logger.info(f"Knowledge graph query returned {len(query_result.get('entities', []))} entities and {len(query_result.get('relationships', []))} relationships")
    
    return query_result

async def test_decision_memory():
    """Test decision memory functionality"""
    logger.info("Testing decision memory...")
    
    # Create a new project ID
    project_id = uuid.uuid4()
    
    # Create decisions
    architecture_decision = await memory_service.create_decision(Decision(
        title="Use React for Frontend",
        description="We decided to use React for the frontend due to its component-based architecture and large ecosystem.",
        category=DecisionCategory.ARCHITECTURE,
        status=DecisionStatus.APPROVED,
        impact=DecisionImpact.HIGH,
        project_id=project_id,
        tags=["frontend", "architecture"],
        metadata={
            "alternatives_considered": ["Angular", "Vue.js"],
            "decision_date": datetime.now().isoformat()
        }
    ))
    logger.info(f"Created architecture decision: {architecture_decision.id}")
    
    design_decision = await memory_service.create_decision(Decision(
        title="Use Material-UI for Component Library",
        description="We decided to use Material-UI as our component library for consistent design and faster development.",
        category=DecisionCategory.DESIGN,
        status=DecisionStatus.APPROVED,
        impact=DecisionImpact.MEDIUM,
        project_id=project_id,
        tags=["frontend", "design"],
        metadata={
            "alternatives_considered": ["Ant Design", "Bootstrap"],
            "decision_date": datetime.now().isoformat()
        }
    ))
    logger.info(f"Created design decision: {design_decision.id}")
    
    # Create technical debt
    technical_debt = await memory_service.create_technical_debt(TechnicalDebt(
        title="Refactor Authentication Logic",
        description="The current authentication logic is tightly coupled with the UI and needs to be refactored into a separate service.",
        impact=DecisionImpact.MEDIUM,
        project_id=project_id,
        tags=["auth", "refactoring"],
        due_date=datetime.now().replace(month=datetime.now().month + 1).isoformat(),
        metadata={
            "created_by": "developer1",
            "estimated_effort": "3 days"
        }
    ))
    logger.info(f"Created technical debt: {technical_debt.id}")
    
    # Query decisions
    from models.decision_memory import DecisionQuery
    decision_results = await memory_service.query_decisions(DecisionQuery(
        project_id=project_id,
        categories=[DecisionCategory.ARCHITECTURE, DecisionCategory.DESIGN],
        statuses=[DecisionStatus.APPROVED]
    ))
    logger.info(f"Decision query returned {len(decision_results)} decisions")
    
    # Get technical debt
    debt_items = await memory_service.get_project_technical_debt(project_id, include_resolved=False)
    logger.info(f"Found {len(debt_items)} technical debt items")
    
    return {
        "decisions": decision_results,
        "technical_debt": debt_items
    }

async def test_context_retrieval():
    """Test context retrieval functionality"""
    logger.info("Testing context retrieval...")
    
    # Create a new project ID
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    # Create a conversation with messages about React components
    conversation = await memory_service.create_conversation(
        project_id=project_id,
        user_id=user_id,
        title="React Component Discussion",
        tags=["react", "frontend"]
    )
    
    await memory_service.add_message(
        conversation_id=conversation.id,
        sender="user",
        content="I'm having trouble with my React components. The state is not updating properly."
    )
    
    await memory_service.add_message(
        conversation_id=conversation.id,
        sender="assistant",
        content="Let's look at your component. Are you using useState or useReducer for state management?"
    )
    
    # Create entities and relationships
    component_entity = await memory_service.create_entity(Entity(
        name="UserProfile",
        entity_type=EntityType.COMPONENT,
        project_id=project_id,
        properties={
            "technology": "React",
            "path": "src/components/UserProfile.jsx"
        }
    ))
    
    # Create a decision about React state management
    state_decision = await memory_service.create_decision(Decision(
        title="Use Redux for State Management",
        description="We decided to use Redux for global state management to handle complex state interactions between components.",
        category=DecisionCategory.IMPLEMENTATION,
        status=DecisionStatus.APPROVED,
        impact=DecisionImpact.MEDIUM,
        project_id=project_id,
        tags=["react", "state-management"]
    ))
    
    # Retrieve context
    context = await memory_service.retrieve_context(
        project_id=project_id,
        query="React state management",
        limit=5
    )
    
    logger.info(f"Context retrieval returned {len(context.get('conversations', []))} conversations, "
                f"{len(context.get('knowledge_graph', {}).get('entities', []))} entities, and "
                f"{len(context.get('decisions', []))} decisions")
    
    return context

async def main():
    """Main function to run the tests"""
    try:
        logger.info("Initializing memory service...")
        await memory_service.initialize()
        
        # Run tests
        conversation_result = await test_conversation_memory()
        knowledge_graph_result = await test_knowledge_graph()
        decision_result = await test_decision_memory()
        context_result = await test_context_retrieval()
        
        logger.info("All tests completed successfully!")
        
        # Shutdown memory service
        await memory_service.shutdown()
        
    except Exception as e:
        logger.error(f"Error during tests: {str(e)}", exc_info=True)
        
        # Ensure memory service is shut down
        try:
            await memory_service.shutdown()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())
