import pytest
from unittest.mock import MagicMock, patch
from ade_model_training.model import ModelFactory
from ade_model_training.config import Config

@pytest.fixture
def model_factory(tmp_path):
    config = Config()
    config.set("log_dir", str(tmp_path / "logs"))
    return ModelFactory(config)

def test_create_transformer(model_factory):
    """Test transformer model creation."""
    model = model_factory.create_model("transformer")
    assert model is not None
    assert hasattr(model, "forward")

def test_create_cnn(model_factory):
    """Test CNN model creation."""
    model = model_factory.create_model("cnn")
    assert model is not None
    assert hasattr(model, "forward")

def test_create_rnn(model_factory):
    """Test RNN model creation."""
    model = model_factory.create_model("rnn")
    assert model is not None
    assert hasattr(model, "forward")

def test_create_gan(model_factory):
    """Test GAN model creation."""
    generator, discriminator = model_factory.create_model("gan")
    assert generator is not None
    assert discriminator is not None
    assert hasattr(generator, "forward")
    assert hasattr(discriminator, "forward")

def test_invalid_model_type(model_factory):
    """Test handling of invalid model type."""
    with pytest.raises(ValueError):
        model_factory.create_model("invalid_type")

def test_model_config_validation(model_factory):
    """Test model configuration validation."""
    model_factory.config.set("model_config", {"hidden_size": -1})
    with pytest.raises(ValueError):
        model_factory.create_model("transformer")

def test_model_initialization(model_factory):
    """Test model initialization with different configurations."""
    # Test with default config
    model = model_factory.create_model("transformer")
    assert model is not None
    
    # Test with custom config
    custom_config = {
        "hidden_size": 1024,
        "num_attention_heads": 16,
        "num_hidden_layers": 8
    }
    model_factory.config.set("model_config", custom_config)
    model = model_factory.create_model("transformer")
    assert model is not None

def test_model_forward_pass(model_factory):
    """Test model forward pass."""
    model = model_factory.create_model("transformer")
    input_data = MagicMock()
    output = model(input_data)
    assert output is not None

def test_model_parameters(model_factory):
    """Test model parameters."""
    model = model_factory.create_model("transformer")
    assert len(list(model.parameters())) > 0

def test_model_device(model_factory, mock_torch):
    """Test model device placement."""
    model = model_factory.create_model("transformer")
    model.to("cuda")
    assert next(model.parameters()).device.type == "cuda"

def test_model_save_load(model_factory, tmp_path):
    """Test model saving and loading."""
    model = model_factory.create_model("transformer")
    save_path = tmp_path / "model.pt"
    model_factory.save_model(model, str(save_path))
    loaded_model = model_factory.load_model(str(save_path))
    assert loaded_model is not None

def test_model_parallelization(model_factory, mock_torch):
    """Test model parallelization."""
    model = model_factory.create_model("transformer")
    parallel_model = model_factory.parallelize_model(model)
    assert parallel_model is not None
    assert isinstance(parallel_model, mock_torch.nn.DataParallel)

def test_model_optimization(model_factory):
    """Test model optimization."""
    model = model_factory.create_model("transformer")
    optimizer = model_factory.create_optimizer(model)
    assert optimizer is not None
    assert hasattr(optimizer, "step")

def test_model_scheduler(model_factory):
    """Test learning rate scheduler creation."""
    model = model_factory.create_model("transformer")
    optimizer = model_factory.create_optimizer(model)
    scheduler = model_factory.create_scheduler(optimizer)
    assert scheduler is not None
    assert hasattr(scheduler, "step") 