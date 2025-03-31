import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    EarlyStoppingCallback,
    IntervalStrategy
)
from datasets import load_dataset
import numpy as np
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    roc_auc_score, mean_squared_error, mean_absolute_error
)
from rouge import Rouge
from sacrebleu import corpus_bleu
from nltk.translate.bleu_score import sentence_bleu
import nltk
from typing import List, Dict, Any, Optional, Tuple
import wandb
from torch.utils.data import DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import (
    LinearLR,
    CosineAnnealingLR,
    OneCycleLR
)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

from .config import TrainingConfig, ModelConfig, DatasetConfig

class ModelManager:
    """Manages model training, evaluation, and deployment."""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize model components
        self.tokenizer = None
        self.model = None
        self.trainer = None
        self.optimizer = None
        self.scheduler = None
        
        # Initialize wandb if configured
        if hasattr(config, 'wandb_project') and config.wandb_project:
            wandb.init(
                project=config.wandb_project,
                config=config.to_dict(),
                name=f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
    def prepare_environment(self, model_name: str, phase: str) -> bool:
        """Prepare the training environment."""
        try:
            # Get model configuration
            model_config = self._get_model_config(model_name)
            if not model_config:
                return False
                
            # Create output directories
            output_dir = Path(self.config.output_dir) / model_name / phase
            checkpoint_dir = Path(self.config.checkpoint_dir) / model_name / phase
            log_dir = Path(self.config.log_dir) / model_name / phase
            
            for directory in [output_dir, checkpoint_dir, log_dir]:
                directory.mkdir(parents=True, exist_ok=True)
                
            # Initialize tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(model_config.base_model)
            self.model = AutoModelForCausalLM.from_pretrained(model_config.base_model)
            
            # Initialize optimizer
            self.optimizer = AdamW(
                self.model.parameters(),
                lr=model_config.learning_rate,
                weight_decay=model_config.weight_decay
            )
            
            # Initialize scheduler based on configuration
            if model_config.scheduler_type == 'linear':
                self.scheduler = LinearLR(
                    self.optimizer,
                    start_factor=1.0,
                    end_factor=0.0,
                    total_iters=model_config.num_train_epochs
                )
            elif model_config.scheduler_type == 'cosine':
                self.scheduler = CosineAnnealingLR(
                    self.optimizer,
                    T_max=model_config.num_train_epochs
                )
            elif model_config.scheduler_type == 'one_cycle':
                self.scheduler = OneCycleLR(
                    self.optimizer,
                    max_lr=model_config.learning_rate,
                    epochs=model_config.num_train_epochs,
                    steps_per_epoch=model_config.steps_per_epoch
                )
            
            # Prepare training arguments
            training_args = TrainingArguments(
                output_dir=str(output_dir),
                num_train_epochs=model_config.num_train_epochs,
                per_device_train_batch_size=model_config.batch_size,
                per_device_eval_batch_size=model_config.batch_size,
                warmup_steps=model_config.warmup_steps,
                weight_decay=model_config.weight_decay,
                logging_dir=str(log_dir),
                logging_steps=100,
                save_strategy="epoch",
                evaluation_strategy="epoch",
                load_best_model_at_end=True,
                metric_for_best_model="eval_loss",
                greater_is_better=False,
                fp16=model_config.fp16,
                gradient_accumulation_steps=model_config.gradient_accumulation_steps,
                device_map=model_config.device_map,
                report_to="wandb" if hasattr(self.config, 'wandb_project') and self.config.wandb_project else "none"
            )
            
            # Initialize trainer with callbacks
            callbacks = [
                EarlyStoppingCallback(
                    early_stopping_patience=self.config.early_stopping_patience,
                    early_stopping_threshold=0.0
                )
            ]
            
            self.trainer = Trainer(
                model=self.model,
                args=training_args,
                data_collator=DataCollatorForLanguageModeling(
                    tokenizer=self.tokenizer,
                    mlm=False
                ),
                callbacks=callbacks,
                optimizers=(self.optimizer, self.scheduler)
            )
            
            self.logger.info(f"Training environment prepared for {model_name} - {phase}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to prepare training environment: {e}")
            return False
            
    def train(self, model_name: str, phase: str) -> bool:
        """Train the model."""
        try:
            # Get dataset configuration
            dataset_config = self._get_dataset_config(phase)
            if not dataset_config:
                return False
                
            # Load and prepare datasets
            train_dataset = self._prepare_dataset(
                dataset_config.train_data_path,
                dataset_config.sample_limit,
                dataset_config.shuffle,
                dataset_config.seed
            )
            
            eval_dataset = self._prepare_dataset(
                dataset_config.validation_data_path,
                dataset_config.sample_limit,
                dataset_config.shuffle,
                dataset_config.seed
            )
            
            # Train the model
            self.trainer.train(
                train_dataset=train_dataset,
                eval_dataset=eval_dataset
            )
            
            # Save the model
            self._save_model(model_name, phase)
            
            # Log final metrics to wandb
            if hasattr(self.config, 'wandb_project') and self.config.wandb_project:
                wandb.log({
                    'final_train_loss': self.trainer.state.log_history[-1]['loss'],
                    'final_eval_loss': self.trainer.state.log_history[-1]['eval_loss']
                })
            
            self.logger.info(f"Model training completed for {model_name} - {phase}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to train model: {e}")
            return False
            
    def evaluate(self, model_name: str, phase: str) -> Dict[str, float]:
        """Evaluate the model."""
        try:
            # Get dataset configuration
            dataset_config = self._get_dataset_config(phase)
            if not dataset_config:
                return {}
                
            # Load test dataset
            test_dataset = self._prepare_dataset(
                dataset_config.test_data_path,
                dataset_config.sample_limit,
                dataset_config.shuffle,
                dataset_config.seed
            )
            
            # Run evaluation
            eval_results = self.trainer.evaluate(test_dataset)
            
            # Calculate additional metrics
            predictions = self.trainer.predict(test_dataset)
            metrics = self._calculate_metrics(predictions, test_dataset)
            
            # Calculate perplexity
            perplexity = torch.exp(torch.tensor(eval_results['eval_loss']))
            
            # Calculate BLEU score
            bleu_score = self._calculate_bleu_score(predictions, test_dataset)
            
            # Combine results
            results = {
                'eval_loss': eval_results['eval_loss'],
                'perplexity': perplexity.item(),
                'bleu_score': bleu_score,
                **metrics
            }
            
            # Save evaluation results
            self._save_evaluation_results(model_name, phase, results)
            
            # Log metrics to wandb
            if hasattr(self.config, 'wandb_project') and self.config.wandb_project:
                wandb.log(results)
            
            self.logger.info(f"Model evaluation completed for {model_name} - {phase}")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to evaluate model: {e}")
            return {}
            
    def deploy(self, model_name: str, phase: str, environment: str) -> bool:
        """Deploy the model to a specific environment."""
        try:
            # Load the model
            if not self._load_model(model_name, phase):
                return False
                
            # Prepare deployment configuration
            deployment_config = self._prepare_deployment_config(environment)
            
            # Save deployment artifacts
            self._save_deployment_artifacts(model_name, phase, deployment_config)
            
            self.logger.info(f"Model deployment prepared for {model_name} - {phase} in {environment}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deploy model: {e}")
            return False
            
    def verify_deployment(self, model_name: str, phase: str, environment: str) -> bool:
        """Verify model deployment."""
        try:
            # Load deployment artifacts
            deployment_dir = Path(self.config.output_dir) / model_name / phase / environment
            if not deployment_dir.exists():
                return False
                
            # Verify model files
            model_files = ['config.json', 'pytorch_model.bin', 'tokenizer.json']
            for file in model_files:
                if not (deployment_dir / file).exists():
                    return False
                    
            # Verify deployment configuration
            config_path = deployment_dir / 'deployment_config.json'
            if not config_path.exists():
                return False
                
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Verify environment-specific settings
            if config['environment'] != environment:
                return False
                
            self.logger.info(f"Model deployment verified for {model_name} - {phase} in {environment}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to verify deployment: {e}")
            return False
            
    def get_model_list(self) -> List[Dict[str, Any]]:
        """Get list of available models."""
        try:
            models = []
            output_dir = Path(self.config.output_dir)
            
            for model_dir in output_dir.iterdir():
                if not model_dir.is_dir():
                    continue
                    
                for phase_dir in model_dir.iterdir():
                    if not phase_dir.is_dir():
                        continue
                        
                    models.append({
                        'name': model_dir.name,
                        'phase': phase_dir.name,
                        'path': str(phase_dir)
                    })
                    
            return models
            
        except Exception as e:
            self.logger.error(f"Failed to get model list: {e}")
            return []
            
    def get_model_status(self, model: Dict[str, Any]) -> str:
        """Get the status of a model."""
        try:
            model_dir = Path(model['path'])
            
            # Check for training completion
            if not (model_dir / 'trainer_state.json').exists():
                return 'Not Trained'
                
            # Check for evaluation results
            if not (model_dir / 'eval_results.json').exists():
                return 'Training Complete'
                
            # Check for deployment artifacts
            deployment_dirs = [d for d in model_dir.iterdir() if d.is_dir() and d.name in ['development', 'production']]
            if not deployment_dirs:
                return 'Evaluation Complete'
                
            return 'Deployed'
            
        except Exception as e:
            self.logger.error(f"Failed to get model status: {e}")
            return 'Unknown'
            
    def get_last_updated(self, model: Dict[str, Any]) -> datetime:
        """Get the last update time of a model."""
        try:
            model_dir = Path(model['path'])
            return datetime.fromtimestamp(model_dir.stat().st_mtime)
            
        except Exception as e:
            self.logger.error(f"Failed to get last update time: {e}")
            return datetime.now()
            
    def _get_model_config(self, model_name: str) -> Optional[ModelConfig]:
        """Get model configuration by name."""
        for model in self.config.models:
            if model.name == model_name:
                return model
        return None
        
    def _get_dataset_config(self, phase: str) -> Optional[DatasetConfig]:
        """Get dataset configuration by phase."""
        return self.config.datasets.get(phase)
        
    def _prepare_dataset(self, data_path: str, sample_limit: Optional[int] = None,
                        shuffle: bool = True, seed: int = 42) -> Any:
        """Prepare dataset for training or evaluation."""
        dataset = load_dataset('json', data_files=data_path)
        
        if sample_limit:
            dataset = dataset['train'].select(range(min(sample_limit, len(dataset['train']))))
            
        if shuffle:
            dataset = dataset.shuffle(seed=seed)
            
        return dataset
        
    def _calculate_metrics(self, predictions: Any, dataset: Any) -> Dict[str, float]:
        """Calculate evaluation metrics."""
        metrics = {}
        
        # Get predictions and labels
        preds = predictions.predictions.argmax(-1)
        labels = predictions.label_ids
        
        # Calculate classification metrics
        if 'accuracy' in self.config.evaluation_metrics:
            metrics['accuracy'] = accuracy_score(labels, preds)
            
        if 'f1' in self.config.evaluation_metrics:
            metrics['f1'] = f1_score(labels, preds, average='weighted')
            
        if 'precision' in self.config.evaluation_metrics:
            metrics['precision'] = precision_score(labels, preds, average='weighted')
            
        if 'recall' in self.config.evaluation_metrics:
            metrics['recall'] = recall_score(labels, preds, average='weighted')
            
        if 'roc_auc' in self.config.evaluation_metrics:
            metrics['roc_auc'] = roc_auc_score(labels, preds, multi_class='ovr')
            
        # Calculate regression metrics
        if 'mse' in self.config.evaluation_metrics:
            metrics['mse'] = mean_squared_error(labels, preds)
            
        if 'mae' in self.config.evaluation_metrics:
            metrics['mae'] = mean_absolute_error(labels, preds)
            
        # Calculate ROUGE scores
        if 'rouge' in self.config.evaluation_metrics:
            rouge = Rouge()
            scores = rouge.get_scores(preds, labels, avg=True)
            metrics['rouge-1'] = scores['rouge-1']['f']
            metrics['rouge-2'] = scores['rouge-2']['f']
            metrics['rouge-l'] = scores['rouge-l']['f']
            
        return metrics
        
    def _calculate_bleu_score(self, predictions: Any, dataset: Any) -> float:
        """Calculate BLEU score for text generation."""
        try:
            # Convert predictions and references to text
            pred_texts = self.tokenizer.batch_decode(predictions.predictions.argmax(-1))
            ref_texts = self.tokenizer.batch_decode(predictions.label_ids)
            
            # Calculate corpus BLEU score
            return corpus_bleu(pred_texts, [ref_texts]).score
            
        except Exception as e:
            self.logger.error(f"Failed to calculate BLEU score: {e}")
            return 0.0
            
    def _save_model(self, model_name: str, phase: str) -> None:
        """Save the trained model."""
        output_dir = Path(self.config.output_dir) / model_name / phase
        
        # Save model and tokenizer
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        # Save optimizer and scheduler state
        torch.save({
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None
        }, output_dir / 'optimizer.pt')
        
        # Save training arguments
        self.trainer.args.save_to_json(output_dir / 'training_args.json')
        
    def _load_model(self, model_name: str, phase: str) -> bool:
        """Load a trained model."""
        try:
            model_dir = Path(self.config.output_dir) / model_name / phase
            if not model_dir.exists():
                return False
                
            # Load model and tokenizer
            self.model = AutoModelForCausalLM.from_pretrained(model_dir)
            self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
            
            # Load optimizer and scheduler state if available
            optimizer_path = model_dir / 'optimizer.pt'
            if optimizer_path.exists():
                checkpoint = torch.load(optimizer_path)
                self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
                if self.scheduler and checkpoint['scheduler_state_dict']:
                    self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            return False
            
    def _save_evaluation_results(self, model_name: str, phase: str, results: Dict[str, float]) -> None:
        """Save evaluation results."""
        output_dir = Path(self.config.output_dir) / model_name / phase
        with open(output_dir / 'eval_results.json', 'w') as f:
            json.dump(results, f, indent=2)
            
    def _prepare_deployment_config(self, environment: str) -> Dict[str, Any]:
        """Prepare deployment configuration."""
        return {
            'environment': environment,
            'model_type': self.model.config.model_type,
            'max_length': self.model.config.max_length,
            'temperature': 0.7,
            'top_p': 0.9,
            'top_k': 50,
            'repetition_penalty': 1.2,
            'do_sample': True
        }
        
    def _save_deployment_artifacts(self, model_name: str, phase: str, config: Dict[str, Any]) -> None:
        """Save deployment artifacts."""
        deployment_dir = Path(self.config.output_dir) / model_name / phase / config['environment']
        deployment_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model and tokenizer
        self.model.save_pretrained(deployment_dir)
        self.tokenizer.save_pretrained(deployment_dir)
        
        # Save deployment configuration
        with open(deployment_dir / 'deployment_config.json', 'w') as f:
            json.dump(config, f, indent=2) 