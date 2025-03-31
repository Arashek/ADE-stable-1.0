import os
import logging
import webbrowser
from pathlib import Path
from dotenv import load_dotenv
import streamlit.web.bootstrap as bootstrap

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def launch_interface():
    """Launch the interactive dataset generation interface"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get host and port from environment variables
        host = os.getenv("STREAMLIT_HOST", "0.0.0.0")
        port = int(os.getenv("STREAMLIT_PORT", "8501"))
        
        # Get the path to the interface script
        interface_path = Path(__file__).parent / "interactive_interface.py"
        
        # Open web browser
        webbrowser.open(f"http://localhost:{port}")
        
        # Start Streamlit server
        bootstrap.run(
            str(interface_path),
            "",
            [],
            {
                "server.address": host,
                "server.port": port,
                "browser.serverAddress": "localhost",
                "browser.serverPort": port,
                "browser.gatherUsageStats": False
            }
        )
        
    except Exception as e:
        logger.error(f"Error launching interface: {str(e)}")
        raise

def main():
    """Main function to run the interface server"""
    try:
        launch_interface()
    except Exception as e:
        logger.error(f"Error running interface server: {str(e)}")
        raise

if __name__ == "__main__":
    main() 