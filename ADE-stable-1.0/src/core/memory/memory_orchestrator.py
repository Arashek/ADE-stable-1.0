from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from dataclasses import dataclass
from .knowledge_repository import KnowledgeRepository, KnowledgeEntry
from .memory_indexer import MemoryIndexer
from .agent_memory import AgentMemory, ConversationContext

@dataclass
class MemoryStats:
    total_entries: int
    total_agents: int
    total_conversations: int
    average_entries_per_agent: float
    last_sync: datetime

class MemoryOrchestrator:
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.repository = KnowledgeRepository(storage_path)
        self.indexer = MemoryIndexer(self.repository)
        self.agent_memories: Dict[str, AgentMemory] = {}
        self.logger = logging.getLogger(__name__)
        self._initialize_orchestrator()

    def _initialize_orchestrator(self):
        """Initialize the memory orchestrator."""
        self.sync_interval = 300  # 5 minutes
        self.last_sync = datetime.now()
        self._load_agent_memories()

    def _load_agent_memories(self):
        """Load all agent memories from disk."""
        try:
            for agent_id in self.repository.get_agent_ids():
                self.agent_memories[agent_id] = AgentMemory(agent_id, self.repository)
        except Exception as e:
            self.logger.error(f"Error loading agent memories: {e}")

    def register_agent(self, agent_id: str) -> bool:
        """Register a new agent with the memory system."""
        try:
            if agent_id not in self.agent_memories:
                self.agent_memories[agent_id] = AgentMemory(agent_id, self.repository)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error registering agent {agent_id}: {e}")
            return False

    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the memory system."""
        try:
            if agent_id in self.agent_memories:
                # Save final state before removal
                self.agent_memories[agent_id]._save_memory()
                del self.agent_memories[agent_id]
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error unregistering agent {agent_id}: {e}")
            return False

    def sync_memories(self):
        """Synchronize all agent memories with the central repository."""
        try:
            for agent_id, agent_memory in self.agent_memories.items():
                # Update agent-specific knowledge
                agent_knowledge = agent_memory.export_memory()
                self.repository.update_agent_knowledge(agent_id, agent_knowledge)

            # Reindex all entries
            self.indexer.reindex_all()
            self.last_sync = datetime.now()
            return True
        except Exception as e:
            self.logger.error(f"Error syncing memories: {e}")
            return False

    def share_knowledge(self, source_agent_id: str, target_agent_id: str, entry_ids: List[str]) -> bool:
        """Share knowledge entries between agents."""
        try:
            if source_agent_id not in self.agent_memories or target_agent_id not in self.agent_memories:
                return False

            source_memory = self.agent_memories[source_agent_id]
            target_memory = self.agent_memories[target_agent_id]

            # Get entries from source agent
            entries = []
            for entry_id in entry_ids:
                entry = source_memory.get_relevant_knowledge(entry_id)
                if entry:
                    entries.extend(entry)

            # Share entries with target agent
            for entry in entries:
                target_memory.record_learning(
                    topic=entry.topic,
                    content=entry.content,
                    source=f"Shared from agent {source_agent_id}"
                )

            return True
        except Exception as e:
            self.logger.error(f"Error sharing knowledge between agents: {e}")
            return False

    def get_shared_knowledge(self, agent_id: str) -> List[KnowledgeEntry]:
        """Get knowledge entries shared with an agent."""
        try:
            if agent_id not in self.agent_memories:
                return []

            agent_memory = self.agent_memories[agent_id]
            shared_entries = []

            # Get learning history from other agents
            for other_id, other_memory in self.agent_memories.items():
                if other_id != agent_id:
                    learning_history = other_memory.get_learning_history()
                    for event in learning_history:
                        if event["source"].startswith("Shared from agent"):
                            shared_entries.append(KnowledgeEntry(
                                id=f"shared_{other_id}_{event['timestamp']}",
                                content=event["content"],
                                topic=event["topic"],
                                tags=["shared", other_id],
                                importance_score=0.5,
                                created_at=datetime.fromisoformat(event["timestamp"]),
                                updated_at=datetime.fromisoformat(event["timestamp"])
                            ))

            return shared_entries
        except Exception as e:
            self.logger.error(f"Error getting shared knowledge for agent {agent_id}: {e}")
            return []

    def get_memory_stats(self) -> MemoryStats:
        """Get statistics about the memory system."""
        total_entries = len(self.repository.index["entries"])
        total_agents = len(self.agent_memories)
        total_conversations = sum(
            len(agent_memory.conversation_contexts)
            for agent_memory in self.agent_memories.values()
        )
        average_entries = total_entries / total_agents if total_agents > 0 else 0

        return MemoryStats(
            total_entries=total_entries,
            total_agents=total_agents,
            total_conversations=total_conversations,
            average_entries_per_agent=average_entries,
            last_sync=self.last_sync
        )

    def get_agent_expertise(self, agent_id: str) -> Dict[str, float]:
        """Get expertise levels for an agent across domains."""
        try:
            if agent_id not in self.agent_memories:
                return {}

            return self.agent_memories[agent_id].get_expertise_summary()
        except Exception as e:
            self.logger.error(f"Error getting expertise for agent {agent_id}: {e}")
            return {}

    def find_expert_agents(self, domain: str, min_expertise: float = 0.7) -> List[str]:
        """Find agents with expertise in a specific domain."""
        expert_agents = []
        for agent_id, agent_memory in self.agent_memories.items():
            expertise = agent_memory.get_expertise_summary()
            if domain in expertise and expertise[domain] >= min_expertise:
                expert_agents.append(agent_id)
        return expert_agents

    def get_conversation_context(self, agent_id: str, conversation_id: str) -> Optional[ConversationContext]:
        """Get the conversation context for a specific agent and conversation."""
        try:
            if agent_id not in self.agent_memories:
                return None

            return self.agent_memories[agent_id].get_conversation_context(conversation_id)
        except Exception as e:
            self.logger.error(f"Error getting conversation context: {e}")
            return None

    def update_conversation_context(self, agent_id: str, conversation_id: str, message: Dict[str, Any]):
        """Update the conversation context for a specific agent and conversation."""
        try:
            if agent_id not in self.agent_memories:
                return False

            self.agent_memories[agent_id].update_conversation_context(conversation_id, message)
            return True
        except Exception as e:
            self.logger.error(f"Error updating conversation context: {e}")
            return False

    def get_similar_conversations(self, agent_id: str, conversation_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Find similar conversations for a specific agent."""
        try:
            if agent_id not in self.agent_memories:
                return []

            return self.agent_memories[agent_id].get_similar_conversations(conversation_id, limit)
        except Exception as e:
            self.logger.error(f"Error finding similar conversations: {e}")
            return []

    def clear_conversation_context(self, agent_id: str, conversation_id: str):
        """Clear the conversation context for a specific agent and conversation."""
        try:
            if agent_id in self.agent_memories:
                self.agent_memories[agent_id].clear_conversation_context(conversation_id)
        except Exception as e:
            self.logger.error(f"Error clearing conversation context: {e}")

    def export_memory_state(self) -> Dict[str, Any]:
        """Export the current state of the memory system."""
        return {
            "stats": self.get_memory_stats().__dict__,
            "agents": {
                agent_id: agent_memory.export_memory()
                for agent_id, agent_memory in self.agent_memories.items()
            }
        } 