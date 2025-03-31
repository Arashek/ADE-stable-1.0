import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
import json
import yaml
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import joblib
import hashlib
import uuid

logger = logging.getLogger(__name__)

@dataclass
class LearningData:
    """Container for learning data"""
    user_id: str
    timestamp: str
    action_type: str
    context: Dict
    outcome: Optional[Dict] = None
    metadata: Dict = field(default_factory=dict)

@dataclass
class ModelConfig:
    """Configuration for model training"""
    name: str
    type: str
    architecture: Dict
    hyperparameters: Dict
    training_config: Dict
    evaluation_metrics: List[str]
    metadata: Dict = field(default_factory=dict)

class LearningDataCollector:
    """Collects and processes learning data from ADE Platform users"""
    
    def __init__(self, data_dir: str = "learning_data"):
        """Initialize the learning data collector
        
        Args:
            data_dir: Directory for storing learning data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.raw_data_dir = self.data_dir / "raw"
        self.processed_data_dir = self.data_dir / "processed"
        self.models_dir = self.data_dir / "models"
        self.raw_data_dir.mkdir(exist_ok=True)
        self.processed_data_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        
        # Initialize data processing components
        self.scaler = StandardScaler()
        
    def collect_data(self, data: LearningData) -> bool:
        """Collect learning data from a user action
        
        Args:
            data: Learning data to collect
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Generate unique data ID
            data_id = str(uuid.uuid4())
            
            # Save raw data
            raw_file = self.raw_data_dir / f"{data_id}.json"
            with open(raw_file, 'w') as f:
                json.dump(data.__dict__, f, indent=4)
                
            # Process data
            self._process_data(data_id, data)
            
            logger.info(f"Collected learning data: {data_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to collect learning data: {str(e)}")
            return False
            
    def _process_data(self, data_id: str, data: LearningData) -> None:
        """Process collected learning data
        
        Args:
            data_id: Unique ID of the data
            data: Learning data to process
        """
        try:
            # Extract features from context
            features = self._extract_features(data.context)
            
            # Create processed data entry
            processed_data = {
                "data_id": data_id,
                "user_id": data.user_id,
                "timestamp": data.timestamp,
                "action_type": data.action_type,
                "features": features,
                "outcome": data.outcome,
                "metadata": data.metadata
            }
            
            # Save processed data
            processed_file = self.processed_data_dir / f"{data_id}.json"
            with open(processed_file, 'w') as f:
                json.dump(processed_data, f, indent=4)
                
        except Exception as e:
            logger.error(f"Failed to process learning data: {str(e)}")
            
    def _extract_features(self, context: Dict) -> Dict:
        """Extract features from context data
        
        Args:
            context: Context data to extract features from
            
        Returns:
            Dict: Extracted features
        """
        features = {}
        
        try:
            # Extract numerical features
            for key, value in context.items():
                if isinstance(value, (int, float)):
                    features[key] = value
                    
            # Extract categorical features
            for key, value in context.items():
                if isinstance(value, str):
                    # Create one-hot encoding for categorical values
                    features[f"{key}_{value}"] = 1
                    
            # Extract temporal features
            if "timestamp" in context:
                timestamp = datetime.fromisoformat(context["timestamp"])
                features["hour"] = timestamp.hour
                features["day_of_week"] = timestamp.weekday()
                features["month"] = timestamp.month
                
            return features
            
        except Exception as e:
            logger.error(f"Failed to extract features: {str(e)}")
            return {}
            
    def prepare_training_data(self, action_type: str) -> Optional[Dict]:
        """Prepare data for model training
        
        Args:
            action_type: Type of action to prepare data for
            
        Returns:
            Optional[Dict]: Prepared training data if successful, None otherwise
        """
        try:
            # Load processed data
            data = []
            for file in self.processed_data_dir.glob("*.json"):
                with open(file, 'r') as f:
                    entry = json.load(f)
                    if entry["action_type"] == action_type:
                        data.append(entry)
                        
            if not data:
                return None
                
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Prepare features and labels
            X = pd.DataFrame([d["features"] for d in data])
            y = pd.DataFrame([d["outcome"] for d in data])
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            return {
                "X_train": X_train_scaled,
                "X_test": X_test_scaled,
                "y_train": y_train,
                "y_test": y_test,
                "feature_names": X.columns.tolist()
            }
            
        except Exception as e:
            logger.error(f"Failed to prepare training data: {str(e)}")
            return None
            
    def train_model(self, config: ModelConfig, training_data: Dict) -> bool:
        """Train a model using collected data
        
        Args:
            config: Model configuration
            training_data: Prepared training data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create model
            model = self._create_model(config)
            
            # Prepare callbacks
            callbacks = [
                EarlyStopping(
                    monitor="val_loss",
                    patience=config.training_config.get("patience", 10),
                    restore_best_weights=True
                ),
                ModelCheckpoint(
                    filepath=str(self.models_dir / f"{config.name}_best.h5"),
                    monitor="val_loss",
                    save_best_only=True
                )
            ]
            
            # Train model
            history = model.fit(
                training_data["X_train"],
                training_data["y_train"],
                validation_split=0.2,
                epochs=config.training_config.get("epochs", 100),
                batch_size=config.training_config.get("batch_size", 32),
                callbacks=callbacks,
                verbose=1
            )
            
            # Save model and metadata
            model.save(str(self.models_dir / f"{config.name}.h5"))
            self._save_model_metadata(config, history.history)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to train model: {str(e)}")
            return False
            
    def _create_model(self, config: ModelConfig) -> tf.keras.Model:
        """Create a model based on configuration
        
        Args:
            config: Model configuration
            
        Returns:
            tf.keras.Model: Created model
        """
        model = Sequential()
        
        # Add layers based on architecture
        for layer_config in config.architecture["layers"]:
            layer_type = layer_config["type"]
            if layer_type == "dense":
                model.add(Dense(
                    units=layer_config["units"],
                    activation=layer_config.get("activation", "relu")
                ))
            elif layer_type == "lstm":
                model.add(LSTM(
                    units=layer_config["units"],
                    return_sequences=layer_config.get("return_sequences", False)
                ))
            elif layer_type == "dropout":
                model.add(Dropout(rate=layer_config["rate"]))
                
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=config.hyperparameters.get("learning_rate", 0.001)),
            loss=config.hyperparameters.get("loss", "mse"),
            metrics=config.evaluation_metrics
        )
        
        return model
        
    def _save_model_metadata(self, config: ModelConfig, history: Dict) -> None:
        """Save model metadata and training history
        
        Args:
            config: Model configuration
            history: Training history
        """
        try:
            metadata = {
                "name": config.name,
                "type": config.type,
                "architecture": config.architecture,
                "hyperparameters": config.hyperparameters,
                "training_config": config.training_config,
                "evaluation_metrics": config.evaluation_metrics,
                "metadata": config.metadata,
                "training_history": history,
                "created_at": datetime.now().isoformat()
            }
            
            metadata_file = self.models_dir / f"{config.name}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)
                
        except Exception as e:
            logger.error(f"Failed to save model metadata: {str(e)}")
            
    def evaluate_model(self, model_name: str, test_data: Dict) -> Optional[Dict]:
        """Evaluate a trained model
        
        Args:
            model_name: Name of the model to evaluate
            test_data: Test data to evaluate on
            
        Returns:
            Optional[Dict]: Evaluation results if successful, None otherwise
        """
        try:
            # Load model
            model = tf.keras.models.load_model(str(self.models_dir / f"{model_name}.h5"))
            
            # Evaluate model
            results = model.evaluate(
                test_data["X_test"],
                test_data["y_test"],
                verbose=0
            )
            
            # Create results dictionary
            evaluation_results = {
                "model_name": model_name,
                "timestamp": datetime.now().isoformat(),
                "metrics": dict(zip(model.metrics_names, results)),
                "test_data_size": len(test_data["X_test"])
            }
            
            # Save results
            results_file = self.models_dir / f"{model_name}_evaluation.json"
            with open(results_file, 'w') as f:
                json.dump(evaluation_results, f, indent=4)
                
            return evaluation_results
            
        except Exception as e:
            logger.error(f"Failed to evaluate model: {str(e)}")
            return None
            
    def get_model_predictions(self, model_name: str, features: Dict) -> Optional[Dict]:
        """Get predictions from a trained model
        
        Args:
            model_name: Name of the model to use
            features: Features to predict on
            
        Returns:
            Optional[Dict]: Model predictions if successful, None otherwise
        """
        try:
            # Load model
            model = tf.keras.models.load_model(str(self.models_dir / f"{model_name}.h5"))
            
            # Prepare features
            feature_df = pd.DataFrame([features])
            scaled_features = self.scaler.transform(feature_df)
            
            # Get predictions
            predictions = model.predict(scaled_features)
            
            return {
                "model_name": model_name,
                "timestamp": datetime.now().isoformat(),
                "features": features,
                "predictions": predictions.tolist()
            }
            
        except Exception as e:
            logger.error(f"Failed to get model predictions: {str(e)}")
            return None
            
    def clean_data(self, data_id: Optional[str] = None) -> bool:
        """Clean up learning data
        
        Args:
            data_id: Optional ID of specific data to clean
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if data_id:
                # Clean specific data
                raw_file = self.raw_data_dir / f"{data_id}.json"
                processed_file = self.processed_data_dir / f"{data_id}.json"
                
                if raw_file.exists():
                    raw_file.unlink()
                if processed_file.exists():
                    processed_file.unlink()
            else:
                # Clean all data
                for file in self.raw_data_dir.glob("*.json"):
                    file.unlink()
                for file in self.processed_data_dir.glob("*.json"):
                    file.unlink()
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to clean learning data: {str(e)}")
            return False 