from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json
from enum import Enum

class MemoryAccessLevel(Enum):
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    FULL_ACCESS = "full_access"

class EventType(Enum):
    CODE_CHANGE = "code_change"
    DOCUMENTATION_UPDATE = "documentation_update"
    CONFIGURATION_CHANGE = "configuration_change"
    DEPENDENCY_UPDATE = "dependency_update"
    SYSTEM_EVENT = "system_event"

@dataclass
class AgentMemory:
    id: str
    agent_id: str
    access_level: MemoryAccessLevel
    memory_data: Dict[str, Any]
    last_sync: datetime
    sync_frequency: int  # in seconds
    is_active: bool

@dataclass
class MemoryEvent:
    id: str
    type: EventType
    timestamp: datetime
    agent_id: str
    details: Dict[str, Any]
    affected_files: List[str]
    priority: int

class AgentMemoryAPI:
    def __init__(self, project_store):
        self.project_store = project_store

    async def create_agent_memory(
        self,
        agent_id: str,
        access_level: MemoryAccessLevel,
        sync_frequency: int = 300  # 5 minutes default
    ) -> AgentMemory:
        """Create a new agent memory instance."""
        memory = AgentMemory(
            id=f"mem_{datetime.now().timestamp()}",
            agent_id=agent_id,
            access_level=access_level,
            memory_data={},
            last_sync=datetime.now(),
            sync_frequency=sync_frequency,
            is_active=True
        )
        
        await self.project_store.save_agent_memory(memory)
        return memory

    async def get_agent_memory(self, agent_id: str) -> Optional[AgentMemory]:
        """Retrieve agent memory by agent ID."""
        return await self.project_store.get_agent_memory(agent_id)

    async def update_agent_memory(
        self,
        agent_id: str,
        updates: Dict[str, Any]
    ) -> Optional[AgentMemory]:
        """Update agent memory data."""
        memory = await self.get_agent_memory(agent_id)
        if not memory:
            return None

        memory.memory_data.update(updates)
        memory.last_sync = datetime.now()
        await self.project_store.save_agent_memory(memory)
        return memory

    async def record_memory_event(
        self,
        agent_id: str,
        event_type: EventType,
        details: Dict[str, Any],
        affected_files: List[str],
        priority: int = 1
    ) -> MemoryEvent:
        """Record a new memory event."""
        event = MemoryEvent(
            id=f"evt_{datetime.now().timestamp()}",
            type=event_type,
            timestamp=datetime.now(),
            agent_id=agent_id,
            details=details,
            affected_files=affected_files,
            priority=priority
        )
        
        await self.project_store.save_memory_event(event)
        return event

    async def get_agent_events(
        self,
        agent_id: str,
        limit: int = 50,
        event_type: Optional[EventType] = None
    ) -> List[MemoryEvent]:
        """Get events for a specific agent."""
        return await self.project_store.get_agent_events(
            agent_id=agent_id,
            limit=limit,
            event_type=event_type
        )

    async def get_relevant_events(
        self,
        agent_id: str,
        file_path: str,
        time_range: Optional[Dict[str, datetime]] = None
    ) -> List[MemoryEvent]:
        """Get events relevant to a specific file."""
        return await self.project_store.get_relevant_events(
            agent_id=agent_id,
            file_path=file_path,
            time_range=time_range
        )

    async def sync_agent_memory(
        self,
        agent_id: str,
        force: bool = False
    ) -> Optional[AgentMemory]:
        """Synchronize agent memory with current state."""
        memory = await self.get_agent_memory(agent_id)
        if not memory:
            return None

        if not force and (datetime.now() - memory.last_sync).total_seconds() < memory.sync_frequency:
            return memory

        # Get recent events
        recent_events = await self.get_agent_events(agent_id, limit=100)
        
        # Update memory based on events
        for event in recent_events:
            if event.type == EventType.CODE_CHANGE:
                await self._handle_code_change(memory, event)
            elif event.type == EventType.DOCUMENTATION_UPDATE:
                await self._handle_doc_update(memory, event)
            # Handle other event types...

        memory.last_sync = datetime.now()
        await self.project_store.save_agent_memory(memory)
        return memory

    async def _handle_code_change(
        self,
        memory: AgentMemory,
        event: MemoryEvent
    ):
        """Handle code change events."""
        if memory.access_level == MemoryAccessLevel.READ_ONLY:
            return

        # Update memory with code changes
        for file_path in event.affected_files:
            if file_path in memory.memory_data.get("code_files", {}):
                # Update code file data
                memory.memory_data["code_files"][file_path].update({
                    "last_modified": event.timestamp,
                    "change_details": event.details
                })

    async def _handle_doc_update(
        self,
        memory: AgentMemory,
        event: MemoryEvent
    ):
        """Handle documentation update events."""
        if memory.access_level == MemoryAccessLevel.READ_ONLY:
            return

        # Update memory with documentation changes
        for file_path in event.affected_files:
            if file_path in memory.memory_data.get("documentation", {}):
                memory.memory_data["documentation"][file_path].update({
                    "last_modified": event.timestamp,
                    "update_details": event.details
                })

    async def get_memory_analytics(
        self,
        agent_id: str,
        time_range: Optional[Dict[str, datetime]] = None
    ) -> Dict[str, Any]:
        """Get analytics about agent memory usage."""
        events = await self.get_agent_events(agent_id, limit=1000)
        
        if time_range:
            events = [
                e for e in events
                if time_range["start"] <= e.timestamp <= time_range["end"]
            ]

        # Calculate analytics
        event_counts = {}
        for event in events:
            event_counts[event.type.value] = event_counts.get(event.type.value, 0) + 1

        return {
            "total_events": len(events),
            "event_counts": event_counts,
            "affected_files": len(set(
                file for event in events
                for file in event.affected_files
            )),
            "average_priority": sum(e.priority for e in events) / len(events) if events else 0
        }

    async def export_memory_data(
        self,
        agent_id: str,
        format: str = "json"
    ) -> str:
        """Export agent memory data."""
        memory = await self.get_agent_memory(agent_id)
        if not memory:
            return "{}"

        if format == "json":
            return json.dumps(vars(memory), default=str)
        raise ValueError(f"Unsupported export format: {format}")

    async def import_memory_data(
        self,
        agent_id: str,
        data: str,
        format: str = "json"
    ) -> Optional[AgentMemory]:
        """Import agent memory data."""
        if format == "json":
            memory_data = json.loads(data)
            memory_data["agent_id"] = agent_id
            memory_data["last_sync"] = datetime.fromisoformat(memory_data["last_sync"])
            memory = AgentMemory(**memory_data)
            await self.project_store.save_agent_memory(memory)
            return memory
        raise ValueError(f"Unsupported import format: {format}") 