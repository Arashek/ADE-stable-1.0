import os
import logging
import uvicorn
import webbrowser
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="ADE Training Monitor")

# Mount static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Serve index.html
@app.get("/")
async def read_root():
    return FileResponse(str(static_dir / "index.html"))

def launch_monitor(host: str = "0.0.0.0", port: int = 8000):
    """Launch the training monitor web interface"""
    try:
        # Verify AWS setup first
        from verify_setup import verify_setup
        if not verify_setup():
            logger.error("AWS setup verification failed. Please fix the issues before launching the monitor.")
            return False
            
        # Start the web server
        logger.info(f"Starting training monitor on http://{host}:{port}")
        webbrowser.open(f"http://localhost:{port}")
        
        uvicorn.run(app, host=host, port=port)
        return True
        
    except Exception as e:
        logger.error(f"Failed to launch training monitor: {str(e)}")
        return False

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("MONITOR_HOST", "0.0.0.0")
    port = int(os.getenv("MONITOR_PORT", "8000"))
    
    if launch_monitor(host, port):
        logger.info("Training monitor launched successfully")
    else:
        logger.error("Failed to launch training monitor") 