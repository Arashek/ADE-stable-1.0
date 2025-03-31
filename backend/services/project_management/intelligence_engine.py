"""
Project Intelligence Engine

This module provides AI-driven insights and predictions for projects based on
historical data, current project state, and container events.
"""

import os
import logging
import asyncio
import json
from typing import Dict, List, Optional, Union, Any, Callable
from enum import Enum
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import uuid

# Configure logging
logger = logging.getLogger(__name__)

class InsightType(str, Enum):
    """Types of project insights."""
    RISK = "risk"  # Potential risks to project success
    OPPORTUNITY = "opportunity"  # Opportunities for improvement
    TREND = "trend"  # Trends in project metrics
    RECOMMENDATION = "recommendation"  # Actionable recommendations
    PREDICTION = "prediction"  # Predictions about future project state

class InsightSeverity(str, Enum):
    """Severity levels for insights."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class InsightStatus(str, Enum):
    """Status of an insight."""
    ACTIVE = "active"  # Insight is active and relevant
    ACKNOWLEDGED = "acknowledged"  # Insight has been acknowledged by a user
    RESOLVED = "resolved"  # Insight has been resolved
    DISMISSED = "dismissed"  # Insight has been dismissed as irrelevant

class ProjectMetric(BaseModel):
    """A metric for a project."""
    id: str
    name: str
    value: Union[int, float, str]
    unit: Optional[str] = None
    timestamp: datetime
    source: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProjectInsight(BaseModel):
    """An insight about a project."""
    id: str
    project_id: str
    type: InsightType
    title: str
    description: str
    severity: InsightSeverity
    status: InsightStatus = InsightStatus.ACTIVE
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    metrics: List[str] = Field(default_factory=list)  # IDs of related metrics
    related_insights: List[str] = Field(default_factory=list)  # IDs of related insights
    actions: List[Dict[str, Any]] = Field(default_factory=list)  # Suggested actions
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProjectPrediction(BaseModel):
    """A prediction about a project's future state."""
    id: str
    project_id: str
    metric_name: str
    current_value: Union[int, float, str]
    predicted_value: Union[int, float, str]
    confidence: float  # 0.0 to 1.0
    prediction_date: datetime
    target_date: datetime
    model_version: str
    features_used: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProjectIntelligenceEngine:
    """
    Project Intelligence Engine
    
    Provides AI-driven insights and predictions for projects, including:
    - Analyzing project metrics and trends
    - Identifying risks and opportunities
    - Making predictions about future project state
    - Generating recommendations for project improvement
    - Monitoring container events for project insights
    """
    
    def __init__(self):
        """Initialize the Project Intelligence Engine."""
        self.metrics: Dict[str, ProjectMetric] = {}
        self.insights: Dict[str, ProjectInsight] = {}
        self.predictions: Dict[str, ProjectPrediction] = {}
        
        # Register insight generators
        self.insight_generators: List[Callable] = [
            self._generate_schedule_insights,
            self._generate_resource_insights,
            self._generate_quality_insights,
            self._generate_container_insights
        ]
        
        logger.info("Project Intelligence Engine initialized")
    
    async def add_metric(
        self,
        project_id: str,
        name: str,
        value: Union[int, float, str],
        unit: Optional[str] = None,
        source: str = "manual",
        metadata: Dict[str, Any] = None
    ) -> ProjectMetric:
        """
        Add a new metric for a project.
        
        Args:
            project_id: ID of the project
            name: Name of the metric
            value: Value of the metric
            unit: Unit of the metric
            source: Source of the metric
            metadata: Additional metadata
            
        Returns:
            The created metric
        """
        metric_id = str(uuid.uuid4())
        now = datetime.now()
        
        # Include project_id in metadata
        meta = metadata or {}
        meta["project_id"] = project_id
        
        metric = ProjectMetric(
            id=metric_id,
            name=name,
            value=value,
            unit=unit,
            timestamp=now,
            source=source,
            metadata=meta
        )
        
        self.metrics[metric_id] = metric
        
        # Generate insights based on the new metric
        await self.generate_insights(project_id)
        
        logger.info(f"Added metric {name} for project {project_id}")
        return metric
    
    async def get_metrics(
        self,
        project_id: str,
        metric_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        source: Optional[str] = None
    ) -> List[ProjectMetric]:
        """
        Get metrics for a project with optional filtering.
        
        Args:
            project_id: ID of the project
            metric_name: Filter by metric name
            start_time: Filter by start time
            end_time: Filter by end time
            source: Filter by source
            
        Returns:
            List of metrics matching the filters
        """
        metrics = list(self.metrics.values())
        
        # Filter by project_id
        metrics = [m for m in metrics if m.metadata.get("project_id") == project_id]
        
        if metric_name:
            metrics = [m for m in metrics if m.name == metric_name]
        
        if start_time:
            metrics = [m for m in metrics if m.timestamp >= start_time]
        
        if end_time:
            metrics = [m for m in metrics if m.timestamp <= end_time]
        
        if source:
            metrics = [m for m in metrics if m.source == source]
        
        # Sort by timestamp (newest first)
        metrics.sort(key=lambda m: m.timestamp, reverse=True)
        
        return metrics
    
    async def generate_insights(self, project_id: str) -> List[ProjectInsight]:
        """
        Generate insights for a project based on metrics and other data.
        
        Args:
            project_id: ID of the project
            
        Returns:
            List of generated insights
        """
        new_insights = []
        
        # Run all insight generators
        for generator in self.insight_generators:
            try:
                insights = await generator(project_id)
                new_insights.extend(insights)
            except Exception as e:
                logger.error(f"Error generating insights: {e}")
        
        # Store new insights
        for insight in new_insights:
            self.insights[insight.id] = insight
        
        logger.info(f"Generated {len(new_insights)} insights for project {project_id}")
        return new_insights
    
    async def _generate_schedule_insights(self, project_id: str) -> List[ProjectInsight]:
        """
        Generate insights related to project schedule.
        
        Args:
            project_id: ID of the project
            
        Returns:
            List of generated insights
        """
        insights = []
        
        # Get schedule-related metrics
        schedule_metrics = await self.get_metrics(
            project_id=project_id,
            metric_name="task_completion_rate"
        )
        
        if not schedule_metrics:
            return insights
        
        # Calculate average task completion rate
        completion_rates = [float(m.value) for m in schedule_metrics if isinstance(m.value, (int, float))]
        if not completion_rates:
            return insights
        
        avg_completion_rate = sum(completion_rates) / len(completion_rates)
        
        # Generate insight if completion rate is low
        if avg_completion_rate < 0.7:
            insight_id = str(uuid.uuid4())
            now = datetime.now()
            
            insight = ProjectInsight(
                id=insight_id,
                project_id=project_id,
                type=InsightType.RISK,
                title="Low Task Completion Rate",
                description=f"The average task completion rate is {avg_completion_rate:.2f}, which is below the recommended threshold of 0.7.",
                severity=InsightSeverity.MEDIUM if avg_completion_rate >= 0.5 else InsightSeverity.HIGH,
                created_at=now,
                updated_at=now,
                expires_at=now + timedelta(days=7),
                metrics=[m.id for m in schedule_metrics],
                actions=[
                    {
                        "title": "Review task assignments",
                        "description": "Review current task assignments and redistribute workload if necessary."
                    },
                    {
                        "title": "Break down large tasks",
                        "description": "Identify large tasks and break them down into smaller, more manageable tasks."
                    }
                ]
            )
            
            insights.append(insight)
        
        return insights
    
    async def _generate_resource_insights(self, project_id: str) -> List[ProjectInsight]:
        """
        Generate insights related to project resources.
        
        Args:
            project_id: ID of the project
            
        Returns:
            List of generated insights
        """
        insights = []
        
        # Get resource-related metrics
        resource_metrics = await self.get_metrics(
            project_id=project_id,
            metric_name="resource_utilization"
        )
        
        if not resource_metrics:
            return insights
        
        # Calculate average resource utilization
        utilization_rates = [float(m.value) for m in resource_metrics if isinstance(m.value, (int, float))]
        if not utilization_rates:
            return insights
        
        avg_utilization = sum(utilization_rates) / len(utilization_rates)
        
        # Generate insight if utilization is high
        if avg_utilization > 0.85:
            insight_id = str(uuid.uuid4())
            now = datetime.now()
            
            insight = ProjectInsight(
                id=insight_id,
                project_id=project_id,
                type=InsightType.RISK,
                title="High Resource Utilization",
                description=f"The average resource utilization is {avg_utilization:.2f}, which is above the recommended threshold of 0.85.",
                severity=InsightSeverity.MEDIUM if avg_utilization <= 0.95 else InsightSeverity.HIGH,
                created_at=now,
                updated_at=now,
                expires_at=now + timedelta(days=7),
                metrics=[m.id for m in resource_metrics],
                actions=[
                    {
                        "title": "Scale up resources",
                        "description": "Consider scaling up resources to handle the current workload."
                    },
                    {
                        "title": "Optimize resource usage",
                        "description": "Identify opportunities to optimize resource usage in the project."
                    }
                ]
            )
            
            insights.append(insight)
        
        return insights
    
    async def _generate_quality_insights(self, project_id: str) -> List[ProjectInsight]:
        """
        Generate insights related to project quality.
        
        Args:
            project_id: ID of the project
            
        Returns:
            List of generated insights
        """
        insights = []
        
        # Get quality-related metrics
        quality_metrics = await self.get_metrics(
            project_id=project_id,
            metric_name="code_quality_score"
        )
        
        if not quality_metrics:
            return insights
        
        # Get the most recent code quality score
        recent_quality = max(quality_metrics, key=lambda m: m.timestamp)
        
        # Generate insight if quality score is low
        if float(recent_quality.value) < 70:
            insight_id = str(uuid.uuid4())
            now = datetime.now()
            
            insight = ProjectInsight(
                id=insight_id,
                project_id=project_id,
                type=InsightType.RECOMMENDATION,
                title="Low Code Quality Score",
                description=f"The current code quality score is {recent_quality.value}, which is below the recommended threshold of 70.",
                severity=InsightSeverity.MEDIUM if float(recent_quality.value) >= 50 else InsightSeverity.HIGH,
                created_at=now,
                updated_at=now,
                expires_at=now + timedelta(days=7),
                metrics=[recent_quality.id],
                actions=[
                    {
                        "title": "Run code quality analysis",
                        "description": "Run a detailed code quality analysis to identify specific issues."
                    },
                    {
                        "title": "Implement code reviews",
                        "description": "Implement or improve code review processes to catch quality issues early."
                    }
                ]
            )
            
            insights.append(insight)
        
        return insights
    
    async def _generate_container_insights(self, project_id: str) -> List[ProjectInsight]:
        """
        Generate insights related to container events.
        
        Args:
            project_id: ID of the project
            
        Returns:
            List of generated insights
        """
        insights = []
        
        # Get container-related metrics
        container_metrics = await self.get_metrics(
            project_id=project_id,
            source="container"
        )
        
        if not container_metrics:
            return insights
        
        # Check for container restarts
        restart_metrics = [m for m in container_metrics if m.name == "container_restarts"]
        if restart_metrics:
            # Get the most recent restart count
            recent_restart = max(restart_metrics, key=lambda m: m.timestamp)
            
            # Generate insight if restart count is high
            if int(recent_restart.value) > 5:
                insight_id = str(uuid.uuid4())
                now = datetime.now()
                
                insight = ProjectInsight(
                    id=insight_id,
                    project_id=project_id,
                    type=InsightType.RISK,
                    title="High Container Restart Count",
                    description=f"The container has restarted {recent_restart.value} times, which may indicate stability issues.",
                    severity=InsightSeverity.HIGH,
                    created_at=now,
                    updated_at=now,
                    expires_at=now + timedelta(days=3),
                    metrics=[recent_restart.id],
                    actions=[
                        {
                            "title": "Check container logs",
                            "description": "Check container logs for error messages or exceptions."
                        },
                        {
                            "title": "Review resource limits",
                            "description": "Review container resource limits and adjust if necessary."
                        }
                    ]
                )
                
                insights.append(insight)
        
        # Check for high CPU usage
        cpu_metrics = [m for m in container_metrics if m.name == "container_cpu_usage"]
        if cpu_metrics:
            # Get the most recent CPU usage
            recent_cpu = max(cpu_metrics, key=lambda m: m.timestamp)
            
            # Generate insight if CPU usage is high
            if float(recent_cpu.value) > 0.9:
                insight_id = str(uuid.uuid4())
                now = datetime.now()
                
                insight = ProjectInsight(
                    id=insight_id,
                    project_id=project_id,
                    type=InsightType.RISK,
                    title="High Container CPU Usage",
                    description=f"The container CPU usage is {float(recent_cpu.value):.2f}, which is above the recommended threshold of 0.9.",
                    severity=InsightSeverity.MEDIUM,
                    created_at=now,
                    updated_at=now,
                    expires_at=now + timedelta(days=1),
                    metrics=[recent_cpu.id],
                    actions=[
                        {
                            "title": "Optimize CPU-intensive operations",
                            "description": "Identify and optimize CPU-intensive operations in the application."
                        },
                        {
                            "title": "Scale up CPU resources",
                            "description": "Consider scaling up CPU resources for the container."
                        }
                    ]
                )
                
                insights.append(insight)
        
        return insights
    
    async def get_insights(
        self,
        project_id: str,
        insight_type: Optional[InsightType] = None,
        severity: Optional[InsightSeverity] = None,
        status: Optional[InsightStatus] = None
    ) -> List[ProjectInsight]:
        """
        Get insights for a project with optional filtering.
        
        Args:
            project_id: ID of the project
            insight_type: Filter by insight type
            severity: Filter by severity
            status: Filter by status
            
        Returns:
            List of insights matching the filters
        """
        insights = list(self.insights.values())
        
        # Filter by project_id
        insights = [i for i in insights if i.project_id == project_id]
        
        if insight_type:
            insights = [i for i in insights if i.type == insight_type]
        
        if severity:
            insights = [i for i in insights if i.severity == severity]
        
        if status:
            insights = [i for i in insights if i.status == status]
        
        # Sort by created_at (newest first)
        insights.sort(key=lambda i: i.created_at, reverse=True)
        
        return insights
    
    async def update_insight_status(
        self,
        insight_id: str,
        status: InsightStatus,
        user_id: str
    ) -> ProjectInsight:
        """
        Update the status of an insight.
        
        Args:
            insight_id: ID of the insight
            status: New status
            user_id: ID of the user making the update
            
        Returns:
            The updated insight
        """
        if insight_id not in self.insights:
            raise ValueError(f"Insight not found: {insight_id}")
        
        insight = self.insights[insight_id]
        
        # Update status
        insight.status = status
        insight.updated_at = datetime.now()
        
        # Add user_id to metadata
        insight.metadata["last_updated_by"] = user_id
        
        logger.info(f"Updated insight {insight_id} status to {status}")
        return insight
    
    async def make_prediction(
        self,
        project_id: str,
        metric_name: str,
        target_date: datetime
    ) -> ProjectPrediction:
        """
        Make a prediction about a project metric's future value.
        
        Args:
            project_id: ID of the project
            metric_name: Name of the metric to predict
            target_date: Date for which to make the prediction
            
        Returns:
            The prediction
        """
        # Get historical metrics
        historical_metrics = await self.get_metrics(
            project_id=project_id,
            metric_name=metric_name
        )
        
        if not historical_metrics:
            raise ValueError(f"No historical data for metric: {metric_name}")
        
        # In a real implementation, this would use a machine learning model
        # For now, we'll use a simple linear extrapolation
        
        # Sort metrics by timestamp
        historical_metrics.sort(key=lambda m: m.timestamp)
        
        # Get the most recent metric
        recent_metric = historical_metrics[-1]
        
        # Make a simple prediction (random variation around the current value)
        import random
        current_value = float(recent_metric.value)
        predicted_value = current_value * (1 + random.uniform(-0.2, 0.3))
        
        # Create prediction
        prediction_id = str(uuid.uuid4())
        now = datetime.now()
        
        prediction = ProjectPrediction(
            id=prediction_id,
            project_id=project_id,
            metric_name=metric_name,
            current_value=current_value,
            predicted_value=predicted_value,
            confidence=0.7,  # Mock confidence level
            prediction_date=now,
            target_date=target_date,
            model_version="1.0.0",
            features_used=["historical_values", "time_of_day", "day_of_week"],
            metadata={
                "project_id": project_id,
                "data_points_used": len(historical_metrics)
            }
        )
        
        self.predictions[prediction_id] = prediction
        
        logger.info(f"Made prediction for {metric_name} in project {project_id}")
        return prediction
    
    async def get_predictions(
        self,
        project_id: str,
        metric_name: Optional[str] = None
    ) -> List[ProjectPrediction]:
        """
        Get predictions for a project with optional filtering.
        
        Args:
            project_id: ID of the project
            metric_name: Filter by metric name
            
        Returns:
            List of predictions matching the filters
        """
        predictions = list(self.predictions.values())
        
        # Filter by project_id
        predictions = [p for p in predictions if p.project_id == project_id]
        
        if metric_name:
            predictions = [p for p in predictions if p.metric_name == metric_name]
        
        # Sort by prediction_date (newest first)
        predictions.sort(key=lambda p: p.prediction_date, reverse=True)
        
        return predictions
    
    async def process_container_event(
        self,
        event_type: str,
        container_id: str,
        project_id: str,
        event_data: Dict[str, Any]
    ) -> None:
        """
        Process a container event and generate metrics/insights.
        
        Args:
            event_type: Type of event
            container_id: ID of the container
            project_id: ID of the project
            event_data: Event data
        """
        logger.info(f"Processing container event: {event_type} for container {container_id}")
        
        # Convert event to metrics
        if event_type == "restart":
            # Add container restart metric
            await self.add_metric(
                project_id=project_id,
                name="container_restarts",
                value=event_data.get("count", 1),
                source="container",
                metadata={
                    "container_id": container_id,
                    "event_type": event_type
                }
            )
        
        elif event_type == "resource_usage":
            # Add CPU usage metric
            if "cpu" in event_data:
                await self.add_metric(
                    project_id=project_id,
                    name="container_cpu_usage",
                    value=event_data["cpu"],
                    unit="cores",
                    source="container",
                    metadata={
                        "container_id": container_id,
                        "event_type": event_type
                    }
                )
            
            # Add memory usage metric
            if "memory" in event_data:
                await self.add_metric(
                    project_id=project_id,
                    name="container_memory_usage",
                    value=event_data["memory"],
                    unit="bytes",
                    source="container",
                    metadata={
                        "container_id": container_id,
                        "event_type": event_type
                    }
                )
        
        # Generate insights based on the new metrics
        await self.generate_insights(project_id)

# Singleton instance
project_intelligence_engine = ProjectIntelligenceEngine()
