from typing import Dict, List, Any, Optional
import logging
import asyncio
from datetime import datetime
import uuid
from pymongo import MongoClient

from ..model_service.model_selector import ModelSelector
from ..agent_service.evaluation_manager import EvaluationManager
from ..agent_service.consensus_manager import ConsensusManager
from .workflow_manager import WorkflowManager
from .monitoring import MonitoringService
from .context_engine import ContextEngine
from .state_manager import StateManager
from .plan_manager import PlanManager
from .task_executor import TaskExecutor

logger = logging.getLogger(__name__)

class CoreOrchestrator:
    """Core orchestrator for managing the ADE platform's operations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize core services
        self.state_manager = StateManager(
            mongodb_uri=config['mongodb_uri'],
            database_name=config['database_name']
        )
        
        self.monitoring = MonitoringService()
        self.context_engine = ContextEngine()
        self.plan_manager = PlanManager()
        self.task_executor = TaskExecutor(max_workers=config.get('max_workers', 5))
        
        # Initialize specialized managers
        self.model_selector = ModelSelector(config['model_config_path'])
        self.evaluation_manager = EvaluationManager()
        self.consensus_manager = ConsensusManager(fault_tolerance=1)
        self.workflow_manager = WorkflowManager(
            git_config=config.get('git_config', {}),
            ci_config=config.get('ci_config', {})
        )
        
        # Task and plan tracking
        self.active_tasks: Dict[str, Dict] = {}
        self.active_plans: Dict[str, Dict] = {}
        
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an incoming request through the orchestration pipeline"""
        request_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Start monitoring
            self.monitoring.start_request_tracking(request_id)
            
            # Create execution plan
            plan = await self.plan_manager.create_plan(
                request=request,
                context=await self.context_engine.get_context(request)
            )
            
            # Register plan
            self.active_plans[plan.id] = {
                'plan': plan,
                'status': 'running',
                'start_time': start_time
            }
            
            # Execute plan steps
            result = await self.execute_plan(plan)
            
            # Record metrics
            self.monitoring.record_plan_execution(
                plan_id=plan.id,
                duration=(datetime.now() - start_time).total_seconds(),
                success=True
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing request {request_id}: {str(e)}")
            self.monitoring.record_error(request_id, str(e))
            raise
            
    async def execute_plan(self, plan: Any) -> Dict[str, Any]:
        """Execute a plan's steps in sequence"""
        results = []
        
        for step in plan.steps:
            # Create task
            task = await self.task_executor.create_task(
                step=step,
                context=plan.context
            )
            
            # Register task
            self.active_tasks[task.id] = {
                'task': task,
                'status': 'running',
                'start_time': datetime.now()
            }
            
            try:
                # Execute task with appropriate handler
                if step.type == 'model_inference':
                    result = await self._handle_model_inference(task)
                elif step.type == 'code_generation':
                    result = await self._handle_code_generation(task)
                elif step.type == 'evaluation':
                    result = await self._handle_evaluation(task)
                elif step.type == 'workflow':
                    result = await self._handle_workflow(task)
                else:
                    raise ValueError(f"Unknown step type: {step.type}")
                    
                results.append(result)
                self.active_tasks[task.id]['status'] = 'completed'
                
            except Exception as e:
                self.active_tasks[task.id]['status'] = 'failed'
                logger.error(f"Task {task.id} failed: {str(e)}")
                raise
                
        return self._combine_results(results)
        
    async def _handle_model_inference(self, task: Any) -> Dict[str, Any]:
        """Handle model inference tasks"""
        model = await self.model_selector.select_model(
            task=task.requirements.get('task_type', 'general'),
            context=task.context
        )
        
        return await model.generate(
            prompt=task.input.get('prompt'),
            parameters=task.parameters
        )
        
    async def _handle_code_generation(self, task: Any) -> Dict[str, Any]:
        """Handle code generation tasks"""
        # Get code generation result
        code_result = await self._handle_model_inference(task)
        
        # Apply context-aware fixes
        code_result = await self.workflow_manager.context_fix_system.apply_fix(
            code=code_result['code'],
            context=task.context
        )
        
        # Version control integration
        if task.parameters.get('commit_changes', False):
            await self.workflow_manager.version_control.commit_changes(
                files=[code_result['file_path']],
                message=f"Generated code for {task.id}"
            )
            
        return code_result
        
    async def _handle_evaluation(self, task: Any) -> Dict[str, Any]:
        """Handle evaluation tasks"""
        return await self.evaluation_manager.evaluate_solution(
            solution=task.input.get('solution'),
            context=task.context
        )
        
    async def _handle_workflow(self, task: Any) -> Dict[str, Any]:
        """Handle workflow tasks"""
        return await self.workflow_manager.execute_workflow(
            workflow_type=task.workflow_type,
            parameters=task.parameters
        )
        
    def _combine_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine multiple task results into a final response"""
        return {
            'success': all(r.get('success', False) for r in results),
            'results': results,
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'num_steps': len(results)
            }
        }
