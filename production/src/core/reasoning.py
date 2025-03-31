from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from enum import Enum
import logging
from datetime import datetime
import json
import asyncio
from .chain_of_thought import ChainOfThought

logger = logging.getLogger(__name__)

class ReasoningType(Enum):
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    CRITICAL = "critical"
    METACOGNITIVE = "metacognitive"

class PlanStatus(Enum):
    DRAFT = "draft"
    VALIDATED = "validated"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ADAPTED = "adapted"

@dataclass
class ReasoningStep:
    step_id: str
    reasoning_type: ReasoningType
    thought: str
    confidence: float
    alternatives: List[str] = field(default_factory=list)
    verification_steps: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ReasoningOutput:
    conclusion: str
    confidence: float
    steps: List[ReasoningStep]
    alternatives: List[str]
    verification_results: Dict[str, bool]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Subgoal:
    goal_id: str
    description: str
    dependencies: Set[str] = field(default_factory=set)
    required_capabilities: Set[str] = field(default_factory=set)
    estimated_duration: float
    priority: int
    status: str = "pending"
    assigned_agent: Optional[str] = None
    progress: float = 0.0
    start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None

@dataclass
class Plan:
    plan_id: str
    goal: str
    subgoals: List[Subgoal]
    dependencies: Dict[str, Set[str]]
    status: PlanStatus = PlanStatus.DRAFT
    created_by: str
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    recovery_plans: Dict[str, List[Subgoal]] = field(default_factory=dict)

class AdvancedReasoning:
    def __init__(self):
        self.reasoning_history: Dict[str, List[ReasoningOutput]] = {}
        self.active_plans: Dict[str, Plan] = {}
        self.plan_history: Dict[str, List[Plan]] = {}
        self._lock = asyncio.Lock()

    async def perform_reasoning(self, 
                              query: str,
                              reasoning_type: ReasoningType,
                              context: Optional[Dict[str, Any]] = None) -> ReasoningOutput:
        """Perform structured reasoning with verification."""
        async with self._lock:
            # Initialize chain of thought
            chain = ChainOfThought(
                steps=[
                    "Analyzing the query",
                    "Generating initial thoughts",
                    "Exploring alternatives",
                    "Verifying conclusions",
                    "Finalizing reasoning"
                ],
                final_decision="",
                confidence=0.0,
                alternatives=[]
            )

            # Generate reasoning steps
            steps = []
            current_thought = ""
            confidence = 0.0
            alternatives = []
            verification_steps = []

            # Step 1: Initial Analysis
            analysis_step = ReasoningStep(
                step_id="analysis",
                reasoning_type=reasoning_type,
                thought="Analyzing query and context",
                confidence=0.7,
                alternatives=["Different analysis approach", "Alternative context interpretation"],
                verification_steps=["Check query understanding", "Validate context relevance"]
            )
            steps.append(analysis_step)

            # Step 2: Thought Generation
            thought_step = ReasoningStep(
                step_id="thought_generation",
                reasoning_type=reasoning_type,
                thought="Generating main reasoning path",
                confidence=0.8,
                alternatives=["Alternative reasoning path", "Different perspective"],
                verification_steps=["Logical consistency", "Completeness check"]
            )
            steps.append(thought_step)

            # Step 3: Alternative Exploration
            alt_step = ReasoningStep(
                step_id="alternatives",
                reasoning_type=reasoning_type,
                thought="Exploring alternative approaches",
                confidence=0.6,
                alternatives=["Different solution approach", "Alternative methodology"],
                verification_steps=["Feasibility check", "Comparison with main approach"]
            )
            steps.append(alt_step)

            # Step 4: Verification
            verification_results = {}
            for step in steps:
                for v_step in step.verification_steps:
                    verification_results[v_step] = True  # In practice, implement actual verification

            # Create reasoning output
            output = ReasoningOutput(
                conclusion="Final reasoned conclusion",
                confidence=0.8,
                steps=steps,
                alternatives=alternatives,
                verification_results=verification_results,
                metadata={
                    "query": query,
                    "reasoning_type": reasoning_type.value,
                    "context": context,
                    "timestamp": datetime.now().isoformat()
                }
            )

            # Store reasoning history
            if query not in self.reasoning_history:
                self.reasoning_history[query] = []
            self.reasoning_history[query].append(output)

            return output

    async def create_plan(self, 
                         goal: str,
                         agent_id: str,
                         capabilities: Set[str],
                         context: Optional[Dict[str, Any]] = None) -> Plan:
        """Create a detailed plan with subgoals and dependencies."""
        async with self._lock:
            # Generate plan ID
            plan_id = f"plan_{datetime.now().timestamp()}"

            # Create initial subgoals through reasoning
            reasoning_output = await self.perform_reasoning(
                query=f"Break down goal into subgoals: {goal}",
                reasoning_type=ReasoningType.ANALYTICAL,
                context=context
            )

            # Convert reasoning into subgoals
            subgoals = []
            dependencies = {}
            
            # Example subgoal creation (in practice, use reasoning output)
            subgoal = Subgoal(
                goal_id="subgoal_1",
                description="Initial analysis and setup",
                required_capabilities={"analysis", "planning"},
                estimated_duration=30.0,
                priority=1
            )
            subgoals.append(subgoal)
            dependencies[subgoal.goal_id] = set()

            # Create plan
            plan = Plan(
                plan_id=plan_id,
                goal=goal,
                subgoals=subgoals,
                dependencies=dependencies,
                created_by=agent_id,
                metadata={
                    "capabilities": list(capabilities),
                    "context": context,
                    "created_at": datetime.now().isoformat()
                }
            )

            # Store plan
            self.active_plans[plan_id] = plan
            if agent_id not in self.plan_history:
                self.plan_history[agent_id] = []
            self.plan_history[agent_id].append(plan)

            return plan

    async def validate_plan(self, plan_id: str) -> bool:
        """Validate plan feasibility and completeness."""
        if plan_id not in self.active_plans:
            return False

        plan = self.active_plans[plan_id]
        
        # Check for circular dependencies
        if self._has_circular_dependencies(plan.dependencies):
            return False

        # Verify all required capabilities are available
        required_capabilities = set()
        for subgoal in plan.subgoals:
            required_capabilities.update(subgoal.required_capabilities)

        # In practice, check against actual agent capabilities
        # For now, assume all capabilities are available
        plan.status = PlanStatus.VALIDATED
        return True

    async def adapt_plan(self, 
                        plan_id: str,
                        changes: Dict[str, Any]) -> Optional[Plan]:
        """Adapt plan based on changing requirements or failures."""
        if plan_id not in self.active_plans:
            return None

        async with self._lock:
            plan = self.active_plans[plan_id]
            
            # Create reasoning about adaptation
            reasoning_output = await self.perform_reasoning(
                query=f"Adapt plan {plan_id} based on changes: {changes}",
                reasoning_type=ReasoningType.CREATIVE,
                context={"plan": plan, "changes": changes}
            )

            # Update plan based on reasoning
            # In practice, implement actual adaptation logic
            plan.status = PlanStatus.ADAPTED
            plan.last_updated = datetime.now()
            plan.metadata["adaptations"] = changes

            return plan

    async def create_recovery_plan(self, 
                                 plan_id: str,
                                 failed_subgoal_id: str) -> Optional[List[Subgoal]]:
        """Create recovery plan for failed subgoal."""
        if plan_id not in self.active_plans:
            return None

        plan = self.active_plans[plan_id]
        failed_subgoal = next(
            (sg for sg in plan.subgoals if sg.goal_id == failed_subgoal_id),
            None
        )
        
        if not failed_subgoal:
            return None

        # Generate recovery steps through reasoning
        reasoning_output = await self.perform_reasoning(
            query=f"Generate recovery steps for failed subgoal: {failed_subgoal_id}",
            reasoning_type=ReasoningType.CRITICAL,
            context={"failed_subgoal": failed_subgoal}
        )

        # Create recovery subgoals
        recovery_subgoals = [
            Subgoal(
                goal_id=f"recovery_{failed_subgoal_id}_1",
                description="Analyze failure cause",
                required_capabilities={"analysis", "debugging"},
                estimated_duration=15.0,
                priority=1
            ),
            Subgoal(
                goal_id=f"recovery_{failed_subgoal_id}_2",
                description="Implement alternative approach",
                required_capabilities={"implementation", "problem_solving"},
                estimated_duration=30.0,
                priority=2
            )
        ]

        # Store recovery plan
        plan.recovery_plans[failed_subgoal_id] = recovery_subgoals

        return recovery_subgoals

    async def evaluate_performance(self, 
                                 agent_id: str,
                                 time_period: Optional[datetime] = None) -> Dict[str, Any]:
        """Evaluate agent performance and identify areas for improvement."""
        if agent_id not in self.plan_history:
            return {}

        # Get relevant plans
        plans = self.plan_history[agent_id]
        if time_period:
            plans = [p for p in plans if p.created_at >= time_period]

        # Calculate metrics
        total_plans = len(plans)
        completed_plans = len([p for p in plans if p.status == PlanStatus.COMPLETED])
        failed_plans = len([p for p in plans if p.status == PlanStatus.FAILED])
        adapted_plans = len([p for p in plans if p.status == PlanStatus.ADAPTED])

        # Calculate average completion time
        completion_times = []
        for plan in plans:
            if plan.status == PlanStatus.COMPLETED:
                for subgoal in plan.subgoals:
                    if subgoal.completion_time and subgoal.start_time:
                        completion_times.append(
                            (subgoal.completion_time - subgoal.start_time).total_seconds()
                        )

        avg_completion_time = (
            sum(completion_times) / len(completion_times)
            if completion_times
            else 0
        )

        # Identify common failure patterns
        failure_patterns = self._analyze_failure_patterns(plans)

        return {
            "total_plans": total_plans,
            "completed_plans": completed_plans,
            "failed_plans": failed_plans,
            "adapted_plans": adapted_plans,
            "success_rate": completed_plans / total_plans if total_plans > 0 else 0,
            "average_completion_time": avg_completion_time,
            "failure_patterns": failure_patterns,
            "evaluation_period": time_period.isoformat() if time_period else "all_time"
        }

    def _has_circular_dependencies(self, dependencies: Dict[str, Set[str]]) -> bool:
        """Check for circular dependencies in a plan."""
        visited = set()
        path = set()

        def dfs(current: str) -> bool:
            if current in path:
                return True
            if current in visited:
                return False

            visited.add(current)
            path.add(current)

            for dep in dependencies.get(current, set()):
                if dfs(dep):
                    return True

            path.remove(current)
            return False

        for node in dependencies:
            if dfs(node):
                return True

        return False

    def _analyze_failure_patterns(self, plans: List[Plan]) -> List[Dict[str, Any]]:
        """Analyze patterns in failed plans."""
        failure_patterns = []
        
        for plan in plans:
            if plan.status == PlanStatus.FAILED:
                # Analyze failed subgoals
                failed_subgoals = [
                    sg for sg in plan.subgoals
                    if sg.status == "failed"
                ]
                
                for subgoal in failed_subgoals:
                    pattern = {
                        "subgoal_type": subgoal.description,
                        "required_capabilities": list(subgoal.required_capabilities),
                        "dependencies": list(plan.dependencies.get(subgoal.goal_id, set())),
                        "occurrence_count": 1
                    }
                    
                    # Update existing patterns
                    for existing in failure_patterns:
                        if (existing["subgoal_type"] == pattern["subgoal_type"] and
                            existing["required_capabilities"] == pattern["required_capabilities"]):
                            existing["occurrence_count"] += 1
                            break
                    else:
                        failure_patterns.append(pattern)

        return failure_patterns 