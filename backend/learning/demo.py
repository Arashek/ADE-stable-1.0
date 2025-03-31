import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any
from .integration import LearningIntegration
from ...config.logging_config import logger

async def run_learning_demo():
    """Run a demo of the learning system"""
    try:
        # Initialize ADE config
        ade_config = {
            'data_dir': 'data',
            'num_examples': 1000,
            'learning_rate': 0.001,
            'batch_size': 32
        }
        
        # Initialize learning integration
        learning = LearningIntegration(ade_config)
        
        # Example code files for training
        code_files = [
            'backend/learning/completion/code_analysis.py',
            'backend/learning/completion/completion_provider.py',
            'backend/learning/completion/training_generator.py'
        ]
        
        # Start learning
        logger.info("Starting learning process...")
        result = await learning.start_learning(code_files)
        
        if result['status'] == 'success':
            logger.info("Learning started successfully")
            
            # Get learning status
            status = learning.get_learning_status()
            logger.info(f"Current learning status: {status}")
            
            # Example of getting completions
            code = """
def process_data(data: Dict[str, Any]) -> List[Any]:
    result = []
    for key, value in data.items():
        if isinstance(value, list):
            result.extend(value)
    return result
"""
            cursor_position = len(code) - 1
            
            completions = await learning.get_completion(code, cursor_position)
            logger.info(f"Completions: {completions}")
            
            # Save checkpoint
            checkpoint_result = learning.save_checkpoint()
            if checkpoint_result['status'] == 'success':
                logger.info(f"Saved checkpoint to {checkpoint_result['checkpoint_file']}")
                
            # Stop learning
            stop_result = learning.stop_learning()
            if stop_result['status'] == 'success':
                logger.info("Learning stopped successfully")
                
        else:
            logger.error(f"Failed to start learning: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Error in demo: {str(e)}")
        
def main():
    """Main entry point for the demo"""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run demo
    asyncio.run(run_learning_demo())
    
if __name__ == "__main__":
    main() 