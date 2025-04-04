from typing import Dict, List, Optional, Any
import logging
import traceback
import asyncio
from uuid import uuid4

from models.codebase import Codebase, File
from models.debugging import DebugSession, DebugResult, Error
from services.utils.llm import LLMClient
from services.utils.code_analysis import CodeAnalyzer
from services.utils.telemetry import track_event

logger = logging.getLogger(__name__)

class DebuggerAgent:
    """
    Agent responsible for debugging code by analyzing errors,
    suggesting fixes, and testing solutions.
    """
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.code_analyzer = CodeAnalyzer()
        self.logger = logging.getLogger(__name__)
        self.active_sessions: Dict[str, DebugSession] = {}
        
    async def debug_error(self, error: Error, codebase: Codebase) -> DebugResult:
        """
        Debug an error by analyzing it and suggesting potential fixes
        
        Args:
            error: The error to debug
            codebase: The codebase containing the error
            
        Returns:
            DebugResult object with suggested fixes and analysis
        """
        session_id = str(uuid4())
        track_event("debug_session_started", {"error_type": error.error_type})
        
        self.logger.info(f"Starting debug session {session_id} for error: {error.message}")
        
        # Create debug session
        session = DebugSession(
            id=session_id,
            error=error,
            status="in_progress",
            codebase=codebase,
            fixes=[],
            analysis=""
        )
        self.active_sessions[session_id] = session
        
        try:
            # Analyze the error
            analysis = await self._analyze_error(error, codebase)
            session.analysis = analysis
            
            # Generate potential fixes
            fixes = await self._generate_fixes(error, codebase, analysis)
            session.fixes = fixes
            
            # Evaluate and rank fixes
            ranked_fixes = await self._evaluate_fixes(fixes, error, codebase)
            session.fixes = ranked_fixes
            session.status = "completed"
            
            result = DebugResult(
                session_id=session_id,
                error=error,
                fixes=ranked_fixes,
                analysis=analysis,
                success=True
            )
            
            self.logger.info(f"Debug session {session_id} completed successfully")
            track_event("debug_session_completed", {"success": True, "fixes_count": len(ranked_fixes)})
            return result
            
        except Exception as e:
            self.logger.error(f"Error in debug session {session_id}: {str(e)}")
            session.status = "failed"
            
            result = DebugResult(
                session_id=session_id,
                error=error,
                fixes=[],
                analysis=f"Debugging failed: {str(e)}",
                success=False
            )
            
            track_event("debug_session_failed", {"error": str(e)})
            return result
    
    async def _analyze_error(self, error: Error, codebase: Codebase) -> str:
        """Analyze an error and determine its root cause"""
        self.logger.debug(f"Analyzing error: {error.message}")
        
        # Extract relevant files
        relevant_files = self._get_relevant_files(error, codebase)
        
        # Build context for LLM
        context = {
            "error_type": error.error_type,
            "error_message": error.message,
            "traceback": error.traceback,
            "relevant_files": [f.to_dict() for f in relevant_files],
            "line_number": error.line_number,
            "file_path": error.file_path
        }
        
        # Generate error analysis
        prompt = self._build_analysis_prompt(context)
        analysis = await self.llm_client.generate_text(prompt)
        
        return analysis
    
    async def _generate_fixes(self, error: Error, codebase: Codebase, analysis: str) -> List[Dict[str, Any]]:
        """Generate potential fixes for the error"""
        self.logger.debug(f"Generating fixes for error: {error.message}")
        
        # Extract relevant files
        relevant_files = self._get_relevant_files(error, codebase)
        
        # Build context for LLM
        context = {
            "error_type": error.error_type,
            "error_message": error.message,
            "traceback": error.traceback,
            "analysis": analysis,
            "relevant_files": [f.to_dict() for f in relevant_files],
            "line_number": error.line_number,
            "file_path": error.file_path
        }
        
        # Generate fixes
        prompt = self._build_fix_prompt(context)
        fix_response = await self.llm_client.generate_structured_output(prompt, "fixes")
        
        # Parse and format fixes
        fixes = []
        for i, fix in enumerate(fix_response.get("fixes", [])):
            fix_id = f"fix_{i+1}"
            formatted_fix = {
                "id": fix_id,
                "description": fix.get("description", ""),
                "changes": fix.get("changes", []),
                "confidence": fix.get("confidence", 0.5),
                "explanation": fix.get("explanation", "")
            }
            fixes.append(formatted_fix)
        
        return fixes
    
    async def _evaluate_fixes(self, fixes: List[Dict[str, Any]], error: Error, codebase: Codebase) -> List[Dict[str, Any]]:
        """Evaluate and rank potential fixes"""
        self.logger.debug(f"Evaluating {len(fixes)} potential fixes")
        
        # In a real implementation, this would apply fixes to a sandbox copy
        # of the codebase and evaluate if they resolve the error
        
        # For now, just rank by confidence
        ranked_fixes = sorted(fixes, key=lambda x: x.get("confidence", 0), reverse=True)
        return ranked_fixes
    
    def _get_relevant_files(self, error: Error, codebase: Codebase) -> List[File]:
        """Get files relevant to the error"""
        relevant_files = []
        
        # Always include the file containing the error
        if error.file_path:
            error_file = None
            for file in codebase.files:
                if file.path == error.file_path:
                    error_file = file
                    break
                    
            if error_file:
                relevant_files.append(error_file)
        
        # Extract files from traceback
        if error.traceback:
            for line in error.traceback.split("\n"):
                if "File " in line:
                    try:
                        file_path = line.split("File ", 1)[1].split(", line")[0].strip('"')
                        for file in codebase.files:
                            if file.path == file_path and file not in relevant_files:
                                relevant_files.append(file)
                                break
                    except:
                        continue
        
        # If we don't have any files yet, include related files based on imports
        if not relevant_files and error.file_path:
            # Find files that import the error file or are imported by it
            error_file_name = error.file_path.split("/")[-1]
            for file in codebase.files:
                content = file.content or ""
                if error_file_name in content and "import" in content and file not in relevant_files:
                    relevant_files.append(file)
        
        return relevant_files
    
    def _build_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for error analysis"""
        return f"""
        Analyze the following error and determine its root cause:
        
        Error Type: {context.get('error_type', 'Unknown')}
        Error Message: {context.get('error_message', '')}
        
        Traceback:
        {context.get('traceback', 'No traceback available')}
        
        File with Error: {context.get('file_path', 'Unknown')}
        Line Number: {context.get('line_number', 'Unknown')}
        
        Provide a detailed analysis of this error, explaining its likely causes 
        and any underlying issues that might be contributing to it.
        """
    
    def _build_fix_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for generating fixes"""
        return f"""
        Based on the following error analysis, generate potential fixes:
        
        Error Type: {context.get('error_type', 'Unknown')}
        Error Message: {context.get('error_message', '')}
        
        Analysis:
        {context.get('analysis', 'No analysis available')}
        
        File with Error: {context.get('file_path', 'Unknown')}
        Line Number: {context.get('line_number', 'Unknown')}
        
        Generate 2-3 potential fixes for this error. For each fix, provide:
        1. A brief description
        2. The specific code changes required
        3. An explanation of why this fix should work
        4. A confidence score (0-1) indicating how likely this is to resolve the issue
        
        Format your response as a structured JSON object with a 'fixes' key containing
        an array of fix objects.
        """
    
    def get_session(self, session_id: str) -> Optional[DebugSession]:
        """Get a debug session by ID"""
        return self.active_sessions.get(session_id)
    
    def list_sessions(self) -> List[DebugSession]:
        """List all active debug sessions"""
        return list(self.active_sessions.values())
