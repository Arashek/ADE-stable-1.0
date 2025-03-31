#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

# Add the model-training directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.registry.model_registry import ModelRegistry

def setup_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(description="Manage model versions in the registry")
    parser.add_argument("--registry-path", default="models/registry",
                      help="Path to the model registry")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Register command
    register_parser = subparsers.add_parser("register", help="Register a new model version")
    register_parser.add_argument("model_path", help="Path to the model files")
    register_parser.add_argument("version", help="Version string (e.g., 1.0.0)")
    register_parser.add_argument("--metadata", help="Path to metadata JSON file")
    
    # List command
    subparsers.add_parser("list", help="List all registered models")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get information about a specific model version")
    get_parser.add_argument("version", help="Version string")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update metadata for a model version")
    update_parser.add_argument("version", help="Version string")
    update_parser.add_argument("key", help="Metadata key")
    update_parser.add_argument("value", help="New value")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a model version")
    delete_parser.add_argument("version", help="Version string")
    
    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare two model versions")
    compare_parser.add_argument("version1", help="First version string")
    compare_parser.add_argument("version2", help="Second version string")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export a model version")
    export_parser.add_argument("version", help="Version string")
    export_parser.add_argument("export_path", help="Path to export the model to")
    
    return parser

def load_metadata(metadata_path: Optional[str]) -> Optional[dict]:
    """Load metadata from a JSON file if provided."""
    if not metadata_path:
        return None
    
    try:
        with open(metadata_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading metadata: {str(e)}")
        return None

def main():
    """Main entry point for the script."""
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    registry = ModelRegistry(args.registry_path)
    
    try:
        if args.command == "register":
            metadata = load_metadata(args.metadata)
            success = registry.register_model(args.model_path, args.version, metadata)
            if success:
                print(f"Successfully registered model version {args.version}")
            else:
                print(f"Failed to register model version {args.version}")
        
        elif args.command == "list":
            models = registry.list_models()
            if not models:
                print("No models registered")
            else:
                print("\nRegistered Models:")
                for model in models:
                    print(f"\nVersion: {model['version']}")
                    print(f"Registration Date: {model['registration_date']}")
                    if model['metadata']:
                        print("Metadata:")
                        for key, value in model['metadata'].items():
                            print(f"  {key}: {value}")
        
        elif args.command == "get":
            model = registry.get_model(args.version)
            if model:
                print(f"\nModel Version: {model['version']}")
                print(f"Registration Date: {model['registration_date']}")
                print(f"Path: {model['path']}")
                if model['metadata']:
                    print("Metadata:")
                    for key, value in model['metadata'].items():
                        print(f"  {key}: {value}")
            else:
                print(f"Model version {args.version} not found")
        
        elif args.command == "update":
            success = registry.update_metadata(args.version, args.key, args.value)
            if success:
                print(f"Successfully updated metadata for version {args.version}")
            else:
                print(f"Failed to update metadata for version {args.version}")
        
        elif args.command == "delete":
            success = registry.delete_model(args.version)
            if success:
                print(f"Successfully deleted model version {args.version}")
            else:
                print(f"Failed to delete model version {args.version}")
        
        elif args.command == "compare":
            try:
                comparison = registry.compare_versions(args.version1, args.version2)
                print(f"\nComparing versions {args.version1} and {args.version2}:")
                if comparison['differences']:
                    print("\nDifferences in metadata:")
                    for key, (v1_val, v2_val) in comparison['differences'].items():
                        print(f"  {key}:")
                        print(f"    {args.version1}: {v1_val}")
                        print(f"    {args.version2}: {v2_val}")
                else:
                    print("No differences found in metadata")
            except ValueError as e:
                print(str(e))
        
        elif args.command == "export":
            success = registry.export_model(args.version, args.export_path)
            if success:
                print(f"Successfully exported model version {args.version} to {args.export_path}")
            else:
                print(f"Failed to export model version {args.version}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 