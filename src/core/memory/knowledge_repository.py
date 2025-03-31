from typing import Dict, List, Optional, Any
import json
import os
from datetime import datetime
import hashlib
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

@dataclass
class KnowledgeEntry:
    id: str
    content: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    version: int
    importance_score: float
    tags: List[str]
    references: List[str]
    embedding: Optional[List[float]] = None

class KnowledgeRepository:
    def __init__(self, storage_path: str = "data/knowledge"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self._initialize_index()

    def _initialize_index(self):
        """Initialize or load the knowledge index."""
        self.index_path = self.storage_path / "index.json"
        if self.index_path.exists():
            with open(self.index_path, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {
                "entries": {},
                "tags": {},
                "versions": {},
                "last_updated": datetime.now().isoformat()
            }
            self._save_index()

    def _save_index(self):
        """Save the current index to disk."""
        with open(self.index_path, 'w') as f:
            json.dump(self.index, f, indent=2)

    def _generate_id(self, content: str) -> str:
        """Generate a unique ID for a knowledge entry."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def add_entry(self, content: str, metadata: Dict[str, Any], tags: List[str] = None) -> str:
        """Add a new knowledge entry to the repository."""
        entry_id = self._generate_id(content)
        now = datetime.now()
        
        entry = KnowledgeEntry(
            id=entry_id,
            content=content,
            metadata=metadata,
            created_at=now,
            updated_at=now,
            version=1,
            importance_score=1.0,
            tags=tags or [],
            references=[]
        )

        # Save entry to disk
        entry_path = self.storage_path / f"{entry_id}.json"
        with open(entry_path, 'w') as f:
            json.dump(asdict(entry), f, indent=2, default=str)

        # Update index
        self.index["entries"][entry_id] = {
            "content_hash": entry_id,
            "created_at": entry.created_at.isoformat(),
            "updated_at": entry.updated_at.isoformat(),
            "version": entry.version,
            "importance_score": entry.importance_score,
            "tags": entry.tags
        }

        # Update tag index
        for tag in entry.tags:
            if tag not in self.index["tags"]:
                self.index["tags"][tag] = []
            self.index["tags"][tag].append(entry_id)

        self._save_index()
        return entry_id

    def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Retrieve a knowledge entry by ID."""
        if entry_id not in self.index["entries"]:
            return None

        entry_path = self.storage_path / f"{entry_id}.json"
        if not entry_path.exists():
            return None

        with open(entry_path, 'r') as f:
            data = json.load(f)
            return KnowledgeEntry(**data)

    def update_entry(self, entry_id: str, content: Optional[str] = None, 
                    metadata: Optional[Dict[str, Any]] = None,
                    tags: Optional[List[str]] = None) -> bool:
        """Update an existing knowledge entry."""
        entry = self.get_entry(entry_id)
        if not entry:
            return False

        if content is not None:
            entry.content = content
        if metadata is not None:
            entry.metadata.update(metadata)
        if tags is not None:
            # Remove old tags from index
            for tag in entry.tags:
                if tag in self.index["tags"]:
                    self.index["tags"][tag].remove(entry_id)
            entry.tags = tags
            # Add new tags to index
            for tag in tags:
                if tag not in self.index["tags"]:
                    self.index["tags"][tag] = []
                self.index["tags"][tag].append(entry_id)

        entry.updated_at = datetime.now()
        entry.version += 1

        # Save updated entry
        entry_path = self.storage_path / f"{entry_id}.json"
        with open(entry_path, 'w') as f:
            json.dump(asdict(entry), f, indent=2, default=str)

        # Update index
        self.index["entries"][entry_id].update({
            "updated_at": entry.updated_at.isoformat(),
            "version": entry.version,
            "tags": entry.tags
        })

        self._save_index()
        return True

    def delete_entry(self, entry_id: str) -> bool:
        """Delete a knowledge entry."""
        if entry_id not in self.index["entries"]:
            return False

        # Remove tags from index
        entry = self.get_entry(entry_id)
        if entry:
            for tag in entry.tags:
                if tag in self.index["tags"]:
                    self.index["tags"][tag].remove(entry_id)

        # Delete entry file
        entry_path = self.storage_path / f"{entry_id}.json"
        if entry_path.exists():
            entry_path.unlink()

        # Remove from index
        del self.index["entries"][entry_id]
        self._save_index()
        return True

    def search_by_tags(self, tags: List[str]) -> List[KnowledgeEntry]:
        """Search for entries by tags."""
        matching_ids = set()
        for tag in tags:
            if tag in self.index["tags"]:
                matching_ids.update(self.index["tags"][tag])

        return [self.get_entry(entry_id) for entry_id in matching_ids]

    def search_by_content(self, query: str) -> List[KnowledgeEntry]:
        """Search for entries by content (simple text matching)."""
        results = []
        for entry_id in self.index["entries"]:
            entry = self.get_entry(entry_id)
            if entry and query.lower() in entry.content.lower():
                results.append(entry)
        return results

    def get_entries_by_importance(self, limit: int = 10) -> List[KnowledgeEntry]:
        """Get entries sorted by importance score."""
        sorted_ids = sorted(
            self.index["entries"].items(),
            key=lambda x: x[1]["importance_score"],
            reverse=True
        )[:limit]
        return [self.get_entry(entry_id) for entry_id, _ in sorted_ids]

    def update_importance_score(self, entry_id: str, score: float) -> bool:
        """Update the importance score of an entry."""
        if entry_id not in self.index["entries"]:
            return False

        entry = self.get_entry(entry_id)
        if not entry:
            return False

        entry.importance_score = score
        entry.updated_at = datetime.now()

        # Save updated entry
        entry_path = self.storage_path / f"{entry_id}.json"
        with open(entry_path, 'w') as f:
            json.dump(asdict(entry), f, indent=2, default=str)

        # Update index
        self.index["entries"][entry_id]["importance_score"] = score
        self.index["entries"][entry_id]["updated_at"] = entry.updated_at.isoformat()
        self._save_index()
        return True

    def get_version_history(self, entry_id: str) -> List[Dict[str, Any]]:
        """Get the version history of an entry."""
        if entry_id not in self.index["entries"]:
            return []

        entry = self.get_entry(entry_id)
        if not entry:
            return []

        history = []
        for version in range(1, entry.version + 1):
            version_path = self.storage_path / f"{entry_id}_v{version}.json"
            if version_path.exists():
                with open(version_path, 'r') as f:
                    history.append(json.load(f))
        return history

    def export_knowledge(self, format: str = "json") -> str:
        """Export all knowledge entries in the specified format."""
        if format == "json":
            export_data = {
                "entries": {},
                "index": self.index,
                "exported_at": datetime.now().isoformat()
            }
            for entry_id in self.index["entries"]:
                entry = self.get_entry(entry_id)
                if entry:
                    export_data["entries"][entry_id] = asdict(entry)
            return json.dumps(export_data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def import_knowledge(self, data: str, format: str = "json") -> bool:
        """Import knowledge entries from the specified format."""
        if format == "json":
            try:
                import_data = json.loads(data)
                for entry_id, entry_data in import_data["entries"].items():
                    entry_path = self.storage_path / f"{entry_id}.json"
                    with open(entry_path, 'w') as f:
                        json.dump(entry_data, f, indent=2)
                self.index = import_data["index"]
                self._save_index()
                return True
            except Exception as e:
                self.logger.error(f"Error importing knowledge: {e}")
                return False
        else:
            raise ValueError(f"Unsupported import format: {format}") 