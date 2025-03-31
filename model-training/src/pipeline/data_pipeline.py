import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
import shutil
import pandas as pd
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DataSource:
    """Represents a data source in the pipeline."""
    name: str
    path: str
    type: str  # e.g., "csv", "json", "parquet"
    schema: Optional[Dict] = None
    last_updated: Optional[datetime] = None

@dataclass
class DataTransform:
    """Represents a data transformation step."""
    name: str
    input_sources: List[str]
    output_schema: Dict
    transform_function: callable

class DataPipeline:
    """Manages the flow of data from ADE learning infrastructure to model training."""
    
    def __init__(self, pipeline_config: Dict):
        """
        Initialize the data pipeline.
        
        Args:
            pipeline_config: Configuration dictionary containing pipeline settings
        """
        self.config = pipeline_config
        self.data_dir = Path(pipeline_config.get("data_dir", "data"))
        self.sources: Dict[str, DataSource] = {}
        self.transforms: Dict[str, DataTransform] = {}
        self._setup_directories()
    
    def _setup_directories(self):
        """Create necessary directories for the pipeline."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "raw").mkdir(exist_ok=True)
        (self.data_dir / "processed").mkdir(exist_ok=True)
        (self.data_dir / "training").mkdir(exist_ok=True)
    
    def add_source(self, source: DataSource):
        """
        Add a data source to the pipeline.
        
        Args:
            source: DataSource object to add
        """
        self.sources[source.name] = source
        logger.info(f"Added data source: {source.name}")
    
    def add_transform(self, transform: DataTransform):
        """
        Add a data transformation step to the pipeline.
        
        Args:
            transform: DataTransform object to add
        """
        self.transforms[transform.name] = transform
        logger.info(f"Added transform: {transform.name}")
    
    def fetch_data(self, source_name: str) -> bool:
        """
        Fetch data from a source.
        
        Args:
            source_name: Name of the source to fetch from
            
        Returns:
            bool: True if fetch was successful
        """
        if source_name not in self.sources:
            logger.error(f"Source {source_name} not found")
            return False
        
        source = self.sources[source_name]
        try:
            # Implement source-specific fetching logic here
            # This is a placeholder for actual implementation
            logger.info(f"Fetching data from {source_name}")
            return True
        except Exception as e:
            logger.error(f"Error fetching data from {source_name}: {str(e)}")
            return False
    
    def apply_transform(self, transform_name: str) -> bool:
        """
        Apply a transformation step.
        
        Args:
            transform_name: Name of the transform to apply
            
        Returns:
            bool: True if transform was successful
        """
        if transform_name not in self.transforms:
            logger.error(f"Transform {transform_name} not found")
            return False
        
        transform = self.transforms[transform_name]
        try:
            # Load input data
            input_data = {}
            for source_name in transform.input_sources:
                if source_name not in self.sources:
                    logger.error(f"Input source {source_name} not found")
                    return False
                input_data[source_name] = self._load_data(self.sources[source_name])
            
            # Apply transformation
            output_data = transform.transform_function(input_data)
            
            # Save transformed data
            output_path = self.data_dir / "processed" / f"{transform_name}.parquet"
            self._save_data(output_data, output_path)
            
            logger.info(f"Successfully applied transform: {transform_name}")
            return True
        except Exception as e:
            logger.error(f"Error applying transform {transform_name}: {str(e)}")
            return False
    
    def prepare_training_data(self, transform_name: str) -> bool:
        """
        Prepare data for model training.
        
        Args:
            transform_name: Name of the transform to use
            
        Returns:
            bool: True if preparation was successful
        """
        try:
            # Load processed data
            processed_path = self.data_dir / "processed" / f"{transform_name}.parquet"
            if not processed_path.exists():
                logger.error(f"Processed data not found for transform: {transform_name}")
                return False
            
            data = self._load_data(processed_path)
            
            # Split data into training and validation sets
            # This is a placeholder for actual implementation
            train_data = data.sample(frac=0.8, random_state=42)
            val_data = data.drop(train_data.index)
            
            # Save training data
            train_path = self.data_dir / "training" / "train.parquet"
            val_path = self.data_dir / "training" / "val.parquet"
            
            self._save_data(train_data, train_path)
            self._save_data(val_data, val_path)
            
            logger.info("Successfully prepared training data")
            return True
        except Exception as e:
            logger.error(f"Error preparing training data: {str(e)}")
            return False
    
    def _load_data(self, source: Union[DataSource, Path]) -> pd.DataFrame:
        """
        Load data from a source or path.
        
        Args:
            source: DataSource object or Path to load from
            
        Returns:
            pd.DataFrame: Loaded data
        """
        if isinstance(source, DataSource):
            path = Path(source.path)
        else:
            path = source
        
        if path.suffix == '.csv':
            return pd.read_csv(path)
        elif path.suffix == '.parquet':
            return pd.read_parquet(path)
        elif path.suffix == '.json':
            return pd.read_json(path)
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")
    
    def _save_data(self, data: pd.DataFrame, path: Path):
        """
        Save data to a file.
        
        Args:
            data: DataFrame to save
            path: Path to save to
        """
        if path.suffix == '.csv':
            data.to_csv(path, index=False)
        elif path.suffix == '.parquet':
            data.to_parquet(path, index=False)
        elif path.suffix == '.json':
            data.to_json(path, orient='records')
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")
    
    def validate_data(self, data: pd.DataFrame, schema: Dict) -> bool:
        """
        Validate data against a schema.
        
        Args:
            data: DataFrame to validate
            schema: Schema to validate against
            
        Returns:
            bool: True if validation was successful
        """
        try:
            # Check required columns
            required_cols = schema.get("required_columns", [])
            missing_cols = [col for col in required_cols if col not in data.columns]
            if missing_cols:
                logger.error(f"Missing required columns: {missing_cols}")
                return False
            
            # Check data types
            for col, dtype in schema.get("column_types", {}).items():
                if col in data.columns and not pd.api.types.is_dtype_equal(data[col].dtype, dtype):
                    logger.error(f"Column {col} has incorrect data type")
                    return False
            
            # Check value constraints
            for col, constraints in schema.get("constraints", {}).items():
                if col in data.columns:
                    if "min" in constraints and data[col].min() < constraints["min"]:
                        logger.error(f"Column {col} violates minimum value constraint")
                        return False
                    if "max" in constraints and data[col].max() > constraints["max"]:
                        logger.error(f"Column {col} violates maximum value constraint")
                        return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating data: {str(e)}")
            return False
    
    def run_pipeline(self) -> bool:
        """
        Run the complete data pipeline.
        
        Returns:
            bool: True if pipeline execution was successful
        """
        try:
            # Fetch data from all sources
            for source_name in self.sources:
                if not self.fetch_data(source_name):
                    return False
            
            # Apply all transforms
            for transform_name in self.transforms:
                if not self.apply_transform(transform_name):
                    return False
            
            # Prepare training data
            if not self.prepare_training_data(self.transforms.keys()[-1]):
                return False
            
            logger.info("Pipeline execution completed successfully")
            return True
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            return False 