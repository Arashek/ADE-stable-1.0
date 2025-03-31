from typing import Optional, Dict, Any, List, Union
import torch
from torch.utils.data import DataLoader
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
import wandb
from pathlib import Path
import json
import logging
from datetime import datetime
import os
from dataclasses import dataclass
import yaml

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for model training"""
    name: str
    model_type: str
    model_size: str
    max_length: int
    temperature: float
    top_p: float
    training_args: Dict[str, Any]

class ModelTrainer:
    """Manages model training operations"""
    
    def __init__(self, models_dir: str = "models"):
        """Initialize the model trainer
        
        Args:
            models_dir: Directory for storing models
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.models: Dict[str, Any] = {}
        self.tokenizers: Dict[str, Any] = {}
        self.configs: Dict[str, ModelConfig] = {}
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    def initialize(self, config: ModelConfig) -> None:
        """Initialize model and tokenizer
        
        Args:
            config: Model configuration
        """
        try:
            # Initialize tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                config.model_type,
                model_max_length=config.max_length
            )
            self.tokenizers[config.name] = tokenizer
            
            # Initialize model
            model = AutoModelForCausalLM.from_pretrained(
                config.model_type,
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32
            )
            model.to(self.device)
            self.models[config.name] = model
            
            # Save config
            self.configs[config.name] = config
            
            logger.info(f"Initialized model {config.name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize model: {str(e)}")
            raise
            
    def train(
        self,
        model_name: str,
        train_dataset: Dataset,
        eval_dataset: Optional[Dataset] = None,
        **kwargs
    ) -> None:
        """Train the model
        
        Args:
            model_name: Name of the model to train
            train_dataset: Training dataset
            eval_dataset: Optional evaluation dataset
            **kwargs: Additional training arguments
        """
        try:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not initialized")
                
            model = self.models[model_name]
            tokenizer = self.tokenizers[model_name]
            config = self.configs[model_name]
            
            # Initialize wandb
            wandb.init(
                project="training-manager",
                name=f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                config=config.__dict__
            )
            
            # Prepare training arguments
            training_args = TrainingArguments(
                **{**config.training_args, **kwargs},
                output_dir=str(self.models_dir / model_name),
                logging_dir=str(self.models_dir / model_name / "logs"),
                report_to="wandb"
            )
            
            # Initialize trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                data_collator=DataCollatorForLanguageModeling(
                    tokenizer=tokenizer,
                    mlm=False
                )
            )
            
            # Train the model
            trainer.train()
            
            # Save the model
            self.save_model(model_name)
            
            # Close wandb
            wandb.finish()
            
            logger.info(f"Completed training for model {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to train model: {str(e)}")
            raise
            
    def evaluate(self, model_name: str, eval_dataset: Dataset) -> Dict[str, float]:
        """Evaluate the model
        
        Args:
            model_name: Name of the model to evaluate
            eval_dataset: Evaluation dataset
            
        Returns:
            Dictionary of evaluation metrics
        """
        try:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not initialized")
                
            model = self.models[model_name]
            tokenizer = self.tokenizers[model_name]
            config = self.configs[model_name]
            
            # Initialize trainer
            trainer = Trainer(
                model=model,
                args=TrainingArguments(
                    output_dir=str(self.models_dir / model_name),
                    per_device_eval_batch_size=config.training_args.get(
                        "per_device_eval_batch_size",
                        8
                    )
                ),
                data_collator=DataCollatorForLanguageModeling(
                    tokenizer=tokenizer,
                    mlm=False
                )
            )
            
            # Evaluate the model
            eval_results = trainer.evaluate(eval_dataset)
            
            # Log results to wandb
            wandb.log(eval_results)
            
            return eval_results
            
        except Exception as e:
            logger.error(f"Failed to evaluate model: {str(e)}")
            raise
            
    def save_model(self, model_name: str) -> None:
        """Save model and configuration
        
        Args:
            model_name: Name of the model to save
        """
        try:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not initialized")
                
            model_dir = self.models_dir / model_name
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Save model
            model = self.models[model_name]
            model.save_pretrained(model_dir)
            
            # Save tokenizer
            tokenizer = self.tokenizers[model_name]
            tokenizer.save_pretrained(model_dir)
            
            # Save config
            config = self.configs[model_name]
            config_path = model_dir / "config.yaml"
            with open(config_path, 'w') as f:
                yaml.dump(config.__dict__, f)
                
            logger.info(f"Saved model {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {str(e)}")
            raise
            
    def load_model(self, model_name: str) -> None:
        """Load model and configuration
        
        Args:
            model_name: Name of the model to load
        """
        try:
            model_dir = self.models_dir / model_name
            if not model_dir.exists():
                raise ValueError(f"Model {model_name} not found")
                
            # Load config
            config_path = model_dir / "config.yaml"
            with open(config_path) as f:
                config_dict = yaml.safe_load(f)
                config = ModelConfig(**config_dict)
                self.configs[model_name] = config
                
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
            self.tokenizers[model_name] = tokenizer
            
            # Load model
            model = AutoModelForCausalLM.from_pretrained(
                str(model_dir),
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32
            )
            model.to(self.device)
            self.models[model_name] = model
            
            logger.info(f"Loaded model {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
            
    def predict(
        self,
        model_name: str,
        text: str,
        max_length: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        **kwargs
    ) -> str:
        """Generate predictions
        
        Args:
            model_name: Name of the model to use
            text: Input text
            max_length: Maximum length of generated text
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            **kwargs: Additional generation arguments
            
        Returns:
            Generated text
        """
        try:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not initialized")
                
            model = self.models[model_name]
            tokenizer = self.tokenizers[model_name]
            config = self.configs[model_name]
            
            # Prepare input
            inputs = tokenizer(text, return_tensors="pt").to(self.device)
            
            # Set generation parameters
            generation_config = {
                "max_length": max_length or config.max_length,
                "temperature": temperature or config.temperature,
                "top_p": top_p or config.top_p,
                **kwargs
            }
            
            # Generate
            outputs = model.generate(**inputs, **generation_config)
            
            # Decode output
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Failed to generate prediction: {str(e)}")
            raise
            
    def fine_tune(
        self,
        model_name: str,
        train_dataset: Dataset,
        eval_dataset: Optional[Dataset] = None,
        **kwargs
    ) -> None:
        """Fine-tune the model
        
        Args:
            model_name: Name of the model to fine-tune
            train_dataset: Training dataset
            eval_dataset: Optional evaluation dataset
            **kwargs: Additional training arguments
        """
        try:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not initialized")
                
            # Adjust training arguments for fine-tuning
            fine_tune_args = {
                "learning_rate": kwargs.get("learning_rate", 2e-5),
                "num_train_epochs": kwargs.get("num_train_epochs", 3),
                "warmup_steps": kwargs.get("warmup_steps", 1000),
                "weight_decay": kwargs.get("weight_decay", 0.01),
                "gradient_accumulation_steps": kwargs.get("gradient_accumulation_steps", 1),
                "gradient_checkpointing": kwargs.get("gradient_checkpointing", True),
                **kwargs
            }
            
            # Train the model
            self.train(model_name, train_dataset, eval_dataset, **fine_tune_args)
            
        except Exception as e:
            logger.error(f"Failed to fine-tune model: {str(e)}")
            raise 