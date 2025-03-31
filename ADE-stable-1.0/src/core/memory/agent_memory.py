from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from dataclasses import dataclass
from .knowledge_repository import KnowledgeEntry, KnowledgeRepository
from .memory_indexer import MemoryIndexer, SearchResult

@dataclass
class ConversationContext:
    messages: List[Dict[str, Any]]
    current_topic: str
    relevant_entries: List[KnowledgeEntry]
    metadata: Dict[str, Any]

class AgentMemory:
    def __init__(self, agent_id: str, repository: KnowledgeRepository):
        self.agent_id = agent_id
        self.repository = repository
        self.indexer = MemoryIndexer(repository)
        self.logger = logging.getLogger(__name__)
        self.conversation_contexts: Dict[str, ConversationContext] = {}
        self._initialize_memory()

    def _initialize_memory(self):
        """Initialize agent-specific memory structures."""
        self.memory_path = self.repository.storage_path / f"agent_{self.agent_id}_memory.json"
        if self.memory_path.exists():
            self._load_memory()
        else:
            self.memory = {
                "conversations": {},
                "preferences": {},
                "expertise": {},
                "learning_history": []
            }
            self._save_memory()

    def _load_memory(self):
        """Load agent memory from disk."""
        try:
            with open(self.memory_path, 'r') as f:
                self.memory = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading agent memory: {e}")
            self.memory = {
                "conversations": {},
                "preferences": {},
                "expertise": {},
                "learning_history": []
            }

    def _save_memory(self):
        """Save agent memory to disk."""
        try:
            with open(self.memory_path, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving agent memory: {e}")

    def update_conversation_context(self, conversation_id: str, message: Dict[str, Any]):
        """Update the conversation context with a new message."""
        if conversation_id not in self.conversation_contexts:
            self.conversation_contexts[conversation_id] = ConversationContext(
                messages=[],
                current_topic="",
                relevant_entries=[],
                metadata={}
            )

        context = self.conversation_contexts[conversation_id]
        context.messages.append(message)

        # Update current topic based on message content
        if "content" in message:
            topic = self._extract_topic(message["content"])
            if topic:
                context.current_topic = topic

        # Find relevant knowledge entries
        relevant_entries = self._find_relevant_entries(message)
        context.relevant_entries = relevant_entries

        # Update metadata
        context.metadata.update({
            "last_updated": datetime.now().isoformat(),
            "message_count": len(context.messages)
        })

    def _extract_topic(self, content: str) -> Optional[str]:
        """Extract the main topic from message content."""
        # TODO: Implement topic extraction using NLP
        # For now, return a simple topic based on keywords
        return None

    def _find_relevant_entries(self, message: Dict[str, Any]) -> List[KnowledgeEntry]:
        """Find knowledge entries relevant to the current message."""
        if "content" not in message:
            return []

        # Perform semantic search
        results = self.indexer.semantic_search(message["content"], limit=5)
        return [result.entry for result in results]

    def get_conversation_context(self, conversation_id: str) -> Optional[ConversationContext]:
        """Get the current context for a conversation."""
        return self.conversation_contexts.get(conversation_id)

    def update_preferences(self, preferences: Dict[str, Any]):
        """Update agent preferences."""
        self.memory["preferences"].update(preferences)
        self._save_memory()

    def update_expertise(self, domain: str, level: float, evidence: List[str]):
        """Update agent expertise in a specific domain."""
        self.memory["expertise"][domain] = {
            "level": level,
            "evidence": evidence,
            "last_updated": datetime.now().isoformat()
        }
        self._save_memory()

    def record_learning(self, topic: str, content: str, source: str):
        """Record a learning event."""
        learning_event = {
            "topic": topic,
            "content": content,
            "source": source,
            "timestamp": datetime.now().isoformat()
        }
        self.memory["learning_history"].append(learning_event)
        self._save_memory()

    def get_relevant_knowledge(self, query: str, limit: int = 5) -> List[KnowledgeEntry]:
        """Get knowledge entries relevant to a query."""
        results = self.indexer.semantic_search(query, limit=limit)
        return [result.entry for result in results]

    def get_similar_conversations(self, conversation_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Find similar past conversations."""
        if conversation_id not in self.conversation_contexts:
            return []

        current_context = self.conversation_contexts[conversation_id]
        similar_conversations = []

        for past_id, past_context in self.conversation_contexts.items():
            if past_id == conversation_id:
                continue

            # Calculate similarity based on topics and relevant entries
            topic_similarity = 1.0 if current_context.current_topic == past_context.current_topic else 0.0
            entry_overlap = len(set(e.id for e in current_context.relevant_entries) &
                              set(e.id for e in past_context.relevant_entries))
            
            similarity_score = topic_similarity * 0.6 + (entry_overlap / max(len(current_context.relevant_entries),
                                                                         len(past_context.relevant_entries))) * 0.4

            if similarity_score > 0.3:  # Threshold for relevance
                similar_conversations.append({
                    "id": past_id,
                    "similarity": similarity_score,
                    "context": past_context
                })

        # Sort by similarity score and return top results
        similar_conversations.sort(key=lambda x: x["similarity"], reverse=True)
        return similar_conversations[:limit]

    def get_expertise_summary(self) -> Dict[str, float]:
        """Get a summary of agent expertise across domains."""
        return {domain: data["level"] for domain, data in self.memory["expertise"].items()}

    def get_learning_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get recent learning history."""
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        return [
            event for event in self.memory["learning_history"]
            if datetime.fromisoformat(event["timestamp"]).timestamp() > cutoff_date
        ]

    def clear_conversation_context(self, conversation_id: str):
        """Clear the context for a specific conversation."""
        if conversation_id in self.conversation_contexts:
            del self.conversation_contexts[conversation_id]

    def clear_all_contexts(self):
        """Clear all conversation contexts."""
        self.conversation_contexts.clear()

    def export_memory(self) -> Dict[str, Any]:
        """Export agent memory for backup or transfer."""
        return {
            "agent_id": self.agent_id,
            "memory": self.memory,
            "conversation_contexts": {
                conv_id: {
                    "messages": context.messages,
                    "current_topic": context.current_topic,
                    "relevant_entries": [entry.id for entry in context.relevant_entries],
                    "metadata": context.metadata
                }
                for conv_id, context in self.conversation_contexts.items()
            }
        } 