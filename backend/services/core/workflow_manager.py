from typing import Dict, List, Any, Optional
import logging
import asyncio
from datetime import datetime
import git
from pathlib import Path

from .context_fix_system import ContextAwareFixSystem
from .version_control import VersionControlManager
from .ci_system import CISystem
from .monitoring import MonitoringService

logger = logging.getLogger(__name__)

class WorkflowManager:
    """Manager for development workflow operations"""
    
    def __init__(self, git_config: Dict[str, Any], ci_config: Dict[str, Any]):
        self.git_config = git_config
        self.ci_config = ci_config
        
        # Initialize subsystems
        self.context_fix_system = ContextAwareFixSystem()
        self.version_control = VersionControlManager(
            project_dir=git_config.get('project_dir', '.')
        )
        self.ci_system = CISystem(ci_config)
        self.monitoring = MonitoringService()
        
        # Workflow tracking
        self.active_workflows: Dict[str, Dict] = {}
        
    async def execute_workflow(
        self,
        workflow_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a development workflow"""
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Start monitoring
            self.monitoring.start_workflow_tracking(workflow_id, workflow_type)
            
            # Execute appropriate workflow
            if workflow_type == 'code_review':
                result = await self._handle_code_review(parameters)
            elif workflow_type == 'git_operation':
                result = await self._handle_git_operation(parameters)
            elif workflow_type == 'ci_pipeline':
                result = await self._handle_ci_pipeline(parameters)
            else:
                raise ValueError(f"Unknown workflow type: {workflow_type}")
                
            # Record success
            self.monitoring.record_workflow_completion(
                workflow_id,
                success=True,
                metadata=result
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {str(e)}")
            self.monitoring.record_workflow_completion(
                workflow_id,
                success=False,
                error=str(e)
            )
            raise
            
    async def _handle_code_review(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code review workflow"""
        files = parameters.get('files', [])
        review_type = parameters.get('review_type', 'full')
        
        reviews = []
        for file_path in files:
            # Apply context-aware analysis
            context = await self.context_fix_system.analyze_context(file_path)
            
            # Generate review
            review = await self.context_fix_system.generate_review(
                file_path=file_path,
                context=context,
                review_type=review_type
            )
            
            # Apply automatic fixes if requested
            if parameters.get('auto_fix', False):
                fixed_code = await self.context_fix_system.apply_fix(
                    code=review['code'],
                    issues=review['issues'],
                    context=context
                )
                review['fixed_code'] = fixed_code
                
            reviews.append(review)
            
        return {
            'success': True,
            'reviews': reviews,
            'summary': self._generate_review_summary(reviews)
        }
        
    async def _handle_git_operation(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Git operations"""
        operation = parameters.get('operation')
        
        if operation == 'commit':
            result = await self.version_control.commit_changes(
                files=parameters.get('files', []),
                message=parameters.get('message', 'Update files')
            )
        elif operation == 'branch':
            result = await self.version_control.create_branch(
                name=parameters['branch_name'],
                from_branch=parameters.get('from_branch', 'main')
            )
        elif operation == 'merge':
            result = await self.version_control.merge_branches(
                source=parameters['source_branch'],
                target=parameters['target_branch']
            )
        else:
            raise ValueError(f"Unknown git operation: {operation}")
            
        return {
            'success': True,
            'operation': operation,
            'result': result
        }
        
    async def _handle_ci_pipeline(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CI pipeline operations"""
        pipeline_type = parameters.get('pipeline_type', 'default')
        
        # Start CI pipeline
        pipeline_id = await self.ci_system.start_pipeline(
            pipeline_type=pipeline_type,
            parameters=parameters
        )
        
        # Wait for completion if requested
        if parameters.get('wait_for_completion', False):
            result = await self.ci_system.wait_for_pipeline(pipeline_id)
        else:
            result = {'pipeline_id': pipeline_id, 'status': 'started'}
            
        return {
            'success': True,
            'pipeline_type': pipeline_type,
            'result': result
        }
        
    def _generate_review_summary(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of code reviews"""
        total_issues = sum(len(r['issues']) for r in reviews)
        critical_issues = sum(
            len([i for i in r['issues'] if i['severity'] == 'critical'])
            for r in reviews
        )
        
        return {
            'total_files': len(reviews),
            'total_issues': total_issues,
            'critical_issues': critical_issues,
            'files_with_issues': len([r for r in reviews if r['issues']])
        }
