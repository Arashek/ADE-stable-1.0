import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import yaml
from datasets import load_dataset, Dataset
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)

@dataclass
class DatasetConfig:
    """Configuration for dataset management"""
    name: str
    source_type: str  # local, github, cloud, public, custom
    source_config: Dict[str, Any]
    processing_config: Dict[str, Any]
    augmentation_config: Optional[Dict[str, Any]] = None

class DatasetManager:
    """Manages dataset operations including loading, processing, and augmentation"""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the dataset manager
        
        Args:
            data_dir: Directory for storing datasets
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.datasets: Dict[str, Dataset] = {}
        self.configs: Dict[str, DatasetConfig] = {}
        
    def create_dataset(self, config: DatasetConfig) -> Dataset:
        """Create a new dataset based on configuration
        
        Args:
            config: Dataset configuration
            
        Returns:
            Created dataset
        """
        try:
            # Load dataset based on source type
            dataset = self._load_dataset(config)
            
            # Process dataset
            dataset = self._process_dataset(dataset, config.processing_config)
            
            # Apply augmentation if configured
            if config.augmentation_config:
                dataset = self._augment_dataset(dataset, config.augmentation_config)
                
            # Save dataset and config
            self._save_dataset(dataset, config)
            
            return dataset
            
        except Exception as e:
            logger.error(f"Failed to create dataset: {str(e)}")
            raise
            
    def load_dataset(self, name: str) -> Dataset:
        """Load an existing dataset
        
        Args:
            name: Name of the dataset to load
            
        Returns:
            Loaded dataset
        """
        try:
            if name not in self.datasets:
                dataset_path = self.data_dir / name
                if not dataset_path.exists():
                    raise ValueError(f"Dataset {name} not found")
                    
                # Load dataset
                dataset = Dataset.load_from_disk(str(dataset_path))
                self.datasets[name] = dataset
                
                # Load config
                config_path = dataset_path / "config.yaml"
                if config_path.exists():
                    with open(config_path) as f:
                        config_dict = yaml.safe_load(f)
                        self.configs[name] = DatasetConfig(**config_dict)
                        
            return self.datasets[name]
            
        except Exception as e:
            logger.error(f"Failed to load dataset: {str(e)}")
            raise
            
    def delete_dataset(self, name: str) -> None:
        """Delete a dataset
        
        Args:
            name: Name of the dataset to delete
        """
        try:
            dataset_path = self.data_dir / name
            if dataset_path.exists():
                import shutil
                shutil.rmtree(dataset_path)
                
            if name in self.datasets:
                del self.datasets[name]
            if name in self.configs:
                del self.configs[name]
                
        except Exception as e:
            logger.error(f"Failed to delete dataset: {str(e)}")
            raise
            
    def list_datasets(self) -> List[str]:
        """List all available datasets
        
        Returns:
            List of dataset names
        """
        try:
            return [d.name for d in self.data_dir.iterdir() if d.is_dir()]
        except Exception as e:
            logger.error(f"Failed to list datasets: {str(e)}")
            raise
            
    def get_dataset_info(self, name: str) -> Dict[str, Any]:
        """Get information about a dataset
        
        Args:
            name: Name of the dataset
            
        Returns:
            Dictionary containing dataset information
        """
        try:
            dataset = self.load_dataset(name)
            config = self.configs.get(name)
            
            return {
                "name": name,
                "size": len(dataset),
                "features": dataset.features,
                "config": config.__dict__ if config else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get dataset info: {str(e)}")
            raise
            
    def _load_dataset(self, config: DatasetConfig) -> Dataset:
        """Load dataset from source based on configuration"""
        source_type = config.source_type.lower()
        source_config = config.source_config
        
        if source_type == "local":
            return self._load_local_dataset(source_config)
        elif source_type == "github":
            return self._load_github_dataset(source_config)
        elif source_type == "cloud":
            return self._load_cloud_dataset(source_config)
        elif source_type == "public":
            return self._load_public_dataset(source_config)
        elif source_type == "custom":
            return self._load_custom_dataset(source_config)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
            
    def _load_local_dataset(self, config: Dict[str, Any]) -> Dataset:
        """Load dataset from local files"""
        file_path = Path(config["path"])
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if file_path.suffix == ".csv":
            df = pd.read_csv(file_path)
        elif file_path.suffix == ".json":
            df = pd.read_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
        return Dataset.from_pandas(df)
        
    def _load_github_dataset(self, config: Dict[str, Any]) -> Dataset:
        """Load dataset from GitHub repository"""
        repo = config["repo"]
        path = config.get("path", "")
        return load_dataset(repo, path=path)
        
    def _load_cloud_dataset(self, config: Dict[str, Any]) -> Dataset:
        """Load dataset from cloud storage"""
        # Implementation depends on cloud provider
        raise NotImplementedError("Cloud storage loading not implemented")
        
    def _load_public_dataset(self, config: Dict[str, Any]) -> Dataset:
        """Load dataset from public source"""
        name = config["name"]
        subset = config.get("subset")
        return load_dataset(name, subset)
        
    def _load_custom_dataset(self, config: Dict[str, Any]) -> Dataset:
        """Load dataset using custom loading function"""
        loader = config["loader"]
        return loader(config)
        
    def _process_dataset(self, dataset: Dataset, config: Dict[str, Any]) -> Dataset:
        """Process dataset according to configuration"""
        # Shuffle if configured
        if config.get("shuffle", False):
            dataset = dataset.shuffle(seed=config.get("seed", 42))
            
        # Split dataset if configured
        if "split" in config:
            split_config = config["split"]
            train_size = split_config.get("train", 0.8)
            val_size = split_config.get("val", 0.1)
            test_size = split_config.get("test", 0.1)
            
            # First split: train and temp
            train_dataset, temp_dataset = train_test_split(
                dataset,
                train_size=train_size,
                random_state=config.get("seed", 42)
            )
            
            # Second split: validation and test
            val_ratio = val_size / (val_size + test_size)
            val_dataset, test_dataset = train_test_split(
                temp_dataset,
                train_size=val_ratio,
                random_state=config.get("seed", 42)
            )
            
            return {
                "train": train_dataset,
                "validation": val_dataset,
                "test": test_dataset
            }
            
        return dataset
        
    def _augment_dataset(self, dataset: Dataset, config: Dict[str, Any]) -> Dataset:
        """Apply data augmentation to dataset"""
        # Implementation depends on augmentation methods
        raise NotImplementedError("Data augmentation not implemented")
        
    def _save_dataset(self, dataset: Dataset, config: DatasetConfig) -> None:
        """Save dataset and configuration to disk"""
        try:
            # Create dataset directory
            dataset_dir = self.data_dir / config.name
            dataset_dir.mkdir(parents=True, exist_ok=True)
            
            # Save dataset
            dataset.save_to_disk(str(dataset_dir))
            
            # Save config
            config_path = dataset_dir / "config.yaml"
            with open(config_path, 'w') as f:
                yaml.dump(config.__dict__, f)
                
        except Exception as e:
            logger.error(f"Failed to save dataset: {str(e)}")
            raise 