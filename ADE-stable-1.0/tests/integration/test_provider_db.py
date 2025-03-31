import pytest
import asyncio
from unittest import mock
import os
from datetime import datetime

from src.core.models.provider_registry import ProviderRegistry, ModelProvider, ModelCapability
from src.storage.document.repositories import ProviderRepository, ProviderConfig
from src.storage.document.mongodb import MongoDBConnection

# Mock MongoDB connection
@pytest.fixture
def mock_mongodb_connection():
    mongodb = mock.AsyncMock(spec=MongoDBConnection)
    
    # Mock collection
    collection = mock.AsyncMock()
    mongodb.get_collection.return_value = collection
    
    return mongodb

# Mock provider repository
@pytest.fixture
def mock_provider_repository(mock_mongodb_connection):
    repo = mock.AsyncMock(spec=ProviderRepository)
    repo.connection = mock_mongodb_connection
    
    # Setup example provider config
    example_config = ProviderConfig(
        id="test-id",
        provider_type="test",
        provider_id="test-provider-id",
        encrypted_api_key="encrypted-key",
        model_map={"chat": "test-model"},
        default_parameters={"temperature": 0.5},
        capability_scores={"code_generation": 0.9, "chat": 0.8},
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Setup return values
    repo.create.return_value = example_config
    repo.get.return_value = example_config
    repo.list.return_value = [example_config]
    repo.update.return_value = example_config
    repo.delete.return_value = True
    repo.get_by_provider_id.return_value = example_config
    
    return repo

# Test provider registry with database
@pytest.mark.asyncio
async def test_load_providers_from_database(mock_provider_repository):
    """Test loading providers from database"""
    # Create provider registry with mock repository
    registry = ProviderRegistry(provider_repository=mock_provider_repository)
    
    # Mock provider class
    class MockProvider(ModelProvider):
        @property
        def provider_type(self) -> str:
            return "test"
        
        def initialize(self) -> bool:
            self.is_initialized = True
            return True
        
        def list_available_models(self) -> list:
            return ["test-model"]
        
        def get_capabilities(self) -> list:
            return [ModelCapability.CODE_GENERATION, ModelCapability.CHAT]
        
        async def generate(self, prompt, model=None, parameters=None, images=None):
            return "Test response"
    
    # Register mock provider class
    registry.register_provider_class("test", MockProvider)
    
    # Test loading from database
    with mock.patch("src.utils.encryption.decrypt_value", return_value="test-api-key"):
        await registry.load_providers_from_database()
    
    # Assertions
    mock_provider_repository.list.assert_called_once()
    assert len(registry.providers) > 0
    assert "test-provider-id" in registry.providers

@pytest.mark.asyncio
async def test_save_provider_to_database(mock_provider_repository):
    """Test saving provider to database"""
    # Create provider registry with mock repository
    registry = ProviderRegistry(provider_repository=mock_provider_repository)
    
    # Mock provider
    provider = mock.MagicMock(spec=ModelProvider)
    provider.provider_id = "test-provider-id"
    provider.provider_type = "test"
    provider._encrypted_api_key = "encrypted-key"
    provider.model_map = {"chat": "test-model"}
    provider.default_parameters = {"temperature": 0.5}
    provider.capabilities_scores = {ModelCapability.CODE_GENERATION: 0.9, ModelCapability.CHAT: 0.8}
    provider.is_active.return_value = True
    
    # Test saving to database
    await registry.save_provider_to_database(provider)
    
    # Assertions
    mock_provider_repository.get_by_provider_id.assert_called_once_with("test-provider-id")
    mock_provider_repository.update.assert_called_once()

@pytest.mark.asyncio
async def test_register_and_unregister_provider(mock_provider_repository):
    """Test registering and unregistering provider with database"""
    # Create provider registry with mock repository
    registry = ProviderRegistry(provider_repository=mock_provider_repository)
    
    # Mock provider class
    class MockProvider(ModelProvider):
        @property
        def provider_type(self) -> str:
            return "test"
        
        def initialize(self) -> bool:
            self.is_initialized = True
            return True
        
        def list_available_models(self) -> list:
            return ["test-model"]
        
        def get_capabilities(self) -> list:
            return [ModelCapability.CODE_GENERATION, ModelCapability.CHAT]
        
        async def generate(self, prompt, model=None, parameters=None, images=None):
            return "Test response"
    
    # Register mock provider class
    registry.register_provider_class("test", MockProvider)
    
    # Test registering provider
    with mock.patch("asyncio.create_task"):
        provider = await registry.register_provider(
            provider_type="test",
            api_key="test-api-key"
        )
    
    # Assertions for register
    assert provider.provider_id in registry.providers
    
    # Test unregistering provider
    with mock.patch("src.utils.encryption.decrypt_value", return_value="test-api-key"):
        result = await registry.unregister_provider(provider.provider_id)
    
    # Assertions for unregister
    assert result == True
    assert provider.provider_id not in registry.providers
    mock_provider_repository.get_by_provider_id.assert_called_with(provider.provider_id)
    mock_provider_repository.delete.assert_called_once()

@pytest.mark.asyncio
async def test_update_provider_in_database(mock_provider_repository):
    """Test updating provider in database"""
    # Create provider registry with mock repository
    registry = ProviderRegistry(provider_repository=mock_provider_repository)
    
    # Mock provider
    provider = mock.MagicMock(spec=ModelProvider)
    provider.provider_id = "test-provider-id"
    provider.provider_type = "test"
    provider._encrypted_api_key = "encrypted-key"
    provider.model_map = {"chat": "test-model"}
    provider.default_parameters = {"temperature": 0.5}
    provider.capabilities_scores = {ModelCapability.CODE_GENERATION: 0.9, ModelCapability.CHAT: 0.8}
    
    # Test updating provider
    await registry.update_provider(
        provider_id="test-provider-id",
        api_key="new-api-key",
        model_map={"chat": "new-model"}
    )
    
    # Assertions
    mock_provider_repository.get_by_provider_id.assert_called_once_with("test-provider-id")
    mock_provider_repository.update.assert_called_once()

@pytest.mark.asyncio
async def test_database_error_handling(mock_provider_repository):
    """Test handling of database errors"""
    # Create provider registry with mock repository
    registry = ProviderRegistry(provider_repository=mock_provider_repository)
    
    # Simulate database error
    mock_provider_repository.list.side_effect = Exception("Database error")
    
    # Test error handling during load
    with pytest.raises(Exception) as exc_info:
        await registry.load_providers_from_database()
    
    assert str(exc_info.value) == "Database error"

@pytest.mark.asyncio
async def test_provider_config_encryption(mock_provider_repository):
    """Test encryption of provider configuration"""
    # Create provider registry with mock repository
    registry = ProviderRegistry(provider_repository=mock_provider_repository)
    
    # Test provider registration with encryption
    with mock.patch("src.utils.encryption.encrypt_value") as mock_encrypt:
        mock_encrypt.return_value = "encrypted-api-key"
        
        provider = await registry.register_provider(
            provider_type="test",
            api_key="test-api-key"
        )
    
    # Assertions
    mock_encrypt.assert_called_once_with("test-api-key")
    assert provider._encrypted_api_key == "encrypted-api-key" 