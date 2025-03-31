from typing import Dict, Any, List, Optional
from datetime import datetime
from .models import LearningModel, Dataset, KnowledgeEntry
from ...config.logging_config import logger

class KnowledgeBase:
    """Knowledge base for managing and updating knowledge"""
    
    def __init__(self):
        self.entries: Dict[str, KnowledgeEntry] = {}
        self.relationships: Dict[str, List[str]] = {}
        
    async def extract_new_knowledge(self,
                                  models: Dict[str, LearningModel],
                                  datasets: Dict[str, Dataset]) -> List[Dict[str, Any]]:
        """Extract new knowledge from models and datasets"""
        try:
            new_knowledge = []
            
            # Extract knowledge from models
            for model_id, model in models.items():
                model_knowledge = self._extract_model_knowledge(model)
                if model_knowledge:
                    new_knowledge.extend(model_knowledge)
                    
            # Extract knowledge from datasets
            for dataset_id, dataset in datasets.items():
                dataset_knowledge = self._extract_dataset_knowledge(dataset)
                if dataset_knowledge:
                    new_knowledge.extend(dataset_knowledge)
                    
            return new_knowledge
            
        except Exception as e:
            logger.error(f"Error extracting new knowledge: {str(e)}")
            return []
            
    def _extract_model_knowledge(self, model: LearningModel) -> List[Dict[str, Any]]:
        """Extract knowledge from a model"""
        try:
            knowledge = []
            
            # Extract model architecture knowledge
            architecture_knowledge = {
                "type": "model_architecture",
                "content": {
                    "model_type": model.type,
                    "parameters": model.parameters,
                    "metrics": model.metrics
                },
                "source": f"model_{model.id}",
                "confidence": 0.9
            }
            knowledge.append(architecture_knowledge)
            
            # Extract performance knowledge
            performance_knowledge = {
                "type": "model_performance",
                "content": {
                    "metrics": model.metrics,
                    "version": model.version
                },
                "source": f"model_{model.id}",
                "confidence": 0.8
            }
            knowledge.append(performance_knowledge)
            
            return knowledge
            
        except Exception as e:
            logger.error(f"Error extracting model knowledge: {str(e)}")
            return []
            
    def _extract_dataset_knowledge(self, dataset: Dataset) -> List[Dict[str, Any]]:
        """Extract knowledge from a dataset"""
        try:
            knowledge = []
            
            # Extract data characteristics
            characteristics = self._analyze_dataset_characteristics(dataset)
            characteristics_knowledge = {
                "type": "data_characteristics",
                "content": characteristics,
                "source": f"dataset_{dataset.id}",
                "confidence": 0.85
            }
            knowledge.append(characteristics_knowledge)
            
            # Extract data patterns
            patterns = self._analyze_data_patterns(dataset)
            patterns_knowledge = {
                "type": "data_patterns",
                "content": patterns,
                "source": f"dataset_{dataset.id}",
                "confidence": 0.75
            }
            knowledge.append(patterns_knowledge)
            
            return knowledge
            
        except Exception as e:
            logger.error(f"Error extracting dataset knowledge: {str(e)}")
            return []
            
    def _analyze_dataset_characteristics(self, dataset: Dataset) -> Dict[str, Any]:
        """Analyze dataset characteristics"""
        try:
            characteristics = {
                "size": len(dataset.data),
                "features": set(),
                "targets": set(),
                "metadata": dataset.metadata
            }
            
            for entry in dataset.data:
                # Extract features
                features = entry.get("features", {})
                characteristics["features"].update(features.keys())
                
                # Extract targets
                target = entry.get("target")
                if target is not None:
                    characteristics["targets"].add(type(target).__name__)
                    
            # Convert sets to lists for JSON serialization
            characteristics["features"] = list(characteristics["features"])
            characteristics["targets"] = list(characteristics["targets"])
            
            return characteristics
            
        except Exception as e:
            logger.error(f"Error analyzing dataset characteristics: {str(e)}")
            return {}
            
    def _analyze_data_patterns(self, dataset: Dataset) -> Dict[str, Any]:
        """Analyze patterns in the dataset"""
        try:
            patterns = {
                "feature_correlations": {},
                "value_distributions": {},
                "missing_values": {}
            }
            
            # Analyze feature correlations
            for entry in dataset.data:
                features = entry.get("features", {})
                for feature, value in features.items():
                    if feature not in patterns["value_distributions"]:
                        patterns["value_distributions"][feature] = {}
                        
                    value_type = type(value).__name__
                    if value_type not in patterns["value_distributions"][feature]:
                        patterns["value_distributions"][feature][value_type] = 0
                    patterns["value_distributions"][feature][value_type] += 1
                    
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing data patterns: {str(e)}")
            return {}
            
    async def update(self, new_knowledge: List[Dict[str, Any]]):
        """Update knowledge base with new knowledge"""
        try:
            for knowledge in new_knowledge:
                entry = KnowledgeEntry(**knowledge)
                self.entries[entry.id] = entry
                
                # Update relationships
                self._update_relationships(entry)
                
        except Exception as e:
            logger.error(f"Error updating knowledge base: {str(e)}")
            
    def _update_relationships(self, entry: KnowledgeEntry):
        """Update relationships between knowledge entries"""
        try:
            if entry.id not in self.relationships:
                self.relationships[entry.id] = []
                
            # Find related entries based on content
            for other_id, other_entry in self.entries.items():
                if other_id != entry.id:
                    if self._are_entries_related(entry, other_entry):
                        self.relationships[entry.id].append(other_id)
                        
        except Exception as e:
            logger.error(f"Error updating relationships: {str(e)}")
            
    def _are_entries_related(self, entry1: KnowledgeEntry, entry2: KnowledgeEntry) -> bool:
        """Check if two knowledge entries are related"""
        try:
            # Check type similarity
            if entry1.type == entry2.type:
                return True
                
            # Check content overlap
            content1 = set(str(v) for v in entry1.content.values())
            content2 = set(str(v) for v in entry2.content.values())
            
            overlap = content1.intersection(content2)
            return len(overlap) > 0
            
        except Exception as e:
            logger.error(f"Error checking entry relationships: {str(e)}")
            return False
            
    def get_related_knowledge(self, entry_id: str) -> List[KnowledgeEntry]:
        """Get knowledge entries related to a specific entry"""
        try:
            if entry_id not in self.relationships:
                return []
                
            related_entries = []
            for related_id in self.relationships[entry_id]:
                if related_id in self.entries:
                    related_entries.append(self.entries[related_id])
                    
            return related_entries
            
        except Exception as e:
            logger.error(f"Error getting related knowledge: {str(e)}")
            return []
            
    def search_knowledge(self, query: str) -> List[KnowledgeEntry]:
        """Search knowledge base for entries matching a query"""
        try:
            results = []
            query_terms = query.lower().split()
            
            for entry in self.entries.values():
                # Search in content
                content_str = str(entry.content).lower()
                if all(term in content_str for term in query_terms):
                    results.append(entry)
                    
            return results
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return []
            
    def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get summary of knowledge base"""
        try:
            summary = {
                "total_entries": len(self.entries),
                "entry_types": {},
                "relationships": len(self.relationships),
                "last_updated": None
            }
            
            # Count entries by type
            for entry in self.entries.values():
                if entry.type not in summary["entry_types"]:
                    summary["entry_types"][entry.type] = 0
                summary["entry_types"][entry.type] += 1
                
            # Get last update time
            if self.entries:
                summary["last_updated"] = max(
                    entry.updated_at for entry in self.entries.values()
                ).isoformat()
                
            return summary
            
        except Exception as e:
            logger.error(f"Error getting knowledge summary: {str(e)}")
            return {} 