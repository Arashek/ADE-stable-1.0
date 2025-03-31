from typing import Dict, List, Optional
from .base import BaseTrainer, TrainingConfig
from ..prompts.manager import PromptManager, PromptContext

class PromptAwareTrainer(BaseTrainer):
    """Base trainer class with prompt integration."""
    
    def __init__(self, config: TrainingConfig):
        super().__init__(config)
        self.prompt_manager = PromptManager()
        self.context_history: List[PromptContext] = []
        
    def update_context(self, context: PromptContext):
        """Update the current context and maintain history."""
        self.context_history.append(context)
        self.prompt_manager.set_context(context)
        
    def get_current_prompt(self) -> str:
        """Get the current prompt based on training phase."""
        return self.prompt_manager.get_training_prompt()
        
    def get_task_specific_prompt(self, task_type: str) -> str:
        """Get a prompt specialized for a specific task."""
        return self.prompt_manager.get_task_specific_prompt(task_type)

class PromptAwarePipeline:
    """Training pipeline with prompt integration."""
    
    def __init__(self, configs: Dict[str, TrainingConfig]):
        self.configs = configs
        self.trainers: Dict[str, PromptAwareTrainer] = {}
        self.prompt_manager = PromptManager()
        
    def initialize_trainers(self):
        """Initialize trainers with prompt awareness."""
        for phase, config in self.configs.items():
            trainer_class = self._get_trainer_class(phase)
            trainer = trainer_class(config)
            self.trainers[phase] = trainer
            
    def update_context(self, context: PromptContext):
        """Update context for all trainers."""
        self.prompt_manager.set_context(context)
        for trainer in self.trainers.values():
            trainer.update_context(context)
            
    def run_phase(self, phase: str, task_type: Optional[str] = None):
        """Run a specific training phase with appropriate prompts."""
        if phase not in self.trainers:
            raise ValueError(f"Trainer for phase {phase} not initialized")
            
        trainer = self.trainers[phase]
        print(f"Starting {phase} phase...")
        
        # Get appropriate prompt
        if task_type:
            prompt = trainer.get_task_specific_prompt(task_type)
        else:
            prompt = trainer.get_current_prompt()
            
        print(f"Using prompt:\n{prompt}\n")
        
        # Run training
        trainer.prepare_data()
        trainer.build_model()
        trainer.train()
        trainer.evaluate()
        
    def run_pipeline(self, task_types: Optional[Dict[str, str]] = None):
        """Run the complete training pipeline with appropriate prompts."""
        for phase in self.trainers:
            task_type = task_types.get(phase) if task_types else None
            self.run_phase(phase, task_type)
            
    def _get_trainer_class(self, phase: str) -> type:
        """Get the appropriate trainer class for each phase."""
        # This will be implemented with specific trainer classes
        raise NotImplementedError 