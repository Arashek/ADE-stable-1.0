import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from prometheus_client import Counter, Gauge
from .agent_orchestrator import agent_orchestrator
from .data_manager import data_manager

# Metrics
ERRORS_DETECTED = Counter('errors_detected_total', 'Total number of errors detected')
ERRORS_FIXED = Counter('errors_fixed_total', 'Total number of errors fixed')
ERROR_RESOLUTION_TIME = Gauge('error_resolution_time_seconds', 'Time taken to fix errors')
ERROR_FIX_RATE = Gauge('error_fix_rate', 'Rate of successful error fixes')

class ErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_history: List[Dict[str, Any]] = []
        self.max_history = 1000
        self.fix_attempts: Dict[str, int] = {}  # Track fix attempts per error type
        self.max_fix_attempts = 3  # Maximum attempts to fix an error
        self.auto_fix_enabled = True  # Enable automatic error fixing

    async def handle_error(self, error: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle an error and attempt to fix it automatically."""
        try:
            # Record error
            ERRORS_DETECTED.inc()
            self.error_history.append({
                **error,
                'timestamp': datetime.now().isoformat(),
                'context': context
            })

            # Trim history if needed
            if len(self.error_history) > self.max_history:
                self.error_history = self.error_history[-self.max_history:]

            if not self.auto_fix_enabled:
                self.logger.warning("Auto-fix is disabled. Skipping error resolution.")
                return None

            # Analyze error
            error_type = self._categorize_error(error)
            fix_attempts = self.fix_attempts.get(error_type, 0)

            if fix_attempts >= self.max_fix_attempts:
                self.logger.warning(f"Max fix attempts reached for error type: {error_type}")
                return None

            # Generate fix
            fix_result = await self._generate_fix(error, context)
            if not fix_result:
                return None

            # Apply fix
            success = await self._apply_fix(fix_result)
            if success:
                ERRORS_FIXED.inc()
                self.fix_attempts[error_type] = fix_attempts + 1
                ERROR_FIX_RATE.set(ERRORS_FIXED._value.get() / ERRORS_DETECTED._value.get())
                
                # Record successful fix
                await data_manager.record_error({
                    'error': error,
                    'fix': fix_result,
                    'success': True,
                    'timestamp': datetime.now().isoformat()
                })

                return fix_result
            else:
                # Record failed fix attempt
                await data_manager.record_error({
                    'error': error,
                    'fix_attempt': fix_result,
                    'success': False,
                    'timestamp': datetime.now().isoformat()
                })
                return None

        except Exception as e:
            self.logger.error(f"Error in error handler: {str(e)}")
            return None

    def _categorize_error(self, error: Dict[str, Any]) -> str:
        """Categorize the error type for better handling."""
        error_message = error.get('error', '').lower()
        
        if 'syntax' in error_message or 'parsing' in error_message:
            return 'syntax_error'
        elif 'import' in error_message or 'module' in error_message:
            return 'import_error'
        elif 'type' in error_message or 'attribute' in error_message:
            return 'type_error'
        elif 'permission' in error_message or 'access' in error_message:
            return 'permission_error'
        elif 'connection' in error_message or 'network' in error_message:
            return 'connection_error'
        elif 'timeout' in error_message or 'deadline' in error_message:
            return 'timeout_error'
        else:
            return 'unknown_error'

    async def _generate_fix(self, error: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate a fix for the error using the agent system."""
        try:
            # Create a prompt for the agent to analyze and fix the error
            prompt = f"""Error Analysis and Fix Generation:

Error: {error.get('error', '')}
Context: {context.get('context', '')}
Location: {error.get('location', 'unknown')}

Please analyze this error and provide a fix. Include:
1. Root cause analysis
2. Proposed solution
3. Implementation steps
4. Verification method"""

            # Use the agent orchestrator to generate a fix
            fix_result = await agent_orchestrator.process_request(
                prompt=prompt,
                context={
                    'task_type': 'error_fix',
                    'error': error,
                    'context': context,
                    'previous_fixes': self.error_history[-5:] if self.error_history else []
                }
            )

            return fix_result

        except Exception as e:
            self.logger.error(f"Error generating fix: {str(e)}")
            return None

    async def _apply_fix(self, fix_result: Dict[str, Any]) -> bool:
        """Apply the generated fix."""
        try:
            # Extract fix details from the result
            fix_implementation = fix_result.get('coordinator_result', '')
            if not fix_implementation:
                return False

            # Apply the fix using the agent orchestrator
            apply_result = await agent_orchestrator.process_request(
                prompt=f"Apply the following fix:\n{fix_implementation}",
                context={
                    'task_type': 'apply_fix',
                    'fix': fix_result
                }
            )

            # Verify the fix was applied successfully
            verification_result = await agent_orchestrator.process_request(
                prompt="Verify that the fix was applied successfully and the error is resolved.",
                context={
                    'task_type': 'verify_fix',
                    'fix': fix_result,
                    'apply_result': apply_result
                }
            )

            return verification_result.get('success', False)

        except Exception as e:
            self.logger.error(f"Error applying fix: {str(e)}")
            return False

    def get_error_history(self) -> List[Dict[str, Any]]:
        """Get the history of errors and their fixes."""
        return self.error_history

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error handling statistics."""
        return {
            'total_errors': ERRORS_DETECTED._value.get(),
            'fixed_errors': ERRORS_FIXED._value.get(),
            'fix_rate': ERROR_FIX_RATE._value.get(),
            'error_types': self.fix_attempts
        }

# Create singleton instance
error_handler = ErrorHandler() 