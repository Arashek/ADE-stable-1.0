from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum

class ModelType(Enum):
    """Supported model types"""
    DEEPSEEK_CODER = "deepseek-coder"
    CODELAMA = "codellama"
    MISTRAL = "mistral"

@dataclass
class ModelConfig:
    """Configuration for code completion models"""
    model_type: ModelType
    model_path: str
    max_length: int = 2048
    context_window: int = 8192
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 50
    repetition_penalty: float = 1.1
    length_penalty: float = 1.0
    early_stopping: bool = True
    do_sample: bool = True
    num_return_sequences: int = 1
    pad_token_id: Optional[int] = None
    eos_token_id: Optional[int] = None
    bos_token_id: Optional[int] = None
    use_cache: bool = True
    device: str = "cuda"
    dtype: str = "float16"
    quantization: Optional[str] = None
    batch_size: int = 1
    max_new_tokens: int = 512
    stop_sequences: List[str] = field(default_factory=list)
    additional_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrainingConfig:
    """Configuration for model training"""
    learning_rate: float = 2e-5
    weight_decay: float = 0.01
    warmup_steps: int = 100
    max_steps: int = 1000
    gradient_accumulation_steps: int = 4
    gradient_checkpointing: bool = True
    fp16: bool = True
    bf16: bool = False
    max_grad_norm: float = 1.0
    logging_steps: int = 10
    save_steps: int = 100
    eval_steps: int = 100
    save_total_limit: int = 3
    remove_unused_columns: bool = True
    report_to: List[str] = field(default_factory=lambda: ["tensorboard"])
    load_best_model_at_end: bool = True
    metric_for_best_model: str = "eval_loss"
    greater_is_better: bool = False
    push_to_hub: bool = False
    hub_model_id: Optional[str] = None
    hub_strategy: str = "every_save"
    hub_token: Optional[str] = None
    hub_private_repo: bool = False
    resume_from_checkpoint: Optional[str] = None
    # LoRA configuration
    lora_rank: int = 8
    lora_alpha: float = 16.0
    lora_dropout: float = 0.05
    additional_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DataConfig:
    """Configuration for data collection and generation"""
    num_examples: int = 1000
    synthetic_ratio: float = 0.3
    min_example_length: int = 50
    max_example_length: int = 500
    include_docstrings: bool = True
    include_type_hints: bool = True
    include_comments: bool = True
    max_context_lines: int = 10
    min_context_lines: int = 3
    max_synthetic_attempts: int = 5
    temperature: float = 0.7
    top_p: float = 0.95
    max_new_tokens: int = 512
    stop_sequences: List[str] = field(default_factory=lambda: ["\n\n", "```"])
    additional_params: Dict[str, Any] = field(default_factory=dict) 