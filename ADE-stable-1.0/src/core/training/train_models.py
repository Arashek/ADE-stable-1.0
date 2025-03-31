import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from ..config import ModelConfig
from .pipeline_manager import TrainingPipelineManager
from ..optimization.performance_manager import PerformanceManager
from ..monitoring.evaluation_manager import EvaluationManager

logger = logging.getLogger(__name__)

class ModelTrainer:
    """Manages the training and evaluation of all model components"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.training_manager = TrainingPipelineManager(config)
        self.performance_manager = PerformanceManager(config)
        self.evaluation_manager = EvaluationManager(config)
        
    async def train_all_components(self):
        """Train all model components"""
        try:
            # Define components and their configurations
            components = {
                "code_understanding": {
                    "model": "codellama/CodeLlama-34b-Instruct-hf",
                    "data_path": Path("data/training/code_understanding"),
                    "output_dir": Path("models/code_understanding")
                },
                "tool_use": {
                    "model": "anthropic/claude-3-sonnet-20240229",
                    "data_path": Path("data/training/tool_use"),
                    "output_dir": Path("models/tool_use")
                },
                "planning": {
                    "model": "anthropic/claude-3-sonnet-20240229",
                    "data_path": Path("data/training/planning"),
                    "output_dir": Path("models/planning")
                },
                "code_generation": {
                    "model": "bigcode/starcoder2-33b",
                    "data_path": Path("data/training/code_generation"),
                    "output_dir": Path("models/code_generation")
                }
            }
            
            # Train each component
            for component, config in components.items():
                logger.info(f"Training {component}...")
                
                # Create training dataset
                dataset = await self.training_manager.create_training_dataset(
                    component=component,
                    data_path=config["data_path"]
                )
                
                # Fine-tune model
                results = await self.training_manager.fine_tune_model(
                    component=component,
                    model_name=config["model"],
                    dataset=dataset,
                    output_dir=config["output_dir"]
                )
                
                if results.get("status") == "success":
                    logger.info(f"Successfully trained {component}")
                    
                    # Evaluate model
                    eval_results = await self.training_manager.evaluate_model(
                        component=component,
                        model_path=config["output_dir"],
                        test_dataset=dataset["test"]
                    )
                    
                    if eval_results.get("status") == "success":
                        logger.info(f"Evaluation results for {component}: {eval_results['metrics']}")
                        
                        # Record metrics
                        self.evaluation_manager.record_model_performance(
                            component=component,
                            metrics=eval_results["metrics"]
                        )
                        
                        # Cache model
                        await self.performance_manager.cache_model(
                            model_key=f"{component}_v1",
                            model=AutoModelForCausalLM.from_pretrained(config["output_dir"])
                        )
                        
                else:
                    logger.error(f"Failed to train {component}: {results.get('error')}")
                    
        except Exception as e:
            logger.error(f"Failed to train components: {e}")
            
    async def run_ab_tests(self):
        """Run A/B tests for all components"""
        try:
            components = {
                "code_understanding": {
                    "model_a": "models/code_understanding/v1",
                    "model_b": "models/code_understanding/v2",
                    "test_data": self._load_test_data("code_understanding")
                },
                "tool_use": {
                    "model_a": "models/tool_use/v1",
                    "model_b": "models/tool_use/v2",
                    "test_data": self._load_test_data("tool_use")
                },
                "planning": {
                    "model_a": "models/planning/v1",
                    "model_b": "models/planning/v2",
                    "test_data": self._load_test_data("planning")
                },
                "code_generation": {
                    "model_a": "models/code_generation/v1",
                    "model_b": "models/code_generation/v2",
                    "test_data": self._load_test_data("code_generation")
                }
            }
            
            for component, config in components.items():
                logger.info(f"Running A/B test for {component}...")
                
                results = await self.evaluation_manager.run_ab_test(
                    component=component,
                    model_a=config["model_a"],
                    model_b=config["model_b"],
                    test_data=config["test_data"]
                )
                
                if results.get("status") == "success":
                    logger.info(f"A/B test results for {component}: {results['comparison']}")
                else:
                    logger.error(f"Failed to run A/B test for {component}: {results.get('error')}")
                    
        except Exception as e:
            logger.error(f"Failed to run A/B tests: {e}")
            
    def _load_test_data(self, component: str) -> List[Dict[str, Any]]:
        """Load test data for a component"""
        # Implement test data loading logic
        # This could load from files, databases, or generate synthetic data
        return []
        
    async def export_metrics(self):
        """Export all metrics"""
        try:
            # Create metrics directory
            metrics_dir = Path("metrics")
            metrics_dir.mkdir(parents=True, exist_ok=True)
            
            # Export training metrics
            self.training_manager.export_metrics(metrics_dir / "training")
            
            # Export performance metrics
            self.performance_manager.export_metrics(metrics_dir / "performance")
            
            # Export evaluation metrics
            self.evaluation_manager.export_metrics(metrics_dir / "evaluation")
            
            logger.info("Successfully exported all metrics")
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            
async def main():
    """Main function to run the training pipeline"""
    try:
        # Initialize configuration
        config = ModelConfig()
        
        # Initialize trainer
        trainer = ModelTrainer(config)
        
        # Train all components
        await trainer.train_all_components()
        
        # Run A/B tests
        await trainer.run_ab_tests()
        
        # Export metrics
        await trainer.export_metrics()
        
    except Exception as e:
        logger.error(f"Training pipeline failed: {e}")
        
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the training pipeline
    asyncio.run(main()) 