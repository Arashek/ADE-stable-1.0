from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from pathlib import Path
import json
import yaml
from dataclasses import dataclass
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

from ..models.code_generation.pattern_analyzer import PatternAnalyzer
from ..training.pipeline_manager import TrainingPipelineManager
from ..config import ModelConfig

logger = logging.getLogger(__name__)

@dataclass
class PatternLearningMetrics:
    """Metrics for pattern learning performance"""
    pattern_accuracy: float
    pattern_coverage: float
    learning_rate: float
    adaptation_success: float
    timestamp: datetime

class PatternLearner:
    """Learns and improves design patterns from successful implementations"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.pattern_analyzer = PatternAnalyzer()
        self.training_manager = TrainingPipelineManager(config)
        self.metrics: List[PatternLearningMetrics] = []
        self.pattern_history: Dict[str, List[Dict[str, Any]]] = {}
        
    async def learn_from_implementation(self, 
                                      code: str, 
                                      pattern_type: str,
                                      success_metrics: Dict[str, float]) -> bool:
        """Learn from a successful pattern implementation"""
        try:
            # Analyze the implementation
            analysis = self.pattern_analyzer.analyze_code(code)
            
            # Extract pattern characteristics
            characteristics = self._extract_pattern_characteristics(analysis)
            
            # Update pattern history
            if pattern_type not in self.pattern_history:
                self.pattern_history[pattern_type] = []
            
            self.pattern_history[pattern_type].append({
                "timestamp": datetime.now(),
                "characteristics": characteristics,
                "success_metrics": success_metrics
            })
            
            # Learn from the implementation
            self._update_pattern_knowledge(pattern_type, characteristics, success_metrics)
            
            # Update metrics
            self._update_learning_metrics(pattern_type, success_metrics)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to learn from implementation: {e}")
            return False
            
    def _extract_pattern_characteristics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract pattern characteristics from code analysis"""
        return {
            "complexity": analysis.get("complexity", 0),
            "dependencies": analysis.get("dependencies", []),
            "methods": analysis.get("methods", []),
            "properties": analysis.get("properties", []),
            "relationships": analysis.get("relationships", []),
            "metrics": analysis.get("metrics", {})
        }
        
    def _update_pattern_knowledge(self, 
                                pattern_type: str,
                                characteristics: Dict[str, Any],
                                success_metrics: Dict[str, float]) -> None:
        """Update pattern knowledge based on successful implementations"""
        # Cluster similar implementations
        implementations = self.pattern_history[pattern_type]
        if len(implementations) < 2:
            return
            
        # Extract features for clustering
        features = self._extract_clustering_features(implementations)
        
        # Normalize features
        scaler = StandardScaler()
        normalized_features = scaler.fit_transform(features)
        
        # Perform clustering
        clustering = DBSCAN(eps=0.5, min_samples=2)
        clusters = clustering.fit_predict(normalized_features)
        
        # Update pattern knowledge based on clusters
        for cluster_id in set(clusters):
            if cluster_id == -1:  # Skip noise points
                continue
                
            cluster_implementations = [
                impl for i, impl in enumerate(implementations)
                if clusters[i] == cluster_id
            ]
            
            # Calculate cluster success rate
            success_rate = np.mean([
                impl["success_metrics"]["success_rate"]
                for impl in cluster_implementations
            ])
            
            if success_rate > 0.8:  # High success rate cluster
                self._incorporate_cluster_knowledge(pattern_type, cluster_implementations)
                
    def _extract_clustering_features(self, 
                                   implementations: List[Dict[str, Any]]) -> np.ndarray:
        """Extract features for clustering implementations"""
        features = []
        for impl in implementations:
            characteristics = impl["characteristics"]
            feature_vector = [
                characteristics["complexity"],
                len(characteristics["dependencies"]),
                len(characteristics["methods"]),
                len(characteristics["properties"]),
                len(characteristics["relationships"]),
                characteristics["metrics"].get("maintainability", 0),
                characteristics["metrics"].get("reusability", 0)
            ]
            features.append(feature_vector)
        return np.array(features)
        
    def _incorporate_cluster_knowledge(self, 
                                     pattern_type: str,
                                     cluster_implementations: List[Dict[str, Any]]) -> None:
        """Incorporate knowledge from successful implementation clusters"""
        # Calculate average characteristics
        avg_characteristics = self._calculate_average_characteristics(cluster_implementations)
        
        # Update pattern template
        self._update_pattern_template(pattern_type, avg_characteristics)
        
        # Update pattern rules
        self._update_pattern_rules(pattern_type, cluster_implementations)
        
    def _calculate_average_characteristics(self, 
                                        implementations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate average characteristics from implementations"""
        characteristics = []
        for impl in implementations:
            characteristics.append(impl["characteristics"])
            
        return {
            "complexity": np.mean([c["complexity"] for c in characteristics]),
            "dependencies": list(set(
                dep for c in characteristics 
                for dep in c["dependencies"]
            )),
            "methods": list(set(
                method for c in characteristics 
                for method in c["methods"]
            )),
            "properties": list(set(
                prop for c in characteristics 
                for prop in c["properties"]
            )),
            "relationships": list(set(
                rel for c in characteristics 
                for rel in c["relationships"]
            )),
            "metrics": {
                "maintainability": np.mean([
                    c["metrics"].get("maintainability", 0) 
                    for c in characteristics
                ]),
                "reusability": np.mean([
                    c["metrics"].get("reusability", 0) 
                    for c in characteristics
                ])
            }
        }
        
    def _update_pattern_template(self, 
                               pattern_type: str,
                               characteristics: Dict[str, Any]) -> None:
        """Update pattern template with learned characteristics"""
        template_path = Path(f"src/core/models/code_generation/patterns/{pattern_type}.yaml")
        if not template_path.exists():
            return
            
        with open(template_path, 'r') as f:
            template = yaml.safe_load(f)
            
        # Update template with learned characteristics
        template["parameters"].update({
            "complexity": characteristics["complexity"],
            "dependencies": characteristics["dependencies"],
            "methods": characteristics["methods"],
            "properties": characteristics["properties"],
            "relationships": characteristics["relationships"],
            "metrics": characteristics["metrics"]
        })
        
        with open(template_path, 'w') as f:
            yaml.dump(template, f)
            
    def _update_pattern_rules(self, 
                            pattern_type: str,
                            implementations: List[Dict[str, Any]]) -> None:
        """Update pattern rules based on successful implementations"""
        # Extract common patterns in successful implementations
        common_patterns = self._extract_common_patterns(implementations)
        
        # Update pattern rules
        rules_path = Path(f"src/core/models/code_generation/patterns/{pattern_type}_rules.yaml")
        if not rules_path.exists():
            return
            
        with open(rules_path, 'r') as f:
            rules = yaml.safe_load(f)
            
        # Update rules with learned patterns
        rules["patterns"].extend(common_patterns)
        
        with open(rules_path, 'w') as f:
            yaml.dump(rules, f)
            
    def _extract_common_patterns(self, 
                               implementations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract common patterns from successful implementations"""
        patterns = []
        
        # Analyze method patterns
        method_patterns = self._analyze_method_patterns(implementations)
        if method_patterns:
            patterns.extend(method_patterns)
            
        # Analyze property patterns
        property_patterns = self._analyze_property_patterns(implementations)
        if property_patterns:
            patterns.extend(property_patterns)
            
        # Analyze relationship patterns
        relationship_patterns = self._analyze_relationship_patterns(implementations)
        if relationship_patterns:
            patterns.extend(relationship_patterns)
            
        return patterns
        
    def _analyze_method_patterns(self, 
                               implementations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze common patterns in methods"""
        patterns = []
        method_counts = {}
        
        # Count method occurrences
        for impl in implementations:
            for method in impl["characteristics"]["methods"]:
                method_counts[method] = method_counts.get(method, 0) + 1
                
        # Identify common methods
        common_methods = [
            method for method, count in method_counts.items()
            if count >= len(implementations) * 0.7  # 70% threshold
        ]
        
        if common_methods:
            patterns.append({
                "type": "method",
                "description": "Common methods in successful implementations",
                "methods": common_methods,
                "confidence": min(1.0, len(common_methods) / len(method_counts))
            })
            
        return patterns
        
    def _analyze_property_patterns(self, 
                                 implementations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze common patterns in properties"""
        patterns = []
        property_counts = {}
        
        # Count property occurrences
        for impl in implementations:
            for prop in impl["characteristics"]["properties"]:
                property_counts[prop] = property_counts.get(prop, 0) + 1
                
        # Identify common properties
        common_properties = [
            prop for prop, count in property_counts.items()
            if count >= len(implementations) * 0.7  # 70% threshold
        ]
        
        if common_properties:
            patterns.append({
                "type": "property",
                "description": "Common properties in successful implementations",
                "properties": common_properties,
                "confidence": min(1.0, len(common_properties) / len(property_counts))
            })
            
        return patterns
        
    def _analyze_relationship_patterns(self, 
                                     implementations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze common patterns in relationships"""
        patterns = []
        relationship_counts = {}
        
        # Count relationship occurrences
        for impl in implementations:
            for rel in impl["characteristics"]["relationships"]:
                relationship_counts[rel] = relationship_counts.get(rel, 0) + 1
                
        # Identify common relationships
        common_relationships = [
            rel for rel, count in relationship_counts.items()
            if count >= len(implementations) * 0.7  # 70% threshold
        ]
        
        if common_relationships:
            patterns.append({
                "type": "relationship",
                "description": "Common relationships in successful implementations",
                "relationships": common_relationships,
                "confidence": min(1.0, len(common_relationships) / len(relationship_counts))
            })
            
        return patterns
        
    def _update_learning_metrics(self, 
                               pattern_type: str,
                               success_metrics: Dict[str, float]) -> None:
        """Update learning metrics"""
        metrics = PatternLearningMetrics(
            pattern_accuracy=success_metrics.get("accuracy", 0),
            pattern_coverage=success_metrics.get("coverage", 0),
            learning_rate=self._calculate_learning_rate(pattern_type),
            adaptation_success=success_metrics.get("adaptation_success", 0),
            timestamp=datetime.now()
        )
        
        self.metrics.append(metrics)
        
        # Keep only recent metrics
        if len(self.metrics) > 100:
            self.metrics.pop(0)
            
    def _calculate_learning_rate(self, pattern_type: str) -> float:
        """Calculate learning rate for a pattern type"""
        if pattern_type not in self.pattern_history:
            return 0.0
            
        implementations = self.pattern_history[pattern_type]
        if len(implementations) < 2:
            return 0.0
            
        # Calculate improvement in success rate
        success_rates = [
            impl["success_metrics"]["success_rate"]
            for impl in implementations
        ]
        
        if len(success_rates) < 2:
            return 0.0
            
        # Calculate rate of change in success rate
        return (success_rates[-1] - success_rates[0]) / len(success_rates)
        
    def get_learning_metrics(self) -> Dict[str, Any]:
        """Get current learning metrics"""
        if not self.metrics:
            return {}
            
        latest_metrics = self.metrics[-1]
        return {
            "pattern_accuracy": latest_metrics.pattern_accuracy,
            "pattern_coverage": latest_metrics.pattern_coverage,
            "learning_rate": latest_metrics.learning_rate,
            "adaptation_success": latest_metrics.adaptation_success,
            "timestamp": latest_metrics.timestamp.isoformat()
        } 