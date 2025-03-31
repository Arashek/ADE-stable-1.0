from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import uuid4

class LearningModel(BaseModel):
    """Model for learning models"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str
    version: str
    parameters: Dict[str, Any]
    metrics: Dict[str, float]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Dataset(BaseModel):
    """Model for datasets"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class KnowledgeEntry(BaseModel):
    """Model for knowledge entries"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str
    content: Dict[str, Any]
    source: str
    confidence: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TrainingSession(BaseModel):
    """Model for training sessions"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    model_id: str
    dataset_id: str
    parameters: Dict[str, Any]
    metrics: Dict[str, float]
    status: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class InstanceData(BaseModel):
    """Model for instance data"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    instance_id: str
    metrics: Dict[str, float]
    events: List[Dict[str, Any]]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AnalyticsReport(BaseModel):
    """Model for analytics reports"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str
    content: Dict[str, Any]
    period: Dict[str, datetime]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AnalyticsData(BaseModel):
    """Data collected from ADE instances"""
    instance_id: str
    timestamp: datetime
    metrics: Dict[str, float]
    events: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    
    async def update(self, new_data: List[Dict[str, Any]]):
        """Update dataset with new data"""
        self.data.extend(new_data)
        self.updated_at = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "version": self.version,
            "dataset_id": self.dataset_id,
            "parameters": self.parameters,
            "metrics": self.metrics,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        } 