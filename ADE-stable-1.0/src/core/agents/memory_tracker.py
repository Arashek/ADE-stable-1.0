from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import threading
import weakref
import gc

@dataclass
class MemoryAccess:
    timestamp: datetime
    operation: str  # 'read', 'write', 'execute'
    resource: str
    agent_id: str
    context: Dict[str, Any]
    size: Optional[int] = None
    duration: Optional[float] = None

@dataclass
class MemorySnapshot:
    timestamp: datetime
    total_memory: int
    used_memory: int
    free_memory: int
    objects: Dict[str, int]
    references: Dict[str, List[str]]

class MemoryTracker:
    def __init__(self):
        self.access_log: List[MemoryAccess] = []
        self.snapshots: List[MemorySnapshot] = []
        self._lock = threading.Lock()
        self._weak_refs: Dict[str, weakref.ref] = {}
        self._gc_callback = None
        
    def track_access(self, operation: str, resource: str, agent_id: str,
                    context: Dict[str, Any], size: Optional[int] = None,
                    duration: Optional[float] = None) -> None:
        """Track a memory access operation."""
        access = MemoryAccess(
            timestamp=datetime.now(),
            operation=operation,
            resource=resource,
            agent_id=agent_id,
            context=context,
            size=size,
            duration=duration
        )
        
        with self._lock:
            self.access_log.append(access)
            
    def take_snapshot(self) -> MemorySnapshot:
        """Take a snapshot of current memory state."""
        gc.collect()  # Force garbage collection
        
        # Get memory usage
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        # Get object counts
        objects = {}
        for obj in gc.get_objects():
            obj_type = type(obj).__name__
            objects[obj_type] = objects.get(obj_type, 0) + 1
            
        # Get reference graph
        references = {}
        for obj in gc.get_objects():
            obj_id = str(id(obj))
            refs = []
            for ref in gc.get_referrers(obj):
                ref_id = str(id(ref))
                refs.append(ref_id)
            references[obj_id] = refs
            
        snapshot = MemorySnapshot(
            timestamp=datetime.now(),
            total_memory=psutil.virtual_memory().total,
            used_memory=memory_info.rss,
            free_memory=psutil.virtual_memory().available,
            objects=objects,
            references=references
        )
        
        with self._lock:
            self.snapshots.append(snapshot)
            
        return snapshot
        
    def track_object(self, obj: Any, name: str) -> None:
        """Track a specific object's lifecycle."""
        def callback(ref):
            with self._lock:
                if name in self._weak_refs:
                    del self._weak_refs[name]
                    
        self._weak_refs[name] = weakref.ref(obj, callback)
        
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics."""
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss,
            'vms': memory_info.vms,
            'percent': process.memory_percent(),
            'threads': process.num_threads(),
            'cpu_percent': process.cpu_percent()
        }
        
    def get_access_history(self, agent_id: Optional[str] = None,
                          operation: Optional[str] = None,
                          resource: Optional[str] = None) -> List[MemoryAccess]:
        """Get filtered access history."""
        with self._lock:
            filtered = self.access_log
            
            if agent_id:
                filtered = [acc for acc in filtered if acc.agent_id == agent_id]
            if operation:
                filtered = [acc for acc in filtered if acc.operation == operation]
            if resource:
                filtered = [acc for acc in filtered if acc.resource == resource]
                
            return filtered
            
    def get_memory_trend(self, window: int = 60) -> Dict[str, List[Any]]:
        """Get memory usage trend over time."""
        with self._lock:
            if not self.snapshots:
                return {}
                
            # Get snapshots within window
            cutoff = datetime.now().timestamp() - window
            recent_snapshots = [
                snap for snap in self.snapshots
                if snap.timestamp.timestamp() > cutoff
            ]
            
            return {
                'timestamps': [snap.timestamp for snap in recent_snapshots],
                'used_memory': [snap.used_memory for snap in recent_snapshots],
                'free_memory': [snap.free_memory for snap in recent_snapshots],
                'object_counts': [
                    sum(snap.objects.values()) for snap in recent_snapshots
                ]
            }
            
    def analyze_memory_patterns(self) -> Dict[str, Any]:
        """Analyze memory access patterns."""
        with self._lock:
            patterns = {
                'frequent_operations': {},
                'large_allocations': [],
                'memory_leaks': [],
                'resource_usage': {}
            }
            
            # Count operation frequencies
            for access in self.access_log:
                op = access.operation
                patterns['frequent_operations'][op] = patterns['frequent_operations'].get(op, 0) + 1
                
                # Track large allocations
                if access.size and access.size > 1024 * 1024:  # 1MB
                    patterns['large_allocations'].append({
                        'timestamp': access.timestamp,
                        'size': access.size,
                        'resource': access.resource,
                        'agent_id': access.agent_id
                    })
                    
                # Track resource usage
                if access.resource not in patterns['resource_usage']:
                    patterns['resource_usage'][access.resource] = {
                        'reads': 0,
                        'writes': 0,
                        'executes': 0,
                        'total_size': 0
                    }
                    
                patterns['resource_usage'][access.resource][access.operation + 's'] += 1
                if access.size:
                    patterns['resource_usage'][access.resource]['total_size'] += access.size
                    
            # Detect potential memory leaks
            if len(self.snapshots) > 1:
                for i in range(1, len(self.snapshots)):
                    prev = self.snapshots[i-1]
                    curr = self.snapshots[i]
                    
                    # Check for continuous memory growth
                    if (curr.used_memory > prev.used_memory * 1.1 and  # 10% growth
                        curr.timestamp.timestamp() - prev.timestamp.timestamp() > 300):  # 5 minutes
                        patterns['memory_leaks'].append({
                            'start_time': prev.timestamp,
                            'end_time': curr.timestamp,
                            'growth': curr.used_memory - prev.used_memory
                        })
                        
            return patterns
            
    def export_data(self, file_path: str) -> None:
        """Export memory tracking data to file."""
        with self._lock:
            data = {
                'access_log': [
                    {
                        'timestamp': acc.timestamp.isoformat(),
                        'operation': acc.operation,
                        'resource': acc.resource,
                        'agent_id': acc.agent_id,
                        'context': acc.context,
                        'size': acc.size,
                        'duration': acc.duration
                    }
                    for acc in self.access_log
                ],
                'snapshots': [
                    {
                        'timestamp': snap.timestamp.isoformat(),
                        'total_memory': snap.total_memory,
                        'used_memory': snap.used_memory,
                        'free_memory': snap.free_memory,
                        'objects': snap.objects,
                        'references': snap.references
                    }
                    for snap in self.snapshots
                ]
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
    def import_data(self, file_path: str) -> None:
        """Import memory tracking data from file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        with self._lock:
            self.access_log = [
                MemoryAccess(
                    timestamp=datetime.fromisoformat(acc['timestamp']),
                    operation=acc['operation'],
                    resource=acc['resource'],
                    agent_id=acc['agent_id'],
                    context=acc['context'],
                    size=acc.get('size'),
                    duration=acc.get('duration')
                )
                for acc in data['access_log']
            ]
            
            self.snapshots = [
                MemorySnapshot(
                    timestamp=datetime.fromisoformat(snap['timestamp']),
                    total_memory=snap['total_memory'],
                    used_memory=snap['used_memory'],
                    free_memory=snap['free_memory'],
                    objects=snap['objects'],
                    references=snap['references']
                )
                for snap in data['snapshots']
            ] 