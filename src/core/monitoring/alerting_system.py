from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import asyncio
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp
import twilio
from twilio.rest import Client
from elasticsearch import AsyncElasticsearch
import yaml
from pathlib import Path
import numpy as np
from enum import Enum

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertConditionType(Enum):
    """Types of alert conditions."""
    THRESHOLD = "threshold"
    TREND = "trend"
    ANOMALY = "anomaly"
    COMPOSITE = "composite"
    RATE_CHANGE = "rate_change"
    WINDOW = "window"

@dataclass
class AlertCondition:
    """Alert condition configuration."""
    type: AlertConditionType
    metric: str
    threshold: Optional[float] = None
    operator: Optional[str] = None
    window_size: Optional[int] = None  # For window-based conditions
    trend_direction: Optional[str] = None  # "increasing" or "decreasing"
    anomaly_threshold: Optional[float] = None  # For anomaly detection
    composite_conditions: Optional[List[Dict[str, Any]]] = None  # For composite conditions
    rate_change_threshold: Optional[float] = None  # For rate change detection

@dataclass
class NotificationChannel:
    """Notification channel configuration."""
    type: str  # email, sms, webhook, slack, pagerduty, teams, discord
    config: Dict[str, Any]
    enabled: bool = True

@dataclass
class EscalationPolicy:
    """Alert escalation policy."""
    name: str
    stages: List[Dict[str, Any]]  # List of stages with delays and channels
    max_stages: int = 3
    auto_resolve: bool = False  # Whether to auto-resolve after max stages
    on_resolve: Optional[List[Dict[str, Any]]] = None  # Actions to take on resolution

@dataclass
class AlertRule:
    """Alert rule configuration."""
    name: str
    condition: AlertCondition
    severity: AlertSeverity
    channels: List[NotificationChannel]
    escalation_policy: Optional[EscalationPolicy] = None
    enabled: bool = True
    cooldown_seconds: int = 300
    description: str = ""
    tags: List[str] = None
    auto_resolve: bool = False  # Whether to auto-resolve when condition is no longer met
    resolution_delay: int = 300  # Delay before auto-resolving
    dependencies: List[str] = None  # Other alerts that must be active for this alert to trigger

class AlertingSystem:
    """Alert management and notification system."""
    
    def __init__(
        self,
        config_dir: str,
        elasticsearch_url: str = "http://localhost:9200"
    ):
        self.config_dir = Path(config_dir)
        self.es = AsyncElasticsearch([elasticsearch_url])
        
        # Load alert rules and escalation policies
        self.alert_rules: Dict[str, AlertRule] = {}
        self.escalation_policies: Dict[str, EscalationPolicy] = {}
        self._load_configs()
        
        # Track alert history and cooldowns
        self.alert_history: Dict[str, List[Dict[str, Any]]] = {}
        self.alert_cooldowns: Dict[str, datetime] = {}
        self.active_alerts: Dict[str, Dict[str, Any]] = {}
        
        # Initialize notification clients
        self._init_notification_clients()
        
    def _load_configs(self) -> None:
        """Load alert rules and escalation policies from config files."""
        # Load alert rules
        rules_file = self.config_dir / "alert_rules.yaml"
        if rules_file.exists():
            with open(rules_file) as f:
                data = yaml.safe_load(f)
                for rule_data in data:
                    rule = AlertRule(
                        name=rule_data["name"],
                        condition=AlertCondition(**rule_data["condition"]),
                        severity=AlertSeverity(rule_data["severity"]),
                        channels=[
                            NotificationChannel(**channel)
                            for channel in rule_data["channels"]
                        ],
                        escalation_policy=rule_data.get("escalation_policy"),
                        enabled=rule_data.get("enabled", True),
                        cooldown_seconds=rule_data.get("cooldown_seconds", 300),
                        description=rule_data.get("description", ""),
                        tags=rule_data.get("tags", []),
                        auto_resolve=rule_data.get("auto_resolve", False),
                        resolution_delay=rule_data.get("resolution_delay", 300),
                        dependencies=rule_data.get("dependencies", [])
                    )
                    self.alert_rules[rule.name] = rule
                    self.alert_history[rule.name] = []
                    
        # Load escalation policies
        policies_file = self.config_dir / "escalation_policies.yaml"
        if policies_file.exists():
            with open(policies_file) as f:
                data = yaml.safe_load(f)
                for policy_data in data:
                    policy = EscalationPolicy(
                        name=policy_data["name"],
                        stages=policy_data["stages"],
                        max_stages=policy_data.get("max_stages", 3),
                        auto_resolve=policy_data.get("auto_resolve", False),
                        on_resolve=policy_data.get("on_resolve", [])
                    )
                    self.escalation_policies[policy.name] = policy
                    
    def _init_notification_clients(self) -> None:
        """Initialize notification service clients."""
        # Load notification configs
        config_file = self.config_dir / "notification_config.yaml"
        if config_file.exists():
            with open(config_file) as f:
                self.notification_configs = yaml.safe_load(f)
                
            # Initialize Twilio client if configured
            if "twilio" in self.notification_configs:
                twilio_config = self.notification_configs["twilio"]
                self.twilio_client = Client(
                    twilio_config["account_sid"],
                    twilio_config["auth_token"]
                )
                
    async def check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check metrics against alert rules."""
        triggered_alerts = []
        
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue
                
            # Check cooldown
            if rule.name in self.alert_cooldowns:
                if datetime.now() < self.alert_cooldowns[rule.name]:
                    continue
                    
            # Evaluate condition
            if self._evaluate_condition(rule.condition, metrics):
                # Create alert
                alert = {
                    "name": rule.name,
                    "severity": rule.severity.value,
                    "timestamp": datetime.now(),
                    "metrics": metrics,
                    "description": rule.description,
                    "tags": rule.tags
                }
                
                # Add to history
                self.alert_history[rule.name].append(alert)
                
                # Set cooldown
                self.alert_cooldowns[rule.name] = datetime.now() + timedelta(
                    seconds=rule.cooldown_seconds
                )
                
                # Store in Elasticsearch
                await self.es.index(
                    index=f"alerts-{datetime.now().strftime('%Y.%m')}",
                    document=alert
                )
                
                # Send notifications
                await self._send_notifications(alert, rule)
                
                triggered_alerts.append(alert)
                
        return triggered_alerts
        
    def _evaluate_condition(
        self,
        condition: AlertCondition,
        metrics: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Evaluate alert condition against metrics."""
        if condition.type == AlertConditionType.THRESHOLD:
            return self._evaluate_threshold(condition, metrics)
        elif condition.type == AlertConditionType.TREND:
            return self._evaluate_trend(condition, historical_data)
        elif condition.type == AlertConditionType.ANOMALY:
            return self._evaluate_anomaly(condition, historical_data)
        elif condition.type == AlertConditionType.COMPOSITE:
            return self._evaluate_composite(condition, metrics, historical_data)
        elif condition.type == AlertConditionType.RATE_CHANGE:
            return self._evaluate_rate_change(condition, historical_data)
        elif condition.type == AlertConditionType.WINDOW:
            return self._evaluate_window(condition, historical_data)
        return False
        
    def _evaluate_threshold(
        self,
        condition: AlertCondition,
        metrics: Dict[str, Any]
    ) -> bool:
        """Evaluate threshold condition."""
        if condition.metric not in metrics:
            return False
            
        value = metrics[condition.metric]
        threshold = condition.threshold
        operator = condition.operator or ">="
        
        if operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "==":
            return value == threshold
        elif operator == "!=":
            return value != threshold
        else:
            return False
            
    def _evaluate_trend(
        self,
        condition: AlertCondition,
        historical_data: List[Dict[str, Any]]
    ) -> bool:
        """Evaluate trend condition."""
        if not historical_data or len(historical_data) < 2:
            return False
            
        values = [d["value"] for d in historical_data]
        if condition.trend_direction == "increasing":
            return all(values[i] <= values[i+1] for i in range(len(values)-1))
        elif condition.trend_direction == "decreasing":
            return all(values[i] >= values[i+1] for i in range(len(values)-1))
        return False
        
    def _evaluate_anomaly(
        self,
        condition: AlertCondition,
        historical_data: List[Dict[str, Any]]
    ) -> bool:
        """Evaluate anomaly condition using statistical methods."""
        if not historical_data or len(historical_data) < 10:
            return False
            
        values = [d["value"] for d in historical_data]
        mean = np.mean(values)
        std = np.std(values)
        latest = values[-1]
        
        # Check if latest value is outside normal distribution
        z_score = abs((latest - mean) / std)
        return z_score > condition.anomaly_threshold
        
    def _evaluate_composite(
        self,
        condition: AlertCondition,
        metrics: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Evaluate composite condition combining multiple conditions."""
        if not condition.composite_conditions:
            return False
            
        results = []
        for sub_condition in condition.composite_conditions:
            sub_alert_condition = AlertCondition(**sub_condition)
            result = self._evaluate_condition(
                sub_alert_condition,
                metrics,
                historical_data
            )
            results.append(result)
            
        # All conditions must be true
        return all(results)
        
    def _evaluate_rate_change(
        self,
        condition: AlertCondition,
        historical_data: List[Dict[str, Any]]
    ) -> bool:
        """Evaluate rate of change condition."""
        if not historical_data or len(historical_data) < 2:
            return False
            
        values = [d["value"] for d in historical_data]
        timestamps = [d["timestamp"] for d in historical_data]
        
        # Calculate rate of change
        rate = (values[-1] - values[0]) / (timestamps[-1] - timestamps[0]).total_seconds()
        return abs(rate) > condition.rate_change_threshold
        
    def _evaluate_window(
        self,
        condition: AlertCondition,
        historical_data: List[Dict[str, Any]]
    ) -> bool:
        """Evaluate window-based condition."""
        if not historical_data or len(historical_data) < condition.window_size:
            return False
            
        # Get last N values
        window_values = [d["value"] for d in historical_data[-condition.window_size:]]
        
        # Check if all values in window meet threshold
        if condition.operator == ">=":
            return all(v >= condition.threshold for v in window_values)
        elif condition.operator == "<=":
            return all(v <= condition.threshold for v in window_values)
        elif condition.operator == "==":
            return all(v == condition.threshold for v in window_values)
        elif condition.operator == "!=":
            return all(v != condition.threshold for v in window_values)
        return False
        
    async def _send_notifications(
        self,
        alert: Dict[str, Any],
        rule: AlertRule
    ) -> None:
        """Send notifications through configured channels."""
        for channel in rule.channels:
            if not channel.enabled:
                continue
                
            try:
                if channel.type == "email":
                    await self._send_email_notification(alert, channel.config)
                elif channel.type == "sms":
                    await self._send_sms_notification(alert, channel.config)
                elif channel.type == "webhook":
                    await self._send_webhook_notification(alert, channel.config)
                elif channel.type == "slack":
                    await self._send_slack_notification(alert, channel.config)
                elif channel.type == "pagerduty":
                    await self._send_pagerduty_notification(alert, channel.config)
                elif channel.type == "teams":
                    await self._send_teams_notification(alert, channel.config)
                elif channel.type == "discord":
                    await self._send_discord_notification(alert, channel.config)
            except Exception as e:
                logger.error(f"Failed to send {channel.type} notification: {str(e)}")
                
    async def _send_email_notification(
        self,
        alert: Dict[str, Any],
        config: Dict[str, Any]
    ) -> None:
        """Send email notification."""
        msg = MIMEMultipart()
        msg["From"] = config["from"]
        msg["To"] = config["to"]
        msg["Subject"] = f"Alert: {alert['name']} ({alert['severity']})"
        
        body = f"""
        Alert: {alert['name']}
        Severity: {alert['severity']}
        Time: {alert['timestamp']}
        Description: {alert['description']}
        
        Metrics:
        {json.dumps(alert['metrics'], indent=2)}
        """
        
        msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP(config["smtp_server"]) as server:
            server.starttls()
            server.login(config["username"], config["password"])
            server.send_message(msg)
            
    async def _send_sms_notification(
        self,
        alert: Dict[str, Any],
        config: Dict[str, Any]
    ) -> None:
        """Send SMS notification using Twilio."""
        message = f"""
        Alert: {alert['name']}
        Severity: {alert['severity']}
        Time: {alert['timestamp']}
        """
        
        self.twilio_client.messages.create(
            body=message,
            from_=config["from_number"],
            to=config["to_number"]
        )
        
    async def _send_webhook_notification(
        self,
        alert: Dict[str, Any],
        config: Dict[str, Any]
    ) -> None:
        """Send webhook notification."""
        async with aiohttp.ClientSession() as session:
            await session.post(
                config["url"],
                json=alert,
                headers=config.get("headers", {})
            )
            
    async def _send_slack_notification(
        self,
        alert: Dict[str, Any],
        config: Dict[str, Any]
    ) -> None:
        """Send Slack notification."""
        async with aiohttp.ClientSession() as session:
            await session.post(
                config["webhook_url"],
                json={
                    "text": f"""
                    *Alert: {alert['name']}*
                    Severity: {alert['severity']}
                    Time: {alert['timestamp']}
                    Description: {alert['description']}
                    
                    Metrics:
                    {json.dumps(alert['metrics'], indent=2)}
                    """
                }
            )
            
    async def _send_pagerduty_notification(
        self,
        alert: Dict[str, Any],
        config: Dict[str, Any]
    ) -> None:
        """Send PagerDuty notification."""
        async with aiohttp.ClientSession() as session:
            payload = {
                "payload": {
                    "summary": f"Alert: {alert['name']}",
                    "severity": alert['severity'],
                    "source": "AlertingSystem",
                    "custom_details": {
                        "description": alert['description'],
                        "metrics": alert['metrics'],
                        "timestamp": alert['timestamp'].isoformat()
                    }
                },
                "routing_key": config["routing_key"],
                "event_action": "trigger",
                "client": "AlertingSystem",
                "client_url": config.get("client_url", "")
            }
            
            await session.post(
                "https://events.pagerduty.com/v2/enqueue",
                json=payload
            )

    async def _send_teams_notification(
        self,
        alert: Dict[str, Any],
        config: Dict[str, Any]
    ) -> None:
        """Send Microsoft Teams notification."""
        async with aiohttp.ClientSession() as session:
            payload = {
                "type": "message",
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": {
                            "type": "AdaptiveCard",
                            "body": [
                                {
                                    "type": "TextBlock",
                                    "text": f"*Alert: {alert['name']}*",
                                    "weight": "bolder",
                                    "size": "large"
                                },
                                {
                                    "type": "TextBlock",
                                    "text": f"Severity: {alert['severity']}"
                                },
                                {
                                    "type": "TextBlock",
                                    "text": f"Time: {alert['timestamp']}"
                                },
                                {
                                    "type": "TextBlock",
                                    "text": f"Description: {alert['description']}"
                                },
                                {
                                    "type": "TextBlock",
                                    "text": "Metrics:",
                                    "weight": "bolder"
                                },
                                {
                                    "type": "TextBlock",
                                    "text": json.dumps(alert['metrics'], indent=2)
                                }
                            ]
                        }
                    }
                ]
            }
            
            await session.post(
                config["webhook_url"],
                json=payload
            )

    async def _send_discord_notification(
        self,
        alert: Dict[str, Any],
        config: Dict[str, Any]
    ) -> None:
        """Send Discord notification."""
        async with aiohttp.ClientSession() as session:
            # Map severity to Discord color
            severity_colors = {
                "info": 0x3498db,    # Blue
                "warning": 0xf1c40f,  # Yellow
                "error": 0xe74c3c,    # Red
                "critical": 0xc0392b  # Dark Red
            }
            
            embed = {
                "title": f"Alert: {alert['name']}",
                "color": severity_colors.get(alert['severity'], 0x95a5a6),
                "fields": [
                    {
                        "name": "Severity",
                        "value": alert['severity'],
                        "inline": True
                    },
                    {
                        "name": "Time",
                        "value": alert['timestamp'].isoformat(),
                        "inline": True
                    },
                    {
                        "name": "Description",
                        "value": alert['description']
                    },
                    {
                        "name": "Metrics",
                        "value": f"```json\n{json.dumps(alert['metrics'], indent=2)}```"
                    }
                ]
            }
            
            payload = {
                "embeds": [embed]
            }
            
            await session.post(
                config["webhook_url"],
                json=payload
            )

    async def get_alert_history(
        self,
        rule_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        severity: Optional[AlertSeverity] = None,
        include_resolved: bool = True,
        include_metrics: bool = True,
        include_notifications: bool = True,
        group_by: Optional[str] = None
    ) -> Union[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
        """Get alert history with enhanced filtering and grouping."""
        try:
            query = {"query": {"bool": {"must": []}}}
            
            if rule_name:
                query["query"]["bool"]["must"].append(
                    {"term": {"name": rule_name}}
                )
                
            if start_time:
                query["query"]["bool"]["must"].append(
                    {"range": {"timestamp": {"gte": start_time}}}
                )
                
            if end_time:
                query["query"]["bool"]["must"].append(
                    {"range": {"timestamp": {"lte": end_time}}}
                )
                
            if severity:
                query["query"]["bool"]["must"].append(
                    {"term": {"severity": severity.value}}
                )
                
            if not include_resolved:
                query["query"]["bool"]["must"].append(
                    {"term": {"resolved": False}}
                )
                
            # Add source filtering
            query["query"]["bool"]["must"].append(
                {"term": {"source": "alerting_system"}}
            )
            
            # Add sorting
            query["sort"] = [
                {"timestamp": "desc"}
            ]
            
            result = await self.es.search(
                index=f"alerts-{datetime.now().strftime('%Y.%m')}",
                body=query
            )
            
            alerts = []
            for hit in result["hits"]["hits"]:
                alert = hit["_source"]
                
                # Add notification history if requested
                if include_notifications:
                    alert["notifications"] = await self._get_notification_history(
                        alert["id"]
                    )
                    
                # Add metric history if requested
                if include_metrics:
                    alert["metric_history"] = await self._get_metric_history(
                        alert["id"]
                    )
                    
                alerts.append(alert)
                
            # Group results if requested
            if group_by:
                return self._group_alerts(alerts, group_by)
                
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get alert history: {str(e)}")
            return []
            
    async def _get_notification_history(
        self,
        alert_id: str
    ) -> List[Dict[str, Any]]:
        """Get notification history for an alert."""
        try:
            query = {
                "query": {
                    "term": {"alert_id": alert_id}
                },
                "sort": [
                    {"timestamp": "desc"}
                ]
            }
            
            result = await self.es.search(
                index=f"notifications-{datetime.now().strftime('%Y.%m')}",
                body=query
            )
            
            return [hit["_source"] for hit in result["hits"]["hits"]]
        except Exception as e:
            logger.error(f"Failed to get notification history: {str(e)}")
            return []
            
    async def _get_metric_history(
        self,
        alert_id: str
    ) -> List[Dict[str, Any]]:
        """Get metric history for an alert."""
        try:
            query = {
                "query": {
                    "term": {"alert_id": alert_id}
                },
                "sort": [
                    {"timestamp": "asc"}
                ]
            }
            
            result = await self.es.search(
                index=f"metrics-{datetime.now().strftime('%Y.%m')}",
                body=query
            )
            
            return [hit["_source"] for hit in result["hits"]["hits"]]
        except Exception as e:
            logger.error(f"Failed to get metric history: {str(e)}")
            return []
            
    def _group_alerts(
        self,
        alerts: List[Dict[str, Any]],
        group_by: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group alerts by specified field."""
        grouped = {}
        for alert in alerts:
            key = alert.get(group_by, "unknown")
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(alert)
        return grouped
        
    async def get_alert_stats(
        self,
        start_time: datetime,
        end_time: datetime,
        include_trends: bool = True,
        include_correlation: bool = True
    ) -> Dict[str, Any]:
        """Get enhanced alert statistics."""
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
                    "by_severity": {
                        "terms": {"field": "severity"}
                    },
                    "by_rule": {
                        "terms": {"field": "name"}
                    },
                    "by_hour": {
                        "date_histogram": {
                            "field": "timestamp",
                            "calendar_interval": "hour"
                        }
                    },
                    "resolution_time": {
                        "avg": {
                            "field": "resolution_time"
                        }
                    }
                }
            }
            
            result = await self.es.search(
                index=f"alerts-{datetime.now().strftime('%Y.%m')}",
                body=query
            )
            
            stats = {
                "total_alerts": result["hits"]["total"]["value"],
                "by_severity": {
                    bucket["key"]: bucket["doc_count"]
                    for bucket in result["aggregations"]["by_severity"]["buckets"]
                },
                "by_rule": {
                    bucket["key"]: bucket["doc_count"]
                    for bucket in result["aggregations"]["by_rule"]["buckets"]
                },
                "hourly_distribution": {
                    bucket["key_as_string"]: bucket["doc_count"]
                    for bucket in result["aggregations"]["by_hour"]["buckets"]
                },
                "avg_resolution_time": result["aggregations"]["resolution_time"]["value"]
            }
            
            # Add trends if requested
            if include_trends:
                stats["trends"] = await self._calculate_alert_trends(
                    start_time,
                    end_time
                )
                
            # Add correlation analysis if requested
            if include_correlation:
                stats["correlations"] = await self._analyze_alert_correlations(
                    start_time,
                    end_time
                )
                
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get alert stats: {str(e)}")
            return {}
            
    async def _calculate_alert_trends(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Calculate alert trends over time."""
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
                    "daily_trends": {
                        "date_histogram": {
                            "field": "timestamp",
                            "calendar_interval": "day"
                        },
                        "aggs": {
                            "by_severity": {
                                "terms": {"field": "severity"}
                            }
                        }
                    }
                }
            }
            
            result = await self.es.search(
                index=f"alerts-{datetime.now().strftime('%Y.%m')}",
                body=query
            )
            
            return {
                "daily_trends": [
                    {
                        "date": bucket["key_as_string"],
                        "severities": {
                            severity["key"]: severity["doc_count"]
                            for severity in bucket["by_severity"]["buckets"]
                        }
                    }
                    for bucket in result["aggregations"]["daily_trends"]["buckets"]
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate alert trends: {str(e)}")
            return {}
            
    async def _analyze_alert_correlations(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Analyze correlations between different alerts."""
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
                    "by_rule": {
                        "terms": {"field": "name"},
                        "aggs": {
                            "cooccurring_alerts": {
                                "terms": {
                                    "field": "name",
                                    "exclude": ["${_key}"]
                                }
                            }
                        }
                    }
                }
            }
            
            result = await self.es.search(
                index=f"alerts-{datetime.now().strftime('%Y.%m')}",
                body=query
            )
            
            correlations = {}
            for bucket in result["aggregations"]["by_rule"]["buckets"]:
                rule_name = bucket["key"]
                correlations[rule_name] = {
                    "cooccurring_alerts": {
                        cooccur["key"]: cooccur["doc_count"]
                        for cooccur in bucket["cooccurring_alerts"]["buckets"]
                    }
                }
                
            return correlations
            
        except Exception as e:
            logger.error(f"Failed to analyze alert correlations: {str(e)}")
            return {}

    async def close(self) -> None:
        """Close connections and cleanup."""
        await self.es.close()
        # Add any other cleanup tasks here 