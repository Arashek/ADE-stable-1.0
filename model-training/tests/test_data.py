import pytest
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from ade_model_training.data import (
    # Dataset classes
    TextDataset,
    ImageDataset,
    TabularDataset,
    AudioDataset,
    VideoDataset,
    
    # DataLoader classes
    TextDataLoader,
    ImageDataLoader,
    TabularDataLoader,
    AudioDataLoader,
    VideoDataLoader,
    
    # Data processing classes
    TextProcessor,
    ImageProcessor,
    TabularProcessor,
    AudioProcessor,
    VideoProcessor,
    
    # Data augmentation classes
    TextAugmentor,
    ImageAugmentor,
    AudioAugmentor,
    VideoAugmentor,
    
    # Data validation classes
    DataValidator,
    DataQualityChecker,
    DataConsistencyChecker
)

@pytest.fixture
def data_loader(tmp_path):
    config = Config()
    config.set("data_dir", str(tmp_path / "data"))
    config.set("batch_size", 32)
    return DataLoader(config)

def test_init(data_loader):
    """Test data loader initialization."""
    assert data_loader.config is not None
    assert data_loader.train_dataset is None
    assert data_loader.eval_dataset is None
    assert data_loader.train_loader is None
    assert data_loader.eval_loader is None

def test_load_data(data_loader, tmp_path):
    """Test data loading."""
    # Create dummy data files
    train_file = tmp_path / "data" / "train.txt"
    eval_file = tmp_path / "data" / "eval.txt"
    train_file.parent.mkdir()
    train_file.touch()
    eval_file.touch()
    
    data_loader.load_data()
    assert data_loader.train_dataset is not None
    assert data_loader.eval_dataset is not None

def test_create_dataloaders(data_loader):
    """Test dataloader creation."""
    data_loader.train_dataset = MagicMock()
    data_loader.eval_dataset = MagicMock()
    data_loader.create_dataloaders()
    assert data_loader.train_loader is not None
    assert data_loader.eval_loader is not None

def test_preprocess_data(data_loader):
    """Test data preprocessing."""
    raw_data = ["Sample 1", "Sample 2", "Sample 3"]
    processed_data = data_loader.preprocess_data(raw_data)
    assert len(processed_data) == len(raw_data)

def test_tokenize_data(data_loader):
    """Test data tokenization."""
    text_data = ["This is a test.", "Another test sentence."]
    tokenized_data = data_loader.tokenize_data(text_data)
    assert len(tokenized_data) == len(text_data)

def test_create_batches(data_loader):
    """Test batch creation."""
    data = list(range(100))
    batches = data_loader.create_batches(data)
    assert len(batches) > 0
    assert len(batches[0]) == data_loader.config.get("batch_size")

def test_data_augmentation(data_loader):
    """Test data augmentation."""
    original_data = ["Sample text"]
    augmented_data = data_loader.augment_data(original_data)
    assert len(augmented_data) >= len(original_data)

def test_data_validation(data_loader):
    """Test data validation."""
    valid_data = ["Valid sample"]
    invalid_data = [None, "", "Valid sample"]
    
    # Test valid data
    assert data_loader.validate_data(valid_data) is True
    
    # Test invalid data
    assert data_loader.validate_data(invalid_data) is False

def test_data_sampling(data_loader):
    """Test data sampling."""
    data = list(range(100))
    sampled_data = data_loader.sample_data(data, sample_size=10)
    assert len(sampled_data) == 10

def test_data_shuffling(data_loader):
    """Test data shuffling."""
    original_data = list(range(100))
    shuffled_data = data_loader.shuffle_data(original_data)
    assert len(shuffled_data) == len(original_data)
    assert shuffled_data != original_data

def test_data_normalization(data_loader):
    """Test data normalization."""
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    normalized_data = data_loader.normalize_data(data)
    assert len(normalized_data) == len(data)
    assert min(normalized_data) >= 0
    assert max(normalized_data) <= 1

def test_data_export(data_loader, tmp_path):
    """Test data export."""
    data = ["Sample 1", "Sample 2"]
    export_path = tmp_path / "exported_data.txt"
    data_loader.export_data(data, str(export_path))
    assert export_path.exists()

def test_data_import(data_loader, tmp_path):
    """Test data import."""
    import_path = tmp_path / "import_data.txt"
    import_path.write_text("Sample 1\nSample 2")
    imported_data = data_loader.import_data(str(import_path))
    assert len(imported_data) == 2

def test_data_statistics(data_loader):
    """Test data statistics calculation."""
    data = [1, 2, 3, 4, 5]
    stats = data_loader.calculate_statistics(data)
    assert "mean" in stats
    assert "std" in stats
    assert "min" in stats
    assert "max" in stats

@pytest.fixture
def sample_text_data():
    """Create sample text data."""
    return {
        "texts": ["Hello world", "This is a test", "Another example"],
        "labels": [0, 1, 2]
    }

@pytest.fixture
def sample_image_data():
    """Create sample image data."""
    return {
        "images": [np.random.rand(32, 32, 3) for _ in range(3)],
        "labels": [0, 1, 2]
    }

@pytest.fixture
def sample_tabular_data():
    """Create sample tabular data."""
    return {
        "features": np.random.rand(3, 5),
        "labels": [0, 1, 2]
    }

@pytest.fixture
def sample_audio_data():
    """Create sample audio data."""
    return {
        "audio": [np.random.rand(16000) for _ in range(3)],
        "labels": [0, 1, 2]
    }

@pytest.fixture
def sample_video_data():
    """Create sample video data."""
    return {
        "videos": [np.random.rand(10, 32, 32, 3) for _ in range(3)],
        "labels": [0, 1, 2]
    }

def test_text_dataset(sample_text_data):
    """Test TextDataset class."""
    dataset = TextDataset(sample_text_data["texts"], sample_text_data["labels"])
    
    # Test length
    assert len(dataset) == 3
    
    # Test item access
    text, label = dataset[0]
    assert isinstance(text, str)
    assert isinstance(label, int)
    assert text == "Hello world"
    assert label == 0
    
    # Test iteration
    texts, labels = zip(*dataset)
    assert len(texts) == 3
    assert len(labels) == 3
    assert texts[0] == "Hello world"
    assert labels[0] == 0

def test_image_dataset(sample_image_data):
    """Test ImageDataset class."""
    dataset = ImageDataset(sample_image_data["images"], sample_image_data["labels"])
    
    # Test length
    assert len(dataset) == 3
    
    # Test item access
    image, label = dataset[0]
    assert isinstance(image, np.ndarray)
    assert isinstance(label, int)
    assert image.shape == (32, 32, 3)
    assert label == 0
    
    # Test iteration
    images, labels = zip(*dataset)
    assert len(images) == 3
    assert len(labels) == 3
    assert images[0].shape == (32, 32, 3)
    assert labels[0] == 0

def test_tabular_dataset(sample_tabular_data):
    """Test TabularDataset class."""
    dataset = TabularDataset(sample_tabular_data["features"], sample_tabular_data["labels"])
    
    # Test length
    assert len(dataset) == 3
    
    # Test item access
    features, label = dataset[0]
    assert isinstance(features, np.ndarray)
    assert isinstance(label, int)
    assert features.shape == (5,)
    assert label == 0
    
    # Test iteration
    features_list, labels = zip(*dataset)
    assert len(features_list) == 3
    assert len(labels) == 3
    assert features_list[0].shape == (5,)
    assert labels[0] == 0

def test_audio_dataset(sample_audio_data):
    """Test AudioDataset class."""
    dataset = AudioDataset(sample_audio_data["audio"], sample_audio_data["labels"])
    
    # Test length
    assert len(dataset) == 3
    
    # Test item access
    audio, label = dataset[0]
    assert isinstance(audio, np.ndarray)
    assert isinstance(label, int)
    assert audio.shape == (16000,)
    assert label == 0
    
    # Test iteration
    audio_list, labels = zip(*dataset)
    assert len(audio_list) == 3
    assert len(labels) == 3
    assert audio_list[0].shape == (16000,)
    assert labels[0] == 0

def test_video_dataset(sample_video_data):
    """Test VideoDataset class."""
    dataset = VideoDataset(sample_video_data["videos"], sample_video_data["labels"])
    
    # Test length
    assert len(dataset) == 3
    
    # Test item access
    video, label = dataset[0]
    assert isinstance(video, np.ndarray)
    assert isinstance(label, int)
    assert video.shape == (10, 32, 32, 3)
    assert label == 0
    
    # Test iteration
    videos, labels = zip(*dataset)
    assert len(videos) == 3
    assert len(labels) == 3
    assert videos[0].shape == (10, 32, 32, 3)
    assert labels[0] == 0

def test_text_dataloader(sample_text_data):
    """Test TextDataLoader class."""
    dataset = TextDataset(sample_text_data["texts"], sample_text_data["labels"])
    dataloader = TextDataLoader(dataset, batch_size=2, shuffle=True)
    
    # Test iteration
    batches = list(dataloader)
    assert len(batches) == 2  # 3 samples with batch_size=2
    
    # Test batch structure
    texts, labels = batches[0]
    assert len(texts) == 2
    assert len(labels) == 2
    assert isinstance(texts, list)
    assert isinstance(labels, torch.Tensor)

def test_image_dataloader(sample_image_data):
    """Test ImageDataLoader class."""
    dataset = ImageDataset(sample_image_data["images"], sample_image_data["labels"])
    dataloader = ImageDataLoader(dataset, batch_size=2, shuffle=True)
    
    # Test iteration
    batches = list(dataloader)
    assert len(batches) == 2  # 3 samples with batch_size=2
    
    # Test batch structure
    images, labels = batches[0]
    assert images.shape == (2, 3, 32, 32)  # (batch_size, channels, height, width)
    assert labels.shape == (2,)
    assert isinstance(images, torch.Tensor)
    assert isinstance(labels, torch.Tensor)

def test_tabular_dataloader(sample_tabular_data):
    """Test TabularDataLoader class."""
    dataset = TabularDataset(sample_tabular_data["features"], sample_tabular_data["labels"])
    dataloader = TabularDataLoader(dataset, batch_size=2, shuffle=True)
    
    # Test iteration
    batches = list(dataloader)
    assert len(batches) == 2  # 3 samples with batch_size=2
    
    # Test batch structure
    features, labels = batches[0]
    assert features.shape == (2, 5)  # (batch_size, n_features)
    assert labels.shape == (2,)
    assert isinstance(features, torch.Tensor)
    assert isinstance(labels, torch.Tensor)

def test_audio_dataloader(sample_audio_data):
    """Test AudioDataLoader class."""
    dataset = AudioDataset(sample_audio_data["audio"], sample_audio_data["labels"])
    dataloader = AudioDataLoader(dataset, batch_size=2, shuffle=True)
    
    # Test iteration
    batches = list(dataloader)
    assert len(batches) == 2  # 3 samples with batch_size=2
    
    # Test batch structure
    audio, labels = batches[0]
    assert audio.shape == (2, 16000)  # (batch_size, n_samples)
    assert labels.shape == (2,)
    assert isinstance(audio, torch.Tensor)
    assert isinstance(labels, torch.Tensor)

def test_video_dataloader(sample_video_data):
    """Test VideoDataLoader class."""
    dataset = VideoDataset(sample_video_data["videos"], sample_video_data["labels"])
    dataloader = VideoDataLoader(dataset, batch_size=2, shuffle=True)
    
    # Test iteration
    batches = list(dataloader)
    assert len(batches) == 2  # 3 samples with batch_size=2
    
    # Test batch structure
    videos, labels = batches[0]
    assert videos.shape == (2, 10, 3, 32, 32)  # (batch_size, n_frames, channels, height, width)
    assert labels.shape == (2,)
    assert isinstance(videos, torch.Tensor)
    assert isinstance(labels, torch.Tensor)

def test_text_processor():
    """Test TextProcessor class."""
    processor = TextProcessor()
    
    # Test text preprocessing
    text = "Hello World!"
    processed = processor.preprocess(text)
    assert isinstance(processed, str)
    assert processed == "hello world"
    
    # Test tokenization
    tokens = processor.tokenize(text)
    assert isinstance(tokens, list)
    assert len(tokens) > 0
    
    # Test encoding
    encoded = processor.encode(text)
    assert isinstance(encoded, np.ndarray)
    assert len(encoded) > 0

def test_image_processor():
    """Test ImageProcessor class."""
    processor = ImageProcessor()
    
    # Test image preprocessing
    image = np.random.rand(32, 32, 3)
    processed = processor.preprocess(image)
    assert isinstance(processed, np.ndarray)
    assert processed.shape == (3, 32, 32)  # (channels, height, width)
    
    # Test normalization
    normalized = processor.normalize(image)
    assert isinstance(normalized, np.ndarray)
    assert normalized.shape == (3, 32, 32)
    
    # Test augmentation
    augmented = processor.augment(image)
    assert isinstance(augmented, np.ndarray)
    assert augmented.shape == (3, 32, 32)

def test_tabular_processor():
    """Test TabularProcessor class."""
    processor = TabularProcessor()
    
    # Test feature preprocessing
    features = np.random.rand(5)
    processed = processor.preprocess(features)
    assert isinstance(processed, np.ndarray)
    assert processed.shape == (5,)
    
    # Test normalization
    normalized = processor.normalize(features)
    assert isinstance(normalized, np.ndarray)
    assert normalized.shape == (5,)
    
    # Test feature selection
    selected = processor.select_features(features, [0, 1, 2])
    assert isinstance(selected, np.ndarray)
    assert selected.shape == (3,)

def test_audio_processor():
    """Test AudioProcessor class."""
    processor = AudioProcessor()
    
    # Test audio preprocessing
    audio = np.random.rand(16000)
    processed = processor.preprocess(audio)
    assert isinstance(processed, np.ndarray)
    assert processed.shape == (16000,)
    
    # Test normalization
    normalized = processor.normalize(audio)
    assert isinstance(normalized, np.ndarray)
    assert normalized.shape == (16000,)
    
    # Test feature extraction
    features = processor.extract_features(audio)
    assert isinstance(features, np.ndarray)
    assert len(features) > 0

def test_video_processor():
    """Test VideoProcessor class."""
    processor = VideoProcessor()
    
    # Test video preprocessing
    video = np.random.rand(10, 32, 32, 3)
    processed = processor.preprocess(video)
    assert isinstance(processed, np.ndarray)
    assert processed.shape == (10, 3, 32, 32)  # (n_frames, channels, height, width)
    
    # Test normalization
    normalized = processor.normalize(video)
    assert isinstance(normalized, np.ndarray)
    assert normalized.shape == (10, 3, 32, 32)
    
    # Test frame extraction
    frames = processor.extract_frames(video)
    assert isinstance(frames, list)
    assert len(frames) == 10

def test_text_augmentor():
    """Test TextAugmentor class."""
    augmentor = TextAugmentor()
    
    # Test text augmentation
    text = "Hello world"
    augmented = augmentor.augment(text)
    assert isinstance(augmented, str)
    assert len(augmented) > 0
    
    # Test multiple augmentations
    augmented_list = augmentor.augment_multiple(text, n=3)
    assert isinstance(augmented_list, list)
    assert len(augmented_list) == 3

def test_image_augmentor():
    """Test ImageAugmentor class."""
    augmentor = ImageAugmentor()
    
    # Test image augmentation
    image = np.random.rand(32, 32, 3)
    augmented = augmentor.augment(image)
    assert isinstance(augmented, np.ndarray)
    assert augmented.shape == (32, 32, 3)
    
    # Test multiple augmentations
    augmented_list = augmentor.augment_multiple(image, n=3)
    assert isinstance(augmented_list, list)
    assert len(augmented_list) == 3

def test_audio_augmentor():
    """Test AudioAugmentor class."""
    augmentor = AudioAugmentor()
    
    # Test audio augmentation
    audio = np.random.rand(16000)
    augmented = augmentor.augment(audio)
    assert isinstance(augmented, np.ndarray)
    assert augmented.shape == (16000,)
    
    # Test multiple augmentations
    augmented_list = augmentor.augment_multiple(audio, n=3)
    assert isinstance(augmented_list, list)
    assert len(augmented_list) == 3

def test_video_augmentor():
    """Test VideoAugmentor class."""
    augmentor = VideoAugmentor()
    
    # Test video augmentation
    video = np.random.rand(10, 32, 32, 3)
    augmented = augmentor.augment(video)
    assert isinstance(augmented, np.ndarray)
    assert augmented.shape == (10, 32, 32, 3)
    
    # Test multiple augmentations
    augmented_list = augmentor.augment_multiple(video, n=3)
    assert isinstance(augmented_list, list)
    assert len(augmented_list) == 3

def test_data_validator():
    """Test DataValidator class."""
    validator = DataValidator()
    
    # Test text validation
    text_data = {"texts": ["Hello", "World"], "labels": [0, 1]}
    assert validator.validate_text(text_data) is True
    
    # Test image validation
    image_data = {"images": [np.random.rand(32, 32, 3) for _ in range(2)], "labels": [0, 1]}
    assert validator.validate_image(image_data) is True
    
    # Test tabular validation
    tabular_data = {"features": np.random.rand(2, 5), "labels": [0, 1]}
    assert validator.validate_tabular(tabular_data) is True
    
    # Test audio validation
    audio_data = {"audio": [np.random.rand(16000) for _ in range(2)], "labels": [0, 1]}
    assert validator.validate_audio(audio_data) is True
    
    # Test video validation
    video_data = {"videos": [np.random.rand(10, 32, 32, 3) for _ in range(2)], "labels": [0, 1]}
    assert validator.validate_video(video_data) is True

def test_data_quality_checker():
    """Test DataQualityChecker class."""
    checker = DataQualityChecker()
    
    # Test text quality check
    text_data = {"texts": ["Hello", "World"], "labels": [0, 1]}
    quality = checker.check_text_quality(text_data)
    assert isinstance(quality, dict)
    assert "completeness" in quality
    assert "consistency" in quality
    
    # Test image quality check
    image_data = {"images": [np.random.rand(32, 32, 3) for _ in range(2)], "labels": [0, 1]}
    quality = checker.check_image_quality(image_data)
    assert isinstance(quality, dict)
    assert "resolution" in quality
    assert "noise" in quality
    
    # Test tabular quality check
    tabular_data = {"features": np.random.rand(2, 5), "labels": [0, 1]}
    quality = checker.check_tabular_quality(tabular_data)
    assert isinstance(quality, dict)
    assert "missing_values" in quality
    assert "outliers" in quality
    
    # Test audio quality check
    audio_data = {"audio": [np.random.rand(16000) for _ in range(2)], "labels": [0, 1]}
    quality = checker.check_audio_quality(audio_data)
    assert isinstance(quality, dict)
    assert "signal_noise_ratio" in quality
    assert "clipping" in quality
    
    # Test video quality check
    video_data = {"videos": [np.random.rand(10, 32, 32, 3) for _ in range(2)], "labels": [0, 1]}
    quality = checker.check_video_quality(video_data)
    assert isinstance(quality, dict)
    assert "frame_rate" in quality
    assert "resolution" in quality

def test_data_consistency_checker():
    """Test DataConsistencyChecker class."""
    checker = DataConsistencyChecker()
    
    # Test text consistency check
    text_data = {"texts": ["Hello", "World"], "labels": [0, 1]}
    consistency = checker.check_text_consistency(text_data)
    assert isinstance(consistency, dict)
    assert "label_distribution" in consistency
    assert "text_length" in consistency
    
    # Test image consistency check
    image_data = {"images": [np.random.rand(32, 32, 3) for _ in range(2)], "labels": [0, 1]}
    consistency = checker.check_image_consistency(image_data)
    assert isinstance(consistency, dict)
    assert "size_distribution" in consistency
    assert "channel_distribution" in consistency
    
    # Test tabular consistency check
    tabular_data = {"features": np.random.rand(2, 5), "labels": [0, 1]}
    consistency = checker.check_tabular_consistency(tabular_data)
    assert isinstance(consistency, dict)
    assert "feature_distribution" in consistency
    assert "correlation" in consistency
    
    # Test audio consistency check
    audio_data = {"audio": [np.random.rand(16000) for _ in range(2)], "labels": [0, 1]}
    consistency = checker.check_audio_consistency(audio_data)
    assert isinstance(consistency, dict)
    assert "duration_distribution" in consistency
    assert "amplitude_distribution" in consistency
    
    # Test video consistency check
    video_data = {"videos": [np.random.rand(10, 32, 32, 3) for _ in range(2)], "labels": [0, 1]}
    consistency = checker.check_video_consistency(video_data)
    assert isinstance(consistency, dict)
    assert "frame_count_distribution" in consistency
    assert "motion_distribution" in consistency 