"""
Agent Cache Service

This module provides a caching mechanism for agent responses to optimize
communication between agents and reduce redundant computations.
"""

import os
import sys
import json
import logging
import hashlib
import time
from typing import Dict, Any, Optional, List, Tuple, Union
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Import error logging system
try:
    from scripts.basic_error_logging import log_error, ErrorCategory, ErrorSeverity
    error_logging_available = True
except ImportError:
    error_logging_available = False
    # Define fallback error categories and severities
    class ErrorCategory:
        CACHE = "CACHE"
        SYSTEM = "SYSTEM"
    
    class ErrorSeverity:
        ERROR = "ERROR"
        WARNING = "WARNING"
        INFO = "INFO"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("agent_cache")

# Constants
CACHE_DIR = os.path.join(project_root, "cache", "agent_responses")
MAX_CACHE_SIZE_MB = 100  # Maximum cache size in MB
DEFAULT_TTL = 60 * 60  # Default time-to-live for cache entries (1 hour)

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

class AgentCacheService:
    """
    The AgentCacheService provides caching functionality for agent responses
    to reduce redundant computations and improve response times.
    """
    
    def __init__(self, ttl: int = DEFAULT_TTL, max_size_mb: int = MAX_CACHE_SIZE_MB):
        """
        Initialize the agent cache service
        
        Args:
            ttl: Time-to-live for cache entries in seconds
            max_size_mb: Maximum cache size in megabytes
        """
        self.ttl = ttl
        self.max_size_mb = max_size_mb
        self.memory_cache = {}  # In-memory cache for frequently accessed items
        self.stats = {
            "hits": 0,
            "misses": 0,
            "total_saved_time": 0.0,  # in seconds
            "last_cleanup": datetime.now()
        }
        logger.info(f"Agent Cache Service initialized with TTL: {ttl}s, Max size: {max_size_mb}MB")
        
        # Perform initial cache cleanup
        self._cleanup_expired()
    
    def _generate_key(self, agent_type: str, prompt: str, context: Dict[str, Any]) -> str:
        """
        Generate a unique cache key based on agent type, prompt, and context
        
        Args:
            agent_type: Type of agent (e.g., 'architecture', 'validation')
            prompt: The prompt sent to the agent
            context: Additional context for the agent
            
        Returns:
            str: Unique cache key
        """
        # Create a deterministic representation of the context
        sorted_context = json.dumps(context, sort_keys=True)
        
        # Combine all inputs and hash them
        combined = f"{agent_type}:{prompt}:{sorted_context}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _get_cache_file_path(self, key: str) -> str:
        """
        Get the file path for a cache entry
        
        Args:
            key: Cache entry key
            
        Returns:
            str: Path to the cache file
        """
        return os.path.join(CACHE_DIR, f"{key}.json")
    
    def _is_expired(self, timestamp: float) -> bool:
        """
        Check if a cache entry has expired
        
        Args:
            timestamp: Timestamp when the cache entry was created
            
        Returns:
            bool: True if expired, False otherwise
        """
        return (time.time() - timestamp) > self.ttl
    
    async def get(self, agent_type: str, prompt: str, context: Dict[str, Any] = None) -> Tuple[bool, Any, float]:
        """
        Get a response from the cache
        
        Args:
            agent_type: Type of agent
            prompt: The prompt sent to the agent
            context: Additional context for the agent
            
        Returns:
            Tuple[bool, Any, float]: (cache_hit, response, processing_time)
        """
        context = context or {}
        key = self._generate_key(agent_type, prompt, context)
        
        # Check memory cache first
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if not self._is_expired(entry["timestamp"]):
                self.stats["hits"] += 1
                logger.info(f"Cache hit (memory) for agent: {agent_type}")
                return True, entry["response"], entry["processing_time"]
        
        # Check file-based cache
        cache_file = self._get_cache_file_path(key)
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    entry = json.load(f)
                
                if not self._is_expired(entry["timestamp"]):
                    # Add to memory cache for faster access next time
                    self.memory_cache[key] = entry
                    self.stats["hits"] += 1
                    logger.info(f"Cache hit (file) for agent: {agent_type}")
                    return True, entry["response"], entry["processing_time"]
                else:
                    # Remove expired entry
                    os.remove(cache_file)
            except Exception as e:
                if error_logging_available:
                    log_error(
                        error=e,
                        category=ErrorCategory.CACHE,
                        severity=ErrorSeverity.WARNING,
                        component="agent_cache",
                        context={"key": key, "agent_type": agent_type}
                    )
                logger.warning(f"Error reading cache entry: {str(e)}")
        
        self.stats["misses"] += 1
        logger.info(f"Cache miss for agent: {agent_type}")
        return False, None, 0.0
    
    async def set(self, agent_type: str, prompt: str, 
                 response: Any, processing_time: float, 
                 context: Dict[str, Any] = None) -> None:
        """
        Store a response in the cache
        
        Args:
            agent_type: Type of agent
            prompt: The prompt sent to the agent
            response: Agent's response
            processing_time: Time taken to process the request
            context: Additional context for the agent
        """
        context = context or {}
        key = self._generate_key(agent_type, prompt, context)
        
        entry = {
            "timestamp": time.time(),
            "agent_type": agent_type,
            "prompt": prompt,
            "context": context,
            "response": response,
            "processing_time": processing_time
        }
        
        try:
            # Store in memory cache
            self.memory_cache[key] = entry
            
            # Store in file-based cache
            cache_file = self._get_cache_file_path(key)
            with open(cache_file, 'w') as f:
                json.dump(entry, f)
            
            logger.info(f"Cached response for agent: {agent_type}, processing time: {processing_time:.2f}s")
            
            # Update stats
            self.stats["total_saved_time"] += processing_time
            
            # Check if we need to run cleanup
            if (datetime.now() - self.stats["last_cleanup"]) > timedelta(hours=1):
                await self._cleanup()
                
        except Exception as e:
            if error_logging_available:
                log_error(
                    error=e,
                    category=ErrorCategory.CACHE,
                    severity=ErrorSeverity.ERROR,
                    component="agent_cache",
                    context={"key": key, "agent_type": agent_type}
                )
            logger.error(f"Error caching response: {str(e)}")
    
    async def invalidate(self, agent_type: str = None) -> None:
        """
        Invalidate cache entries for a specific agent type
        
        Args:
            agent_type: Type of agent, or None to invalidate all
        """
        try:
            # Clear from memory cache
            if agent_type:
                keys_to_remove = [k for k, v in self.memory_cache.items() if v["agent_type"] == agent_type]
                for key in keys_to_remove:
                    self.memory_cache.pop(key, None)
            else:
                self.memory_cache.clear()
            
            # Clear from file-based cache
            for file_name in os.listdir(CACHE_DIR):
                if file_name.endswith(".json"):
                    file_path = os.path.join(CACHE_DIR, file_name)
                    if agent_type:
                        try:
                            with open(file_path, 'r') as f:
                                entry = json.load(f)
                            if entry["agent_type"] == agent_type:
                                os.remove(file_path)
                        except:
                            # If we can't read the file, better to remove it
                            os.remove(file_path)
                    else:
                        os.remove(file_path)
            
            logger.info(f"Invalidated cache entries for agent: {agent_type or 'ALL'}")
        except Exception as e:
            if error_logging_available:
                log_error(
                    error=e,
                    category=ErrorCategory.CACHE,
                    severity=ErrorSeverity.ERROR,
                    component="agent_cache",
                    context={"agent_type": agent_type}
                )
            logger.error(f"Error invalidating cache: {str(e)}")
    
    async def _cleanup(self) -> None:
        """
        Perform cache cleanup operations:
        - Remove expired entries
        - Enforce maximum cache size
        """
        logger.info("Starting cache cleanup")
        self.stats["last_cleanup"] = datetime.now()
        
        # Clean expired entries
        await self._cleanup_expired()
        
        # Enforce maximum cache size
        await self._enforce_max_size()
        
        logger.info("Cache cleanup completed")
    
    async def _cleanup_expired(self) -> None:
        """
        Remove expired cache entries
        """
        try:
            # Clean from memory cache
            keys_to_remove = [k for k, v in self.memory_cache.items() if self._is_expired(v["timestamp"])]
            for key in keys_to_remove:
                self.memory_cache.pop(key, None)
            
            # Clean from file-based cache
            current_time = time.time()
            for file_name in os.listdir(CACHE_DIR):
                if file_name.endswith(".json"):
                    file_path = os.path.join(CACHE_DIR, file_name)
                    try:
                        with open(file_path, 'r') as f:
                            entry = json.load(f)
                        if self._is_expired(entry["timestamp"]):
                            os.remove(file_path)
                    except:
                        # If we can't read the file, better to remove it
                        os.remove(file_path)
            
            logger.info(f"Removed {len(keys_to_remove)} expired entries from memory cache")
        except Exception as e:
            if error_logging_available:
                log_error(
                    error=e,
                    category=ErrorCategory.CACHE,
                    severity=ErrorSeverity.WARNING,
                    component="agent_cache",
                    context={"operation": "cleanup_expired"}
                )
            logger.warning(f"Error during expired cache cleanup: {str(e)}")
    
    async def _enforce_max_size(self) -> None:
        """
        Enforce maximum cache size by removing oldest entries
        """
        try:
            # Get current cache size
            total_size = 0
            cache_files = []
            
            for file_name in os.listdir(CACHE_DIR):
                if file_name.endswith(".json"):
                    file_path = os.path.join(CACHE_DIR, file_name)
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    
                    try:
                        with open(file_path, 'r') as f:
                            entry = json.load(f)
                        timestamp = entry.get("timestamp", 0)
                    except:
                        timestamp = 0
                    
                    cache_files.append((file_path, file_size, timestamp))
            
            # Convert to MB
            total_size_mb = total_size / (1024 * 1024)
            
            if total_size_mb > self.max_size_mb:
                logger.info(f"Cache size ({total_size_mb:.2f}MB) exceeds limit ({self.max_size_mb}MB), cleaning up")
                
                # Sort files by timestamp (oldest first)
                cache_files.sort(key=lambda x: x[2])
                
                # Remove oldest files until we're under the limit
                size_to_remove = total_size - (self.max_size_mb * 1024 * 1024)
                removed_size = 0
                
                for file_path, file_size, _ in cache_files:
                    if removed_size >= size_to_remove:
                        break
                    
                    # Remove from file system
                    os.remove(file_path)
                    
                    # If in memory, remove from there too
                    key = os.path.basename(file_path).replace(".json", "")
                    if key in self.memory_cache:
                        self.memory_cache.pop(key)
                    
                    removed_size += file_size
                
                logger.info(f"Removed {len(cache_files)} oldest cache entries ({removed_size / (1024 * 1024):.2f}MB)")
            else:
                logger.info(f"Cache size is within limits: {total_size_mb:.2f}MB / {self.max_size_mb}MB")
        
        except Exception as e:
            if error_logging_available:
                log_error(
                    error=e,
                    category=ErrorCategory.CACHE,
                    severity=ErrorSeverity.WARNING,
                    component="agent_cache",
                    context={"operation": "enforce_max_size"}
                )
            logger.warning(f"Error enforcing max cache size: {str(e)}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dict: Cache statistics
        """
        # Calculate hit rate
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests) * 100 if total_requests > 0 else 0
        
        # Get current cache size
        total_size = 0
        file_count = 0
        
        for file_name in os.listdir(CACHE_DIR):
            if file_name.endswith(".json"):
                file_path = os.path.join(CACHE_DIR, file_name)
                total_size += os.path.getsize(file_path)
                file_count += 1
        
        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": f"{hit_rate:.2f}%",
            "total_requests": total_requests,
            "total_saved_time": f"{self.stats['total_saved_time']:.2f}s",
            "memory_entries": len(self.memory_cache),
            "file_entries": file_count,
            "cache_size_mb": total_size / (1024 * 1024),
            "max_size_mb": self.max_size_mb,
            "last_cleanup": self.stats["last_cleanup"].isoformat()
        }

# Singleton instance
_cache_instance = None

def get_agent_cache(ttl: int = DEFAULT_TTL, max_size_mb: int = MAX_CACHE_SIZE_MB) -> AgentCacheService:
    """
    Get the singleton instance of the agent cache service
    
    Args:
        ttl: Time-to-live for cache entries in seconds
        max_size_mb: Maximum cache size in megabytes
        
    Returns:
        AgentCacheService: The singleton instance
    """
    global _cache_instance
    
    if _cache_instance is None:
        _cache_instance = AgentCacheService(ttl, max_size_mb)
    
    return _cache_instance
