from flask import Flask, render_template, request, jsonify
import os
import json
from pathlib import Path
import sys
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, TrainingArguments, Trainer
from datasets import load_dataset
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# Add the model-training directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.registry.model_registry import ModelRegistry
from src.pipeline.data_pipeline import DataPipeline, DataSource, DataTransform

app = Flask(__name__)

# Initialize registry and pipeline
REGISTRY_PATH = Path("models/registry")
registry = ModelRegistry(str(REGISTRY_PATH))

# Training state
training_state = {
    'is_training': False,
    'current_model': None,
    'progress': 0,
    'metrics': {}
}

def load_pipeline_config():
    """Load pipeline configuration from file."""
    config_path = Path("config/pipeline_config.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

def compute_metrics(eval_pred):
    """Compute metrics for model evaluation."""
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    
    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='weighted')
    acc = accuracy_score(labels, predictions)
    
    return {
        'accuracy': acc,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }

@app.route('/')
def index():
    """Render the main interface."""
    return render_template('index.html')

@app.route('/api/models', methods=['GET'])
def list_models():
    """List all registered models."""
    models = registry.list_models()
    return jsonify(models)

@app.route('/api/models', methods=['POST'])
def register_model():
    """Register a new model."""
    data = request.json
    success = registry.register_model(
        data['model_path'],
        data['version'],
        data.get('metadata')
    )
    return jsonify({'success': success})

@app.route('/api/models/<version>', methods=['GET'])
def get_model(version):
    """Get model details."""
    model = registry.get_model(version)
    if model:
        return jsonify(model)
    return jsonify({'error': 'Model not found'}), 404

@app.route('/api/models/<version>', methods=['DELETE'])
def delete_model(version):
    """Delete a model version."""
    success = registry.delete_model(version)
    return jsonify({'success': success})

@app.route('/api/pipeline/config', methods=['GET'])
def get_pipeline_config():
    """Get pipeline configuration."""
    config = load_pipeline_config()
    return jsonify(config)

@app.route('/api/pipeline/config', methods=['POST'])
def update_pipeline_config():
    """Update pipeline configuration."""
    config = request.json
    config_path = Path("config/pipeline_config.json")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return jsonify({'success': True})

@app.route('/api/pipeline/run', methods=['POST'])
def run_pipeline():
    """Run the data pipeline."""
    config = load_pipeline_config()
    pipeline = DataPipeline(config)
    
    # Add data sources
    for source_config in config.get("sources", []):
        source = DataSource(
            name=source_config["name"],
            path=source_config["path"],
            type=source_config["type"],
            schema=source_config.get("schema"),
            last_updated=None
        )
        pipeline.add_source(source)
    
    # Add transforms
    for transform_config in config.get("transforms", []):
        transform = DataTransform(
            name=transform_config["name"],
            input_sources=transform_config["input_sources"],
            output_schema=transform_config["output_schema"],
            transform_function=eval(transform_config["transform_function"])
        )
        pipeline.add_transform(transform)
    
    success = pipeline.run_pipeline()
    return jsonify({'success': success})

@app.route('/api/aws/connect', methods=['POST'])
def connect_aws():
    """Connect to AWS services."""
    data = request.json
    # Implement AWS connection logic here
    return jsonify({'success': True})

@app.route('/api/training/models', methods=['GET'])
def list_available_models():
    """List available pre-trained models for fine-tuning."""
    models = [
        {'id': 'bert-base-uncased', 'name': 'BERT Base Uncased'},
        {'id': 'roberta-base', 'name': 'RoBERTa Base'},
        {'id': 'distilbert-base-uncased', 'name': 'DistilBERT Base Uncased'},
        {'id': 'albert-base-v2', 'name': 'ALBERT Base v2'}
    ]
    return jsonify(models)

@app.route('/api/training/start', methods=['POST'])
def start_training():
    """Start model training/fine-tuning."""
    if training_state['is_training']:
        return jsonify({'error': 'Training already in progress'}), 400
    
    data = request.json
    model_id = data.get('model_id')
    training_args = data.get('training_args', {})
    
    try:
        # Initialize model and tokenizer
        model = AutoModelForSequenceClassification.from_pretrained(model_id)
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        # Load dataset
        dataset = load_dataset(data.get('dataset_path', 'data/training'))
        
        # Prepare training arguments
        training_args = TrainingArguments(
            output_dir="./results",
            num_train_epochs=training_args.get('num_train_epochs', 3),
            per_device_train_batch_size=training_args.get('batch_size', 8),
            per_device_eval_batch_size=training_args.get('eval_batch_size', 8),
            warmup_steps=training_args.get('warmup_steps', 500),
            weight_decay=training_args.get('weight_decay', 0.01),
            logging_dir='./logs',
            logging_steps=10,
            evaluation_strategy="steps",
            eval_steps=500,
            save_strategy="steps",
            save_steps=500,
            load_best_model_at_end=True,
            metric_for_best_model="f1"
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=dataset['train'],
            eval_dataset=dataset['validation'],
            compute_metrics=compute_metrics
        )
        
        # Start training in background
        training_state['is_training'] = True
        training_state['current_model'] = model_id
        training_state['trainer'] = trainer
        
        # Start training thread
        import threading
        training_thread = threading.Thread(target=train_model, args=(trainer,))
        training_thread.start()
        
        return jsonify({'success': True, 'message': 'Training started'})
    
    except Exception as e:
        training_state['is_training'] = False
        return jsonify({'error': str(e)}), 500

def train_model(trainer):
    """Train the model and update state."""
    try:
        trainer.train()
        training_state['metrics'] = trainer.evaluate()
        training_state['is_training'] = False
    except Exception as e:
        training_state['error'] = str(e)
        training_state['is_training'] = False

@app.route('/api/training/status', methods=['GET'])
def get_training_status():
    """Get current training status."""
    return jsonify(training_state)

@app.route('/api/training/stop', methods=['POST'])
def stop_training():
    """Stop current training process."""
    if not training_state['is_training']:
        return jsonify({'error': 'No training in progress'}), 400
    
    try:
        training_state['trainer'].state.is_local_process = False
        training_state['is_training'] = False
        return jsonify({'success': True, 'message': 'Training stopped'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 