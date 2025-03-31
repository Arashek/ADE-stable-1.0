import argparse
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import sys
from datetime import datetime

from .config.aws_config import AWSServiceConfig, AWSServiceVerifier, AWSConfigManager
from .config.training_config import (
    TrainingPipelineConfig,
    TrainingConfigManager,
    TrainingPhase
)
from .base import BaseTrainer
from .base_understanding import BaseUnderstandingTrainer
from .completion import CompletionTrainer
from .tool_use import ToolUseTrainer
from .specialized import SpecializedTrainer

class TrainingInterface:
    """Main interface for training the ADE assistant."""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        
        # Initialize configuration managers
        self.training_config_manager = TrainingConfigManager(config_path)
        self.training_config = None
        self.aws_config = None
        self.aws_verifier = None
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('training.log')
            ]
        )
        
    def initialize(self) -> bool:
        """Initialize the training interface."""
        try:
            # Load training configuration
            self.training_config = self.training_config_manager.load_config()
            if not self.training_config:
                self.logger.error("Failed to load training configuration")
                return False
                
            # Load and verify AWS configuration
            aws_config_manager = AWSConfigManager(self.training_config.aws_config_path)
            self.aws_config = aws_config_manager.load_config()
            if not self.aws_config:
                self.logger.error("Failed to load AWS configuration")
                return False
                
            # Verify AWS services
            self.aws_verifier = AWSServiceVerifier(self.aws_config)
            service_statuses = self.aws_verifier.verify_services()
            
            # Check service availability
            for status in service_statuses:
                if not status.is_available:
                    self.logger.error(f"AWS service {status.service_name} is not available: {status.error_message}")
                    return False
                    
            # Verify S3 bucket
            bucket_status = self.aws_verifier.verify_s3_bucket(self.training_config.s3_bucket)
            if not bucket_status.is_available:
                self.logger.error(f"S3 bucket {self.training_config.s3_bucket} is not accessible: {bucket_status.error_message}")
                return False
                
            # Verify SageMaker role
            role_status = self.aws_verifier.verify_sagemaker_role(self.training_config.sagemaker_role)
            if not role_status.is_available:
                self.logger.error(f"SageMaker role {self.training_config.sagemaker_role} is not properly configured: {role_status.error_message}")
                return False
                
            self.logger.info("Training interface initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize training interface: {e}")
            return False
            
    def create_default_configs(self) -> bool:
        """Create default configuration files."""
        try:
            # Create default training configuration
            default_training_config = self.training_config_manager.create_default_config()
            if not self.training_config_manager.save_config(default_training_config):
                self.logger.error("Failed to save default training configuration")
                return False
                
            # Create default AWS configuration
            aws_config_manager = AWSConfigManager(self.training_config.aws_config_path)
            default_aws_config = aws_config_manager.create_default_config()
            if not aws_config_manager.save_config(default_aws_config):
                self.logger.error("Failed to save default AWS configuration")
                return False
                
            self.logger.info("Default configurations created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create default configurations: {e}")
            return False
            
    def get_trainer(self, phase: TrainingPhase) -> Optional[BaseTrainer]:
        """Get the appropriate trainer for a training phase."""
        trainer_map = {
            TrainingPhase.BASE_UNDERSTANDING: BaseUnderstandingTrainer,
            TrainingPhase.COMPLETION_SPECIALIZATION: CompletionTrainer,
            TrainingPhase.TOOL_USE_INTERACTION: ToolUseTrainer,
            TrainingPhase.SPECIALIZED_TRAINING: SpecializedTrainer
        }
        
        trainer_class = trainer_map.get(phase)
        if not trainer_class:
            self.logger.error(f"No trainer found for phase {phase}")
            return None
            
        # Find phase configuration
        phase_config = next(
            (p for p in self.training_config.phases if p.phase == phase),
            None
        )
        if not phase_config:
            self.logger.error(f"No configuration found for phase {phase}")
            return None
            
        return trainer_class(phase_config)
        
    def train_phase(self, phase: TrainingPhase) -> bool:
        """Train a specific phase."""
        try:
            trainer = self.get_trainer(phase)
            if not trainer:
                return False
                
            self.logger.info(f"Starting training for phase {phase.value}")
            
            # Prepare data
            if not trainer.prepare_data():
                self.logger.error(f"Failed to prepare data for phase {phase.value}")
                return False
                
            # Build model
            if not trainer.build_model():
                self.logger.error(f"Failed to build model for phase {phase.value}")
                return False
                
            # Train model
            if not trainer.train():
                self.logger.error(f"Training failed for phase {phase.value}")
                return False
                
            # Evaluate model
            if not trainer.evaluate():
                self.logger.error(f"Evaluation failed for phase {phase.value}")
                return False
                
            # Save model
            if not trainer.save_model():
                self.logger.error(f"Failed to save model for phase {phase.value}")
                return False
                
            self.logger.info(f"Successfully completed training for phase {phase.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during training phase {phase.value}: {e}")
            return False
            
    def train_all_phases(self) -> bool:
        """Train all phases in sequence."""
        try:
            for phase in TrainingPhase:
                if not self.train_phase(phase):
                    self.logger.error(f"Training failed at phase {phase.value}")
                    return False
                    
            self.logger.info("Successfully completed all training phases")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during training pipeline: {e}")
            return False
            
    def evaluate_training(self) -> Dict[str, Any]:
        """Evaluate the complete training process."""
        results = {}
        
        try:
            for phase in TrainingPhase:
                trainer = self.get_trainer(phase)
                if trainer:
                    phase_results = trainer.evaluate()
                    results[phase.value] = phase_results
                    
            return results
            
        except Exception as e:
            self.logger.error(f"Error during evaluation: {e}")
            return {}

def main():
    """Main entry point for the training interface."""
    parser = argparse.ArgumentParser(description="Train the ADE assistant")
    parser.add_argument("--config", type=str, required=True, help="Path to training configuration file")
    parser.add_argument("--phase", type=str, help="Specific phase to train (optional)")
    parser.add_argument("--create-configs", action="store_true", help="Create default configuration files")
    parser.add_argument("--evaluate", action="store_true", help="Evaluate training results")
    
    args = parser.parse_args()
    
    # Initialize training interface
    interface = TrainingInterface(args.config)
    
    if args.create_configs:
        if interface.create_default_configs():
            print("Default configurations created successfully")
        else:
            print("Failed to create default configurations")
        return
        
    if not interface.initialize():
        print("Failed to initialize training interface")
        return
        
    if args.evaluate:
        results = interface.evaluate_training()
        print("\nTraining Evaluation Results:")
        for phase, metrics in results.items():
            print(f"\n{phase}:")
            for metric, value in metrics.items():
                print(f"  {metric}: {value}")
        return
        
    if args.phase:
        # Train specific phase
        phase = TrainingPhase(args.phase)
        if interface.train_phase(phase):
            print(f"Successfully completed training for phase {phase.value}")
        else:
            print(f"Training failed for phase {phase.value}")
    else:
        # Train all phases
        if interface.train_all_phases():
            print("Successfully completed all training phases")
        else:
            print("Training pipeline failed")

if __name__ == "__main__":
    main() 