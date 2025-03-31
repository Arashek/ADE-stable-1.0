import os
from pathlib import Path
from dotenv import load_dotenv

def init_environment():
    # Load environment variables
    load_dotenv()
    
    # Create necessary directories
    directories = [
        os.getenv("UPLOAD_DIR", "uploads"),
        os.getenv("STORAGE_DIR", "storage"),
        "logs",
        "models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Create empty imagenet_labels.txt if it doesn't exist
    imagenet_labels_path = os.getenv("IMAGENET_LABELS_PATH", "imagenet_labels.txt")
    if not Path(imagenet_labels_path).exists():
        Path(imagenet_labels_path).touch()
        print(f"Created file: {imagenet_labels_path}")
    
    # Check for required API keys
    required_keys = [
        "GOOGLE_SPEECH_RECOGNITION_API_KEY"
    ]
    
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    if missing_keys:
        print("\nWARNING: The following API keys are missing:")
        for key in missing_keys:
            print(f"- {key}")
        print("\nPlease add them to your .env file")
    
    print("\nEnvironment initialization complete!")

if __name__ == "__main__":
    init_environment() 