from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import asyncio
import logging
import uuid
import sys
import traceback
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Import error logging system
try:
    from scripts.basic_error_logging import log_error, ErrorCategory, ErrorSeverity
    error_logging_available = True
except ImportError:
    error_logging_available = False
    # Define fallback error categories and severities
    class ErrorCategory:
        API = "API"
        COORDINATION = "COORDINATION"
        AGENT = "AGENT"
        COMMUNICATION = "COMMUNICATION"
        PROCESSING = "PROCESSING"
        SYSTEM = "SYSTEM"
        VALIDATION = "VALIDATION"
    
    class ErrorSeverity:
        CRITICAL = "CRITICAL"
        ERROR = "ERROR"
        WARNING = "WARNING"
        INFO = "INFO"

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
    errors: Dict[str, Any] = {}


# In-memory storage for active conflicts and consensus decisions
# In a production environment, this would be stored in a database
active_conflicts = []
active_consensus_decisions = []
coordination_active = False
api_errors = []


# Helper function to get agent coordinator instance
def get_coordinator():
    return AgentCoordinator()


# Helper function to get agent registry instance
def get_registry():
    return AgentRegistry()


# Helper function to log errors
def log_api_error(error: Any, category: str = ErrorCategory.API, 
                 severity: str = ErrorSeverity.ERROR, context: Dict[str, Any] = None):
    """
    Log an error using the error logging system
    
    Args:
        error: The error object or message
        category: Category of the error
        severity: Severity level of the error
        context: Additional context information
    """
    error_message = str(error)
    
    # Log to console
    logger.error(f"API Error [{category}][{severity}]: {error_message}")
    
    # Add to in-memory error list
    error_entry = {
        "message": error_message,
        "category": category,
        "severity": severity,
        "timestamp": datetime.now().isoformat(),
        "context": context or {}
    }
    
    api_errors.append(error_entry)
    
    # Log to error logging system if available
    if error_logging_available:
        try:
            error_id = log_error(
                error=error,
                category=category,
                severity=severity,
                component="coordination_api",
                source="backend.routes.coordination_api",
                context=context or {}
            )
            error_entry["id"] = error_id
        except Exception as e:
            logger.error(f"Failed to log error: {str(e)}")


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
        
        # Compile error statistics
        error_stats = {}
        if hasattr(coordinator, 'errors'):
            coordinator_errors = coordinator.errors
            error_stats["coordinator"] = {
                "total": len(coordinator_errors),
                "by_severity": {}
            }
            for error in coordinator_errors:
                severity = error.get("severity", "UNKNOWN")
                error_stats["coordinator"]["by_severity"][severity] = error_stats["coordinator"]["by_severity"].get(severity, 0) + 1
        
        error_stats["api"] = {
            "total": len(api_errors),
            "by_severity": {}
        }
        for error in api_errors:
            severity = error.get("severity", "UNKNOWN")
            error_stats["api"]["by_severity"][severity] = error_stats["api"]["by_severity"].get(severity, 0) + 1
        
        return CoordinationStatusResponse(
            active=coordination_active,
            agents=agents,
            conflicts=conflicts,
            consensus_decisions=consensus_decisions,
            errors=error_stats
        )
    
    except Exception as e:
        error_context = {"action": "get_coordination_status"}
        log_api_error(e, context=error_context)
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
        error_context = {"action": "start_coordination"}
        log_api_error(e, context=error_context)
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
        error_context = {"action": "stop_coordination"}
        log_api_error(e, context=error_context)
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
            error_msg = "Coordination system is not active"
            log_api_error(
                error_msg,
                category=ErrorCategory.API,
                severity=ErrorSeverity.WARNING,
                context={"action": "create_consensus_decision"}
            )
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Validate required fields
        required_fields = ["key", "description", "options"]
        for field in required_fields:
            if field not in decision:
                error_msg = f"Missing required field: {field}"
                log_api_error(
                    error_msg,
                    category=ErrorCategory.VALIDATION,
                    severity=ErrorSeverity.ERROR,
                    context={"action": "create_consensus_decision", "decision": decision}
                )
                raise HTTPException(status_code=400, detail=error_msg)
        
        # Create decision object
        decision_id = str(uuid.uuid4())
        new_decision = {
            "id": decision_id,
            "key": decision["key"],
            "description": decision["description"],
            "options": decision["options"],
            "votes": [],
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        active_consensus_decisions.append(new_decision)
        
        # Start async process to collect votes if agents are specified
        if "agents" in decision and isinstance(decision["agents"], list) and len(decision["agents"]) > 0:
            asyncio.create_task(process_consensus_decision(decision_id, decision["agents"], coordinator))
        
        return ConsensusDecisionResponse(
            id=new_decision["id"],
            key=new_decision["key"],
            description=new_decision["description"],
            options=new_decision["options"],
            status=new_decision["status"]
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        error_context = {"action": "create_consensus_decision", "decision": decision}
        log_api_error(e, context=error_context)
        raise HTTPException(status_code=500, detail=f"Failed to create consensus decision: {str(e)}")


@router.get("/consensus/{decision_id}", response_model=ConsensusDecisionResponse)
async def get_consensus_decision(decision_id: str):
    """
    Get the status of a consensus decision.
    """
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
        
        # Decision not found
        error_msg = f"Consensus decision not found: {decision_id}"
        log_api_error(
            error_msg,
            category=ErrorCategory.API,
            severity=ErrorSeverity.WARNING,
            context={"action": "get_consensus_decision", "decision_id": decision_id}
        )
        raise HTTPException(status_code=404, detail=error_msg)
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        error_context = {"action": "get_consensus_decision", "decision_id": decision_id}
        log_api_error(e, context=error_context)
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
    try:
        if not coordination_active:
            error_msg = "Coordination system is not active"
            log_api_error(
                error_msg,
                category=ErrorCategory.API,
                severity=ErrorSeverity.WARNING,
                context={"action": "submit_vote", "decision_id": decision_id}
            )
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Find the decision
        decision_index = None
        for i, decision in enumerate(active_consensus_decisions):
            if decision["id"] == decision_id:
                decision_index = i
                break
        
        if decision_index is None:
            error_msg = f"Consensus decision not found: {decision_id}"
            log_api_error(
                error_msg,
                category=ErrorCategory.API,
                severity=ErrorSeverity.WARNING,
                context={"action": "submit_vote", "decision_id": decision_id}
            )
            raise HTTPException(status_code=404, detail=error_msg)
        
        # Check if decision is still pending
        if active_consensus_decisions[decision_index]["status"] != "pending":
            error_msg = f"Consensus decision is already {active_consensus_decisions[decision_index]['status']}"
            log_api_error(
                error_msg,
                category=ErrorCategory.API,
                severity=ErrorSeverity.WARNING,
                context={"action": "submit_vote", "decision_id": decision_id}
            )
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Add the vote
        vote_entry = {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "option": vote.option,
            "confidence": vote.confidence,
            "reasoning": vote.reasoning,
            "timestamp": datetime.now().isoformat()
        }
        
        active_consensus_decisions[decision_index]["votes"].append(vote_entry)
        
        return {"success": True, "message": "Vote submitted successfully"}
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        error_context = {
            "action": "submit_vote", 
            "decision_id": decision_id, 
            "agent_id": agent_id,
            "vote": vote.dict() if hasattr(vote, "dict") else str(vote)
        }
        log_api_error(e, context=error_context)
        raise HTTPException(status_code=500, detail=f"Failed to submit vote: {str(e)}")


async def process_consensus_decision(decision_id: str, agents: List[str], coordinator: AgentCoordinator):
    """
    Process a consensus decision asynchronously.
    """
    try:
        # Find the decision
        decision_index = None
        for i, decision in enumerate(active_consensus_decisions):
            if decision["id"] == decision_id:
                decision_index = i
                break
        
        if decision_index is None:
            error_msg = f"Consensus decision not found: {decision_id}"
            log_api_error(
                error_msg,
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.ERROR,
                context={"action": "process_consensus_decision", "decision_id": decision_id}
            )
            return
        
        # Wait for votes (with timeout)
        max_wait_time = 60  # seconds
        wait_interval = 1  # seconds
        total_waited = 0
        
        while total_waited < max_wait_time:
            # Check if we have votes from all agents
            votes = active_consensus_decisions[decision_index]["votes"]
            voting_agents = [vote["agent_id"] for vote in votes]
            
            if all(agent in voting_agents for agent in agents):
                break
            
            await asyncio.sleep(wait_interval)
            total_waited += wait_interval
        
        # Process votes
        votes = active_consensus_decisions[decision_index]["votes"]
        if not votes:
            active_consensus_decisions[decision_index]["status"] = "failed"
            active_consensus_decisions[decision_index]["error"] = "No votes received"
            error_msg = f"No votes received for decision: {decision_id}"
            log_api_error(
                error_msg,
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.WARNING,
                context={"action": "process_consensus_decision", "decision_id": decision_id}
            )
            return
        
        # Simple consensus mechanism: select option with highest confidence
        option_scores = {}
        for vote in votes:
            option = vote["option"]
            confidence = vote["confidence"]
            
            if option not in option_scores:
                option_scores[option] = 0
            
            option_scores[option] += confidence
        
        # Find option with highest score
        selected_option = max(option_scores.items(), key=lambda x: x[1])
        
        # Update decision
        active_consensus_decisions[decision_index]["selected_option"] = selected_option[0]
        active_consensus_decisions[decision_index]["confidence"] = selected_option[1] / len(votes)
        active_consensus_decisions[decision_index]["status"] = "completed"
        
        logger.info(f"Consensus decision {decision_id} completed with option: {selected_option[0]}")
    
    except Exception as e:
        error_context = {"action": "process_consensus_decision", "decision_id": decision_id}
        log_api_error(e, severity=ErrorSeverity.ERROR, context=error_context)
        
        # Update decision status
        for i, decision in enumerate(active_consensus_decisions):
            if decision["id"] == decision_id:
                active_consensus_decisions[i]["status"] = "failed"
                active_consensus_decisions[i]["error"] = str(e)
                break


@router.post("/conflict")
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
            error_msg = "Coordination system is not active"
            log_api_error(
                error_msg,
                category=ErrorCategory.API,
                severity=ErrorSeverity.WARNING,
                context={"action": "record_conflict_resolution"}
            )
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Validate required fields
        required_fields = ["attribute", "values", "selected_value", "selected_agent", "confidence"]
        for field in required_fields:
            if field not in conflict:
                error_msg = f"Missing required field: {field}"
                log_api_error(
                    error_msg,
                    category=ErrorCategory.VALIDATION,
                    severity=ErrorSeverity.ERROR,
                    context={"action": "record_conflict_resolution", "conflict": conflict}
                )
                raise HTTPException(status_code=400, detail=error_msg)
        
        # Add timestamp
        conflict["timestamp"] = datetime.now().isoformat()
        
        # Add to active conflicts
        active_conflicts.append(conflict)
        
        return {"success": True, "message": "Conflict resolution recorded"}
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        error_context = {"action": "record_conflict_resolution", "conflict": conflict}
        log_api_error(e, context=error_context)
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
        error_context = {"action": "get_agents"}
        log_api_error(e, context=error_context)
        raise HTTPException(status_code=500, detail=f"Failed to get agents: {str(e)}")


@router.get("/errors")
async def get_errors(
    limit: int = 50,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    coordinator: AgentCoordinator = Depends(get_coordinator)
):
    """
    Get errors from the coordination system.
    """
    try:
        errors = []
        
        # Get errors from coordinator
        if hasattr(coordinator, 'errors'):
            coordinator_errors = coordinator.errors
            for error in coordinator_errors:
                if (severity is None or error.get("severity") == severity) and \
                   (category is None or error.get("category") == category):
                    errors.append({
                        "source": "coordinator",
                        **error
                    })
        
        # Get errors from API
        for error in api_errors:
            if (severity is None or error.get("severity") == severity) and \
               (category is None or error.get("category") == category):
                errors.append({
                    "source": "api",
                    **error
                })
        
        # Sort by timestamp (most recent first) and limit
        errors.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        errors = errors[:limit]
        
        return {
            "total": len(errors),
            "errors": errors
        }
    
    except Exception as e:
        error_context = {"action": "get_errors", "limit": limit, "severity": severity, "category": category}
        log_api_error(e, context=error_context)
        raise HTTPException(status_code=500, detail=f"Failed to get errors: {str(e)}")


@router.delete("/errors")
async def clear_errors(
    coordinator: AgentCoordinator = Depends(get_coordinator)
):
    """
    Clear errors from the coordination system.
    """
    global api_errors
    
    try:
        # Clear API errors
        api_errors = []
        
        # Clear coordinator errors if possible
        if hasattr(coordinator, 'errors'):
            coordinator.errors = []
        
        return {"success": True, "message": "Errors cleared"}
    
    except Exception as e:
        error_context = {"action": "clear_errors"}
        log_api_error(e, context=error_context)
        raise HTTPException(status_code=500, detail=f"Failed to clear errors: {str(e)}")
