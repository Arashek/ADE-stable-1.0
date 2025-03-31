import os
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from .server import app as chat_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()

# Mount static files
web_dir = Path(__file__).parent / "web"
app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

# Mount chat app
app.mount("/api", chat_app)

@app.get("/")
async def read_root():
    """Serve the web interface"""
    return FileResponse(str(web_dir / "index.html"))

def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the training chat server with web interface"""
    logger.info(f"Starting training chat server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server() 