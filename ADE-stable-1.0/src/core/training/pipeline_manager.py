from typing import Dict, Any, List, Optional
import logging
from pathlib import Path
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import load_dataset, Dataset
import numpy as np
from sklearn.metrics import precision_recall_fscore_support, accuracy_score
import wandb
from concurrent.futures import ThreadPoolExecutor
import asyncio

from ..config import ModelConfig

logger = logging.getLogger(__name__)

class TrainingPipelineManager:
    """Manages the training pipeline for model components"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._initialize_wandb()
        
    def _initialize_wandb(self):
        """Initialize Weights & Biases for experiment tracking"""
        try:
            wandb.init(
                project="ade-training",
                config=self.config.dict(),
                mode="disabled" if self.config.environment == "production" else "online"
            )
        except Exception as e:
            logger.warning(f"Failed to initialize Weights & Biases: {e}")
            
    async def create_training_dataset(self, component: str, data_path: Path) -> Dataset:
        """Create specialized training dataset for a component"""
        try:
            # Load raw data
            dataset = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._load_raw_data,
                data_path
            )
            
            # Preprocess data based on component
            processed_dataset = await self._preprocess_dataset(dataset, component)
            
            # Split into train/validation/test
            splits = processed_dataset.train_test_split(test_size=0.1, seed=42)
            splits = splits["train"].train_test_split(test_size=0.1, seed=42)
            
            return splits
            
        except Exception as e:
            logger.error(f"Failed to create training dataset: {e}")
            raise
            
    def _load_raw_data(self, data_path: Path) -> Dataset:
        """Load raw data from various sources"""
        if data_path.suffix == ".json":
            return load_dataset("json", data_files=str(data_path))
        elif data_path.suffix == ".csv":
            return load_dataset("csv", data_files=str(data_path))
        else:
            raise ValueError(f"Unsupported data format: {data_path.suffix}")
            
    async def _preprocess_dataset(self, dataset: Dataset, component: str) -> Dataset:
        """Preprocess dataset based on component requirements"""
        if component == "code_understanding":
            return await self._preprocess_code_understanding(dataset)
        elif component == "tool_use":
            return await self._preprocess_tool_use(dataset)
        elif component == "planning":
            return await self._preprocess_planning(dataset)
        elif component == "code_generation":
            return await self._preprocess_code_generation(dataset)
        else:
            raise ValueError(f"Unknown component: {component}")
            
    async def _preprocess_code_understanding(self, dataset: Dataset) -> Dataset:
        """Preprocess dataset for code understanding"""
        def process_example(example):
            # Extract code and context
            code = example["code"]
            context = example.get("context", "")
            
            # Create input format
            input_text = f"Context: {context}\nCode: {code}"
            
            # Create target format
            target_text = example.get("understanding", "")
            
            return {
                "input": input_text,
                "target": target_text
            }
            
        return dataset.map(process_example)
        
    async def _preprocess_tool_use(self, dataset: Dataset) -> Dataset:
        """Preprocess dataset for tool use"""
        def process_example(example):
            # Extract task and available tools
            task = example["task"]
            tools = example["available_tools"]
            
            # Create input format
            input_text = f"Task: {task}\nAvailable Tools: {tools}"
            
            # Create target format
            target_text = example.get("selected_tools", "")
            
            return {
                "input": input_text,
                "target": target_text
            }
            
        return dataset.map(process_example)
        
    async def _preprocess_planning(self, dataset: Dataset) -> Dataset:
        """Preprocess dataset for planning"""
        def process_example(example):
            # Extract task and context
            task = example["task"]
            context = example.get("context", "")
            
            # Create input format
            input_text = f"Task: {task}\nContext: {context}"
            
            # Create target format
            target_text = example.get("plan", "")
            
            return {
                "input": input_text,
                "target": target_text
            }
            
        return dataset.map(process_example)
        
    async def _preprocess_code_generation(self, dataset: Dataset) -> Dataset:
        """Preprocess dataset for code generation"""
        def process_example(example):
            # Extract requirements and context
            requirements = example["requirements"]
            context = example.get("context", "")
            
            # Create input format
            input_text = f"Requirements: {requirements}\nContext: {context}"
            
            # Create target format
            target_text = example.get("code", "")
            
            return {
                "input": input_text,
                "target": target_text
            }
            
        return dataset.map(process_example)
        
    async def fine_tune_model(
        self,
        component: str,
        model_name: str,
        dataset: Dataset,
        output_dir: Path
    ) -> Dict[str, Any]:
        """Fine-tune a model component"""
        try:
            # Initialize model and tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Prepare training arguments
            training_args = TrainingArguments(
                output_dir=str(output_dir),
                num_train_epochs=3,
                per_device_train_batch_size=4,
                per_device_eval_batch_size=4,
                warmup_steps=500,
                weight_decay=0.01,
                logging_dir=str(output_dir / "logs"),
                logging_steps=100,
                evaluation_strategy="steps",
                eval_steps=500,
                save_strategy="steps",
                save_steps=500,
                load_best_model_at_end=True,
                metric_for_best_model="eval_loss",
                report_to="wandb"
            )
            
            # Prepare data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=tokenizer,
                mlm=False
            )
            
            # Initialize trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=dataset["train"],
                eval_dataset=dataset["validation"],
                data_collator=data_collator,
                compute_metrics=self._compute_metrics
            )
            
            # Train model
            trainer.train()
            
            # Save model
            trainer.save_model()
            
            # Evaluate model
            eval_results = trainer.evaluate()
            
            return {
                "status": "success",
                "eval_results": eval_results,
                "model_path": output_dir
            }
            
        except Exception as e:
            logger.error(f"Failed to fine-tune model: {e}")
            return {"error": str(e)}
            
    def _compute_metrics(self, eval_pred):
        """Compute evaluation metrics"""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, predictions, average='weighted'
        )
        accuracy = accuracy_score(labels, predictions)
        
        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1
        }
        
    async def evaluate_model(
        self,
        component: str,
        model_path: Path,
        test_dataset: Dataset
    ) -> Dict[str, Any]:
        """Evaluate a fine-tuned model"""
        try:
            # Load model and tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForCausalLM.from_pretrained(model_path)
            
            # Prepare evaluation arguments
            eval_args = TrainingArguments(
                output_dir=str(model_path / "eval"),
                per_device_eval_batch_size=4,
                logging_dir=str(model_path / "eval_logs"),
                report_to="wandb"
            )
            
            # Initialize trainer
            trainer = Trainer(
                model=model,
                args=eval_args,
                eval_dataset=test_dataset,
                compute_metrics=self._compute_metrics
            )
            
            # Run evaluation
            eval_results = trainer.evaluate()
            
            # Log results
            wandb.log({
                f"{component}_eval_accuracy": eval_results["eval_accuracy"],
                f"{component}_eval_precision": eval_results["eval_precision"],
                f"{component}_eval_recall": eval_results["eval_recall"],
                f"{component}_eval_f1": eval_results["eval_f1"]
            })
            
            return {
                "status": "success",
                "metrics": eval_results
            }
            
        except Exception as e:
            logger.error(f"Failed to evaluate model: {e}")
            return {"error": str(e)}
            
    async def run_ab_test(
        self,
        component: str,
        model_a: Path,
        model_b: Path,
        test_dataset: Dataset
    ) -> Dict[str, Any]:
        """Run A/B test between two model versions"""
        try:
            # Evaluate both models
            results_a = await self.evaluate_model(component, model_a, test_dataset)
            results_b = await self.evaluate_model(component, model_b, test_dataset)
            
            # Compare results
            comparison = {
                "model_a": results_a["metrics"],
                "model_b": results_b["metrics"],
                "differences": {
                    metric: results_b["metrics"][f"eval_{metric}"] - results_a["metrics"][f"eval_{metric}"]
                    for metric in ["accuracy", "precision", "recall", "f1"]
                }
            }
            
            # Log comparison
            wandb.log({
                f"{component}_ab_test_comparison": comparison
            })
            
            return {
                "status": "success",
                "comparison": comparison
            }
            
        except Exception as e:
            logger.error(f"Failed to run A/B test: {e}")
            return {"error": str(e)} 