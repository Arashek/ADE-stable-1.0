import asyncio
import argparse
import uuid
import json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, Any, List
from .training_interface import TrainingInterface
from .rl.algorithms import DQNAlgorithm, PPOAlgorithm, A3CAlgorithm
from .config.training_config import ConfigManager, TrainingConfig
from .checkpoint_manager import CheckpointManager
from .owner.interface.training_monitor import TrainingMonitor
from ...config.logging_config import logger

async def train_algorithm(algorithm_name: str,
                         config: TrainingConfig,
                         session_id: str,
                         checkpoint_path: str = None) -> Dict[str, Any]:
    """Train a single algorithm"""
    try:
        # Create algorithm
        if algorithm_name == 'dqn':
            algorithm = DQNAlgorithm(config.algorithms['dqn'].params)
        elif algorithm_name == 'ppo':
            algorithm = PPOAlgorithm(config.algorithms['ppo'].params)
        else:  # a3c
            algorithm = A3CAlgorithm(config.algorithms['a3c'].params)
            
        # Create training interface
        interface = TrainingInterface(output_dir=str(Path(config.output_dir) / session_id))
        
        # Load checkpoint if provided
        if checkpoint_path:
            checkpoint_manager = CheckpointManager(config.output_dir)
            checkpoint_data = checkpoint_manager.load_checkpoint(checkpoint_path)
            algorithm.load(checkpoint_data['algorithm_states'][algorithm_name])
            
        # Start training
        await interface.start_training(algorithm, config.num_episodes)
        
        return {
            'algorithm': algorithm_name,
            'metrics': interface.training_data
        }
        
    except Exception as e:
        logger.error(f"Error training {algorithm_name}: {str(e)}")
        raise

async def train_parallel(config: TrainingConfig, session_id: str):
    """Train multiple algorithms in parallel"""
    try:
        # Create process pool
        with ProcessPoolExecutor(max_workers=config.max_workers) as executor:
            # Create tasks for each enabled algorithm
            tasks = []
            for name, alg_config in config.algorithms.items():
                if alg_config.enabled:
                    task = asyncio.create_task(
                        train_algorithm(name, config, session_id)
                    )
                    tasks.append(task)
                    
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks)
            
        return results
        
    except Exception as e:
        logger.error(f"Error in parallel training: {str(e)}")
        raise

async def main():
    """Main training script"""
    try:
        # Parse arguments
        parser = argparse.ArgumentParser(description='Train code completion model')
        parser.add_argument('--config', type=str, required=True,
                          help='Name of training configuration to use')
        parser.add_argument('--resume-from', type=str,
                          help='Path to checkpoint to resume from')
        parser.add_argument('--output-dir', type=str,
                          help='Override output directory from config')
        parser.add_argument('--port', type=int, default=8000,
                          help='Port for training monitor')
        args = parser.parse_args()
        
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config(args.config)
        
        # Override output directory if specified
        if args.output_dir:
            config.output_dir = args.output_dir
            
        # Override resume path if specified
        if args.resume_from:
            config.resume_from = args.resume_from
            
        # Create output directory
        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Start training monitor
        monitor = TrainingMonitor(output_dir=str(output_dir))
        monitor.start_session(session_id, args.config)
        
        # Start monitor in background
        monitor_task = asyncio.create_task(
            monitor.run(port=args.port)
        )
        
        try:
            # Train algorithms
            results = await train_parallel(config, session_id)
            
            # Save results
            results_file = output_dir / f"results_{session_id}.json"
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
                
            logger.info(f"Training completed successfully. Results saved to {results_file}")
            
        finally:
            # End session
            monitor.end_session(session_id)
            
            # Cancel monitor task
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
                
    except Exception as e:
        logger.error(f"Error in training script: {str(e)}")
        raise

if __name__ == '__main__':
    asyncio.run(main()) 