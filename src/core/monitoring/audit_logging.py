from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import json
import hashlib
import hmac
import base64
from enum import Enum
from elasticsearch import AsyncElasticsearch
import yaml
from pathlib import Path
import asyncio
import uuid

logger = logging.getLogger(__name__)

class AuditEventType(Enum):
    """Types of audit events."""
    AUTHENTICATION = "authentication"
    DATA_ACCESS = "data_access"
    CONFIG_CHANGE = "config_change"
    ACCESS_CONTROL = "access_control"
    SYSTEM_CHANGE = "system_change"
    SECURITY_EVENT = "security_event"

class AuditEventSeverity(Enum):
    """Severity levels for audit events."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class AuditEvent:
    """Audit event data structure."""
    event_id: str
    event_type: AuditEventType
    severity: AuditEventSeverity
    timestamp: datetime
    user_id: Optional[str]
    action: str
    resource: str
    details: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    session_id: Optional[str]
    correlation_id: Optional[str]
    metadata: Dict[str, Any]

class AuditLogger:
    """Tamper-proof audit logging system."""
    
    def __init__(
        self,
        config_dir: str,
        elasticsearch_url: str = "http://localhost:9200",
        retention_days: int = 90,
        secret_key: Optional[str] = None
    ):
        self.config_dir = Path(config_dir)
        self.es = AsyncElasticsearch([elasticsearch_url])
        self.retention_days = retention_days
        self.secret_key = secret_key or str(uuid.uuid4())
        
        # Load audit configurations
        self.event_filters: Dict[str, List[Dict[str, Any]]] = {}
        self._load_configs()
        
        # Initialize indices
        asyncio.create_task(self._init_indices())
        
    def _load_configs(self) -> None:
        """Load audit configurations from files."""
        # Load event filters
        filters_file = self.config_dir / "audit_filters.yaml"
        if filters_file.exists():
            with open(filters_file) as f:
                self.event_filters = yaml.safe_load(f)
                
    async def _init_indices(self) -> None:
        """Initialize Elasticsearch indices for audit logs."""
        try:
            # Create audit logs index
            await self.es.indices.create(
                index=f"audit-logs-{datetime.now().strftime('%Y.%m')}",
                body={
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 1
                    },
                    "mappings": {
                        "properties": {
                            "event_id": {"type": "keyword"},
                            "event_type": {"type": "keyword"},
                            "severity": {"type": "keyword"},
                            "timestamp": {"type": "date"},
                            "user_id": {"type": "keyword"},
                            "action": {"type": "keyword"},
                            "resource": {"type": "keyword"},
                            "details": {"type": "object"},
                            "ip_address": {"type": "ip"},
                            "user_agent": {"type": "keyword"},
                            "session_id": {"type": "keyword"},
                            "correlation_id": {"type": "keyword"},
                            "metadata": {"type": "object"},
                            "hash": {"type": "keyword"}
                        }
                    }
                },
                ignore=400  # Ignore if index already exists
            )
            
            # Set up retention policy
            await self._enforce_retention_policy()
            
        except Exception as e:
            logger.error(f"Failed to initialize audit indices: {str(e)}")
            
    def _generate_hash(self, event: AuditEvent) -> str:
        """Generate tamper-proof hash for event."""
        # Create string representation of event
        event_str = json.dumps({
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "severity": event.severity.value,
            "timestamp": event.timestamp.isoformat(),
            "user_id": event.user_id,
            "action": event.action,
            "resource": event.resource,
            "details": event.details,
            "ip_address": event.ip_address,
            "user_agent": event.user_agent,
            "session_id": event.session_id,
            "correlation_id": event.correlation_id,
            "metadata": event.metadata
        }, sort_keys=True)
        
        # Generate HMAC using secret key
        hmac_obj = hmac.new(
            self.secret_key.encode(),
            event_str.encode(),
            hashlib.sha256
        )
        return base64.b64encode(hmac_obj.digest()).decode()
        
    def _should_log_event(self, event: AuditEvent) -> bool:
        """Check if event should be logged based on filters."""
        if event.event_type.value not in self.event_filters:
            return True
            
        filters = self.event_filters[event.event_type.value]
        for filter_rule in filters:
            # Check severity filter
            if "min_severity" in filter_rule:
                if event.severity.value < filter_rule["min_severity"]:
                    continue
                    
            # Check action filter
            if "actions" in filter_rule:
                if event.action not in filter_rule["actions"]:
                    continue
                    
            # Check resource filter
            if "resources" in filter_rule:
                if event.resource not in filter_rule["resources"]:
                    continue
                    
            # Check user filter
            if "users" in filter_rule and event.user_id:
                if event.user_id not in filter_rule["users"]:
                    continue
                    
            # If all filters pass, check if event should be included or excluded
            return filter_rule.get("action", "include") == "include"
            
        return True
        
    async def log_event(self, event: AuditEvent) -> bool:
        """Log an audit event with tamper-proof verification."""
        try:
            # Check if event should be logged
            if not self._should_log_event(event):
                return False
                
            # Generate tamper-proof hash
            event_hash = self._generate_hash(event)
            
            # Prepare document for Elasticsearch
            doc = {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "severity": event.severity.value,
                "timestamp": event.timestamp,
                "user_id": event.user_id,
                "action": event.action,
                "resource": event.resource,
                "details": event.details,
                "ip_address": event.ip_address,
                "user_agent": event.user_agent,
                "session_id": event.session_id,
                "correlation_id": event.correlation_id,
                "metadata": event.metadata,
                "hash": event_hash
            }
            
            # Store in Elasticsearch
            await self.es.index(
                index=f"audit-logs-{event.timestamp.strftime('%Y.%m')}",
                document=doc
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
            return False
            
    async def verify_event_integrity(self, event_id: str) -> bool:
        """Verify the integrity of an audit event."""
        try:
            # Search for event
            result = await self.es.search(
                index=f"audit-logs-*",
                body={
                    "query": {
                        "term": {"event_id": event_id}
                    }
                }
            )
            
            if not result["hits"]["hits"]:
                return False
                
            event_doc = result["hits"]["hits"][0]["_source"]
            
            # Recreate event object
            event = AuditEvent(
                event_id=event_doc["event_id"],
                event_type=AuditEventType(event_doc["event_type"]),
                severity=AuditEventSeverity(event_doc["severity"]),
                timestamp=datetime.fromisoformat(event_doc["timestamp"]),
                user_id=event_doc["user_id"],
                action=event_doc["action"],
                resource=event_doc["resource"],
                details=event_doc["details"],
                ip_address=event_doc["ip_address"],
                user_agent=event_doc["user_agent"],
                session_id=event_doc["session_id"],
                correlation_id=event_doc["correlation_id"],
                metadata=event_doc["metadata"]
            )
            
            # Generate hash and compare
            expected_hash = self._generate_hash(event)
            return expected_hash == event_doc["hash"]
            
        except Exception as e:
            logger.error(f"Failed to verify event integrity: {str(e)}")
            return False
            
    async def _enforce_retention_policy(self) -> None:
        """Enforce retention policy for audit logs."""
        try:
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            # Get all audit log indices
            indices = await self.es.indices.get_alias(name="audit-logs-*")
            
            for index_name in indices:
                # Check index date
                index_date = datetime.strptime(
                    index_name.split("-")[-1],
                    "%Y.%m"
                )
                
                if index_date < cutoff_date:
                    # Delete old index
                    await self.es.indices.delete(index=index_name)
                    logger.info(f"Deleted old audit log index: {index_name}")
                    
        except Exception as e:
            logger.error(f"Failed to enforce retention policy: {str(e)}")
            
    async def search_events(
        self,
        event_type: Optional[AuditEventType] = None,
        severity: Optional[AuditEventSeverity] = None,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        include_details: bool = True
    ) -> List[Dict[str, Any]]:
        """Search audit events with filtering."""
        try:
            query = {"query": {"bool": {"must": []}}}
            
            if event_type:
                query["query"]["bool"]["must"].append(
                    {"term": {"event_type": event_type.value}}
                )
                
            if severity:
                query["query"]["bool"]["must"].append(
                    {"term": {"severity": severity.value}}
                )
                
            if user_id:
                query["query"]["bool"]["must"].append(
                    {"term": {"user_id": user_id}}
                )
                
            if action:
                query["query"]["bool"]["must"].append(
                    {"term": {"action": action}}
                )
                
            if resource:
                query["query"]["bool"]["must"].append(
                    {"term": {"resource": resource}}
                )
                
            if start_time:
                query["query"]["bool"]["must"].append(
                    {"range": {"timestamp": {"gte": start_time}}}
                )
                
            if end_time:
                query["query"]["bool"]["must"].append(
                    {"range": {"timestamp": {"lte": end_time}}}
                )
                
            # Add sorting
            query["sort"] = [{"timestamp": "desc"}]
            
            # Execute search
            result = await self.es.search(
                index=f"audit-logs-*",
                body=query
            )
            
            events = []
            for hit in result["hits"]["hits"]:
                event = hit["_source"]
                
                # Verify event integrity
                if not await self.verify_event_integrity(event["event_id"]):
                    logger.warning(f"Event integrity check failed: {event['event_id']}")
                    continue
                    
                # Remove sensitive details if not requested
                if not include_details:
                    event.pop("details", None)
                    
                events.append(event)
                
            return events
            
        except Exception as e:
            logger.error(f"Failed to search audit events: {str(e)}")
            return []
            
    async def get_event_stats(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get statistics about audit events."""
        try:
            query = {
                "query": {
                    "range": {
                        "timestamp": {
                            "gte": start_time,
                            "lte": end_time
                        }
                    }
                },
                "aggs": {
                    "by_event_type": {
                        "terms": {"field": "event_type"}
                    },
                    "by_severity": {
                        "terms": {"field": "severity"}
                    },
                    "by_action": {
                        "terms": {"field": "action"}
                    },
                    "by_resource": {
                        "terms": {"field": "resource"}
                    },
                    "by_user": {
                        "terms": {"field": "user_id"}
                    },
                    "hourly_distribution": {
                        "date_histogram": {
                            "field": "timestamp",
                            "calendar_interval": "hour"
                        }
                    }
                }
            }
            
            result = await self.es.search(
                index=f"audit-logs-*",
                body=query
            )
            
            return {
                "total_events": result["hits"]["total"]["value"],
                "by_event_type": {
                    bucket["key"]: bucket["doc_count"]
                    for bucket in result["aggregations"]["by_event_type"]["buckets"]
                },
                "by_severity": {
                    bucket["key"]: bucket["doc_count"]
                    for bucket in result["aggregations"]["by_severity"]["buckets"]
                },
                "by_action": {
                    bucket["key"]: bucket["doc_count"]
                    for bucket in result["aggregations"]["by_action"]["buckets"]
                },
                "by_resource": {
                    bucket["key"]: bucket["doc_count"]
                    for bucket in result["aggregations"]["by_resource"]["buckets"]
                },
                "by_user": {
                    bucket["key"]: bucket["doc_count"]
                    for bucket in result["aggregations"]["by_user"]["buckets"]
                },
                "hourly_distribution": {
                    bucket["key_as_string"]: bucket["doc_count"]
                    for bucket in result["aggregations"]["hourly_distribution"]["buckets"]
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get event stats: {str(e)}")
            return {}
            
    async def close(self) -> None:
        """Close connections and cleanup."""
        await self.es.close() 