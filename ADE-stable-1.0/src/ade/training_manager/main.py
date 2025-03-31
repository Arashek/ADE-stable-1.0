import sys
import os
import asyncio
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from src.ade.training_manager.dashboard import DashboardWindow
from src.ade.training_manager.model_config import ModelConfig
from src.ade.training_manager.model_trainer import ModelTrainer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def initialize_training_components():
    """Initialize model training components"""
    try:
        # Initialize configuration
        config = ModelConfig()
        
        # Initialize trainer
        trainer = ModelTrainer(config)
        
        # Export initial metrics
        await trainer.export_metrics()
        
        return trainer
    except Exception as e:
        logger.error(f"Failed to initialize training components: {e}")
        return None

def main():
    # Set up environment
    app_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    os.environ["PYTHONPATH"] = str(app_dir.parent.parent.parent)
    
    # Create application
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Initialize training components
    trainer = asyncio.run(initialize_training_components())
    
    # Create and show main window
    window = DashboardWindow(trainer)
    window.show()
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 