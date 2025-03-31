import os
import logging
import argparse
from typing import List, Dict, Any
from pathlib import Path
from processors.base import ProcessingConfig
from processors.code_understanding import CodeUnderstandingProcessor
from processors.code_completion import CodeCompletionProcessor
from processors.tool_usage import ToolUsageProcessor
from processors.multi_turn import MultiTurnProcessor
from dataset_manager import DatasetManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_dataset(
    output_dir: str,
    language: str = "python",
    min_quality_score: float = 0.7,
    max_examples: int = 10000,
    context_window: int = 100,
    include_metadata: bool = True
) -> None:
    """Generate a complete dataset using all processors"""
    try:
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize dataset manager
        dataset_manager = DatasetManager(str(output_path))
        
        # Create processing config
        config = ProcessingConfig(
            source_type="github",
            language=language,
            min_quality_score=min_quality_score,
            max_examples=max_examples,
            context_window=context_window,
            include_metadata=include_metadata
        )
        
        # Initialize processors
        processors = {
            "code_understanding": CodeUnderstandingProcessor(config),
            "code_completion": CodeCompletionProcessor(config),
            "tool_usage": ToolUsageProcessor(config),
            "multi_turn": MultiTurnProcessor(config)
        }
        
        # Process each dataset type
        for dataset_type, processor in processors.items():
            try:
                logger.info(f"Generating {dataset_type} dataset...")
                
                # Create source directory
                source_path = output_path / "sources" / dataset_type
                source_path.mkdir(parents=True, exist_ok=True)
                
                # Process source
                examples = processor.process_source(str(source_path))
                
                # Calculate quality scores
                examples = processor.calculate_quality_scores(examples)
                
                # Filter by quality
                examples = [
                    example for example in examples
                    if example.quality_score >= min_quality_score
                ]
                
                # Limit examples
                if max_examples:
                    examples = examples[:max_examples]
                    
                # Create dataset version
                version = dataset_manager.create_version(
                    examples=examples,
                    version=f"{dataset_type}_v1",
                    description=f"{dataset_type} dataset generated from GitHub repositories"
                )
                
                logger.info(f"Generated {len(examples)} examples for {dataset_type}")
                
            except Exception as e:
                logger.error(f"Error generating {dataset_type} dataset: {str(e)}")
                continue
                
        logger.info("Dataset generation completed successfully")
        
    except Exception as e:
        logger.error(f"Error generating dataset: {str(e)}")
        raise

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Generate AI training dataset")
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Output directory for the dataset"
    )
    parser.add_argument(
        "--language",
        type=str,
        default="python",
        help="Programming language to focus on"
    )
    parser.add_argument(
        "--min-quality-score",
        type=float,
        default=0.7,
        help="Minimum quality score for examples"
    )
    parser.add_argument(
        "--max-examples",
        type=int,
        default=10000,
        help="Maximum number of examples per dataset type"
    )
    parser.add_argument(
        "--context-window",
        type=int,
        default=100,
        help="Context window size for code snippets"
    )
    parser.add_argument(
        "--include-metadata",
        action="store_true",
        help="Include metadata in examples"
    )
    
    args = parser.parse_args()
    
    generate_dataset(
        output_dir=args.output_dir,
        language=args.language,
        min_quality_score=args.min_quality_score,
        max_examples=args.max_examples,
        context_window=args.context_window,
        include_metadata=args.include_metadata
    )

if __name__ == "__main__":
    main() 