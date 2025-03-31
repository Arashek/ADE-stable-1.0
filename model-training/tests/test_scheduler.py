import pytest
from unittest.mock import MagicMock, patch
from ade_model_training.scheduler import SchedulerFactory
from ade_model_training.config import Config

@pytest.fixture
def scheduler_factory(tmp_path):
    config = Config()
    config.set("log_dir", str(tmp_path / "logs"))
    return SchedulerFactory(config)

def test_init(scheduler_factory):
    """Test scheduler factory initialization."""
    assert scheduler_factory.config is not None

def test_create_cosine_scheduler(scheduler_factory):
    """Test cosine scheduler creation."""
    optimizer = MagicMock()
    scheduler = scheduler_factory.create_scheduler("cosine", optimizer)
    assert scheduler is not None
    assert hasattr(scheduler, "step")

def test_create_step_scheduler(scheduler_factory):
    """Test step scheduler creation."""
    optimizer = MagicMock()
    scheduler = scheduler_factory.create_scheduler("step", optimizer)
    assert scheduler is not None
    assert hasattr(scheduler, "step")

def test_create_reduce_on_plateau_scheduler(scheduler_factory):
    """Test reduce on plateau scheduler creation."""
    optimizer = MagicMock()
    scheduler = scheduler_factory.create_scheduler("reduce_on_plateau", optimizer)
    assert scheduler is not None
    assert hasattr(scheduler, "step")

def test_create_linear_scheduler(scheduler_factory):
    """Test linear scheduler creation."""
    optimizer = MagicMock()
    scheduler = scheduler_factory.create_scheduler("linear", optimizer)
    assert scheduler is not None
    assert hasattr(scheduler, "step")

def test_create_polynomial_scheduler(scheduler_factory):
    """Test polynomial scheduler creation."""
    optimizer = MagicMock()
    scheduler = scheduler_factory.create_scheduler("polynomial", optimizer)
    assert scheduler is not None
    assert hasattr(scheduler, "step")

def test_invalid_scheduler_type(scheduler_factory):
    """Test handling of invalid scheduler type."""
    optimizer = MagicMock()
    with pytest.raises(ValueError):
        scheduler_factory.create_scheduler("invalid_type", optimizer)

def test_scheduler_config(scheduler_factory):
    """Test scheduler configuration."""
    optimizer = MagicMock()
    config = {
        "num_warmup_steps": 100,
        "num_training_steps": 1000,
        "num_cycles": 0.5
    }
    scheduler_factory.config.set("scheduler_config", config)
    scheduler = scheduler_factory.create_scheduler("cosine", optimizer)
    assert scheduler is not None

def test_scheduler_step(scheduler_factory):
    """Test scheduler step."""
    optimizer = MagicMock()
    scheduler = scheduler_factory.create_scheduler("cosine", optimizer)
    scheduler_factory.step(scheduler)
    assert scheduler.step.called

def test_scheduler_get_lr(scheduler_factory):
    """Test getting learning rate from scheduler."""
    optimizer = MagicMock()
    scheduler = scheduler_factory.create_scheduler("cosine", optimizer)
    lr = scheduler_factory.get_lr(scheduler)
    assert lr is not None

def test_scheduler_save_load(scheduler_factory, tmp_path):
    """Test scheduler saving and loading."""
    optimizer = MagicMock()
    scheduler = scheduler_factory.create_scheduler("cosine", optimizer)
    save_path = tmp_path / "scheduler.pt"
    scheduler_factory.save_scheduler(scheduler, str(save_path))
    loaded_scheduler = scheduler_factory.load_scheduler(str(save_path))
    assert loaded_scheduler is not None

def test_scheduler_warmup(scheduler_factory):
    """Test scheduler warmup."""
    optimizer = MagicMock()
    scheduler = scheduler_factory.create_scheduler("cosine", optimizer)
    scheduler_factory.warmup(scheduler, num_steps=100)
    assert hasattr(scheduler, "warmup_steps")

def test_scheduler_state_dict(scheduler_factory):
    """Test scheduler state dictionary."""
    optimizer = MagicMock()
    scheduler = scheduler_factory.create_scheduler("cosine", optimizer)
    state_dict = scheduler_factory.get_state_dict(scheduler)
    assert state_dict is not None

def test_scheduler_load_state_dict(scheduler_factory):
    """Test loading scheduler state dictionary."""
    optimizer = MagicMock()
    scheduler = scheduler_factory.create_scheduler("cosine", optimizer)
    state_dict = scheduler_factory.get_state_dict(scheduler)
    scheduler_factory.load_state_dict(scheduler, state_dict)
    assert scheduler is not None

def test_scheduler_last_epoch(scheduler_factory):
    """Test scheduler last epoch."""
    optimizer = MagicMock()
    scheduler = scheduler_factory.create_scheduler("cosine", optimizer)
    last_epoch = scheduler_factory.get_last_epoch(scheduler)
    assert last_epoch is not None

def test_scheduler_num_steps(scheduler_factory):
    """Test scheduler number of steps."""
    optimizer = MagicMock()
    scheduler = scheduler_factory.create_scheduler("cosine", optimizer)
    num_steps = scheduler_factory.get_num_steps(scheduler)
    assert num_steps is not None

def test_scheduler_cycle_length(scheduler_factory):
    """Test scheduler cycle length."""
    optimizer = MagicMock()
    scheduler = scheduler_factory.create_scheduler("cosine", optimizer)
    cycle_length = scheduler_factory.get_cycle_length(scheduler)
    assert cycle_length is not None 