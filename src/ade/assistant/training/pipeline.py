from typing import Dict, Optional
from .base import TrainingConfig, TrainingPhase, TrainingPipeline
from .base_understanding import BaseUnderstandingTrainer
from .completion import CompletionTrainer
from .tool_use import ToolUseTrainer
from .specialized import SpecializedTrainer

class CodeAwareAssistantPipeline(TrainingPipeline):
    """Main training pipeline for the code-aware assistant."""
    
    def _get_trainer_class(self, phase: TrainingPhase) -> type:
        """Get the appropriate trainer class for each phase."""
        trainer_map = {
            TrainingPhase.BASE_UNDERSTANDING: BaseUnderstandingTrainer,
            TrainingPhase.COMPLETION_SPECIALIZATION: CompletionTrainer,
            TrainingPhase.TOOL_USE_INTERACTION: ToolUseTrainer,
            TrainingPhase.SPECIALIZED_TRAINING: SpecializedTrainer
        }
        return trainer_map.get(phase)
    
    def create_default_configs(self) -> Dict[TrainingPhase, TrainingConfig]:
        """Create default configurations for all training phases."""
        return {
            TrainingPhase.BASE_UNDERSTANDING: TrainingConfig(
                phase=TrainingPhase.BASE_UNDERSTANDING,
                base_understanding_config={
                    "model_name": "microsoft/codebert-base",
                    "max_sequence_length": 512,
                    "warmup_steps": 1000
                }
            ),
            TrainingPhase.COMPLETION_SPECIALIZATION: TrainingConfig(
                phase=TrainingPhase.COMPLETION_SPECIALIZATION,
                completion_config={
                    "model_name": "microsoft/codebert-base",
                    "max_sequence_length": 1024,
                    "completion_temperature": 0.7
                }
            ),
            TrainingPhase.TOOL_USE_INTERACTION: TrainingConfig(
                phase=TrainingPhase.TOOL_USE_INTERACTION,
                tool_use_config={
                    "model_name": "microsoft/codebert-base",
                    "max_sequence_length": 512,
                    "tool_use_threshold": 0.8
                }
            ),
            TrainingPhase.SPECIALIZED_TRAINING: TrainingConfig(
                phase=TrainingPhase.SPECIALIZED_TRAINING,
                specialized_config={
                    "model_name": "microsoft/codebert-base",
                    "domain": "general",
                    "max_sequence_length": 512
                }
            )
        }
    
    def run_phase(self, phase: TrainingPhase):
        """Run a specific training phase."""
        if phase not in self.trainers:
            raise ValueError(f"Trainer for phase {phase} not initialized")
            
        trainer = self.trainers[phase]
        print(f"Starting {phase.value} phase...")
        trainer.prepare_data()
        trainer.build_model()
        trainer.train()
        trainer.evaluate()
        
        if trainer.config.model_checkpoint_path:
            trainer.save_model(trainer.config.model_checkpoint_path)
            
    def run_pipeline(self, phases: Optional[list[TrainingPhase]] = None):
        """Run the complete training pipeline or specific phases."""
        if phases is None:
            phases = list(TrainingPhase)
            
        for phase in phases:
            self.run_phase(phase)
            
    def evaluate_pipeline(self):
        """Evaluate the complete pipeline across all phases."""
        results = {}
        for phase, trainer in self.trainers.items():
            print(f"Evaluating {phase.value} phase...")
            results[phase] = trainer.evaluate()
        return results 