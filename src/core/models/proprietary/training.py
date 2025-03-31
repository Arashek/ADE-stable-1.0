from typing import Dict, Any, List, Optional
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training
)
from .config import ModelConfig, TrainingConfig
from .data import CodeExample, TrainingDataCollector, SyntheticDataGenerator

class CodeCompletionTrainer:
    """Trainer for code completion models"""
    
    def __init__(
        self,
        model_config: ModelConfig,
        training_config: TrainingConfig
    ):
        self.model_config = model_config
        self.training_config = training_config
        self.model = None
        self.tokenizer = None
        
    def prepare_model(self):
        """Prepare model for training"""
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_config.model_path,
                trust_remote_code=True
            )
            
            # Set up CUDA if available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()  # Clear GPU memory
                torch.backends.cudnn.benchmark = True  # Enable cuDNN benchmarking
            
            # Determine device map
            device = "cuda" if torch.cuda.is_available() else "cpu"
            if device == "cuda":
                device_map = "auto"
            else:
                device_map = {"": device}  # Map all layers to CPU
            
            # Load model with proper configuration
            model_kwargs = {
                "trust_remote_code": True,
                "torch_dtype": torch.float16 if self.training_config.fp16 else torch.float32,
                "device_map": device_map
            }
            
            # Add quantization settings if specified
            if self.model_config.quantization:
                if self.model_config.quantization == "4bit":
                    model_kwargs["load_in_4bit"] = True
                elif self.model_config.quantization == "8bit":
                    model_kwargs["load_in_8bit"] = True
                    
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_config.model_path,
                **model_kwargs
            )
            
            # Prepare for k-bit training if needed
            if self.model_config.quantization in ["int8", "int4"]:
                self.model = prepare_model_for_kbit_training(self.model)
                
            # Configure LoRA
            lora_config = LoraConfig(
                r=self.training_config.lora_rank,
                lora_alpha=self.training_config.lora_alpha,
                target_modules=["q_proj", "v_proj"],  # Adjust based on model architecture
                lora_dropout=self.training_config.lora_dropout,
                bias="none",
                task_type="CAUSAL_LM"
            )
            
            self.model = get_peft_model(self.model, lora_config)
            
            return self.model, self.tokenizer
            
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {str(e)}")
        
    async def prepare_dataset(
        self,
        examples: List[CodeExample],
        synthetic_ratio: float = 0.3,
        eval_ratio: float = 0.1
    ) -> tuple[Dataset, Dataset]:
        """Prepare dataset for training"""
        # Generate synthetic examples if needed
        if synthetic_ratio > 0:
            generator = SyntheticDataGenerator(self.model, self.tokenizer)
            num_synthetic = int(len(examples) * synthetic_ratio)
            synthetic_examples = await generator.generate_examples(
                num_synthetic,
                example_types=["function", "class"]
            )
            examples.extend(synthetic_examples)
            
        # Convert examples to format expected by trainer
        data = []
        for example in examples:
            # Combine context and completion
            text = f"{example.context}\n{example.completion}"
            
            # Tokenize
            encoded = self.tokenizer(
                text,
                truncation=True,
                max_length=self.model_config.max_length,
                padding="max_length"
            )
            
            data.append({
                "input_ids": encoded["input_ids"],
                "attention_mask": encoded["attention_mask"],
                "labels": encoded["input_ids"].copy()
            })
            
        # Split into train and eval datasets
        dataset = Dataset.from_list(data)
        split_dataset = dataset.train_test_split(test_size=eval_ratio, seed=42)
        
        return split_dataset["train"], split_dataset["test"]
        
    def train(
        self,
        train_dataset: Dataset,
        eval_dataset: Optional[Dataset] = None,
        output_dir: Optional[str] = None
    ):
        """Train the model"""
        if self.model is None:
            self.prepare_model()
            
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir or "output",
            max_steps=self.training_config.max_steps,
            per_device_train_batch_size=self.model_config.batch_size,
            gradient_accumulation_steps=self.training_config.gradient_accumulation_steps,
            learning_rate=self.training_config.learning_rate,
            weight_decay=self.training_config.weight_decay,
            warmup_steps=self.training_config.warmup_steps,
            logging_steps=self.training_config.logging_steps,
            save_steps=self.training_config.save_steps,
            eval_steps=self.training_config.eval_steps,
            evaluation_strategy="steps" if eval_dataset else "no",
            fp16=self.training_config.fp16,
            bf16=self.training_config.bf16,
            gradient_checkpointing=self.training_config.gradient_checkpointing,
            # GPU-specific optimizations
            dataloader_pin_memory=True,
            dataloader_num_workers=4,
            optim="adamw_torch",
            lr_scheduler_type="cosine",
            # Mixed precision training
            fp16_full_eval=False,
            # Memory optimizations
            max_grad_norm=self.training_config.max_grad_norm,
            # Logging and monitoring
            report_to=["tensorboard"],
            logging_first_step=True,
            logging_nan_inf_filter=False,
            # Save best model
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            save_total_limit=3
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator
        )
        
        # Train
        trainer.train()
        
        # Save model
        trainer.save_model()
        
    def save_model(self, output_dir: str):
        """Save the trained model"""
        if self.model is None:
            raise ValueError("No model to save")
            
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
    def load_model(self, model_dir: str):
        """Load a trained model"""
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_dir,
            trust_remote_code=True
        )
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.float16 if self.training_config.fp16 else torch.float32
        ) 