import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from ade_model_training.config import Config
from ade_model_training.gui import LearningHubInterface
from ade_model_training.trainer import DistributedTrainer
from ade_model_training.visualizer import LearningVisualizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('model_training.log')
    ]
)
logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='ADE Model Training Application')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--standalone', action='store_true', help='Run in standalone mode')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--no-gui', action='store_true', help='Run without GUI')
    return parser.parse_args()

def setup_environment(config_path: Optional[str] = None) -> Config:
    """Set up the environment and load configuration."""
    config = Config()
    if config_path:
        config.load(config_path)
    return config

def main():
    """Main entry point for the Model-Training application."""
    args = parse_args()
    
    # Set up logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Set up environment and load configuration
        config = setup_environment(args.config)
        
        # Initialize components
        visualizer = LearningVisualizer(config)
        trainer = DistributedTrainer(config)
        
        if not args.no_gui:
            # Launch GUI
            interface = LearningHubInterface(config, trainer, visualizer)
            interface.run()
        else:
            # Run in headless mode
            logger.info("Running in headless mode")
            trainer.train()
            
    except Exception as e:
        logger.error(f"Error during application startup: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main() 