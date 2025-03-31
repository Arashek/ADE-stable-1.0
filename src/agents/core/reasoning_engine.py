from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

from src.core.providers import ProviderRegistry, Capability
from .task_processor import AITaskProcessor, TaskResult
from .context_manager import ContextManager

logger = logging.getLogger(__name__)

@dataclass
class ReasoningStep:
    """A single step in the reasoning process"""
    step_id: str
    description: str
    status: str  # 'pending', 'in_progress', 'completed', 'failed'
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = datetime.now()
    completed_at: Optional[datetime] = None

@dataclass
class ReasoningResult:
    """Result of the reasoning process"""
    success: bool
    steps: List[ReasoningStep]
    final_decision: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()

class ReasoningEngine:
    """Engine for breaking down problems and making decisions"""
    
    def __init__(self, provider_registry: ProviderRegistry, context_manager: ContextManager):
        self.provider_registry = provider_registry
        self.context_manager = context_manager
        self.task_processor = AITaskProcessor(provider_registry)
        self.reasoning_history: List[ReasoningResult] = []
        
    async def solve_problem(
        self,
        problem: str,
        session_id: str,
        max_steps: int = 10,
        **kwargs
    ) -> ReasoningResult:
        """Solve a complex problem by breaking it down into steps
        
        Args:
            problem: Description of the problem to solve
            session_id: ID of the conversation session
            max_steps: Maximum number of reasoning steps
            **kwargs: Additional parameters for reasoning
            
        Returns:
            ReasoningResult containing the solution
        """
        try:
            # Create initial reasoning result
            result = ReasoningResult(
                success=False,
                steps=[],
                metadata={
                    "problem": problem,
                    "max_steps": max_steps,
                    "session_id": session_id
                }
            )
            
            # Get conversation context
            context = self.context_manager.get_conversation(session_id)
            if not context:
                context = []
            
            # Step 1: Problem Analysis
            analysis_step = await self._analyze_problem(problem, context)
            result.steps.append(analysis_step)
            
            if not analysis_step.status == "completed":
                raise ValueError(f"Problem analysis failed: {analysis_step.error}")
            
            # Step 2: Generate Solution Steps
            steps = await self._generate_solution_steps(analysis_step.result, context)
            result.steps.extend(steps)
            
            # Step 3: Execute Steps
            for step in result.steps[1:]:  # Skip analysis step
                if len(result.steps) >= max_steps:
                    break
                    
                step_result = await self._execute_step(step, context)
                if not step_result.status == "completed":
                    raise ValueError(f"Step execution failed: {step_result.error}")
                
                # Update context with step result
                self.context_manager.add_context(
                    session_id,
                    f"step_{step.step_id}",
                    step_result.result
                )
            
            # Step 4: Make Final Decision
            decision = await self._make_final_decision(result.steps, context)
            result.final_decision = decision
            
            # Mark as successful
            result.success = True
            
            # Add to history
            self.reasoning_history.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Problem solving failed: {str(e)}")
            return ReasoningResult(
                success=False,
                steps=result.steps if 'result' in locals() else [],
                error=str(e),
                metadata={
                    "problem": problem,
                    "session_id": session_id,
                    "error": str(e)
                }
            )
    
    async def _analyze_problem(
        self,
        problem: str,
        context: List[Dict[str, str]]
    ) -> ReasoningStep:
        """Analyze the problem to understand its components
        
        Args:
            problem: Problem description
            context: Conversation context
            
        Returns:
            ReasoningStep containing analysis results
        """
        step = ReasoningStep(
            step_id="analysis",
            description="Analyzing problem components and requirements",
            status="in_progress"
        )
        
        try:
            # Create analysis prompt
            prompt = f"""
            Analyze the following problem and break it down into key components:
            
            Problem: {problem}
            
            Consider:
            1. Main objectives
            2. Key requirements
            3. Potential challenges
            4. Required resources
            5. Success criteria
            
            Provide a structured analysis.
            """
            
            # Get analysis from AI
            result = await self.task_processor.process_task(
                task_description=prompt,
                required_capabilities=[Capability.TEXT_GENERATION],
                context={"previous_messages": context}
            )
            
            if not result.success:
                raise ValueError(f"Analysis failed: {result.error}")
            
            step.result = result.output
            step.status = "completed"
            step.completed_at = datetime.now()
            
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            step.completed_at = datetime.now()
            
        return step
    
    async def _generate_solution_steps(
        self,
        analysis: str,
        context: List[Dict[str, str]]
    ) -> List[ReasoningStep]:
        """Generate solution steps based on problem analysis
        
        Args:
            analysis: Problem analysis
            context: Conversation context
            
        Returns:
            List of reasoning steps
        """
        steps = []
        
        try:
            # Create step generation prompt
            prompt = f"""
            Based on the following problem analysis, generate a sequence of steps to solve the problem:
            
            Analysis: {analysis}
            
            For each step, provide:
            1. Clear description
            2. Required inputs
            3. Expected outputs
            4. Potential risks
            
            Format as a numbered list.
            """
            
            # Get steps from AI
            result = await self.task_processor.process_task(
                task_description=prompt,
                required_capabilities=[Capability.TEXT_GENERATION],
                context={"previous_messages": context}
            )
            
            if not result.success:
                raise ValueError(f"Step generation failed: {result.error}")
            
            # Parse steps from response
            step_texts = result.output.split("\n")
            for i, text in enumerate(step_texts, 1):
                if text.strip():
                    steps.append(ReasoningStep(
                        step_id=f"step_{i}",
                        description=text.strip(),
                        status="pending"
                    ))
                    
        except Exception as e:
            logger.error(f"Failed to generate solution steps: {str(e)}")
            
        return steps
    
    async def _execute_step(
        self,
        step: ReasoningStep,
        context: List[Dict[str, str]]
    ) -> ReasoningStep:
        """Execute a single reasoning step
        
        Args:
            step: Step to execute
            context: Conversation context
            
        Returns:
            Updated reasoning step
        """
        step.status = "in_progress"
        
        try:
            # Create execution prompt
            prompt = f"""
            Execute the following step:
            
            Step: {step.description}
            
            Provide:
            1. Detailed execution plan
            2. Required actions
            3. Expected outcomes
            4. Success criteria
            
            Format as a structured response.
            """
            
            # Get execution plan from AI
            result = await self.task_processor.process_task(
                task_description=prompt,
                required_capabilities=[Capability.TEXT_GENERATION],
                context={"previous_messages": context}
            )
            
            if not result.success:
                raise ValueError(f"Step execution failed: {result.error}")
            
            step.result = result.output
            step.status = "completed"
            step.completed_at = datetime.now()
            
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            step.completed_at = datetime.now()
            
        return step
    
    async def _make_final_decision(
        self,
        steps: List[ReasoningStep],
        context: List[Dict[str, str]]
    ) -> Any:
        """Make final decision based on completed steps
        
        Args:
            steps: Completed reasoning steps
            context: Conversation context
            
        Returns:
            Final decision
        """
        try:
            # Create decision prompt
            prompt = f"""
            Based on the following completed steps, make a final decision:
            
            Steps:
            {self._format_steps(steps)}
            
            Provide:
            1. Clear decision
            2. Justification
            3. Implementation plan
            4. Success metrics
            
            Format as a structured response.
            """
            
            # Get decision from AI
            result = await self.task_processor.process_task(
                task_description=prompt,
                required_capabilities=[Capability.TEXT_GENERATION],
                context={"previous_messages": context}
            )
            
            if not result.success:
                raise ValueError(f"Decision making failed: {result.error}")
            
            return result.output
            
        except Exception as e:
            logger.error(f"Failed to make final decision: {str(e)}")
            return None
    
    def _format_steps(self, steps: List[ReasoningStep]) -> str:
        """Format steps for prompt"""
        formatted = []
        for step in steps:
            status = "✓" if step.status == "completed" else "✗" if step.status == "failed" else "•"
            formatted.append(f"{status} {step.description}")
            if step.result:
                formatted.append(f"  Result: {step.result}")
            if step.error:
                formatted.append(f"  Error: {step.error}")
        return "\n".join(formatted)
    
    def get_reasoning_history(self) -> List[ReasoningResult]:
        """Get history of reasoning processes"""
        return self.reasoning_history
    
    def clear_history(self) -> None:
        """Clear the reasoning history"""
        self.reasoning_history = [] 