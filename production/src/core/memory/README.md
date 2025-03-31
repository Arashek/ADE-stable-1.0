# Multi-Agent Memory System

This module implements a hierarchical memory architecture for multi-agent systems, providing both individual agent memory management and shared knowledge capabilities.

## Components

### 1. Memory Manager (`memory_manager.py`)

The `MemoryManager` class implements a hierarchical memory system with four distinct memory types:

- **Working Memory**: Short-term, high-priority information
- **Episodic Memory**: Recent interactions and decisions
- **Semantic Memory**: General knowledge and patterns
- **Procedural Memory**: Task execution knowledge

#### Key Features:
- Automatic memory consolidation from working to long-term storage
- Importance-based memory pruning
- Memory relationships tracking
- Access control (PRIVATE, SHARED, PUBLIC)
- Efficient retrieval with indexing
- SQLite-based persistence

### 2. Shared Knowledge Repository (`shared_knowledge.py`)

The `SharedKnowledgeRepository` class manages knowledge sharing between agents with the following features:

- **Knowledge Domains**:
  - TASK: Task-related information
  - PROCEDURE: Procedural knowledge
  - PATTERN: Pattern recognition
  - RULE: Rule-based knowledge
  - FACT: Factual information
  - RELATIONSHIP: Relationship knowledge

#### Key Features:
- Conflict detection and resolution
- Version control
- Confidence-based knowledge management
- Tagging system
- Efficient retrieval with indexing
- SQLite-based persistence

## Usage Examples

### Memory Management

```python
# Initialize memory manager
memory_manager = MemoryManager("agent_memory.db")

# Store a memory
memory_entry = MemoryEntry(
    type=MemoryType.WORKING,
    content={"task": "process_data", "status": "in_progress"},
    importance=0.8,
    owner_id="agent1",
    tags=["task", "processing"]
)
memory_manager.add_memory(memory_entry)

# Retrieve memories
memories = memory_manager.retrieve_memories(
    memory_type=MemoryType.WORKING,
    tags=["task"],
    agent_id="agent1"
)
```

### Shared Knowledge

```python
# Initialize shared knowledge repository
shared_knowledge = SharedKnowledgeRepository("shared_knowledge.db")

# Share knowledge
entry = KnowledgeEntry(
    domain=KnowledgeDomain.FACT,
    content={
        "subject": "data_processing",
        "predicate": "requires",
        "object": "validation"
    },
    created_by="agent1",
    confidence=0.8,
    tags=["data", "processing"]
)
shared_knowledge.add_knowledge(entry)

# Retrieve shared knowledge
knowledge = shared_knowledge.retrieve_knowledge(
    domain=KnowledgeDomain.FACT,
    tags=["data"],
    confidence_threshold=0.7
)
```

## Integration with Agent System

The memory system is integrated with the agent system through the `Agent` class, which provides methods for:

- Memory storage and retrieval
- Knowledge sharing
- Task-related memory management
- Memory statistics tracking

## Testing

The implementation includes comprehensive tests in `tests/test_shared_knowledge.py` covering:

- Memory addition and retrieval
- Knowledge sharing and updates
- Conflict detection and resolution
- Agent integration
- Task knowledge management

## Best Practices

1. **Memory Management**:
   - Use appropriate memory types for different kinds of information
   - Set appropriate importance levels for memory consolidation
   - Use tags for efficient retrieval
   - Monitor memory usage and prune when necessary

2. **Knowledge Sharing**:
   - Set appropriate confidence levels for shared knowledge
   - Use tags for better organization and retrieval
   - Monitor conflicts and resolve them promptly
   - Keep knowledge up to date with regular updates

3. **Performance**:
   - Use appropriate indices for efficient retrieval
   - Monitor database size and performance
   - Implement proper cleanup procedures
   - Use batch operations for bulk updates

## Future Enhancements

1. **Memory System**:
   - Implement memory summarization
   - Add memory compression
   - Enhance memory relationships
   - Add memory search capabilities

2. **Shared Knowledge**:
   - Implement distributed knowledge storage
   - Add knowledge validation
   - Enhance conflict resolution strategies
   - Add knowledge versioning

3. **Integration**:
   - Add memory visualization tools
   - Implement memory analytics
   - Add memory backup and recovery
   - Enhance monitoring capabilities 