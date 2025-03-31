import json
import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

import boto3
from google.cloud import storage
from ade_model_training.cloud.cloud_manager import CloudManager

@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    return {
        "aws": {
            "region": "us-east-1",
            "bucket": "test-bucket"
        },
        "gcp": {
            "project": "test-project",
            "bucket": "test-bucket"
        }
    }

@pytest.fixture
def cloud_manager(mock_config):
    """Create a CloudManager instance for testing."""
    with patch('ade_model_training.cloud.cloud_manager.CloudManager._load_config', return_value=mock_config):
        manager = CloudManager()
        return manager

def test_init(cloud_manager, mock_config):
    """Test initialization of CloudManager."""
    assert cloud_manager.config == mock_config
    assert isinstance(cloud_manager.aws_client, MagicMock)
    assert isinstance(cloud_manager.gcp_client, MagicMock)

def test_upload_dataset_aws(cloud_manager):
    """Test uploading dataset to AWS S3."""
    test_file = "test_dataset.csv"
    test_data = "test,data\n1,2"
    
    with patch('builtins.open', create=True) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = test_data
        cloud_manager.upload_dataset(test_file, "aws")
        
        cloud_manager.aws_client.upload_file.assert_called_once()
        args = cloud_manager.aws_client.upload_file.call_args[0]
        assert args[0] == test_file
        assert args[1] == "test-bucket"
        assert args[2] == f"datasets/{test_file}"

def test_upload_dataset_gcp(cloud_manager):
    """Test uploading dataset to Google Cloud Storage."""
    test_file = "test_dataset.csv"
    test_data = "test,data\n1,2"
    
    with patch('builtins.open', create=True) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = test_data
        cloud_manager.upload_dataset(test_file, "gcp")
        
        bucket = cloud_manager.gcp_client.bucket.return_value
        blob = bucket.blob.return_value
        blob.upload_from_filename.assert_called_once_with(test_file)

def test_download_dataset_aws(cloud_manager):
    """Test downloading dataset from AWS S3."""
    test_file = "test_dataset.csv"
    cloud_manager.download_dataset(test_file, "aws")
    
    cloud_manager.aws_client.download_file.assert_called_once()
    args = cloud_manager.aws_client.download_file.call_args[0]
    assert args[0] == "test-bucket"
    assert args[1] == f"datasets/{test_file}"
    assert args[2] == test_file

def test_download_dataset_gcp(cloud_manager):
    """Test downloading dataset from Google Cloud Storage."""
    test_file = "test_dataset.csv"
    cloud_manager.download_dataset(test_file, "gcp")
    
    bucket = cloud_manager.gcp_client.bucket.return_value
    blob = bucket.blob.return_value
    blob.download_to_filename.assert_called_once_with(test_file)

def test_upload_model_aws(cloud_manager):
    """Test uploading model to AWS S3."""
    test_file = "test_model.pt"
    test_data = b"test model data"
    
    with patch('builtins.open', create=True) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = test_data
        cloud_manager.upload_model(test_file, "aws")
        
        cloud_manager.aws_client.upload_file.assert_called_once()
        args = cloud_manager.aws_client.upload_file.call_args[0]
        assert args[0] == test_file
        assert args[1] == "test-bucket"
        assert args[2] == f"models/{test_file}"

def test_upload_model_gcp(cloud_manager):
    """Test uploading model to Google Cloud Storage."""
    test_file = "test_model.pt"
    test_data = b"test model data"
    
    with patch('builtins.open', create=True) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = test_data
        cloud_manager.upload_model(test_file, "gcp")
        
        bucket = cloud_manager.gcp_client.bucket.return_value
        blob = bucket.blob.return_value
        blob.upload_from_filename.assert_called_once_with(test_file)

def test_download_model_aws(cloud_manager):
    """Test downloading model from AWS S3."""
    test_file = "test_model.pt"
    cloud_manager.download_model(test_file, "aws")
    
    cloud_manager.aws_client.download_file.assert_called_once()
    args = cloud_manager.aws_client.download_file.call_args[0]
    assert args[0] == "test-bucket"
    assert args[1] == f"models/{test_file}"
    assert args[2] == test_file

def test_download_model_gcp(cloud_manager):
    """Test downloading model from Google Cloud Storage."""
    test_file = "test_model.pt"
    cloud_manager.download_model(test_file, "gcp")
    
    bucket = cloud_manager.gcp_client.bucket.return_value
    blob = bucket.blob.return_value
    blob.download_to_filename.assert_called_once_with(test_file)

def test_list_datasets_aws(cloud_manager):
    """Test listing datasets from AWS S3."""
    mock_objects = [
        {'Key': 'datasets/dataset1.csv'},
        {'Key': 'datasets/dataset2.csv'}
    ]
    cloud_manager.aws_client.list_objects_v2.return_value = {'Contents': mock_objects}
    
    datasets = cloud_manager.list_datasets("aws")
    assert len(datasets) == 2
    assert all(dataset.endswith('.csv') for dataset in datasets)

def test_list_datasets_gcp(cloud_manager):
    """Test listing datasets from Google Cloud Storage."""
    mock_blobs = [
        MagicMock(name='datasets/dataset1.csv'),
        MagicMock(name='datasets/dataset2.csv')
    ]
    bucket = cloud_manager.gcp_client.bucket.return_value
    bucket.list_blobs.return_value = mock_blobs
    
    datasets = cloud_manager.list_datasets("gcp")
    assert len(datasets) == 2
    assert all(dataset.endswith('.csv') for dataset in datasets)

def test_list_models_aws(cloud_manager):
    """Test listing models from AWS S3."""
    mock_objects = [
        {'Key': 'models/model1.pt'},
        {'Key': 'models/model2.pt'}
    ]
    cloud_manager.aws_client.list_objects_v2.return_value = {'Contents': mock_objects}
    
    models = cloud_manager.list_models("aws")
    assert len(models) == 2
    assert all(model.endswith('.pt') for model in models)

def test_list_models_gcp(cloud_manager):
    """Test listing models from Google Cloud Storage."""
    mock_blobs = [
        MagicMock(name='models/model1.pt'),
        MagicMock(name='models/model2.pt')
    ]
    bucket = cloud_manager.gcp_client.bucket.return_value
    bucket.list_blobs.return_value = mock_blobs
    
    models = cloud_manager.list_models("gcp")
    assert len(models) == 2
    assert all(model.endswith('.pt') for model in models)

def test_invalid_cloud_provider(cloud_manager):
    """Test handling of invalid cloud provider."""
    with pytest.raises(ValueError, match="Unsupported cloud provider"):
        cloud_manager.upload_dataset("test.csv", "invalid")
        cloud_manager.download_dataset("test.csv", "invalid")
        cloud_manager.upload_model("test.pt", "invalid")
        cloud_manager.download_model("test.pt", "invalid")
        cloud_manager.list_datasets("invalid")
        cloud_manager.list_models("invalid")

def test_file_not_found(cloud_manager):
    """Test handling of file not found."""
    with patch('builtins.open', side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            cloud_manager.upload_dataset("nonexistent.csv", "aws")
            cloud_manager.upload_model("nonexistent.pt", "aws")

def test_cloud_errors(cloud_manager):
    """Test handling of cloud service errors."""
    # Test AWS errors
    cloud_manager.aws_client.upload_file.side_effect = Exception("AWS error")
    with pytest.raises(Exception, match="AWS error"):
        cloud_manager.upload_dataset("test.csv", "aws")
    
    # Test GCP errors
    bucket = cloud_manager.gcp_client.bucket.return_value
    blob = bucket.blob.return_value
    blob.upload_from_filename.side_effect = Exception("GCP error")
    with pytest.raises(Exception, match="GCP error"):
        cloud_manager.upload_dataset("test.csv", "gcp")

def test_main():
    """Test the main function."""
    with patch('ade_model_training.cloud.cloud_manager.CloudManager') as mock_manager:
        mock_instance = MagicMock()
        mock_manager.return_value = mock_instance
        
        from ade_model_training.cloud.cloud_manager import main
        main()
        
        assert mock_instance.list_datasets.called
        assert mock_instance.list_models.called 