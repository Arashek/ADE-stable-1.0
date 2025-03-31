import os
import logging
import json
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime
import streamlit as st
import pandas as pd
from .generator import DatasetGenerator, GenerationConfig
from .github_integration import GitHubIntegration
from .dataset_manager import DatasetManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InteractiveInterface:
    """Interactive interface for dataset creation"""
    
    def __init__(
        self,
        generator: DatasetGenerator,
        github: GitHubIntegration,
        dataset_manager: DatasetManager
    ):
        """Initialize the interface"""
        self.generator = generator
        self.github = github
        self.dataset_manager = dataset_manager
        
    def run(self):
        """Run the interactive interface"""
        st.set_page_config(
            page_title="ADE Dataset Generator",
            page_icon="📊",
            layout="wide"
        )
        
        st.title("ADE Dataset Generator")
        
        # Sidebar for configuration
        with st.sidebar:
            st.header("Configuration")
            
            # Generation strategy
            strategy = st.selectbox(
                "Generation Strategy",
                ["code_pair", "bug_fix", "comment_code", "project_structure"]
            )
            
            # Language
            language = st.text_input("Programming Language", "python")
            
            # GitHub parameters
            min_stars = st.number_input("Minimum Stars", min_value=0, value=100)
            min_activity = st.number_input("Minimum Activity (days)", min_value=0, value=30)
            
            # Quality parameters
            quality_threshold = st.slider(
                "Quality Threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1
            )
            
            # Deduplication
            deduplicate = st.checkbox("Enable Deduplication", value=True)
            
            # Version
            version = st.text_input("Dataset Version", "1.0.0")
            
            # Description
            description = st.text_area("Dataset Description")
            
            # Generate button
            if st.button("Generate Dataset"):
                self._generate_dataset(
                    strategy=strategy,
                    language=language,
                    min_stars=min_stars,
                    min_activity=min_activity,
                    quality_threshold=quality_threshold,
                    deduplicate=deduplicate,
                    version=version,
                    description=description
                )
                
        # Main content area
        st.header("Dataset Preview")
        
        # Load existing dataset if available
        versions = self.dataset_manager.list_versions()
        if versions:
            selected_version = st.selectbox(
                "Select Version",
                options=[v.version for v in versions],
                format_func=lambda x: f"{x} ({versions[0].created_at.strftime('%Y-%m-%d')})"
            )
            
            if selected_version:
                examples = self.dataset_manager.load_version(selected_version)
                if examples:
                    self._display_examples(examples)
                    
    def _generate_dataset(
        self,
        strategy: str,
        language: str,
        min_stars: int,
        min_activity: int,
        quality_threshold: float,
        deduplicate: bool,
        version: str,
        description: str
    ):
        """Generate a new dataset"""
        try:
            with st.spinner("Generating dataset..."):
                # Create generation config
                config = GenerationConfig(
                    strategy=strategy,
                    language=language,
                    min_stars=min_stars,
                    min_activity=min_activity,
                    quality_threshold=quality_threshold,
                    deduplicate=deduplicate,
                    version=version
                )
                
                # Generate examples
                examples = self.generator.generate_examples(config)
                
                # Calculate quality scores
                quality_scores = self.dataset_manager.calculate_quality_scores(examples)
                
                # Add quality scores to examples
                for example, score in zip(examples, quality_scores):
                    example["quality_score"] = score
                    
                # Filter by quality threshold
                examples = [
                    ex for ex, score in zip(examples, quality_scores)
                    if score >= quality_threshold
                ]
                
                # Deduplicate if enabled
                if deduplicate:
                    examples = self.dataset_manager.deduplicate_examples(examples)
                    
                # Create dataset version
                self.dataset_manager.create_version(
                    examples=examples,
                    version=version,
                    description=description,
                    metadata={
                        "strategy": strategy,
                        "language": language,
                        "min_stars": min_stars,
                        "min_activity": min_activity,
                        "quality_threshold": quality_threshold,
                        "deduplicate": deduplicate
                    }
                )
                
                st.success(f"Generated {len(examples)} examples")
                self._display_examples(examples)
                
        except Exception as e:
            st.error(f"Error generating dataset: {str(e)}")
            logger.error(f"Error generating dataset: {str(e)}")
            
    def _display_examples(self, examples: List[Dict]):
        """Display examples in the interface"""
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Table View", "Card View", "Statistics"])
        
        with tab1:
            # Convert to DataFrame for table view
            df = pd.DataFrame(examples)
            st.dataframe(df)
            
        with tab2:
            # Display examples as cards
            for i, example in enumerate(examples):
                with st.expander(f"Example {i+1} (Score: {example['quality_score']:.2f})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Input")
                        st.code(example["input"], language=example.get("language", "python"))
                        
                    with col2:
                        st.subheader("Output")
                        st.code(example["output"], language=example.get("language", "python"))
                        
                    if "metadata" in example:
                        st.subheader("Metadata")
                        st.json(example["metadata"])
                        
        with tab3:
            # Display statistics
            st.subheader("Dataset Statistics")
            
            # Basic stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Examples", len(examples))
            with col2:
                avg_score = sum(ex["quality_score"] for ex in examples) / len(examples)
                st.metric("Average Quality Score", f"{avg_score:.2f}")
            with col3:
                st.metric("Language", examples[0].get("language", "python"))
                
            # Quality score distribution
            scores = [ex["quality_score"] for ex in examples]
            st.line_chart(pd.Series(scores).value_counts().sort_index())
            
            # Export options
            st.subheader("Export Options")
            export_format = st.selectbox(
                "Export Format",
                ["csv", "jsonl", "huggingface"]
            )
            
            if st.button("Export Dataset"):
                try:
                    output_path = f"dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    self.dataset_manager.convert_format(
                        examples=examples,
                        target_format=export_format,
                        output_path=output_path
                    )
                    st.success(f"Dataset exported to {output_path}")
                except Exception as e:
                    st.error(f"Error exporting dataset: {str(e)}")
                    
def main():
    """Main function to run the interface"""
    try:
        # Initialize components
        generator = DatasetGenerator()
        github = GitHubIntegration()
        dataset_manager = DatasetManager("datasets")
        
        # Create and run interface
        interface = InteractiveInterface(generator, github, dataset_manager)
        interface.run()
        
    except Exception as e:
        logger.error(f"Error running interface: {str(e)}")
        st.error(f"Error running interface: {str(e)}")
        
if __name__ == "__main__":
    main() 