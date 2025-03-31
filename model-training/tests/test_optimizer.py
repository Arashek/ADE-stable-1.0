import pytest
from unittest.mock import MagicMock, patch
from ade_model_training.optimizer import OptimizerFactory
from ade_model_training.config import Config

@pytest.fixture
def optimizer_factory(tmp_path):
    config = Config()
    config.set("log_dir", str(tmp_path / "logs"))
    return OptimizerFactory(config)

def test_init(optimizer_factory):
    """Test optimizer factory initialization."""
    assert optimizer_factory.config is not None

def test_create_adam(optimizer_factory):
    """Test Adam optimizer creation."""
    model = MagicMock()
    optimizer = optimizer_factory.create_optimizer("adam", model)
    assert optimizer is not None
    assert hasattr(optimizer, "step")

def test_create_sgd(optimizer_factory):
    """Test SGD optimizer creation."""
    model = MagicMock()
    optimizer = optimizer_factory.create_optimizer("sgd", model)
    assert optimizer is not None
    assert hasattr(optimizer, "step")

def test_create_adamw(optimizer_factory):
    """Test AdamW optimizer creation."""
    model = MagicMock()
    optimizer = optimizer_factory.create_optimizer("adamw", model)
    assert optimizer is not None
    assert hasattr(optimizer, "step")

def test_create_radam(optimizer_factory):
    """Test RAdam optimizer creation."""
    model = MagicMock()
    optimizer = optimizer_factory.create_optimizer("radam", model)
    assert optimizer is not None
    assert hasattr(optimizer, "step")

def test_invalid_optimizer_type(optimizer_factory):
    """Test handling of invalid optimizer type."""
    model = MagicMock()
    with pytest.raises(ValueError):
        optimizer_factory.create_optimizer("invalid_type", model)

def test_optimizer_config(optimizer_factory):
    """Test optimizer configuration."""
    model = MagicMock()
    config = {
        "learning_rate": 0.0001,
        "weight_decay": 0.01,
        "momentum": 0.9
    }
    optimizer_factory.config.set("optimizer_config", config)
    optimizer = optimizer_factory.create_optimizer("adam", model)
    assert optimizer is not None

def test_optimizer_state(optimizer_factory):
    """Test optimizer state management."""
    model = MagicMock()
    optimizer = optimizer_factory.create_optimizer("adam", model)
    state = optimizer_factory.get_optimizer_state(optimizer)
    assert state is not None

def test_optimizer_step(optimizer_factory):
    """Test optimizer step."""
    model = MagicMock()
    optimizer = optimizer_factory.create_optimizer("adam", model)
    loss = MagicMock()
    optimizer_factory.step(optimizer, loss)
    assert optimizer.step.called

def test_optimizer_zero_grad(optimizer_factory):
    """Test optimizer gradient zeroing."""
    model = MagicMock()
    optimizer = optimizer_factory.create_optimizer("adam", model)
    optimizer_factory.zero_grad(optimizer)
    assert optimizer.zero_grad.called

def test_optimizer_clip_gradients(optimizer_factory):
    """Test gradient clipping."""
    model = MagicMock()
    optimizer = optimizer_factory.create_optimizer("adam", model)
    optimizer_factory.clip_gradients(optimizer, max_norm=1.0)
    assert hasattr(optimizer, "clip_grad_norm_")

def test_optimizer_save_load(optimizer_factory, tmp_path):
    """Test optimizer saving and loading."""
    model = MagicMock()
    optimizer = optimizer_factory.create_optimizer("adam", model)
    save_path = tmp_path / "optimizer.pt"
    optimizer_factory.save_optimizer(optimizer, str(save_path))
    loaded_optimizer = optimizer_factory.load_optimizer(str(save_path))
    assert loaded_optimizer is not None

def test_optimizer_scheduler(optimizer_factory):
    """Test learning rate scheduler creation."""
    model = MagicMock()
    optimizer = optimizer_factory.create_optimizer("adam", model)
    scheduler = optimizer_factory.create_scheduler(optimizer)
    assert scheduler is not None
    assert hasattr(scheduler, "step")

def test_optimizer_warmup(optimizer_factory):
    """Test optimizer warmup."""
    model = MagicMock()
    optimizer = optimizer_factory.create_optimizer("adam", model)
    optimizer_factory.warmup(optimizer, num_steps=100)
    assert hasattr(optimizer, "warmup_steps")

def test_optimizer_mixed_precision(optimizer_factory):
    """Test mixed precision optimization."""
    model = MagicMock()
    optimizer = optimizer_factory.create_optimizer("adam", model)
    scaler = optimizer_factory.create_scaler()
    assert scaler is not None
    assert hasattr(scaler, "scale")
    assert hasattr(scaler, "unscale_")

def test_optimizer_gradient_accumulation(optimizer_factory):
    """Test gradient accumulation."""
    model = MagicMock()
    optimizer = optimizer_factory.create_optimizer("adam", model)
    optimizer_factory.set_gradient_accumulation_steps(optimizer, steps=4)
    assert hasattr(optimizer, "gradient_accumulation_steps")

def test_optimizer_parameter_groups(optimizer_factory):
    """Test parameter group management."""
    model = MagicMock()
    optimizer = optimizer_factory.create_optimizer("adam", model)
    groups = optimizer_factory.get_parameter_groups(optimizer)
    assert len(groups) > 0 