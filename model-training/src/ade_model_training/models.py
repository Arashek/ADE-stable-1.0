from typing import Dict, List, Optional, Union
import torch
import torch.nn as nn
import torch.optim as optim
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class BaseModel:
    """Base class for all models."""
    
    def __init__(self, model_name: str, config: Dict):
        self.model_name = model_name
        self.config = config
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    def save(self, path: Path):
        """Save model to disk."""
        raise NotImplementedError
        
    def load(self, path: Path):
        """Load model from disk."""
        raise NotImplementedError
        
    def train(self, data: pd.DataFrame):
        """Train the model."""
        raise NotImplementedError
        
    def predict(self, data: pd.DataFrame):
        """Make predictions."""
        raise NotImplementedError

class CodeCompletionModel(BaseModel):
    """Model for code completion tasks."""
    
    def __init__(self, model_name: str, config: Dict):
        super().__init__(model_name, config)
        self.tokenizer = AutoTokenizer.from_pretrained(
            config.get('base_model', 'gpt2')
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            config.get('base_model', 'gpt2')
        ).to(self.device)
        
        self.training_args = TrainingArguments(
            output_dir=str(Path('models') / model_name),
            num_train_epochs=config.get('epochs', 3),
            per_device_train_batch_size=config.get('batch_size', 8),
            save_steps=config.get('save_steps', 1000),
            save_total_limit=config.get('save_total_limit', 2),
            logging_dir=str(Path('logs') / model_name),
            logging_steps=config.get('logging_steps', 100),
        )
        
    def prepare_data(self, data: pd.DataFrame) -> Dict:
        """Prepare data for training."""
        # Combine prompt and response for training
        texts = data.apply(
            lambda x: f"Prompt: {x['prompt']}\nResponse: {x['response']}",
            axis=1
        ).tolist()
        
        # Tokenize
        encodings = self.tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=self.config.get('max_length', 512),
            return_tensors='pt'
        )
        
        return {
            'input_ids': encodings['input_ids'],
            'attention_mask': encodings['attention_mask'],
            'labels': encodings['input_ids'].clone()
        }
        
    def train(self, data: pd.DataFrame):
        """Train the model."""
        try:
            # Prepare data
            train_data = self.prepare_data(data)
            
            # Create trainer
            trainer = Trainer(
                model=self.model,
                args=self.training_args,
                train_dataset=train_data
            )
            
            # Train
            trainer.train()
            
            logger.info(f"Model {self.model_name} training completed")
            
        except Exception as e:
            logger.error(f"Error training model {self.model_name}: {e}")
            raise
            
    def predict(self, prompt: str, max_length: int = 100) -> str:
        """Generate code completion."""
        try:
            # Tokenize input
            inputs = self.tokenizer(
                f"Prompt: {prompt}\nResponse:",
                return_tensors='pt',
                truncation=True,
                max_length=self.config.get('max_length', 512)
            ).to(self.device)
            
            # Generate
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
            
            # Decode
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response.split("Response:")[-1].strip()
            
        except Exception as e:
            logger.error(f"Error generating prediction: {e}")
            raise

class PerformancePredictionModel(BaseModel):
    """Model for predicting agent performance metrics."""
    
    def __init__(self, model_name: str, config: Dict):
        super().__init__(model_name, config)
        self.model = RandomForestClassifier(
            n_estimators=config.get('n_estimators', 100),
            max_depth=config.get('max_depth', 10),
            random_state=42
        )
        self.scaler = StandardScaler()
        
    def prepare_data(self, data: pd.DataFrame) -> tuple:
        """Prepare data for training."""
        # Features for prediction
        features = [
            'execution_time',
            'memory_usage',
            'error_rate',
            'success_rate'
        ]
        
        # Target variables
        targets = ['feedback_score']
        
        # Scale features
        X = self.scaler.fit_transform(data[features])
        y = data[targets].values.ravel()
        
        return X, y
        
    def train(self, data: pd.DataFrame):
        """Train the model."""
        try:
            # Prepare data
            X, y = self.prepare_data(data)
            
            # Train
            self.model.fit(X, y)
            
            logger.info(f"Model {self.model_name} training completed")
            
        except Exception as e:
            logger.error(f"Error training model {self.model_name}: {e}")
            raise
            
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Predict performance metrics."""
        try:
            # Prepare features
            features = [
                'execution_time',
                'memory_usage',
                'error_rate',
                'success_rate'
            ]
            X = self.scaler.transform(data[features])
            
            # Predict
            predictions = self.model.predict(X)
            return predictions
            
        except Exception as e:
            logger.error(f"Error making predictions: {e}")
            raise
            
    def save(self, path: Path):
        """Save model to disk."""
        import joblib
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler
        }, path)
        
    def load(self, path: Path):
        """Load model from disk."""
        import joblib
        saved = joblib.load(path)
        self.model = saved['model']
        self.scaler = saved['scaler']

class ModelFactory:
    """Factory for creating model instances."""
    
    @staticmethod
    def create_model(model_type: str, model_name: str, config: Dict) -> BaseModel:
        """Create a model instance based on type."""
        if model_type == 'code_completion':
            return CodeCompletionModel(model_name, config)
        elif model_type == 'performance_prediction':
            return PerformancePredictionModel(model_name, config)
        else:
            raise ValueError(f"Unknown model type: {model_type}") 