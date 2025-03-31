from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from ..services.agent_orchestrator import agent_orchestrator
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class AgentRequest(BaseModel):
    prompt: str
    context: Dict[str, Any] = {
        'task_description': '',
        'progress_status': 'Not started',
        'blockers': [],
        'previous_solutions': []
    }

class AgentResponse(BaseModel):
    workflow_guidance: Dict[str, str]
    agent_solutions: List[Dict[str, Any]]
    coordinator_result: str

@router.post("/process", response_model=AgentResponse)
async def process_with_agents(request: AgentRequest):
    """Process a request using multiple agents and coordinate their responses."""
    try:
        result = await agent_orchestrator.process_request(
            prompt=request.prompt,
            context=request.context
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing agent request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/agents")
async def list_agents():
    """List all available agents and their configurations."""
    try:
        agents = {
            'solver_agents': [
                {
                    'name': name,
                    'role': config['role'],
                    'model': config['model']
                }
                for name, config in agent_orchestrator.agents.items()
                if name != 'coordinator_agent'
            ],
            'workflow_agents': [
                {
                    'name': name,
                    'role': config['role'],
                    'model': config['model']
                }
                for name, config in agent_orchestrator.workflow_agents.items()
            ],
            'coordinator': {
                'name': 'coordinator_agent',
                'role': agent_orchestrator.agents['coordinator_agent']['role'],
                'model': agent_orchestrator.agents['coordinator_agent']['model']
            }
        }
        return agents
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 