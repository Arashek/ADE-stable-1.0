import os
import logging
import torch
import argparse
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer
from .config import ModelConfig, TrainingConfig, ModelType
from .data import TrainingDataCollector, SyntheticDataGenerator
from .training import CodeCompletionTrainer
from ...providers.registry import ProviderRegistry
from ...providers.config import ProviderConfig, ProviderTier, Capability

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Hugging Face cache location
def setup_cache():
    """Set up Hugging Face cache location"""
    cache_dir = Path("D:/huggingface_cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Set environment variables
    os.environ["HF_HOME"] = str(cache_dir)
    os.environ["TRANSFORMERS_CACHE"] = str(cache_dir)
    
    logger.info(f"Hugging Face cache location set to: {cache_dir}")

# Bypass orchestrator initialization
import sys
sys.modules['src.core.orchestrator'] = type('MockOrchestrator', (), {})()
sys.modules['src.core.api.websocket_server'] = type('MockWebSocketServer', (), {})()

async def train_code_completion_model(
    codebase_path: str,
    output_dir: str,
    base_model: str,
    num_examples: int = 1000,
    synthetic_ratio: float = 0.3,
    eval_ratio: float = 0.1
) -> str:
    """Train a code completion model"""
    try:
        # Check CUDA availability
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            logger.info(f"CUDA is available. Using GPU: {torch.cuda.get_device_name(0)}")
            device = "cuda"
            dtype = "float16"
            fp16 = True
        else:
            logger.warning("CUDA is not available. Training will proceed on CPU.")
            device = "cpu"
            dtype = "float32"
            fp16 = False

        # Configure model
        model_config = ModelConfig(
            model_type=ModelType.DEEPSEEK_CODER,
            model_path=base_model,
            max_length=2048,
            batch_size=4 if cuda_available else 1,
            quantization="4bit" if cuda_available else None,
            device=device,
            dtype=dtype
        )

        # Configure training
        training_config = TrainingConfig(
            max_steps=1000,
            learning_rate=2e-5,
            weight_decay=0.01,
            warmup_steps=100,
            logging_steps=10,
            save_steps=100,
            eval_steps=100,
            gradient_accumulation_steps=4,
            gradient_checkpointing=True,
            fp16=fp16,
            bf16=False,
            lora_rank=8,
            lora_alpha=16,
            lora_dropout=0.05,
            max_grad_norm=1.0
        )

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Initialize trainer
        trainer = CodeCompletionTrainer(model_config, training_config)
        
        # Prepare model and tokenizer
        model, tokenizer = trainer.prepare_model()
        
        # Collect training examples
        collector = TrainingDataCollector(codebase_path)
        training_examples = collector.collect_examples(num_examples)
        
        # Prepare dataset
        train_dataset, eval_dataset = await trainer.prepare_dataset(
            training_examples,
            synthetic_ratio=synthetic_ratio,
            eval_ratio=eval_ratio
        )
        
        # Train model
        trainer.train(train_dataset, eval_dataset, output_dir=output_dir)
        
        # Save model
        final_model_path = os.path.join(output_dir, "final_model")
        trainer.save_model(final_model_path)
        
        return final_model_path
        
    except Exception as e:
        logger.error(f"Failed to train model: {str(e)}")
        raise

def register_model_with_provider(
    model_path: str,
    provider_name: str = "proprietary",
    capabilities: Optional[Dict[Capability, float]] = None
) -> bool:
    """Register the trained model with the provider registry"""
    try:
        # Initialize provider config
        config = ProviderConfig(
            tier=ProviderTier.PREMIUM,
            model_path=model_path,
            device="cuda",
            batch_size=1,
            quantization="4bit",
            capabilities=capabilities or {
                Capability.CODE_COMPLETION: 0.95,
                Capability.PLANNING: 0.85,
                Capability.CONTEXT_AWARENESS: 0.9,
                Capability.CODE_ANALYSIS: 0.8,
                Capability.REFACTORING: 0.75,
                Capability.TEST_GENERATION: 0.7,
                Capability.DOCUMENTATION: 0.8,
                Capability.DEBUGGING: 0.75
            }
        )
        
        # Register with provider registry
        registry = ProviderRegistry()
        success = registry.register_provider(
            name=provider_name,
            config=config,
            adapter_class=CodeCompletionAdapter
        )
        
        if success:
            logger.info(f"Successfully registered model with provider: {provider_name}")
        else:
            logger.error(f"Failed to register model with provider: {provider_name}")
            
        return success
        
    except Exception as e:
        logger.error(f"Failed to register model: {str(e)}")
        return False

def main():
    """Main function to train and register a code completion model"""
    parser = argparse.ArgumentParser(description="Train a code completion model")
    parser.add_argument("--codebase_path", type=str, required=True, help="Path to the codebase to train on")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory to save the trained model")
    parser.add_argument("--base_model", type=str, default="deepseek-ai/deepseek-coder-1.3b-instruct", help="Base model to fine-tune")
    parser.add_argument("--num_examples", type=int, default=1000, help="Number of training examples to collect")
    parser.add_argument("--synthetic_ratio", type=float, default=0.3, help="Ratio of synthetic examples to generate")
    
    args = parser.parse_args()
    
    try:
        logger.info("Starting training process...")
        logger.info(f"Using base model: {args.base_model}")
        logger.info(f"Training on codebase: {args.codebase_path}")
        logger.info(f"Output directory: {args.output_dir}")
        
        # Set up cache
        setup_cache()
        
        # Create and run event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Train model
        logger.info("Starting model training...")
        model_path = loop.run_until_complete(train_code_completion_model(
            codebase_path=args.codebase_path,
            output_dir=args.output_dir,
            base_model=args.base_model,
            num_examples=args.num_examples,
            synthetic_ratio=args.synthetic_ratio
        ))
        
        logger.info(f"Model training completed. Saved to: {model_path}")
        
        # Register model
        logger.info("Registering model with provider...")
        success = register_model_with_provider(model_path)
        
        if success:
            logger.info("Successfully trained and registered model")
        else:
            logger.error("Failed to register model")
            
    except Exception as e:
        logger.error(f"Failed to complete training process: {str(e)}")
        raise
    finally:
        loop.close()

if __name__ == "__main__":
    main() 