import pytest
from unittest.mock import MagicMock, patch
from ade_model_training.trainer import DistributedTrainer
from ade_model_training.config import Config
from datetime import datetime
from pathlib import Path
import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient

@pytest.fixture
def config():
    return Config(
        mongodb_uri='mongodb://localhost:27017',
        mongodb_database='ade_test',
        redis_host='localhost',
        redis_port=6379
    )

@pytest.fixture
async def trainer(config):
    trainer = DistributedTrainer(config)
    yield trainer
    await cleanup_test_data(trainer)

async def cleanup_test_data(trainer):
    """Clean up test data after tests."""
    await trainer.db.drop_collection('agent_interactions')
    await trainer.db.drop_collection('trained_models')
    trainer.cleanup()

@pytest.mark.asyncio
async def test_collect_interaction_data(trainer):
    # Insert test data
    test_interaction = {
        'timestamp': datetime.now(),
        'agent_id': 'test_agent',
        'model_name': 'test_model',
        'prompt': 'test prompt',
        'response': 'test response',
        'feedback_score': 0.8,
        'execution_time': 100,
        'memory_usage': 50,
        'error_rate': 0.1,
        'success_rate': 0.9
    }
    await trainer.interactions_collection.insert_one(test_interaction)
    
    # Test collection
    interactions = await trainer.collect_interaction_data()
    assert len(interactions) == 1
    assert interactions[0]['agent_id'] == 'test_agent'

@pytest.mark.asyncio
async def test_process_interactions(trainer):
    # Create test data
    test_interactions = [
        {
            'timestamp': datetime.now(),
            'agent_id': 'agent1',
            'model_name': 'model1',
            'prompt': 'prompt1',
            'response': 'response1',
            'feedback_score': 0.8,
            'execution_time': 100,
            'memory_usage': 50,
            'error_rate': 0.1,
            'success_rate': 0.9
        },
        {
            'timestamp': datetime.now(),
            'agent_id': 'agent2',
            'model_name': 'model2',
            'prompt': 'prompt2',
            'response': 'response2',
            'feedback_score': 0.9,
            'execution_time': 120,
            'memory_usage': 60,
            'error_rate': 0.05,
            'success_rate': 0.95
        }
    ]
    
    # Process interactions
    df = await trainer.process_interactions(test_interactions)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert all(col in df.columns for col in [
        'timestamp', 'agent_id', 'model_name', 'prompt', 'response',
        'feedback_score', 'execution_time', 'memory_usage', 'error_rate',
        'success_rate'
    ])

@pytest.mark.asyncio
async def test_train(trainer):
    # Insert test data
    test_interactions = [
        {
            'timestamp': datetime.now(),
            'agent_id': 'test_agent',
            'model_name': 'test_model',
            'prompt': 'test prompt',
            'response': 'test response',
            'feedback_score': 0.8,
            'execution_time': 100,
            'memory_usage': 50,
            'error_rate': 0.1,
            'success_rate': 0.9
        }
    ]
    await trainer.interactions_collection.insert_many(test_interactions)
    
    # Test training
    await trainer.train(model_name='test_model')
    
    # Verify metrics were stored
    metrics = await trainer.models_collection.find_one({'model_name': 'test_model'})
    assert metrics is not None
    assert metrics['num_interactions'] == 1
    assert metrics['avg_feedback_score'] == 0.8
    assert metrics['avg_success_rate'] == 0.9

def test_init(trainer):
    """Test trainer initialization."""
    assert trainer.config is not None
    assert trainer.model is None
    assert trainer.optimizer is None
    assert trainer.scheduler is None
    assert trainer.scaler is None

def test_create_scheduler(trainer):
    """Test learning rate scheduler creation."""
    # Test cosine scheduler
    scheduler = trainer._create_scheduler("cosine")
    assert scheduler is not None
    
    # Test step scheduler
    scheduler = trainer._create_scheduler("step")
    assert scheduler is not None
    
    # Test reduce on plateau scheduler
    scheduler = trainer._create_scheduler("reduce_on_plateau")
    assert scheduler is not None

def test_init_model_parallel(trainer, mock_torch):
    """Test model parallelism initialization."""
    trainer.config.set("use_model_parallel", True)
    trainer.config.set("num_gpus", 2)
    trainer._init_model_parallel()
    assert trainer.model is not None
    assert len(trainer.optimizers) == 2

def test_init_pipeline_parallel(trainer, mock_torch):
    """Test pipeline parallelism initialization."""
    trainer.config.set("use_pipeline_parallel", True)
    trainer.config.set("num_gpus", 2)
    trainer._init_pipeline_parallel()
    assert len(trainer.stages) == 2
    assert len(trainer.stage_optimizers) == 2

def test_split_model_into_stages(trainer, mock_torch):
    """Test model splitting into stages."""
    model = MagicMock()
    stages = trainer._split_model_into_stages(model, 2)
    assert len(stages) == 2

def test_create_pipeline_schedule(trainer):
    """Test pipeline schedule creation."""
    schedule = trainer._create_pipeline_schedule(2, 4)
    assert len(schedule) == 2  # forward and backward passes
    assert len(schedule[0]) == 4  # number of micro-batches

def test_process_batch_pipeline(trainer, mock_torch):
    """Test batch processing with pipeline parallelism."""
    trainer.config.set("use_pipeline_parallel", True)
    trainer.config.set("num_gpus", 2)
    trainer._init_pipeline_parallel()
    
    batch = MagicMock()
    loss = trainer._process_batch_pipeline(batch)
    assert loss is not None

def test_train(trainer, mock_torch):
    """Test training process."""
    with patch('ade_model_training.trainer.DistributedTrainer._process_batch') as mock_process:
        mock_process.return_value = 0.5
        trainer.train()
        assert mock_process.called

def test_save_checkpoint(trainer, tmp_path):
    """Test checkpoint saving."""
    checkpoint_dir = tmp_path / "checkpoints"
    checkpoint_dir.mkdir()
    trainer.config.set("checkpoint_dir", str(checkpoint_dir))
    
    trainer.save_checkpoint(epoch=1, step=100)
    assert (checkpoint_dir / "checkpoint_epoch_1_step_100.pt").exists()

def test_load_checkpoint(trainer, tmp_path):
    """Test checkpoint loading."""
    checkpoint_dir = tmp_path / "checkpoints"
    checkpoint_dir.mkdir()
    trainer.config.set("checkpoint_dir", str(checkpoint_dir))
    
    # Create a dummy checkpoint
    checkpoint_path = checkpoint_dir / "checkpoint_epoch_1_step_100.pt"
    checkpoint_path.touch()
    
    trainer.load_checkpoint(str(checkpoint_path))
    assert trainer.start_epoch == 1
    assert trainer.start_step == 100 