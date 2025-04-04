from typing import Dict, List, Optional, Any
import logging
import asyncio
from uuid import uuid4

from models.codebase import Codebase, File
from models.optimization import OptimizationSession, OptimizationResult, OptimizationProfile
from services.utils.llm import LLMClient
from services.utils.code_analysis import CodeAnalyzer
from services.utils.performance_analyzer import PerformanceAnalyzer
from services.utils.telemetry import track_event

logger = logging.getLogger(__name__)

class OptimizerAgent:
    """
    Agent responsible for optimizing code performance, memory usage,
    and identifying bottlenecks.
    """
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.code_analyzer = CodeAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()
        self.logger = logging.getLogger(__name__)
        self.active_sessions: Dict[str, OptimizationSession] = {}
        
    async def optimize_codebase(self, codebase: Codebase, profile: OptimizationProfile) -> OptimizationResult:
        """
        Optimize a codebase based on the provided optimization profile
        
        Args:
            codebase: The codebase to optimize
            profile: Optimization profile specifying targets and constraints
            
        Returns:
            OptimizationResult with suggested optimizations
        """
        session_id = str(uuid4())
        track_event("optimization_session_started", {"profile_type": profile.profile_type})
        
        self.logger.info(f"Starting optimization session {session_id} with profile: {profile.profile_type}")
        
        # Create optimization session
        session = OptimizationSession(
            id=session_id,
            codebase=codebase,
            profile=profile,
            status="in_progress",
            optimizations=[],
            analysis=""
        )
        self.active_sessions[session_id] = session
        
        try:
            # Analyze codebase for optimization opportunities
            analysis = await self._analyze_codebase(codebase, profile)
            session.analysis = analysis
            
            # Generate optimizations
            optimizations = await self._generate_optimizations(codebase, profile, analysis)
            session.optimizations = optimizations
            
            # Evaluate and rank optimizations
            ranked_optimizations = await self._evaluate_optimizations(optimizations, codebase, profile)
            session.optimizations = ranked_optimizations
            session.status = "completed"
            
            result = OptimizationResult(
                session_id=session_id,
                optimizations=ranked_optimizations,
                analysis=analysis,
                success=True
            )
            
            self.logger.info(f"Optimization session {session_id} completed successfully")
            track_event("optimization_session_completed", {
                "success": True, 
                "optimizations_count": len(ranked_optimizations)
            })
            return result
            
        except Exception as e:
            self.logger.error(f"Error in optimization session {session_id}: {str(e)}")
            session.status = "failed"
            
            result = OptimizationResult(
                session_id=session_id,
                optimizations=[],
                analysis=f"Optimization failed: {str(e)}",
                success=False
            )
            
            track_event("optimization_session_failed", {"error": str(e)})
            return result
    
    async def _analyze_codebase(self, codebase: Codebase, profile: OptimizationProfile) -> str:
        """Analyze a codebase for optimization opportunities"""
        self.logger.debug(f"Analyzing codebase for optimization opportunities")
        
        analysis_results = []
        
        # Analyze each file based on optimization profile
        for file in codebase.files:
            # Skip files that don't match target file types
            if not self._should_analyze_file(file, profile):
                continue
                
            file_analysis = self.performance_analyzer.analyze_file(file.path)
            if file_analysis.get("estimated_performance") in ["poor", "moderate"]:
                analysis_results.append({
                    "file": file.path,
                    "issues": file_analysis.get("issues", []),
                    "complexity_score": file_analysis.get("complexity_score", 0),
                    "estimated_performance": file_analysis.get("estimated_performance", "unknown")
                })
        
        # Build context for LLM
        context = {
            "profile_type": profile.profile_type,
            "target_metrics": profile.target_metrics,
            "constraints": profile.constraints,
            "file_analysis": analysis_results
        }
        
        # Generate codebase analysis
        prompt = self._build_analysis_prompt(context)
        analysis = await self.llm_client.generate_text(prompt)
        
        return analysis
    
    async def _generate_optimizations(
        self, 
        codebase: Codebase, 
        profile: OptimizationProfile, 
        analysis: str
    ) -> List[Dict[str, Any]]:
        """Generate potential optimizations based on analysis"""
        self.logger.debug(f"Generating optimizations for codebase")
        
        # Build context for LLM
        context = {
            "profile_type": profile.profile_type,
            "target_metrics": profile.target_metrics,
            "constraints": profile.constraints,
            "analysis": analysis,
            "file_count": len(codebase.files)
        }
        
        # Generate optimizations
        prompt = self._build_optimization_prompt(context)
        optimization_response = await self.llm_client.generate_structured_output(
            prompt, 
            "optimizations"
        )
        
        # Parse and format optimizations
        optimizations = []
        for i, opt in enumerate(optimization_response.get("optimizations", [])):
            opt_id = f"opt_{i+1}"
            formatted_opt = {
                "id": opt_id,
                "title": opt.get("title", ""),
                "description": opt.get("description", ""),
                "target_files": opt.get("target_files", []),
                "changes": opt.get("changes", []),
                "expected_impact": opt.get("expected_impact", {}),
                "complexity": opt.get("complexity", "medium"),
                "priority": opt.get("priority", "medium")
            }
            optimizations.append(formatted_opt)
        
        return optimizations
    
    async def _evaluate_optimizations(
        self, 
        optimizations: List[Dict[str, Any]], 
        codebase: Codebase, 
        profile: OptimizationProfile
    ) -> List[Dict[str, Any]]:
        """Evaluate and rank potential optimizations"""
        self.logger.debug(f"Evaluating {len(optimizations)} potential optimizations")
        
        # In a real implementation, this would apply optimizations to a sandbox copy
        # of the codebase and benchmark the results
        
        # For now, rank by priority and expected impact
        def rank_score(opt):
            priority_scores = {"high": 3, "medium": 2, "low": 1}
            impact_scores = {
                "high": 3, 
                "medium": 2, 
                "low": 1, 
                "unknown": 0
            }
            
            priority = opt.get("priority", "medium")
            impact = opt.get("expected_impact", {}).get("overall", "medium")
            
            return (priority_scores.get(priority, 2) * 2) + impact_scores.get(impact, 2)
            
        ranked_optimizations = sorted(optimizations, key=rank_score, reverse=True)
        return ranked_optimizations
    
    def _should_analyze_file(self, file: File, profile: OptimizationProfile) -> bool:
        """Determine if a file should be analyzed based on profile"""
        # Skip if file path contains excluded patterns
        for exclude in profile.excludes:
            if exclude in file.path:
                return False
                
        # Check if file matches target file types
        if profile.target_file_types:
            file_ext = file.path.split(".")[-1] if "." in file.path else ""
            if file_ext and file_ext not in profile.target_file_types:
                return False
                
        return True
    
    def _build_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for codebase analysis"""
        return f"""
        Analyze the following codebase for optimization opportunities:
        
        Optimization Profile: {context.get('profile_type', 'general')}
        Target Metrics: {', '.join(context.get('target_metrics', ['performance']))}
        Constraints: {', '.join(context.get('constraints', []))}
        
        File Analysis:
        {self._format_file_analysis(context.get('file_analysis', []))}
        
        Based on this information, provide a comprehensive analysis of optimization
        opportunities in this codebase. Consider performance bottlenecks, memory usage,
        and any other areas that could be improved based on the target metrics.
        """
    
    def _format_file_analysis(self, file_analysis: List[Dict[str, Any]]) -> str:
        """Format file analysis results for prompt"""
        if not file_analysis:
            return "No file analysis available"
            
        result = ""
        for analysis in file_analysis[:5]:  # Limit to top 5 files
            result += f"\nFile: {analysis.get('file', 'Unknown')}\n"
            result += f"Performance: {analysis.get('estimated_performance', 'unknown')}\n"
            result += f"Complexity Score: {analysis.get('complexity_score', 0)}\n"
            
            issues = analysis.get('issues', [])
            if issues:
                result += "Issues:\n"
                for issue in issues[:3]:  # Limit to top 3 issues per file
                    result += f"- {issue.get('type', 'Unknown')}: {issue.get('description', '')}\n"
            
            result += "\n"
            
        if len(file_analysis) > 5:
            result += f"\n...and {len(file_analysis) - 5} more files with optimization potential.\n"
            
        return result
    
    def _build_optimization_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for generating optimizations"""
        return f"""
        Based on the following codebase analysis, generate optimization suggestions:
        
        Optimization Profile: {context.get('profile_type', 'general')}
        Target Metrics: {', '.join(context.get('target_metrics', ['performance']))}
        Constraints: {', '.join(context.get('constraints', []))}
        
        Analysis:
        {context.get('analysis', 'No analysis available')}
        
        Generate 3-5 optimization suggestions for this codebase. For each suggestion, provide:
        1. A clear title and description of the optimization
        2. The specific files that should be modified
        3. The code changes required (as specific as possible)
        4. The expected impact on performance, memory usage, or other relevant metrics
        5. The complexity of implementing the optimization (low, medium, high)
        6. The priority level (low, medium, high)
        
        Format your response as a structured JSON object with an 'optimizations' key containing
        an array of optimization objects.
        """
    
    def get_session(self, session_id: str) -> Optional[OptimizationSession]:
        """Get an optimization session by ID"""
        return self.active_sessions.get(session_id)
    
    def list_sessions(self) -> List[OptimizationSession]:
        """List all active optimization sessions"""
        return list(self.active_sessions.values())
