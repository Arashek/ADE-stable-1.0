import os
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM

def load_env_vars():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent.parent.parent.parent / ".env"
    if not env_path.exists():
        print(f"Error: .env file not found at {env_path}")
        return False
        
    try:
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        return True
    except Exception as e:
        print(f"Error loading .env file: {str(e)}")
        return False

def verify_cache_setup():
    """Verify Hugging Face cache setup and test model loading"""
    # Load environment variables
    if not load_env_vars():
        return False
        
    # Check environment variables
    hf_home = os.getenv("HF_HOME")
    transformers_cache = os.getenv("TRANSFORMERS_CACHE")
    
    print(f"HF_HOME: {hf_home}")
    print(f"TRANSFORMERS_CACHE: {transformers_cache}")
    
    if not hf_home or not transformers_cache:
        print("Error: Environment variables not set")
        return False
        
    # Check if cache directory exists
    cache_path = Path(hf_home)
    if not cache_path.exists():
        print(f"Error: Cache directory not found at {cache_path}")
        return False
        
    print(f"Cache directory exists at {cache_path}")
    
    # Test model loading
    try:
        print("\nTesting model loading...")
        model_name = "deepseek-ai/deepseek-coder-1.3b-instruct"
        
        print(f"Loading tokenizer from {model_name}")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        print("Tokenizer loaded successfully")
        
        print(f"Loading model from {model_name}")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            device_map="auto"
        )
        print("Model loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return False

if __name__ == "__main__":
    success = verify_cache_setup()
    if success:
        print("\nCache setup verified successfully!")
    else:
        print("\nCache setup verification failed!") 