import os
import shutil
import sys
from pathlib import Path

def move_huggingface_cache():
    """Move Hugging Face cache from C drive to D drive"""
    # Define paths
    old_cache = Path.home() / ".cache" / "huggingface"
    new_cache = Path("D:/huggingface_cache")
    
    # Create new cache directory if it doesn't exist
    new_cache.mkdir(parents=True, exist_ok=True)
    
    try:
        # Set environment variables
        os.environ["HF_HOME"] = str(new_cache)
        os.environ["TRANSFORMERS_CACHE"] = str(new_cache)
        
        # Create a .env file in the project root
        env_path = Path(__file__).parent.parent.parent.parent / ".env"
        with open(env_path, "w") as f:  # Overwrite the file to ensure clean state
            f.write(f"HF_HOME={new_cache}\n")
            f.write(f"TRANSFORMERS_CACHE={new_cache}\n")
            
        print(f"Created cache directory at {new_cache}")
        print("Environment variables set successfully")
        
        # Verify environment variables
        print("\nVerifying environment variables:")
        print(f"HF_HOME: {os.getenv('HF_HOME')}")
        print(f"TRANSFORMERS_CACHE: {os.getenv('TRANSFORMERS_CACHE')}")
        
        # If old cache exists, move it
        if old_cache.exists():
            print(f"\nMoving existing cache from {old_cache}")
            # If new cache already has files, merge them
            if new_cache.exists() and any(new_cache.iterdir()):
                print("Merging with existing cache...")
                for item in old_cache.glob("*"):
                    if item.is_file():
                        shutil.copy2(item, new_cache / item.name)
                    elif item.is_dir():
                        target_dir = new_cache / item.name
                        if target_dir.exists():
                            shutil.rmtree(target_dir)
                        shutil.copytree(item, target_dir)
            else:
                print("Moving cache files...")
                # First copy everything
                shutil.copytree(str(old_cache), str(new_cache), dirs_exist_ok=True)
                # Then remove the old cache
                shutil.rmtree(str(old_cache))
            print("Cache move completed successfully")
        
    except Exception as e:
        print(f"Error setting up cache: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    move_huggingface_cache() 