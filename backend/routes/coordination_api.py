from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import asyncio
import logging
import uuid
from datetime import datetime

from services.coordination.agent_coordinator import AgentCoordinator
from services.coordination.agent_registry import AgentRegistry
from services.coordination.consensus_mechanism import ConsensusMechanism, ConflictResolutionStrategy

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/coordination",
    tags=["coordination"],
    responses={404: {"description": "Not found"}},
)

# Models for API requests and responses
class AgentStatusResponse(BaseModel):
    id: str
    type: str
    status: str
    capabilities: List[str]
    last_activity: Optional[str] = None


class ConflictResolutionResponse(BaseModel):
    attribute: str
    values: Dict[str, Any]
    selected_value: Any
    selected_agent: str
    confidence: float


class ConsensusVoteRequest(BaseModel):
    option: Any
    confidence: float
    reasoning: str


class ConsensusDecisionResponse(BaseModel):
    id: str
    key: str
    description: str
    options: List[Any]
    selected_option: Optional[Any] = None
    votes: List[Dict[str, Any]] = []
    confidence: float = 0.0
    status: str = "pending"


class CoordinationStatusResponse(BaseModel):
    active: bool
    agents: List[AgentStatusResponse]
    conflicts: List[ConflictResolutionResponse] = []
    consensus_decisions: List[ConsensusDecisionResponse] = []


# In-memory storage for active conflicts and consensus decisions
# In a production environment, this would be stored in a database
active_conflicts = []
active_consensus_decisions = []
coordination_active = False


# Helper function to get agent coordinator instance
def get_coordinator():
    return AgentCoordinator()


# Helper function to get agent registry instance
def get_registry():
    return AgentRegistry()


@router.get("/status", response_model=CoordinationStatusResponse)
async def get_coordination_status(
    coordinator: AgentCoordinator = Depends(get_coordinator),
    registry: AgentRegistry = Depends(get_registry)
):
    """
    Get the current status of the agent coordination system.
    """
    try:
        # Get registered agents
        agent_ids = await registry.get_all_agent_ids()
        agents = []
        
        for agent_id in agent_ids:
            agent_info = await registry.get_agent_info(agent_id)
            if agent_info:
                status = "active"
                if agent_info.get("status") == "busy":
                    status = "busy"
                elif agent_info.get("status") == "offline":
                    status = "inactive"
                
                agents.append(AgentStatusResponse(
                    id=agent_id,
                    type=agent_info.get("type", "unknown"),
                    status=status,
                    capabilities=agent_info.get("capabilities", []),
                    last_activity=agent_info.get("last_activity")
                ))
        
        # Convert active conflicts to response format
        conflicts = []
        for conflict in active_conflicts:
            conflicts.append(ConflictResolutionResponse(
                attribute=conflict["attribute"],
                values=conflict["values"],
                selected_value=conflict["selected_value"],
                selected_agent=conflict["selected_agent"],
                confidence=conflict["confidence"]
            ))
        
        # Convert active consensus decisions to response format
        consensus_decisions = []
        for decision in active_consensus_decisions:
            consensus_decisions.append(ConsensusDecisionResponse(
                id=decision["id"],
                key=decision["key"],
                description=decision["description"],
                options=decision["options"],
                selected_option=decision.get("selected_option"),
                votes=decision.get("votes", []),
                confidence=decision.get("confidence", 0.0),
                status=decision.get("status", "pending")
            ))
        
        return CoordinationStatusResponse(
            active=coordination_active,
            agents=agents,
            conflicts=conflicts,
            consensus_decisions=consensus_decisions
        )
    
    except Exception as e:
        logger.error(f"Error getting coordination status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get coordination status: {str(e)}")


@router.post("/start")
async def start_coordination(
    coordinator: AgentCoordinator = Depends(get_coordinator)
):
    """
    Start the agent coordination system.
    """
    global coordination_active
    
    try:
        # Initialize the coordinator if needed
        if not coordinator._initialized:
            await coordinator._initialize_agents()
        
        coordination_active = True
        
        return {"success": True, "message": "Agent coordination system started"}
    
    except Exception as e:
        logger.error(f"Error starting coordination: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start coordination: {str(e)}")


@router.post("/stop")
async def stop_coordination():
    """
    Stop the agent coordination system.
    """
    global coordination_active, active_conflicts, active_consensus_decisions
    
    try:
        coordination_active = False
        active_conflicts = []
        active_consensus_decisions = []
        
        return {"success": True, "message": "Agent coordination system stopped"}
    
    except Exception as e:
        logger.error(f"Error stopping coordination: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to stop coordination: {str(e)}")


@router.post("/consensus", response_model=ConsensusDecisionResponse)
async def create_consensus_decision(
    decision: Dict[str, Any] = Body(...),
    coordinator: AgentCoordinator = Depends(get_coordinator)
):
    """
    Create a new consensus decision point.
    """
    global active_consensus_decisions
    
    try:
        if not coordination_active:
            raise HTTPException(status_code=400, detail="Agent coordination system is not active")
        
        # Generate a unique ID for the decision
        decision_id = f"decision_{uuid.uuid4().hex[:8]}"
        
        # Create the decision point
        decision_point = {
            "id": decision_id,
            "key": decision.get("key", "unnamed_decision"),
            "description": decision.get("description", "No description provided"),
            "options": decision.get("options", []),
            "status": "pending",
            "votes": [],
            "confidence": 0.0,
            "created_at": datetime.now().isoformat()
        }
        
        # Add to active decisions
        active_consensus_decisions.append(decision_point)
        
        # If agents are specified, start the consensus process asynchronously
        if "agents" in decision and decision["agents"]:
            asyncio.create_task(
                process_consensus_decision(decision_id, decision["agents"], coordinator)
            )
        
        return ConsensusDecisionResponse(
            id=decision_point["id"],
            key=decision_point["key"],
            description=decision_point["description"],
            options=decision_point["options"],
            status=decision_point["status"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating consensus decision: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create consensus decision: {str(e)}")


@router.get("/consensus/{decision_id}", response_model=ConsensusDecisionResponse)
async def get_consensus_decision(decision_id: str):
    """
    Get the status of a consensus decision.
    """
    global active_consensus_decisions
    
    try:
        # Find the decision
        for decision in active_consensus_decisions:
            if decision["id"] == decision_id:
                return ConsensusDecisionResponse(
                    id=decision["id"],
                    key=decision["key"],
                    description=decision["description"],
                    options=decision["options"],
                    selected_option=decision.get("selected_option"),
                    votes=decision.get("votes", []),
                    confidence=decision.get("confidence", 0.0),
                    status=decision.get("status", "pending")
                )
        
        raise HTTPException(status_code=404, detail=f"Consensus decision {decision_id} not found")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting consensus decision: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get consensus decision: {str(e)}")


@router.post("/consensus/{decision_id}/vote")
async def submit_vote(
    decision_id: str,
    vote: ConsensusVoteRequest,
    agent_id: str = Body(...),
    agent_type: str = Body(...)
):
    """
    Submit a vote for a consensus decision.
    """
    global active_consensus_decisions
    
    try:
        # Find the decision
        decision_index = None
        for i, decision in enumerate(active_consensus_decisions):
            if decision["id"] == decision_id:
                decision_index = i
                break
        
        if decision_index is None:
            raise HTTPException(status_code=404, detail=f"Consensus decision {decision_id} not found")
        
        # Add the vote
        if "votes" not in active_consensus_decisions[decision_index]:
            active_consensus_decisions[decision_index]["votes"] = []
        
        active_consensus_decisions[decision_index]["votes"].append({
            "agent": agent_type,
            "agent_id": agent_id,
            "option": vote.option,
            "confidence": vote.confidence,
            "reasoning": vote.reasoning,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update status to in_progress
        active_consensus_decisions[decision_index]["status"] = "in_progress"
        
        return {"success": True, "message": "Vote submitted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting vote: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit vote: {str(e)}")


async def process_consensus_decision(decision_id: str, agents: List[str], coordinator: AgentCoordinator):
    """
    Process a consensus decision asynchronously.
    """
    global active_consensus_decisions
    
    try:
        # Find the decision
        decision_index = None
        for i, decision in enumerate(active_consensus_decisions):
            if decision["id"] == decision_id:
                decision_index = i
                break
        
        if decision_index is None:
            logger.error(f"Consensus decision {decision_id} not found for processing")
            return
        
        # Update status
        active_consensus_decisions[decision_index]["status"] = "in_progress"
        
        # Build consensus using the coordinator
        decision_point = {
            "id": decision_id,
            "key": active_consensus_decisions[decision_index]["key"],
            "description": active_consensus_decisions[decision_index]["description"],
            "options": active_consensus_decisions[decision_index]["options"]
        }
        
        result = await coordinator.build_consensus(
            decision_point=active_consensus_decisions[decision_index]["key"],
            options=active_consensus_decisions[decision_index]["options"],
            agents=agents
        )
        
        # Update the decision with the result
        active_consensus_decisions[decision_index]["selected_option"] = result
        active_consensus_decisions[decision_index]["status"] = "resolved"
        
        # Calculate confidence based on votes
        votes = active_consensus_decisions[decision_index].get("votes", [])
        if votes:
            # Find votes for the selected option
            matching_votes = [v for v in votes if v["option"] == result]
            if matching_votes:
                avg_confidence = sum(v["confidence"] for v in matching_votes) / len(matching_votes)
                active_consensus_decisions[decision_index]["confidence"] = avg_confidence
            else:
                active_consensus_decisions[decision_index]["confidence"] = 0.5
        else:
            active_consensus_decisions[decision_index]["confidence"] = 0.7  # Default confidence
    
    except Exception as e:
        logger.error(f"Error processing consensus decision: {str(e)}")
        
        # Update status to indicate error
        if decision_index is not None:
            active_consensus_decisions[decision_index]["status"] = "error"
            active_consensus_decisions[decision_index]["error"] = str(e)


@router.post("/conflicts")
async def record_conflict_resolution(
    conflict: Dict[str, Any] = Body(...),
    coordinator: AgentCoordinator = Depends(get_coordinator)
):
    """
    Record a conflict resolution.
    """
    global active_conflicts
    
    try:
        if not coordination_active:
            raise HTTPException(status_code=400, detail="Agent coordination system is not active")
        
        # Add to active conflicts
        active_conflicts.append(conflict)
        
        # Limit the number of stored conflicts
        if len(active_conflicts) > 10:
            active_conflicts = active_conflicts[-10:]
        
        return {"success": True, "message": "Conflict resolution recorded"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording conflict resolution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to record conflict resolution: {str(e)}")


@router.get("/agents", response_model=List[AgentStatusResponse])
async def get_agents(registry: AgentRegistry = Depends(get_registry)):
    """
    Get all registered agents.
    """
    try:
        # Get registered agents
        agent_ids = await registry.get_all_agent_ids()
        agents = []
        
        for agent_id in agent_ids:
            agent_info = await registry.get_agent_info(agent_id)
            if agent_info:
                status = "active"
                if agent_info.get("status") == "busy":
                    status = "busy"
                elif agent_info.get("status") == "offline":
                    status = "inactive"
                
                agents.append(AgentStatusResponse(
                    id=agent_id,
                    type=agent_info.get("type", "unknown"),
                    status=status,
                    capabilities=agent_info.get("capabilities", []),
                    last_activity=agent_info.get("last_activity")
                ))
        
        return agents
    
    except Exception as e:
        logger.error(f"Error getting agents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get agents: {str(e)}")
