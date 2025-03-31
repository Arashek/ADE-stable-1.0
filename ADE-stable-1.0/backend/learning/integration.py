from typing import Dict, List, Any, Optional
import asyncio
from pathlib import Path
import logging
from datetime import datetime
from ...config.logging_config import logger
from .pipeline_manager import LearningPipelineManager
from .completion.completion_provider import CompletionProvider
from .completion.code_analysis import CodeAnalyzer
import json

class LearningIntegration:
    """Integrates learning components with ADE"""
    
    def __init__(self, ade_config: Dict[str, Any]):
        self.config = ade_config
        self.pipeline_manager = LearningPipelineManager(
            output_dir=str(Path(ade_config['data_dir']) / "learning")
        )
        self.completion_provider = CompletionProvider()
        self.code_analyzer = CodeAnalyzer()
        
        # Initialize learning state
        self.learning_state = {
            'is_training': False,
            'current_episode': 0,
            'total_examples': 0,
            'last_update': None
        }
        
    async def start_learning(self, code_files: List[str]):
        """Start the learning process"""
        try:
            if self.learning_state['is_training']:
                logger.warning("Learning already in progress")
                return {'status': 'already_running'}
                
            # Update state
            self.learning_state['is_training'] = True
            self.learning_state['last_update'] = datetime.now()
            
            # Start training pipeline
            result = self.pipeline_manager.start_training_pipeline(
                code_files=code_files,
                num_examples=self.config.get('num_examples', 1000)
            )
            
            if result['status'] == 'success':
                # Start background training task
                asyncio.create_task(self._background_training(result))
                
            return result
            
        except Exception as e:
            logger.error(f"Error starting learning: {str(e)}")
            self.learning_state['is_training'] = False
            return {'status': 'error', 'message': str(e)}
            
    async def _background_training(self, initial_result: Dict[str, Any]):
        """Run training in the background"""
        try:
            while self.learning_state['is_training']:
                # Update learning state
                self.learning_state['current_episode'] += 1
                self.learning_state['last_update'] = datetime.now()
                
                # Get new examples
                new_examples = await self._collect_new_examples()
                
                if new_examples:
                    # Update training data
                    initial_result['training_data']['examples'].extend(new_examples)
                    
                    # Continue RL training
                    self.pipeline_manager._start_rl_training(
                        initial_result['training_data'],
                        initial_result['evaluation_data']
                    )
                    
                # Sleep to prevent CPU overload
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error in background training: {str(e)}")
            self.learning_state['is_training'] = False
            
    async def _collect_new_examples(self) -> List[Dict[str, Any]]:
        """Collect new examples from ADE usage"""
        try:
            # Get active files
            active_files = await self._get_active_files()
            
            new_examples = []
            for file_path in active_files:
                # Analyze file
                analysis = self.code_analyzer.analyze_file(file_path)
                
                # Generate examples
                examples = self.pipeline_manager.training_generator._generate_file_examples(
                    file_path,
                    analysis,
                    num_examples=10  # Small batch for real-time learning
                )
                
                new_examples.extend(examples)
                
            return new_examples
            
        except Exception as e:
            logger.error(f"Error collecting new examples: {str(e)}")
            return []
            
    async def _get_active_files(self) -> List[str]:
        """Get list of currently active files in ADE"""
        # This would integrate with ADE's file tracking system
        # For now, return empty list
        return []
        
    def stop_learning(self):
        """Stop the learning process"""
        try:
            self.learning_state['is_training'] = False
            return {'status': 'success', 'message': 'Learning stopped'}
            
        except Exception as e:
            logger.error(f"Error stopping learning: {str(e)}")
            return {'status': 'error', 'message': str(e)}
            
    def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning status"""
        return {
            'is_training': self.learning_state['is_training'],
            'current_episode': self.learning_state['current_episode'],
            'total_examples': self.learning_state['total_examples'],
            'last_update': self.learning_state['last_update'].isoformat() if self.learning_state['last_update'] else None
        }
        
    async def get_completion(self, code: str, cursor_position: int) -> List[Dict[str, Any]]:
        """Get code completion suggestions"""
        try:
            # Get completions from provider
            completions = self.completion_provider.get_completions(code, cursor_position)
            
            # If learning is active, update model with this interaction
            if self.learning_state['is_training']:
                await self._update_model_with_interaction(code, cursor_position, completions)
                
            return completions
            
        except Exception as e:
            logger.error(f"Error getting completion: {str(e)}")
            return []
            
    async def _update_model_with_interaction(self, code: str, cursor_position: int, completions: List[Dict[str, Any]]):
        """Update model with user interaction"""
        try:
            # Create example from interaction
            example = {
                'context': code[:cursor_position],
                'position': cursor_position,
                'completions': completions,
                'actual_completion': code[cursor_position:].split()[0],  # Get next word
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'interaction_type': 'user'
                }
            }
            
            # Store in replay buffer
            self.pipeline_manager._store_experience(
                self.pipeline_manager._get_state_representation(example),
                example['actual_completion'],
                1.0  # Reward for user interaction
            )
            
            # Update model if buffer is full enough
            self.pipeline_manager._update_model()
            
        except Exception as e:
            logger.error(f"Error updating model with interaction: {str(e)}")
            
    def save_checkpoint(self):
        """Save current learning state"""
        try:
            checkpoint_dir = Path(self.config['data_dir']) / "learning" / "checkpoints"
            checkpoint_dir.mkdir(parents=True, exist_ok=True)
            
            checkpoint = {
                'learning_state': self.learning_state,
                'pipeline_state': self.pipeline_manager.rl_state,
                'timestamp': datetime.now().isoformat()
            }
            
            checkpoint_file = checkpoint_dir / f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint, f, indent=2)
                
            return {'status': 'success', 'checkpoint_file': str(checkpoint_file)}
            
        except Exception as e:
            logger.error(f"Error saving checkpoint: {str(e)}")
            return {'status': 'error', 'message': str(e)}
            
    def load_checkpoint(self, checkpoint_file: str):
        """Load learning state from checkpoint"""
        try:
            with open(checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
                
            # Restore states
            self.learning_state = checkpoint['learning_state']
            self.pipeline_manager.rl_state = checkpoint['pipeline_state']
            
            return {'status': 'success', 'message': 'Checkpoint loaded'}
            
        except Exception as e:
            logger.error(f"Error loading checkpoint: {str(e)}")
            return {'status': 'error', 'message': str(e)} 