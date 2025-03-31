import unittest
import tempfile
import shutil
import os
from datetime import datetime
from ..knowledge_repository import KnowledgeRepository, KnowledgeEntry
from ..memory_indexer import MemoryIndexer, SearchResult
from ..agent_memory import AgentMemory, ConversationContext
from ..memory_orchestrator import MemoryOrchestrator, MemoryStats

class TestMemorySystem(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.repository = KnowledgeRepository(self.temp_dir)
        self.indexer = MemoryIndexer(self.repository)
        self.orchestrator = MemoryOrchestrator(self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_knowledge_repository(self):
        """Test knowledge repository functionality."""
        # Create test entry
        entry = KnowledgeEntry(
            id="test1",
            content="Test content",
            topic="Test topic",
            tags=["test", "unit"],
            importance_score=0.8,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Test adding entry
        self.assertTrue(self.repository.add_entry(entry))
        self.assertEqual(len(self.repository.index["entries"]), 1)

        # Test retrieving entry
        retrieved = self.repository.get_entry("test1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.content, "Test content")

        # Test updating entry
        entry.content = "Updated content"
        self.assertTrue(self.repository.update_entry(entry))
        updated = self.repository.get_entry("test1")
        self.assertEqual(updated.content, "Updated content")

        # Test deleting entry
        self.assertTrue(self.repository.delete_entry("test1"))
        self.assertEqual(len(self.repository.index["entries"]), 0)

    def test_memory_indexer(self):
        """Test memory indexer functionality."""
        # Create test entries
        entry1 = KnowledgeEntry(
            id="test1",
            content="First test content",
            topic="Test topic 1",
            tags=["test", "unit"],
            importance_score=0.8,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        entry2 = KnowledgeEntry(
            id="test2",
            content="Second test content",
            topic="Test topic 2",
            tags=["test", "unit"],
            importance_score=0.6,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Add entries to repository
        self.repository.add_entry(entry1)
        self.repository.add_entry(entry2)

        # Test indexing
        self.assertTrue(self.indexer.index_entry(entry1))
        self.assertTrue(self.indexer.index_entry(entry2))

        # Test semantic search
        results = self.indexer.semantic_search("test content", limit=2)
        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0], SearchResult)

        # Test finding similar entries
        similar = self.indexer.find_similar_entries("test1", limit=1)
        self.assertEqual(len(similar), 1)
        self.assertEqual(similar[0].entry.id, "test2")

    def test_agent_memory(self):
        """Test agent memory functionality."""
        agent_id = "test_agent"
        agent_memory = AgentMemory(agent_id, self.repository)

        # Test conversation context
        message = {
            "role": "user",
            "content": "Test message",
            "timestamp": datetime.now().isoformat()
        }
        agent_memory.update_conversation_context("test_conversation", message)
        context = agent_memory.get_conversation_context("test_conversation")
        self.assertIsNotNone(context)
        self.assertEqual(len(context.messages), 1)

        # Test preferences
        preferences = {"theme": "dark", "language": "en"}
        agent_memory.update_preferences(preferences)
        self.assertEqual(agent_memory.memory["preferences"], preferences)

        # Test expertise
        agent_memory.update_expertise("python", 0.8, ["test1", "test2"])
        expertise = agent_memory.get_expertise_summary()
        self.assertEqual(expertise["python"], 0.8)

        # Test learning history
        agent_memory.record_learning("test_topic", "test_content", "test_source")
        history = agent_memory.get_learning_history()
        self.assertEqual(len(history), 1)

    def test_memory_orchestrator(self):
        """Test memory orchestrator functionality."""
        # Test agent registration
        agent_id = "test_agent"
        self.assertTrue(self.orchestrator.register_agent(agent_id))
        self.assertIn(agent_id, self.orchestrator.agent_memories)

        # Test knowledge sharing
        entry = KnowledgeEntry(
            id="test1",
            content="Test content",
            topic="Test topic",
            tags=["test", "unit"],
            importance_score=0.8,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.repository.add_entry(entry)
        self.indexer.index_entry(entry)

        target_agent_id = "target_agent"
        self.orchestrator.register_agent(target_agent_id)
        self.assertTrue(self.orchestrator.share_knowledge(agent_id, target_agent_id, ["test1"]))

        # Test memory stats
        stats = self.orchestrator.get_memory_stats()
        self.assertIsInstance(stats, MemoryStats)
        self.assertEqual(stats.total_entries, 1)
        self.assertEqual(stats.total_agents, 2)

        # Test expertise tracking
        expertise = self.orchestrator.get_agent_expertise(agent_id)
        self.assertIsInstance(expertise, dict)

        # Test conversation context
        message = {
            "role": "user",
            "content": "Test message",
            "timestamp": datetime.now().isoformat()
        }
        self.assertTrue(self.orchestrator.update_conversation_context(agent_id, "test_conversation", message))
        context = self.orchestrator.get_conversation_context(agent_id, "test_conversation")
        self.assertIsNotNone(context)

        # Test unregistering agent
        self.assertTrue(self.orchestrator.unregister_agent(agent_id))
        self.assertNotIn(agent_id, self.orchestrator.agent_memories)

    def test_error_handling(self):
        """Test error handling in memory system."""
        # Test invalid entry ID
        entry = self.repository.get_entry("nonexistent")
        self.assertIsNone(entry)

        # Test invalid agent ID
        context = self.orchestrator.get_conversation_context("nonexistent", "test_conversation")
        self.assertIsNone(context)

        # Test invalid knowledge sharing
        success = self.orchestrator.share_knowledge("source", "target", ["nonexistent"])
        self.assertFalse(success)

        # Test invalid expertise retrieval
        expertise = self.orchestrator.get_agent_expertise("nonexistent")
        self.assertEqual(expertise, {})

    def test_persistence(self):
        """Test persistence of memory system."""
        # Create and save test data
        agent_id = "test_agent"
        self.orchestrator.register_agent(agent_id)
        agent_memory = self.orchestrator.agent_memories[agent_id]
        
        # Update agent memory
        agent_memory.update_preferences({"theme": "dark"})
        agent_memory.update_expertise("python", 0.8, ["test1"])
        agent_memory.record_learning("test_topic", "test_content", "test_source")

        # Create new orchestrator instance
        new_orchestrator = MemoryOrchestrator(self.temp_dir)
        new_agent_memory = new_orchestrator.agent_memories[agent_id]

        # Verify persistence
        self.assertEqual(new_agent_memory.memory["preferences"]["theme"], "dark")
        self.assertEqual(new_agent_memory.get_expertise_summary()["python"], 0.8)
        self.assertEqual(len(new_agent_memory.get_learning_history()), 1)

if __name__ == '__main__':
    unittest.main() 