from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..core.security import get_current_user
from ..models.agent_capabilities import (
    GenerationType,
    GenerationContext,
    GeneratedCode,
    ReviewType,
    CodeReviewRequest,
    CodeReview,
    TestType,
    TestRequest,
    TestSuite,
    DocumentationType,
    DocumentationRequest,
    Documentation
)
from ..services.agent_service import AgentService

router = APIRouter(prefix="/api/agent", tags=["agent"])
agent_service = AgentService()

# Code Generation Endpoints
@router.post("/generate", response_model=GeneratedCode)
async def generate_code(
    context: GenerationContext,
    current_user = Depends(get_current_user)
):
    """Generate code based on context and requirements"""
    try:
        return await agent_service.generate_code(context, current_user)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/generation-history", response_model=List[GeneratedCode])
async def get_generation_history(
    project_id: str,
    type: Optional[GenerationType] = None,
    limit: Optional[int] = Query(10, ge=1, le=100),
    offset: Optional[int] = Query(0, ge=0),
    current_user = Depends(get_current_user)
):
    """Get code generation history"""
    try:
        # TODO: Implement history retrieval logic
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Code Review Endpoints
@router.post("/review", response_model=CodeReview)
async def review_code(
    request: CodeReviewRequest,
    current_user = Depends(get_current_user)
):
    """Perform code review"""
    try:
        return await agent_service.review_code(request, current_user)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reviews", response_model=List[CodeReview])
async def get_reviews(
    project_id: str,
    file_path: Optional[str] = None,
    review_type: Optional[ReviewType] = None,
    limit: Optional[int] = Query(10, ge=1, le=100),
    offset: Optional[int] = Query(0, ge=0),
    current_user = Depends(get_current_user)
):
    """Get code review history"""
    try:
        # TODO: Implement review history retrieval logic
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Testing Endpoints
@router.post("/generate-tests", response_model=TestSuite)
async def generate_tests(
    request: TestRequest,
    current_user = Depends(get_current_user)
):
    """Generate test suite"""
    try:
        return await agent_service.generate_tests(request, current_user)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-suites", response_model=List[TestSuite])
async def get_test_suites(
    project_id: str,
    file_path: Optional[str] = None,
    test_type: Optional[TestType] = None,
    limit: Optional[int] = Query(10, ge=1, le=100),
    offset: Optional[int] = Query(0, ge=0),
    current_user = Depends(get_current_user)
):
    """Get test suite history"""
    try:
        # TODO: Implement test suite history retrieval logic
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Documentation Endpoints
@router.post("/generate-docs", response_model=Documentation)
async def generate_documentation(
    request: DocumentationRequest,
    current_user = Depends(get_current_user)
):
    """Generate documentation"""
    try:
        return await agent_service.generate_documentation(request, current_user)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documentation", response_model=List[Documentation])
async def get_documentation(
    project_id: str,
    doc_type: Optional[DocumentationType] = None,
    format: Optional[str] = None,
    limit: Optional[int] = Query(10, ge=1, le=100),
    offset: Optional[int] = Query(0, ge=0),
    current_user = Depends(get_current_user)
):
    """Get documentation history"""
    try:
        # TODO: Implement documentation history retrieval logic
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Agent Capabilities Discovery
@router.get("/capabilities")
async def get_capabilities(
    current_user = Depends(get_current_user)
):
    """Get available agent capabilities"""
    return {
        "code_generation": {
            "types": [t.value for t in GenerationType],
            "supported_languages": ["python", "typescript", "javascript", "java", "go"],
            "features": ["context_aware", "style_guide_compliance", "test_generation"]
        },
        "code_review": {
            "types": [t.value for t in ReviewType],
            "features": ["automated_analysis", "best_practices", "security_scanning"]
        },
        "testing": {
            "types": [t.value for t in TestType],
            "features": ["coverage_tracking", "automated_test_generation", "test_optimization"]
        },
        "documentation": {
            "types": [t.value for t in DocumentationType],
            "formats": ["markdown", "html", "pdf"],
            "features": ["code_examples", "diagram_generation", "api_documentation"]
        }
    } 