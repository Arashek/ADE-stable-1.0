#!/usr/bin/env python3
import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

# Add the model-training directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.pipeline.data_pipeline import DataPipeline, DataSource, DataTransform

def setup_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(description="Run the ADE data pipeline")
    parser.add_argument("--config", required=True,
                      help="Path to pipeline configuration file")
    parser.add_argument("--data-dir", default="data",
                      help="Directory for data storage")
    parser.add_argument("--log-level", default="INFO",
                      choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                      help="Logging level")
    return parser

def load_config(config_path: str) -> dict:
    """
    Load pipeline configuration from file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        dict: Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
        sys.exit(1)

def create_data_sources(config: dict) -> list:
    """
    Create DataSource objects from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        list: List of DataSource objects
    """
    sources = []
    for source_config in config.get("sources", []):
        source = DataSource(
            name=source_config["name"],
            path=source_config["path"],
            type=source_config["type"],
            schema=source_config.get("schema"),
            last_updated=datetime.fromisoformat(source_config["last_updated"])
            if "last_updated" in source_config else None
        )
        sources.append(source)
    return sources

def create_data_transforms(config: dict) -> list:
    """
    Create DataTransform objects from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        list: List of DataTransform objects
    """
    transforms = []
    for transform_config in config.get("transforms", []):
        transform = DataTransform(
            name=transform_config["name"],
            input_sources=transform_config["input_sources"],
            output_schema=transform_config["output_schema"],
            transform_function=eval(transform_config["transform_function"])
        )
        transforms.append(transform)
    return transforms

def main():
    """Main entry point for the script."""
    parser = setup_parser()
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Update configuration with command line arguments
    config["data_dir"] = args.data_dir
    
    # Create pipeline
    pipeline = DataPipeline(config)
    
    # Add data sources
    for source in create_data_sources(config):
        pipeline.add_source(source)
    
    # Add transforms
    for transform in create_data_transforms(config):
        pipeline.add_transform(transform)
    
    # Run pipeline
    success = pipeline.run_pipeline()
    
    if success:
        print("Pipeline execution completed successfully")
    else:
        print("Pipeline execution failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 