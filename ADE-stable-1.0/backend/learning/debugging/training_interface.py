from typing import Dict, Any, List, Optional
import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
import json
from datetime import datetime
from .dataset_generator import DebuggingDatasetGenerator
from .evaluator import DebuggingEvaluator
from ...config.logging_config import logger

class DebuggingTrainingInterface:
    """Interface for debugging training with visualization tools"""
    
    def __init__(self):
        self.dataset_generator = DebuggingDatasetGenerator()
        self.evaluator = DebuggingEvaluator()
        self.current_example = None
        self.user_solution = None
        self.evaluation_results = None
        
    def run_training_session(self):
        """Run the training interface"""
        try:
            st.title("Debugging Training Interface")
            
            # Sidebar for controls
            with st.sidebar:
                st.header("Training Controls")
                error_type = st.selectbox(
                    "Select Error Type",
                    ["syntax", "runtime", "logical", "concurrency", "security"]
                )
                num_examples = st.slider("Number of Examples", 1, 10, 5)
                
                if st.button("Generate Examples"):
                    self._generate_examples(error_type, num_examples)
                    
            # Main content area
            if self.current_example:
                self._display_example()
                self._display_visualizations()
                self._display_evaluation()
                
        except Exception as e:
            logger.error(f"Error running training session: {str(e)}")
            st.error("An error occurred while running the training session")
            
    def _generate_examples(self, error_type: str, num_examples: int):
        """Generate training examples"""
        try:
            examples = self.dataset_generator.generate_dataset(num_examples)
            if examples:
                self.current_example = examples[0]
                st.success(f"Generated {num_examples} examples")
            else:
                st.error("Failed to generate examples")
                
        except Exception as e:
            logger.error(f"Error generating examples: {str(e)}")
            st.error("Failed to generate examples")
            
    def _display_example(self):
        """Display the current example"""
        try:
            st.header("Current Example")
            
            # Display buggy code
            st.subheader("Buggy Code")
            st.code(self.current_example["buggy_code"], language="python")
            
            # User solution input
            st.subheader("Your Solution")
            self.user_solution = st.text_area(
                "Enter your solution",
                value=self.current_example["buggy_code"],
                height=200
            )
            
            # Submit button
            if st.button("Submit Solution"):
                self._evaluate_solution()
                
            # Show error message
            st.subheader("Error Message")
            st.error(self.current_example["error_message"])
            
            # Show explanation
            st.subheader("Explanation")
            st.info(self.current_example["explanation"])
            
        except Exception as e:
            logger.error(f"Error displaying example: {str(e)}")
            st.error("Failed to display example")
            
    def _display_visualizations(self):
        """Display debugging visualizations"""
        try:
            st.header("Debugging Visualizations")
            
            # Code comparison visualization
            st.subheader("Code Comparison")
            self._create_code_comparison_visualization()
            
            # Debugging steps visualization
            st.subheader("Debugging Steps")
            self._create_debugging_steps_visualization()
            
            # Error flow visualization
            st.subheader("Error Flow")
            self._create_error_flow_visualization()
            
        except Exception as e:
            logger.error(f"Error displaying visualizations: {str(e)}")
            st.error("Failed to display visualizations")
            
    def _create_code_comparison_visualization(self):
        """Create code comparison visualization"""
        try:
            # Create a figure with two subplots
            fig = go.Figure()
            
            # Add buggy code
            fig.add_trace(go.Scatter(
                y=self.current_example["buggy_code"].splitlines(),
                name="Buggy Code",
                mode="lines+markers"
            ))
            
            # Add fixed code
            fig.add_trace(go.Scatter(
                y=self.current_example["fixed_code"].splitlines(),
                name="Fixed Code",
                mode="lines+markers"
            ))
            
            fig.update_layout(
                title="Code Comparison",
                yaxis_title="Lines of Code",
                showlegend=True
            )
            
            st.plotly_chart(fig)
            
        except Exception as e:
            logger.error(f"Error creating code comparison visualization: {str(e)}")
            st.error("Failed to create code comparison visualization")
            
    def _create_debugging_steps_visualization(self):
        """Create debugging steps visualization"""
        try:
            # Create a directed graph
            G = nx.DiGraph()
            
            # Add nodes for each step
            for i, step in enumerate(self.current_example["debugging_steps"]):
                G.add_node(i, label=step)
                
            # Add edges between steps
            for i in range(len(self.current_example["debugging_steps"]) - 1):
                G.add_edge(i, i + 1)
                
            # Create the visualization
            pos = nx.spring_layout(G)
            fig, ax = plt.subplots()
            nx.draw(G, pos, ax=ax, with_labels=True, node_color='lightblue',
                   node_size=2000, font_size=8, font_weight='bold')
            
            st.pyplot(fig)
            
        except Exception as e:
            logger.error(f"Error creating debugging steps visualization: {str(e)}")
            st.error("Failed to create debugging steps visualization")
            
    def _create_error_flow_visualization(self):
        """Create error flow visualization"""
        try:
            # Create a Sankey diagram
            fig = go.Figure(data=[go.Sankey(
                node = dict(
                    pad = 15,
                    thickness = 20,
                    line = dict(color = "black", width = 0.5),
                    label = ["Buggy Code", "Error Detection", "Analysis", "Fix Implementation", "Verification"],
                    color = "blue"
                ),
                link = dict(
                    source = [0, 1, 2, 3],
                    target = [1, 2, 3, 4],
                    value = [1, 1, 1, 1]
                )
            )])
            
            fig.update_layout(title_text="Error Resolution Flow")
            st.plotly_chart(fig)
            
        except Exception as e:
            logger.error(f"Error creating error flow visualization: {str(e)}")
            st.error("Failed to create error flow visualization")
            
    def _evaluate_solution(self):
        """Evaluate the user's solution"""
        try:
            self.evaluation_results = self.evaluator.evaluate_solution(
                self.current_example["buggy_code"],
                self.user_solution,
                self.current_example["fixed_code"],
                self.current_example["debugging_steps"]
            )
            
            # Display evaluation results
            st.header("Evaluation Results")
            
            # Create radar chart for metrics
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=list(self.evaluation_results.values()),
                theta=list(self.evaluation_results.keys()),
                fill='toself',
                name='Solution Quality'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )),
                showlegend=False,
                title="Solution Quality Metrics"
            )
            
            st.plotly_chart(fig)
            
            # Display detailed metrics
            for metric, score in self.evaluation_results.items():
                st.metric(metric.replace('_', ' ').title(), f"{score:.2f}")
                
            # Save evaluation results
            self._save_evaluation_results()
            
        except Exception as e:
            logger.error(f"Error evaluating solution: {str(e)}")
            st.error("Failed to evaluate solution")
            
    def _save_evaluation_results(self):
        """Save evaluation results"""
        try:
            output_dir = Path("data/evaluations")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"evaluation_{timestamp}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.evaluation_results, f, indent=2)
                
            st.success(f"Evaluation results saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving evaluation results: {str(e)}")
            st.error("Failed to save evaluation results") 