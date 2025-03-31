from typing import Dict, Any, List, Optional
import asyncio
from pathlib import Path
import json
from datetime import datetime
from .visualization.learning_visualizer import LearningVisualizer
from .rl.algorithms import RLAlgorithm
from ...config.logging_config import logger

class TrainingInterface:
    """Provides real-time feedback and visualization during model training"""
    
    def __init__(self, output_dir: str = "data/learning/training"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.visualizer = LearningVisualizer(output_dir=str(self.output_dir / "visualizations"))
        self.training_data = {
            'rewards': [],
            'accuracy': [],
            'exploration': [],
            'examples': []
        }
        self.current_episode = 0
        
    async def start_training(self, algorithm: RLAlgorithm, num_episodes: int):
        """Start training with real-time visualization"""
        try:
            logger.info(f"Starting training for {num_episodes} episodes")
            
            for episode in range(1, num_episodes + 1):
                self.current_episode = episode
                
                # Run episode
                episode_data = await self._run_episode(algorithm)
                
                # Update training data
                self._update_training_data(episode_data)
                
                # Generate visualizations
                await self._generate_visualizations()
                
                # Log progress
                logger.info(f"Completed episode {episode}/{num_episodes}")
                
            # Save final training data
            self._save_training_data()
            
        except Exception as e:
            logger.error(f"Error during training: {str(e)}")
            raise
            
    async def _run_episode(self, algorithm: RLAlgorithm) -> Dict[str, Any]:
        """Run a single training episode"""
        try:
            # Initialize episode data
            episode_data = {
                'rewards': [],
                'accuracy': [],
                'exploration': [],
                'examples': []
            }
            
            # Run episode steps
            while True:
                # Get action from algorithm
                action = algorithm.select_action()
                
                # Execute action and get reward
                reward, done, info = await self._execute_action(action)
                
                # Update episode data
                episode_data['rewards'].append(reward)
                episode_data['accuracy'].append(info.get('accuracy', 0))
                episode_data['exploration'].append(info.get('exploration_rate', 0))
                episode_data['examples'].append(info.get('example', {}))
                
                # Update algorithm
                algorithm.update(reward, done, info)
                
                if done:
                    break
                    
            return episode_data
            
        except Exception as e:
            logger.error(f"Error running episode: {str(e)}")
            raise
            
    async def _execute_action(self, action: Dict[str, Any]) -> tuple:
        """Execute an action and return reward, done flag, and info"""
        try:
            # Simulate action execution
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Generate mock reward and info
            reward = self._calculate_reward(action)
            info = {
                'accuracy': self._calculate_accuracy(action),
                'exploration_rate': self._calculate_exploration_rate(action),
                'example': self._generate_example(action)
            }
            
            return reward, False, info
            
        except Exception as e:
            logger.error(f"Error executing action: {str(e)}")
            raise
            
    def _calculate_reward(self, action: Dict[str, Any]) -> float:
        """Calculate reward for an action"""
        # Mock reward calculation
        return 0.5
        
    def _calculate_accuracy(self, action: Dict[str, Any]) -> float:
        """Calculate accuracy for an action"""
        # Mock accuracy calculation
        return 0.8
        
    def _calculate_exploration_rate(self, action: Dict[str, Any]) -> float:
        """Calculate exploration rate for an action"""
        # Mock exploration rate calculation
        return 0.3
        
    def _generate_example(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Generate example completion"""
        # Mock example generation
        return {
            'context': 'def process_data(data):',
            'predicted': '    return data.process()',
            'actual': '    return data.process()',
            'reward': 1.0
        }
        
    def _update_training_data(self, episode_data: Dict[str, Any]):
        """Update training data with episode results"""
        try:
            # Update rewards
            self.training_data['rewards'].append(
                sum(episode_data['rewards']) / len(episode_data['rewards'])
            )
            
            # Update accuracy
            self.training_data['accuracy'].append(
                sum(episode_data['accuracy']) / len(episode_data['accuracy'])
            )
            
            # Update exploration
            self.training_data['exploration'].append(
                sum(episode_data['exploration']) / len(episode_data['exploration'])
            )
            
            # Update examples
            self.training_data['examples'].extend(episode_data['examples'])
            
        except Exception as e:
            logger.error(f"Error updating training data: {str(e)}")
            raise
            
    async def _generate_visualizations(self):
        """Generate visualizations for current training state"""
        try:
            # Create reward plot
            self.visualizer.create_reward_plot(
                self.training_data['rewards'],
                self.current_episode
            )
            
            # Create accuracy plot
            self.visualizer.create_completion_accuracy_plot(
                {'accuracy': self.training_data['accuracy']},
                self.current_episode
            )
            
            # Create exploration plot
            self.visualizer.create_exploration_plot(
                {'exploration': self.training_data['exploration']},
                self.current_episode
            )
            
            # Create learning curves
            self.visualizer.create_learning_curves(
                self.training_data,
                self.current_episode
            )
            
            # Create completion examples
            self.visualizer.create_completion_examples(
                self.training_data['examples'][-10:],
                self.current_episode
            )
            
            # Create dashboard
            self.visualizer.create_dashboard(
                self.training_data,
                self.current_episode
            )
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {str(e)}")
            raise
            
    def _save_training_data(self):
        """Save training data to file"""
        try:
            filename = f'training_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            filepath = self.output_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(self.training_data, f, indent=2)
                
            logger.info(f"Saved training data to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving training data: {str(e)}")
            raise 