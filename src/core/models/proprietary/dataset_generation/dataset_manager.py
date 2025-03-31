import os
import logging
import json
import hashlib
from typing import List, Dict, Optional, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatasetVersion:
    """Represents a version of a dataset"""
    version: str
    created_at: datetime
    description: str
    total_examples: int
    metadata: Dict
    checksum: str

class DatasetManager:
    """Manages dataset versioning, quality scoring, and format conversion"""
    
    def __init__(self, base_path: str):
        """Initialize dataset manager"""
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    def create_version(
        self,
        examples: List[Dict],
        version: str,
        description: str,
        metadata: Optional[Dict] = None
    ) -> DatasetVersion:
        """Create a new version of the dataset"""
        try:
            # Create version directory
            version_dir = self.base_path / version
            version_dir.mkdir(exist_ok=True)
            
            # Save examples
            examples_file = version_dir / "examples.jsonl"
            with open(examples_file, "w") as f:
                for example in examples:
                    f.write(json.dumps(example) + "\n")
                    
            # Calculate checksum
            checksum = self._calculate_checksum(examples_file)
            
            # Create version metadata
            version_metadata = {
                "version": version,
                "created_at": datetime.utcnow().isoformat(),
                "description": description,
                "total_examples": len(examples),
                "checksum": checksum,
                "metadata": metadata or {}
            }
            
            # Save version metadata
            metadata_file = version_dir / "metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(version_metadata, f, indent=2)
                
            logger.info(f"Created dataset version {version}")
            return DatasetVersion(**version_metadata)
            
        except Exception as e:
            logger.error(f"Error creating dataset version: {str(e)}")
            raise
            
    def load_version(self, version: str) -> Optional[List[Dict]]:
        """Load examples from a specific version"""
        try:
            version_dir = self.base_path / version
            if not version_dir.exists():
                return None
                
            examples_file = version_dir / "examples.jsonl"
            examples = []
            
            with open(examples_file) as f:
                for line in f:
                    examples.append(json.loads(line))
                    
            return examples
            
        except Exception as e:
            logger.error(f"Error loading dataset version: {str(e)}")
            return None
            
    def list_versions(self) -> List[DatasetVersion]:
        """List all available dataset versions"""
        versions = []
        
        try:
            for version_dir in self.base_path.iterdir():
                if not version_dir.is_dir():
                    continue
                    
                metadata_file = version_dir / "metadata.json"
                if not metadata_file.exists():
                    continue
                    
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    versions.append(DatasetVersion(**metadata))
                    
            return sorted(versions, key=lambda x: x.created_at, reverse=True)
            
        except Exception as e:
            logger.error(f"Error listing dataset versions: {str(e)}")
            return []
            
    def calculate_quality_scores(
        self,
        examples: List[Dict],
        metrics: Optional[List[str]] = None
    ) -> List[float]:
        """Calculate quality scores for examples"""
        if metrics is None:
            metrics = ["length", "complexity", "similarity"]
            
        scores = []
        
        for example in examples:
            example_scores = []
            
            if "length" in metrics:
                example_scores.append(self._calculate_length_score(example))
                
            if "complexity" in metrics:
                example_scores.append(self._calculate_complexity_score(example))
                
            if "similarity" in metrics:
                example_scores.append(self._calculate_similarity_score(example))
                
            # Average the scores
            scores.append(sum(example_scores) / len(example_scores))
            
        return scores
        
    def _calculate_length_score(self, example: Dict) -> float:
        """Calculate score based on input/output length"""
        input_len = len(example["input"])
        output_len = len(example["output"])
        
        # Score should be between 0 and 1
        # Prefer examples with reasonable lengths (not too short or too long)
        min_len = 50
        max_len = 1000
        
        input_score = 1.0 - abs(input_len - (min_len + max_len) / 2) / ((max_len - min_len) / 2)
        output_score = 1.0 - abs(output_len - (min_len + max_len) / 2) / ((max_len - min_len) / 2)
        
        return (input_score + output_score) / 2
        
    def _calculate_complexity_score(self, example: Dict) -> float:
        """Calculate score based on code complexity"""
        # TODO: Implement code complexity scoring
        return 0.5
        
    def _calculate_similarity_score(self, example: Dict) -> float:
        """Calculate score based on input/output similarity"""
        # Use TF-IDF and cosine similarity
        vectorizer = TfidfVectorizer()
        try:
            tfidf_matrix = vectorizer.fit_transform([example["input"], example["output"]])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return 1.0 - similarity  # Lower similarity is better
        except:
            return 0.5
            
    def deduplicate_examples(
        self,
        examples: List[Dict],
        similarity_threshold: float = 0.8
    ) -> List[Dict]:
        """Remove duplicate examples based on similarity"""
        if not examples:
            return []
            
        # Create TF-IDF matrix
        vectorizer = TfidfVectorizer()
        texts = [ex["input"] + " " + ex["output"] for ex in examples]
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Find duplicates
        unique_indices = []
        for i in range(len(examples)):
            is_duplicate = False
            for j in unique_indices:
                if similarity_matrix[i, j] > similarity_threshold:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_indices.append(i)
                
        return [examples[i] for i in unique_indices]
        
    def convert_format(
        self,
        examples: List[Dict],
        target_format: str,
        output_path: Optional[str] = None
    ) -> Union[pd.DataFrame, str]:
        """Convert dataset to different formats"""
        if target_format == "csv":
            df = pd.DataFrame(examples)
            if output_path:
                df.to_csv(output_path, index=False)
            return df
            
        elif target_format == "jsonl":
            if output_path:
                with open(output_path, "w") as f:
                    for example in examples:
                        f.write(json.dumps(example) + "\n")
                return output_path
            return "\n".join(json.dumps(ex) for ex in examples)
            
        elif target_format == "huggingface":
            # Convert to HuggingFace dataset format
            if output_path:
                output_dir = Path(output_path)
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Save as JSONL
                examples_file = output_dir / "examples.jsonl"
                with open(examples_file, "w") as f:
                    for example in examples:
                        f.write(json.dumps(example) + "\n")
                        
                # Create dataset info
                info = {
                    "features": {
                        "input": {"dtype": "string"},
                        "output": {"dtype": "string"},
                        "metadata": {"dtype": "dict"},
                        "quality_score": {"dtype": "float"}
                    },
                    "splits": {
                        "train": {
                            "num_examples": len(examples),
                            "shard_lengths": [len(examples)]
                        }
                    }
                }
                
                info_file = output_dir / "dataset_info.json"
                with open(info_file, "w") as f:
                    json.dump(info, f, indent=2)
                    
                return str(output_dir)
                
        else:
            raise ValueError(f"Unsupported format: {target_format}")
            
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest() 