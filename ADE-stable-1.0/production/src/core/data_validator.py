import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
import json
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from pydantic import BaseModel, Field, validator
import jsonschema
from jsonschema import validate

logger = logging.getLogger(__name__)

class DataSchema(BaseModel):
    """Schema for validating learning data"""
    user_id: str
    timestamp: str
    action_type: str
    context: Dict
    outcome: Optional[Dict] = None
    metadata: Dict = Field(default_factory=dict)

    @validator('timestamp')
    def validate_timestamp(cls, v):
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError('Invalid timestamp format')

class DataValidator:
    """Validates and ensures quality of learning data"""
    
    def __init__(self, schema_file: Optional[str] = None):
        """Initialize the data validator
        
        Args:
            schema_file: Optional path to custom JSON schema file
        """
        self.schema = self._load_schema(schema_file)
        self.data_schema = DataSchema
        
    def _load_schema(self, schema_file: Optional[str]) -> Dict:
        """Load JSON schema for validation
        
        Args:
            schema_file: Path to schema file
            
        Returns:
            Dict: Loaded schema
        """
        if schema_file:
            try:
                with open(schema_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load custom schema: {str(e)}")
                
        # Default schema
        return {
            "type": "object",
            "required": ["user_id", "timestamp", "action_type", "context"],
            "properties": {
                "user_id": {"type": "string"},
                "timestamp": {"type": "string", "format": "date-time"},
                "action_type": {"type": "string"},
                "context": {"type": "object"},
                "outcome": {"type": "object"},
                "metadata": {"type": "object"}
            }
        }
        
    def validate_data(self, data: Dict) -> bool:
        """Validate data against schema
        
        Args:
            data: Data to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Validate against JSON schema
            validate(instance=data, schema=self.schema)
            
            # Validate against Pydantic model
            self.data_schema(**data)
            
            return True
            
        except Exception as e:
            logger.error(f"Data validation failed: {str(e)}")
            return False
            
    def check_data_quality(self, data: Dict) -> Dict:
        """Check data quality metrics
        
        Args:
            data: Data to check
            
        Returns:
            Dict: Quality metrics
        """
        quality_metrics = {
            "timestamp": datetime.now().isoformat(),
            "is_valid": True,
            "metrics": {}
        }
        
        try:
            # Check context completeness
            context_metrics = self._check_context_quality(data.get("context", {}))
            quality_metrics["metrics"]["context"] = context_metrics
            
            # Check outcome quality if present
            if data.get("outcome"):
                outcome_metrics = self._check_outcome_quality(data["outcome"])
                quality_metrics["metrics"]["outcome"] = outcome_metrics
                
            # Check metadata quality
            metadata_metrics = self._check_metadata_quality(data.get("metadata", {}))
            quality_metrics["metrics"]["metadata"] = metadata_metrics
            
            # Overall quality score
            quality_metrics["quality_score"] = self._calculate_quality_score(
                quality_metrics["metrics"]
            )
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Data quality check failed: {str(e)}")
            quality_metrics["is_valid"] = False
            quality_metrics["error"] = str(e)
            return quality_metrics
            
    def _check_context_quality(self, context: Dict) -> Dict:
        """Check quality of context data
        
        Args:
            context: Context data to check
            
        Returns:
            Dict: Context quality metrics
        """
        metrics = {
            "completeness": 0.0,
            "validity": True,
            "issues": []
        }
        
        try:
            # Check for required fields
            required_fields = ["model_name", "training_params"]
            present_fields = [f for f in required_fields if f in context]
            metrics["completeness"] = len(present_fields) / len(required_fields)
            
            # Validate field types
            if "training_params" in context:
                if not isinstance(context["training_params"], dict):
                    metrics["validity"] = False
                    metrics["issues"].append("training_params must be a dictionary")
                    
            # Check for numeric values
            numeric_fields = ["batch_size", "learning_rate", "epochs"]
            for field in numeric_fields:
                if field in context.get("training_params", {}):
                    try:
                        float(context["training_params"][field])
                    except (ValueError, TypeError):
                        metrics["validity"] = False
                        metrics["issues"].append(f"Invalid numeric value for {field}")
                        
            return metrics
            
        except Exception as e:
            logger.error(f"Context quality check failed: {str(e)}")
            metrics["validity"] = False
            metrics["issues"].append(str(e))
            return metrics
            
    def _check_outcome_quality(self, outcome: Dict) -> Dict:
        """Check quality of outcome data
        
        Args:
            outcome: Outcome data to check
            
        Returns:
            Dict: Outcome quality metrics
        """
        metrics = {
            "completeness": 0.0,
            "validity": True,
            "issues": []
        }
        
        try:
            # Check for required fields
            required_fields = ["success", "accuracy"]
            present_fields = [f for f in required_fields if f in outcome]
            metrics["completeness"] = len(present_fields) / len(required_fields)
            
            # Validate field types
            if "success" in outcome and not isinstance(outcome["success"], bool):
                metrics["validity"] = False
                metrics["issues"].append("success must be a boolean")
                
            if "accuracy" in outcome:
                try:
                    accuracy = float(outcome["accuracy"])
                    if not 0 <= accuracy <= 1:
                        metrics["validity"] = False
                        metrics["issues"].append("accuracy must be between 0 and 1")
                except (ValueError, TypeError):
                    metrics["validity"] = False
                    metrics["issues"].append("Invalid accuracy value")
                    
            return metrics
            
        except Exception as e:
            logger.error(f"Outcome quality check failed: {str(e)}")
            metrics["validity"] = False
            metrics["issues"].append(str(e))
            return metrics
            
    def _check_metadata_quality(self, metadata: Dict) -> Dict:
        """Check quality of metadata
        
        Args:
            metadata: Metadata to check
            
        Returns:
            Dict: Metadata quality metrics
        """
        metrics = {
            "completeness": 0.0,
            "validity": True,
            "issues": []
        }
        
        try:
            # Check for required fields
            required_fields = ["version", "environment"]
            present_fields = [f for f in required_fields if f in metadata]
            metrics["completeness"] = len(present_fields) / len(required_fields)
            
            # Validate field types
            if "version" in metadata and not isinstance(metadata["version"], str):
                metrics["validity"] = False
                metrics["issues"].append("version must be a string")
                
            if "environment" in metadata and not isinstance(metadata["environment"], dict):
                metrics["validity"] = False
                metrics["issues"].append("environment must be a dictionary")
                
            return metrics
            
        except Exception as e:
            logger.error(f"Metadata quality check failed: {str(e)}")
            metrics["validity"] = False
            metrics["issues"].append(str(e))
            return metrics
            
    def _calculate_quality_score(self, metrics: Dict) -> float:
        """Calculate overall quality score
        
        Args:
            metrics: Quality metrics for different aspects
            
        Returns:
            float: Overall quality score between 0 and 1
        """
        try:
            weights = {
                "context": 0.4,
                "outcome": 0.4,
                "metadata": 0.2
            }
            
            score = 0.0
            total_weight = 0.0
            
            for aspect, weight in weights.items():
                if aspect in metrics:
                    aspect_metrics = metrics[aspect]
                    if aspect_metrics["validity"]:
                        score += aspect_metrics["completeness"] * weight
                        total_weight += weight
                        
            return score / total_weight if total_weight > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate quality score: {str(e)}")
            return 0.0
            
    def generate_validation_report(self, data: Dict) -> Dict:
        """Generate comprehensive validation report
        
        Args:
            data: Data to validate
            
        Returns:
            Dict: Validation report
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "validation_status": "failed",
            "quality_score": 0.0,
            "issues": [],
            "metrics": {}
        }
        
        try:
            # Validate data
            if not self.validate_data(data):
                report["issues"].append("Data validation failed")
                return report
                
            # Check quality
            quality_metrics = self.check_data_quality(data)
            report["metrics"] = quality_metrics["metrics"]
            report["quality_score"] = quality_metrics.get("quality_score", 0.0)
            
            # Collect issues
            for aspect, metrics in quality_metrics["metrics"].items():
                if not metrics["validity"]:
                    report["issues"].extend(metrics["issues"])
                    
            # Update status
            report["validation_status"] = "passed" if not report["issues"] else "failed"
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate validation report: {str(e)}")
            report["issues"].append(str(e))
            return report 