from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..core.analysis.context_analyzer import ContextAnalyzer
from ..core.analysis.pattern_matcher import PatternMatcher
from ..core.analysis.llm_reasoning import LLMReasoning
from ..core.analysis.domain_knowledge import DomainKnowledge
from ..core.analysis.error_knowledge_base import ErrorKnowledgeBase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Error Analysis Platform",
    description="A platform for analyzing and resolving software errors using AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
context_analyzer = ContextAnalyzer()
pattern_matcher = PatternMatcher()
llm_reasoning = LLMReasoning()
domain_knowledge = DomainKnowledge()
knowledge_base = ErrorKnowledgeBase()

# Pydantic models for request/response
class ErrorAnalysisRequest(BaseModel):
    error_message: str
    stack_trace: Optional[List[str]] = None
    code_context: Optional[Dict[str, Any]] = None
    environment_info: Optional[Dict[str, Any]] = None
    domain: Optional[str] = None

class ErrorAnalysisResponse(BaseModel):
    error_analysis: str
    root_cause: str
    solution_steps: List[str]
    confidence_score: float
    reasoning_chain: List[str]
    related_patterns: List[str]
    impact_analysis: Optional[Dict[str, Any]]
    prevention_strategies: Optional[List[str]]
    monitoring_suggestions: Optional[List[str]]
    timestamp: datetime

class PatternMatchRequest(BaseModel):
    pattern_type: str
    error_message: str
    context: Optional[Dict[str, Any]] = None

class PatternMatchResponse(BaseModel):
    matches: List[Dict[str, Any]]
    confidence_scores: List[float]
    context_similarity: List[float]

class SolutionRequest(BaseModel):
    pattern_id: str
    context: Optional[Dict[str, Any]] = None

class SolutionResponse(BaseModel):
    solution: Dict[str, Any]
    confidence_score: float
    reasoning_chain: List[str]
    risk_assessment: Dict[str, Any]
    monitoring_plan: Dict[str, Any]
    maintenance_requirements: List[str]

class StatisticsResponse(BaseModel):
    total_analyses: int
    average_confidence: float
    categories_analyzed: int
    patterns_matched: int
    domain_statistics: Dict[str, Any]

@app.post("/analyze", response_model=ErrorAnalysisResponse)
async def analyze_error(request: ErrorAnalysisRequest):
    """Analyze an error and provide comprehensive analysis."""
    try:
        # Analyze context
        context = context_analyzer.analyze(
            error_message=request.error_message,
            stack_trace=request.stack_trace,
            code_context=request.code_context,
            environment_info=request.environment_info
        )
        
        # Match patterns
        matches = pattern_matcher.match(
            error_message=request.error_message,
            context=context
        )
        
        # Get domain-specific context if domain is provided
        domain_prompt = ""
        if request.domain:
            domain_prompt = domain_knowledge.get_domain_prompt(request.domain)
        
        # Perform LLM reasoning
        result = llm_reasoning.analyze_error(context, matches)
        
        return ErrorAnalysisResponse(
            error_analysis=result.error_analysis,
            root_cause=result.root_cause,
            solution_steps=result.solution_steps,
            confidence_score=result.confidence_score,
            reasoning_chain=result.reasoning_chain,
            related_patterns=result.related_patterns,
            impact_analysis=result.impact_analysis,
            prevention_strategies=result.prevention_strategies,
            monitoring_suggestions=result.monitoring_suggestions,
            timestamp=result.timestamp
        )
        
    except Exception as e:
        logger.error(f"Error in analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/match-patterns", response_model=PatternMatchResponse)
async def match_patterns(request: PatternMatchRequest):
    """Match error patterns against an error message."""
    try:
        matches = pattern_matcher.match(
            error_message=request.error_message,
            context=request.context
        )
        
        return PatternMatchResponse(
            matches=[m.__dict__ for m in matches],
            confidence_scores=[m.match_score for m in matches],
            context_similarity=[m.context_similarity for m in matches]
        )
        
    except Exception as e:
        logger.error(f"Error in pattern matching: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-solution", response_model=SolutionResponse)
async def generate_solution(request: SolutionRequest):
    """Generate a solution for a specific error pattern."""
    try:
        pattern = knowledge_base.get_pattern(request.pattern_id)
        if not pattern:
            raise HTTPException(status_code=404, detail="Pattern not found")
        
        solution = llm_reasoning.generate_solution(pattern, request.context)
        
        return SolutionResponse(
            solution=solution["solution"].__dict__,
            confidence_score=solution["confidence_score"],
            reasoning_chain=solution["reasoning_chain"],
            risk_assessment=solution["risk_assessment"],
            monitoring_plan=solution["monitoring_plan"],
            maintenance_requirements=solution["maintenance_requirements"]
        )
        
    except Exception as e:
        logger.error(f"Error generating solution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """Get statistics about the error analysis system."""
    try:
        stats = llm_reasoning.get_statistics()
        
        # Add domain-specific statistics
        domain_stats = {}
        for domain in domain_knowledge.domains:
            context = domain_knowledge.get_domain_context(domain)
            if context:
                domain_stats[domain] = {
                    "frameworks": len(context.frameworks),
                    "patterns": len(context.common_patterns),
                    "components": len(context.critical_components),
                    "metrics": len(context.monitoring_metrics)
                }
        
        stats["domain_statistics"] = domain_stats
        
        return StatisticsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/domains")
async def get_domains():
    """Get list of supported domains."""
    return {"domains": list(domain_knowledge.domains.keys())}

@app.get("/domain/{domain}")
async def get_domain_info(domain: str):
    """Get detailed information about a specific domain."""
    context = domain_knowledge.get_domain_context(domain)
    if not context:
        raise HTTPException(status_code=404, detail="Domain not found")
    return context.__dict__ 