import os
import time
from typing import Dict, List, Callable, Optional
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .models import FileChange
from .utils import get_file_info

class FileChangeHandler(FileSystemEventHandler):
    """Handler for file system events."""
    
    def __init__(self, callback: Callable[[FileChange], None]):
        self.callback = callback
        self.last_modified: Dict[str, float] = {}
        
    def on_created(self, event):
        if not event.is_directory:
            file_info = get_file_info(event.src_path)
            change = FileChange(
                path=event.src_path,
                change_type="created",
                timestamp=datetime.now(),
                new_content=None,  # Will be populated by the callback
                metadata={"event": "created"}
            )
            self.callback(change)
            
    def on_modified(self, event):
        if not event.is_directory:
            current_time = time.time()
            last_modified = self.last_modified.get(event.src_path, 0)
            
            # Debounce rapid modifications
            if current_time - last_modified < 1.0:
                return
                
            self.last_modified[event.src_path] = current_time
            file_info = get_file_info(event.src_path)
            
            change = FileChange(
                path=event.src_path,
                change_type="modified",
                timestamp=datetime.now(),
                new_content=None,  # Will be populated by the callback
                metadata={"event": "modified"}
            )
            self.callback(change)
            
    def on_deleted(self, event):
        if not event.is_directory:
            change = FileChange(
                path=event.src_path,
                change_type="deleted",
                timestamp=datetime.now(),
                old_content=None,  # Will be populated by the callback
                metadata={"event": "deleted"}
            )
            self.callback(change)

class FileSystemWatcher:
    """Watcher for monitoring file system changes."""
    
    def __init__(self):
        self.observer = Observer()
        self.handlers: Dict[str, FileChangeHandler] = {}
        self.watched_paths: List[str] = []
        
    def start(self):
        """Start the file system watcher."""
        if not self.observer.is_alive():
            self.observer.start()
            
    def stop(self):
        """Stop the file system watcher."""
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            
    def watch(self, path: str, callback: Callable[[FileChange], None], recursive: bool = True):
        """Watch a directory for changes.
        
        Args:
            path: Path to watch
            callback: Function to call when changes occur
            recursive: Whether to watch subdirectories
        """
        if path in self.watched_paths:
            return
            
        handler = FileChangeHandler(callback)
        self.handlers[path] = handler
        self.watched_paths.append(path)
        
        self.observer.schedule(
            handler,
            path,
            recursive=recursive
        )
        
    def unwatch(self, path: str):
        """Stop watching a directory.
        
        Args:
            path: Path to stop watching
        """
        if path in self.watched_paths:
            self.observer.unschedule(self.handlers[path])
            del self.handlers[path]
            self.watched_paths.remove(path)
            
    def is_watching(self, path: str) -> bool:
        """Check if a path is being watched.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path is being watched
        """
        return path in self.watched_paths
        
    def get_watched_paths(self) -> List[str]:
        """Get list of watched paths.
        
        Returns:
            List of watched paths
        """
        return self.watched_paths.copy()
        
    def clear(self):
        """Clear all watched paths."""
        for path in self.watched_paths.copy():
            self.unwatch(path)
            
    def __enter__(self):
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop() 