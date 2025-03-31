from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json
from enum import Enum

class ContextType(Enum):
    CODE = "code"
    DOCUMENTATION = "documentation"
    IMAGE = "image"
    URL = "url"
    CONVERSATION = "conversation"

class ContextSource(Enum):
    FILE = "file"
    CLIPBOARD = "clipboard"
    URL = "url"
    CONVERSATION = "conversation"

@dataclass
class ContextReference:
    id: str
    type: ContextType
    title: str
    content: str
    source: ContextSource
    source_path: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    priority: int
    is_active: bool

@dataclass
class ContextInfluence:
    reference_id: str
    influence_score: float
    usage_count: int
    last_used: datetime
    relevance_factors: Dict[str, float]

class ContextManagementAPI:
    def __init__(self, project_store):
        self.project_store = project_store

    async def create_context_reference(
        self,
        type: ContextType,
        title: str,
        content: str,
        source: ContextSource,
        source_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ContextReference:
        """Create a new context reference."""
        context = ContextReference(
            id=f"ctx_{datetime.now().timestamp()}",
            type=type,
            title=title,
            content=content,
            source=source,
            source_path=source_path,
            metadata=metadata or {},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            priority=0,
            is_active=True
        )
        
        await self.project_store.save_context_reference(context)
        return context

    async def get_context_reference(self, reference_id: str) -> Optional[ContextReference]:
        """Retrieve a context reference by ID."""
        return await self.project_store.get_context_reference(reference_id)

    async def update_context_reference(
        self,
        reference_id: str,
        updates: Dict[str, Any]
    ) -> Optional[ContextReference]:
        """Update a context reference."""
        context = await self.get_context_reference(reference_id)
        if not context:
            return None

        for key, value in updates.items():
            if hasattr(context, key):
                setattr(context, key, value)
        
        context.updated_at = datetime.now()
        await self.project_store.save_context_reference(context)
        return context

    async def delete_context_reference(self, reference_id: str) -> bool:
        """Delete a context reference."""
        return await self.project_store.delete_context_reference(reference_id)

    async def get_active_contexts(self) -> List[ContextReference]:
        """Get all active context references."""
        return await self.project_store.get_context_references(active_only=True)

    async def update_context_priority(
        self,
        reference_id: str,
        priority: int
    ) -> Optional[ContextReference]:
        """Update the priority of a context reference."""
        return await self.update_context_reference(reference_id, {"priority": priority})

    async def toggle_context_active(
        self,
        reference_id: str,
        is_active: bool
    ) -> Optional[ContextReference]:
        """Toggle the active state of a context reference."""
        return await self.update_context_reference(reference_id, {"is_active": is_active})

    async def record_context_usage(
        self,
        reference_id: str,
        influence_score: float,
        relevance_factors: Optional[Dict[str, float]] = None
    ) -> Optional[ContextInfluence]:
        """Record the usage of a context reference."""
        influence = ContextInfluence(
            reference_id=reference_id,
            influence_score=influence_score,
            usage_count=1,
            last_used=datetime.now(),
            relevance_factors=relevance_factors or {}
        )
        
        await self.project_store.save_context_influence(influence)
        return influence

    async def get_context_influence(
        self,
        reference_id: str
    ) -> Optional[ContextInfluence]:
        """Get the influence metrics for a context reference."""
        return await self.project_store.get_context_influence(reference_id)

    async def get_context_history(
        self,
        reference_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get the usage history for a context reference."""
        return await self.project_store.get_context_history(reference_id, limit)

    async def search_contexts(
        self,
        query: str,
        type: Optional[ContextType] = None,
        source: Optional[ContextSource] = None
    ) -> List[ContextReference]:
        """Search for context references."""
        return await self.project_store.search_context_references(
            query=query,
            type=type,
            source=source
        )

    async def get_context_suggestions(
        self,
        current_context: str,
        limit: int = 5
    ) -> List[ContextReference]:
        """Get suggested context references based on current context."""
        return await self.project_store.get_context_suggestions(
            current_context=current_context,
            limit=limit
        )

    async def analyze_context_relevance(
        self,
        reference_id: str,
        current_context: str
    ) -> Dict[str, float]:
        """Analyze the relevance of a context reference to current context."""
        # Implementation would use NLP/ML to analyze relevance
        return {
            "semantic_similarity": 0.8,
            "temporal_relevance": 0.6,
            "domain_relevance": 0.7
        }

    async def export_context_data(
        self,
        format: str = "json"
    ) -> str:
        """Export all context data in specified format."""
        contexts = await self.project_store.get_all_context_references()
        if format == "json":
            return json.dumps([vars(ctx) for ctx in contexts], default=str)
        # Add support for other formats as needed
        raise ValueError(f"Unsupported export format: {format}")

    async def import_context_data(
        self,
        data: str,
        format: str = "json"
    ) -> List[ContextReference]:
        """Import context data from specified format."""
        if format == "json":
            contexts_data = json.loads(data)
            contexts = []
            for ctx_data in contexts_data:
                ctx_data["created_at"] = datetime.fromisoformat(ctx_data["created_at"])
                ctx_data["updated_at"] = datetime.fromisoformat(ctx_data["updated_at"])
                context = ContextReference(**ctx_data)
                await self.project_store.save_context_reference(context)
                contexts.append(context)
            return contexts
        # Add support for other formats as needed
        raise ValueError(f"Unsupported import format: {format}") 