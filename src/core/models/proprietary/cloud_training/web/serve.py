import os
import logging
import webbrowser
from pathlib import Path
from dotenv import load_dotenv
import uvicorn
from app import app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def launch_monitor():
    """Launch the training monitor web interface"""
    try:
        # Get host and port from environment variables
        host = os.getenv('MONITOR_HOST', '0.0.0.0')
        port = int(os.getenv('MONITOR_PORT', '8000'))
        
        # Open web browser
        url = f'http://localhost:{port}'
        webbrowser.open(url)
        
        # Start the server
        logger.info(f"Starting training monitor at {url}")
        uvicorn.run(app, host=host, port=port)
        
    except Exception as e:
        logger.error(f"Failed to launch training monitor: {str(e)}")
        raise

if __name__ == "__main__":
    launch_monitor() 