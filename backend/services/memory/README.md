# ADE Memory Infrastructure

The Memory Infrastructure is a core component of the ADE platform that provides persistent memory capabilities across user interactions and projects. It enables specialized agents to maintain context, retrieve relevant information, and make informed decisions based on historical data.

## Overview

The Memory Infrastructure consists of three main components:

1. **Conversation Memory**: Stores and retrieves conversation histories between users and agents, with support for semantic search using vector embeddings.
2. **Knowledge Graph**: Maintains a structured representation of project entities and their relationships, enabling complex queries and insights.
3. **Decision Memory**: Tracks design decisions, architectural choices, and technical debt, providing a historical record of project evolution.

## Architecture

The Memory Infrastructure follows a modular architecture with the following components:

- **Models**: Defines data structures for conversation memory, knowledge graph, and decision memory.
- **Repositories**: Provides data access and management for each memory component.
- **API**: Exposes RESTful endpoints for accessing and manipulating memory data.
- **Services**: Implements business logic and coordinates between different memory components.

## Components

### MongoDB Connection Manager

Handles connections to MongoDB for storing and retrieving memory data.

```python
from services.memory.mongodb_connection import mongodb_manager

# Connect to MongoDB
await mongodb_manager.connect()

# Get a collection
collection = await mongodb_manager.get_collection("conversations")
```

### Vector Embeddings Service

Generates and manages vector embeddings for semantic search capabilities.

```python
from services.memory.vector_embeddings import vector_embeddings_service

# Generate embeddings for a text
embeddings = await vector_embeddings_service.generate_embeddings("Sample text")

# Find similar texts
similar_texts = await vector_embeddings_service.find_similar(embeddings, collection_name="conversations")
```

### Memory Service

Provides a unified interface for accessing and managing memory data.

```python
from services.memory.memory_service import memory_service

# Initialize the memory service
await memory_service.initialize()

# Create a conversation
conversation = await memory_service.create_conversation(project_id, user_id, "Conversation Title")

# Add a message to the conversation
await memory_service.add_message(conversation_id, "user", "Hello, I need help with my project")

# Retrieve context for a query
context = await memory_service.retrieve_context(project_id, "React state management")
```

## API Endpoints

The Memory Infrastructure exposes the following API endpoints:

### Conversation Memory

- `POST /api/v1/memory/conversations`: Create a new conversation
- `GET /api/v1/memory/conversations/{conversation_id}`: Get a conversation by ID
- `PUT /api/v1/memory/conversations/{conversation_id}`: Update an existing conversation
- `DELETE /api/v1/memory/conversations/{conversation_id}`: Delete a conversation
- `POST /api/v1/memory/conversations/{conversation_id}/messages`: Add a message to a conversation
- `GET /api/v1/memory/projects/{project_id}/conversations`: Get conversations for a project
- `GET /api/v1/memory/projects/{project_id}/conversations/search`: Search conversations using semantic search

### Knowledge Graph

- `POST /api/v1/memory/entities`: Create a new entity
- `GET /api/v1/memory/entities/{entity_id}`: Get an entity by ID
- `PUT /api/v1/memory/entities/{entity_id}`: Update an existing entity
- `DELETE /api/v1/memory/entities/{entity_id}`: Delete an entity
- `POST /api/v1/memory/relationships`: Create a new relationship
- `GET /api/v1/memory/relationships/{relationship_id}`: Get a relationship by ID
- `PUT /api/v1/memory/relationships/{relationship_id}`: Update an existing relationship
- `DELETE /api/v1/memory/relationships/{relationship_id}`: Delete a relationship
- `POST /api/v1/memory/knowledge-graph/query`: Query the knowledge graph
- `GET /api/v1/memory/entities/{entity_id}/relationships`: Get relationships for an entity
- `POST /api/v1/memory/projects/{project_id}/ontology`: Create or update a project ontology
- `GET /api/v1/memory/projects/{project_id}/ontology`: Get the ontology for a project

### Decision Memory

- `POST /api/v1/memory/decisions`: Create a new decision
- `GET /api/v1/memory/decisions/{decision_id}`: Get a decision by ID
- `PUT /api/v1/memory/decisions/{decision_id}`: Update an existing decision
- `DELETE /api/v1/memory/decisions/{decision_id}`: Delete a decision
- `POST /api/v1/memory/technical-debt`: Create a new technical debt item
- `GET /api/v1/memory/technical-debt/{debt_id}`: Get a technical debt item by ID
- `PUT /api/v1/memory/technical-debt/{debt_id}`: Update an existing technical debt item
- `DELETE /api/v1/memory/technical-debt/{debt_id}`: Delete a technical debt item
- `POST /api/v1/memory/technical-debt/{debt_id}/resolve`: Mark a technical debt item as resolved
- `POST /api/v1/memory/projects/{project_id}/decisions/query`: Query decisions
- `GET /api/v1/memory/projects/{project_id}/technical-debt`: Get technical debt items for a project
- `GET /api/v1/memory/projects/{project_id}/technical-debt/summary`: Get a summary of technical debt for a project

## Configuration

The Memory Infrastructure can be configured using the following environment variables:

- `MONGODB_URI`: Connection string for MongoDB (default: `mongodb://localhost:27017`)
- `MONGODB_DB`: Database name for MongoDB (default: `ade_memory`)
- `OPENAI_API_KEY`: API key for accessing OpenAI's embeddings service
- `OPENAI_EMBEDDING_MODEL`: Model to use for generating embeddings (default: `text-embedding-ada-002`)
- `MEMORY_ENABLED`: Whether the memory infrastructure is enabled (default: `True`)
- `VECTOR_SIMILARITY_THRESHOLD`: Threshold for vector similarity search (default: `0.7`)
- `KNOWLEDGE_GRAPH_MAX_DEPTH`: Maximum depth for knowledge graph queries (default: `3`)

## Testing

To test the Memory Infrastructure, run the `test_memory_service.py` script:

```bash
cd backend/services/memory
python test_memory_service.py
```

This script tests all components of the Memory Infrastructure, including conversation memory, knowledge graph, and decision memory.

## Integration with ADE Platform

The Memory Infrastructure is integrated with the ADE platform and can be accessed by specialized agents to maintain context and retrieve relevant information. The memory service is automatically initialized when the ADE platform starts, and the memory API endpoints are registered with the FastAPI application.

## Future Enhancements

- **Multi-modal Memory**: Support for storing and retrieving images, audio, and other media types.
- **Temporal Memory**: Enhanced support for tracking changes over time and understanding temporal relationships.
- **Cross-project Memory**: Ability to share and retrieve context across multiple projects.
- **Memory Optimization**: Automatic pruning and summarization of memory data to reduce storage requirements.
- **Enhanced Security**: Fine-grained access control and encryption for sensitive memory data.
