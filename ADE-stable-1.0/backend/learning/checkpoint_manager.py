from typing import Dict, Any, Optional
from pathlib import Path
import json
import shutil
from datetime import datetime
from .config.training_config import TrainingConfig
from ...config.logging_config import logger

class CheckpointManager:
    """Manages training checkpoints"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.checkpoint_dir = self.output_dir / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
    def save_checkpoint(self, 
                       training_data: Dict[str, Any],
                       config: TrainingConfig,
                       algorithm_states: Dict[str, Any],
                       episode: int) -> str:
        """Save training checkpoint"""
        try:
            # Create checkpoint directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            checkpoint_path = self.checkpoint_dir / f"checkpoint_{episode}_{timestamp}"
            checkpoint_path.mkdir(parents=True, exist_ok=True)
            
            # Save training data
            with open(checkpoint_path / "training_data.json", 'w') as f:
                json.dump(training_data, f, indent=2)
                
            # Save config
            with open(checkpoint_path / "config.json", 'w') as f:
                json.dump(config.__dict__, f, indent=2)
                
            # Save algorithm states
            for name, state in algorithm_states.items():
                algorithm_dir = checkpoint_path / name
                algorithm_dir.mkdir(exist_ok=True)
                self._save_algorithm_state(algorithm_dir, state)
                
            logger.info(f"Saved checkpoint to {checkpoint_path}")
            return str(checkpoint_path)
            
        except Exception as e:
            logger.error(f"Error saving checkpoint: {str(e)}")
            raise
            
    def load_checkpoint(self, checkpoint_path: str) -> Dict[str, Any]:
        """Load training checkpoint"""
        try:
            checkpoint_dir = Path(checkpoint_path)
            if not checkpoint_dir.exists():
                raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
                
            # Load training data
            with open(checkpoint_dir / "training_data.json", 'r') as f:
                training_data = json.load(f)
                
            # Load config
            with open(checkpoint_dir / "config.json", 'r') as f:
                config_data = json.load(f)
                
            # Load algorithm states
            algorithm_states = {}
            for algorithm_dir in checkpoint_dir.iterdir():
                if algorithm_dir.is_dir():
                    algorithm_states[algorithm_dir.name] = self._load_algorithm_state(algorithm_dir)
                    
            return {
                'training_data': training_data,
                'config': config_data,
                'algorithm_states': algorithm_states
            }
            
        except Exception as e:
            logger.error(f"Error loading checkpoint: {str(e)}")
            raise
            
    def _save_algorithm_state(self, algorithm_dir: Path, state: Dict[str, Any]):
        """Save algorithm-specific state"""
        try:
            # Save model weights
            if 'weights' in state:
                weights_dir = algorithm_dir / "weights"
                weights_dir.mkdir(exist_ok=True)
                self._save_weights(weights_dir, state['weights'])
                
            # Save optimizer state
            if 'optimizer' in state:
                with open(algorithm_dir / "optimizer.json", 'w') as f:
                    json.dump(state['optimizer'], f, indent=2)
                    
            # Save other state data
            if 'other' in state:
                with open(algorithm_dir / "other.json", 'w') as f:
                    json.dump(state['other'], f, indent=2)
                    
        except Exception as e:
            logger.error(f"Error saving algorithm state: {str(e)}")
            raise
            
    def _load_algorithm_state(self, algorithm_dir: Path) -> Dict[str, Any]:
        """Load algorithm-specific state"""
        try:
            state = {}
            
            # Load model weights
            weights_dir = algorithm_dir / "weights"
            if weights_dir.exists():
                state['weights'] = self._load_weights(weights_dir)
                
            # Load optimizer state
            optimizer_file = algorithm_dir / "optimizer.json"
            if optimizer_file.exists():
                with open(optimizer_file, 'r') as f:
                    state['optimizer'] = json.load(f)
                    
            # Load other state data
            other_file = algorithm_dir / "other.json"
            if other_file.exists():
                with open(other_file, 'r') as f:
                    state['other'] = json.load(f)
                    
            return state
            
        except Exception as e:
            logger.error(f"Error loading algorithm state: {str(e)}")
            raise
            
    def _save_weights(self, weights_dir: Path, weights: Dict[str, Any]):
        """Save model weights"""
        try:
            for name, weight in weights.items():
                weight_file = weights_dir / f"{name}.npy"
                np.save(weight_file, weight)
                
        except Exception as e:
            logger.error(f"Error saving weights: {str(e)}")
            raise
            
    def _load_weights(self, weights_dir: Path) -> Dict[str, Any]:
        """Load model weights"""
        try:
            weights = {}
            for weight_file in weights_dir.glob("*.npy"):
                weights[weight_file.stem] = np.load(weight_file)
            return weights
            
        except Exception as e:
            logger.error(f"Error loading weights: {str(e)}")
            raise
            
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List all available checkpoints"""
        try:
            checkpoints = []
            for checkpoint_dir in self.checkpoint_dir.iterdir():
                if checkpoint_dir.is_dir():
                    info_file = checkpoint_dir / "info.json"
                    if info_file.exists():
                        with open(info_file, 'r') as f:
                            info = json.load(f)
                            checkpoints.append({
                                'path': str(checkpoint_dir),
                                'episode': info['episode'],
                                'timestamp': info['timestamp'],
                                'metrics': info['metrics']
                            })
            return sorted(checkpoints, key=lambda x: x['episode'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error listing checkpoints: {str(e)}")
            raise
            
    def delete_checkpoint(self, checkpoint_path: str):
        """Delete a checkpoint"""
        try:
            checkpoint_dir = Path(checkpoint_path)
            if checkpoint_dir.exists():
                shutil.rmtree(checkpoint_dir)
                logger.info(f"Deleted checkpoint: {checkpoint_path}")
            else:
                logger.warning(f"Checkpoint not found: {checkpoint_path}")
                
        except Exception as e:
            logger.error(f"Error deleting checkpoint: {str(e)}")
            raise 