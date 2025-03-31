import os
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProcessingConfig:
    """Configuration for dataset processing"""
    source_type: str  # github, documentation, synthetic
    language: str
    min_quality_score: float = 0.7
    max_examples: Optional[int] = None
    context_window: int = 5  # Number of lines before/after for context
    include_metadata: bool = True

@dataclass
class ProcessedExample:
    """Represents a processed example with metadata"""
    input_text: str
    output_text: str
    metadata: Dict[str, Any]
    quality_score: float = 1.0

class BaseProcessor(ABC):
    """Base class for dataset processors"""
    
    def __init__(self, config: ProcessingConfig):
        """Initialize the processor"""
        self.config = config
        self.examples: List[ProcessedExample] = []
        
    @abstractmethod
    def process_source(self, source_path: str) -> List[ProcessedExample]:
        """Process the source data into examples"""
        pass
        
    @abstractmethod
    def validate_example(self, example: ProcessedExample) -> bool:
        """Validate a processed example"""
        pass
        
    def add_example(self, example: ProcessedExample):
        """Add a validated example to the dataset"""
        if self.validate_example(example):
            self.examples.append(example)
            
    def get_examples(self) -> List[ProcessedExample]:
        """Get all processed examples"""
        return self.examples
        
    def save_examples(self, output_path: str):
        """Save processed examples to disk"""
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save examples
        examples_file = output_dir / "examples.jsonl"
        with open(examples_file, "w", encoding="utf-8") as f:
            for example in self.examples:
                f.write(self._example_to_jsonl(example) + "\n")
                
        # Save metadata
        metadata = {
            "config": self.config.__dict__,
            "total_examples": len(self.examples),
            "language": self.config.language,
            "source_type": self.config.source_type
        }
        
        metadata_file = output_dir / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
            
        logger.info(f"Saved {len(self.examples)} examples to {output_path}")
        
    def load_examples(self, input_path: str):
        """Load processed examples from disk"""
        input_dir = Path(input_path)
        
        # Load examples
        examples_file = input_dir / "examples.jsonl"
        self.examples = []
        with open(examples_file, "r", encoding="utf-8") as f:
            for line in f:
                self.examples.append(self._jsonl_to_example(line))
                
        logger.info(f"Loaded {len(self.examples)} examples from {input_path}")
        
    def _example_to_jsonl(self, example: ProcessedExample) -> str:
        """Convert example to JSONL format"""
        return json.dumps({
            "input": example.input_text,
            "output": example.output_text,
            "metadata": example.metadata,
            "quality_score": example.quality_score
        })
        
    def _jsonl_to_example(self, jsonl: str) -> ProcessedExample:
        """Convert JSONL to example"""
        data = json.loads(jsonl)
        return ProcessedExample(
            input_text=data["input"],
            output_text=data["output"],
            metadata=data["metadata"],
            quality_score=data["quality_score"]
        )
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get dataset statistics"""
        return {
            "total_examples": len(self.examples),
            "average_quality_score": sum(ex.quality_score for ex in self.examples) / len(self.examples) if self.examples else 0,
            "language": self.config.language,
            "source_type": self.config.source_type
        } 