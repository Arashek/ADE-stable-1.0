import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class ModelRegistry:
    def __init__(self, registry_path: str):
        self.registry_path = Path(registry_path)
        self.metadata_file = self.registry_path / "metadata.json"
        self.models_dir = self.registry_path / "models"
        self._ensure_registry_structure()
        self.metadata = self._load_metadata()

    def _ensure_registry_structure(self):
        """Create registry directory structure if it doesn't exist."""
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        
        if not self.metadata_file.exists():
            self._save_metadata({})

    def _load_metadata(self) -> Dict:
        """Load registry metadata from file."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_metadata(self, metadata: Dict):
        """Save registry metadata to file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    def register_model(self, model_path: str, version: str, metadata: Optional[Dict] = None) -> bool:
        """
        Register a new model version in the registry.
        
        Args:
            model_path: Path to the model files
            version: Version string (e.g., "1.0.0")
            metadata: Additional metadata about the model
            
        Returns:
            bool: True if registration was successful
        """
        try:
            # Create version directory
            version_dir = self.models_dir / version
            version_dir.mkdir(exist_ok=True)

            # Copy model files
            model_path = Path(model_path)
            if model_path.is_file():
                shutil.copy2(model_path, version_dir)
            else:
                shutil.copytree(model_path, version_dir, dirs_exist_ok=True)

            # Update metadata
            model_metadata = {
                "version": version,
                "registration_date": datetime.now().isoformat(),
                "path": str(version_dir),
                "metadata": metadata or {}
            }

            self.metadata[version] = model_metadata
            self._save_metadata(self.metadata)

            return True
        except Exception as e:
            print(f"Error registering model: {str(e)}")
            return False

    def get_model(self, version: str) -> Optional[Dict]:
        """
        Get model information for a specific version.
        
        Args:
            version: Version string
            
        Returns:
            Optional[Dict]: Model metadata if found, None otherwise
        """
        return self.metadata.get(version)

    def list_models(self) -> List[Dict]:
        """
        List all registered models.
        
        Returns:
            List[Dict]: List of model metadata
        """
        return list(self.metadata.values())

    def update_metadata(self, version: str, key: str, value: any) -> bool:
        """
        Update metadata for a specific model version.
        
        Args:
            version: Version string
            key: Metadata key
            value: New value
            
        Returns:
            bool: True if update was successful
        """
        if version not in self.metadata:
            return False

        self.metadata[version]["metadata"][key] = value
        self._save_metadata(self.metadata)
        return True

    def delete_model(self, version: str) -> bool:
        """
        Delete a model version from the registry.
        
        Args:
            version: Version string
            
        Returns:
            bool: True if deletion was successful
        """
        if version not in self.metadata:
            return False

        try:
            # Remove model files
            version_dir = self.models_dir / version
            if version_dir.exists():
                shutil.rmtree(version_dir)

            # Update metadata
            del self.metadata[version]
            self._save_metadata(self.metadata)
            return True
        except Exception as e:
            print(f"Error deleting model: {str(e)}")
            return False

    def get_latest_version(self) -> Optional[str]:
        """
        Get the latest model version.
        
        Returns:
            Optional[str]: Latest version string if any models exist
        """
        if not self.metadata:
            return None

        versions = list(self.metadata.keys())
        return max(versions, key=lambda v: [int(x) for x in v.split('.')])

    def compare_versions(self, version1: str, version2: str) -> Dict:
        """
        Compare two model versions.
        
        Args:
            version1: First version string
            version2: Second version string
            
        Returns:
            Dict: Comparison results
        """
        if version1 not in self.metadata or version2 not in self.metadata:
            raise ValueError("One or both versions not found in registry")

        v1_meta = self.metadata[version1]
        v2_meta = self.metadata[version2]

        return {
            "version1": v1_meta,
            "version2": v2_meta,
            "differences": {
                k: (v1_meta["metadata"].get(k), v2_meta["metadata"].get(k))
                for k in set(v1_meta["metadata"]) | set(v2_meta["metadata"])
                if v1_meta["metadata"].get(k) != v2_meta["metadata"].get(k)
            }
        }

    def export_model(self, version: str, export_path: str) -> bool:
        """
        Export a model version to a specified location.
        
        Args:
            version: Version string
            export_path: Path to export the model to
            
        Returns:
            bool: True if export was successful
        """
        if version not in self.metadata:
            return False

        try:
            source_path = self.metadata[version]["path"]
            export_path = Path(export_path)
            
            if Path(source_path).is_file():
                shutil.copy2(source_path, export_path)
            else:
                shutil.copytree(source_path, export_path, dirs_exist_ok=True)
            
            return True
        except Exception as e:
            print(f"Error exporting model: {str(e)}")
            return False 