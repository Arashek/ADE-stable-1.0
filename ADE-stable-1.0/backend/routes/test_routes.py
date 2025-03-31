from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from ..services.test_orchestrator import test_orchestrator
from ..services.model_trainer import model_trainer
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class TestConfig(BaseModel):
    num_iterations: int = 100
    learning_rate: Optional[float] = None
    batch_size: Optional[int] = None
    max_epochs: Optional[int] = None

class TestResult(BaseModel):
    prompt: str
    success: bool
    metrics: Dict[str, Any]
    agent_metrics: List[Dict[str, Any]]
    error: Optional[str] = None

class TestHistory(BaseModel):
    results: List[TestResult]
    total_iterations: int
    success_rate: float
    average_latency: float

@router.post("/start")
async def start_automated_testing(config: TestConfig):
    """Start automated testing with specified configuration."""
    try:
        if config.learning_rate:
            test_orchestrator.learning_rate = config.learning_rate
        if config.batch_size:
            model_trainer.batch_size = config.batch_size
        if config.max_epochs:
            model_trainer.max_epochs = config.max_epochs

        # Start testing in background
        await test_orchestrator.start_automated_testing(config.num_iterations)
        return {"message": "Automated testing started", "config": config}
    except Exception as e:
        logger.error(f"Error starting automated testing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_automated_testing():
    """Stop automated testing."""
    try:
        test_orchestrator.stop_automated_testing()
        return {"message": "Automated testing stopped"}
    except Exception as e:
        logger.error(f"Error stopping automated testing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_test_status():
    """Get current status of automated testing."""
    try:
        return {
            "is_running": test_orchestrator.is_running,
            "current_iteration": test_orchestrator.current_iteration,
            "test_history_length": len(test_orchestrator.test_history)
        }
    except Exception as e:
        logger.error(f"Error getting test status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_test_history():
    """Get test history with metrics."""
    try:
        history = test_orchestrator.test_history
        success_count = sum(1 for t in history if t['success'])
        total_latency = sum(t['metrics']['total_latency'] for t in history)
        
        return TestHistory(
            results=[
                TestResult(
                    prompt=t['prompt'],
                    success=t['success'],
                    metrics=t['metrics'],
                    agent_metrics=t['agent_metrics'],
                    error=t.get('error')
                )
                for t in history
            ],
            total_iterations=len(history),
            success_rate=success_count / len(history) if history else 0,
            average_latency=total_latency / len(history) if history else 0
        )
    except Exception as e:
        logger.error(f"Error getting test history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save-policies")
async def save_policies(path: str):
    """Save trained policies to disk."""
    try:
        await model_trainer.save_policies(path)
        return {"message": "Policies saved successfully"}
    except Exception as e:
        logger.error(f"Error saving policies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/load-policies")
async def load_policies(path: str):
    """Load trained policies from disk."""
    try:
        await model_trainer.load_policies(path)
        return {"message": "Policies loaded successfully"}
    except Exception as e:
        logger.error(f"Error loading policies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 