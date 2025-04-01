from typing import Dict, Any, List, Optional
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json
import asyncio
from datetime import datetime
from learning.config.training_config import ConfigManager
from learning.checkpoint_manager import CheckpointManager
from learning.visualization.learning_visualizer import LearningVisualizer
from config.logging_config import logger

class TrainingMonitor:
    """Web interface for monitoring training progress"""
    
    def __init__(self, output_dir: str = "data/learning/training"):
        self.output_dir = Path(output_dir)
        self.app = FastAPI()
        self.config_manager = ConfigManager()
        self.checkpoint_manager = CheckpointManager(output_dir)
        self.visualizer = LearningVisualizer(output_dir=str(self.output_dir / "visualizations"))
        
        # Setup static files and templates
        self.app.mount("/static", StaticFiles(directory="static"), name="static")
        self.templates = Jinja2Templates(directory="templates")
        
        # Setup routes
        self._setup_routes()
        
        # Active training sessions
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def home(request):
            """Home page with training dashboard"""
            return self.templates.TemplateResponse(
                "training_dashboard.html",
                {"request": request}
            )
            
        @self.app.get("/api/configs")
        async def list_configs():
            """List available training configurations"""
            try:
                configs = []
                for config_file in self.config_manager.config_path.glob("*.yaml"):
                    configs.append({
                        'name': config_file.stem,
                        'path': str(config_file)
                    })
                return {"configs": configs}
                
            except Exception as e:
                logger.error(f"Error listing configs: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/api/config/{config_name}")
        async def get_config(config_name: str):
            """Get specific training configuration"""
            try:
                config = self.config_manager.load_config(config_name)
                return config.__dict__
                
            except Exception as e:
                logger.error(f"Error getting config: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/api/checkpoints")
        async def list_checkpoints():
            """List available checkpoints"""
            try:
                checkpoints = self.checkpoint_manager.list_checkpoints()
                return {"checkpoints": checkpoints}
                
            except Exception as e:
                logger.error(f"Error listing checkpoints: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/api/sessions")
        async def list_sessions():
            """List active training sessions"""
            return {"sessions": self.active_sessions}
            
        @self.app.websocket("/ws/training/{session_id}")
        async def training_websocket(websocket: WebSocket, session_id: str):
            """WebSocket connection for real-time training updates"""
            await websocket.accept()
            
            try:
                while True:
                    if session_id in self.active_sessions:
                        session = self.active_sessions[session_id]
                        await websocket.send_json({
                            'episode': session['current_episode'],
                            'metrics': session['metrics'],
                            'visualizations': session['visualizations']
                        })
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"WebSocket error: {str(e)}")
                await websocket.close()
                
    def start_session(self, session_id: str, config_name: str):
        """Start a new training session"""
        try:
            # Load configuration
            config = self.config_manager.load_config(config_name)
            
            # Initialize session
            self.active_sessions[session_id] = {
                'config': config.__dict__,
                'start_time': datetime.now().isoformat(),
                'current_episode': 0,
                'metrics': {
                    'rewards': [],
                    'accuracy': [],
                    'exploration': []
                },
                'visualizations': {
                    'reward_plot': None,
                    'accuracy_plot': None,
                    'exploration_plot': None,
                    'dashboard': None
                }
            }
            
            logger.info(f"Started training session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error starting session: {str(e)}")
            raise
            
    def update_session(self, session_id: str, episode: int, metrics: Dict[str, Any]):
        """Update training session with new metrics"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session not found: {session_id}")
                
            session = self.active_sessions[session_id]
            session['current_episode'] = episode
            
            # Update metrics
            for metric, value in metrics.items():
                if metric in session['metrics']:
                    session['metrics'][metric].append(value)
                    
            # Update visualizations
            session['visualizations'] = {
                'reward_plot': self.visualizer.create_reward_plot(
                    session['metrics']['rewards'],
                    episode
                ),
                'accuracy_plot': self.visualizer.create_completion_accuracy_plot(
                    {'accuracy': session['metrics']['accuracy']},
                    episode
                ),
                'exploration_plot': self.visualizer.create_exploration_plot(
                    {'exploration': session['metrics']['exploration']},
                    episode
                ),
                'dashboard': self.visualizer.create_dashboard(
                    session['metrics'],
                    episode
                )
            }
            
        except Exception as e:
            logger.error(f"Error updating session: {str(e)}")
            raise
            
    def end_session(self, session_id: str):
        """End a training session"""
        try:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session['end_time'] = datetime.now().isoformat()
                
                # Save final metrics
                metrics_file = self.output_dir / f"metrics_{session_id}.json"
                with open(metrics_file, 'w') as f:
                    json.dump(session, f, indent=2)
                    
                del self.active_sessions[session_id]
                logger.info(f"Ended training session: {session_id}")
                
        except Exception as e:
            logger.error(f"Error ending session: {str(e)}")
            raise
            
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the web interface"""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port) 