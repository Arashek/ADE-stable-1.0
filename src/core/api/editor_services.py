from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
import logging
from ..services.language_servers import LanguageServerManager
from ..services.ai_assistant import AIAssistant
from ..services.session_manager import SessionManager
from ..config.editor_config import EditorConfig
from pathlib import Path
import json
import aiohttp
from ..models.language_models import LanguageModel
from ..services.ai_provider import AIProviderRegistry
from ..utils.code_analysis import CodeAnalyzer
from ..config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class LintRequest(BaseModel):
    """Request model for code linting."""
    code: str
    language: str
    file_path: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class LintResponse(BaseModel):
    """Response model for code linting."""
    diagnostics: List[Dict[str, Any]]
    style_issues: List[Dict[str, Any]]
    suggestions: List[Dict[str, Any]]

class FormatRequest(BaseModel):
    """Request model for code formatting."""
    code: str
    language: str
    file_path: Optional[str] = None
    style_config: Optional[Dict[str, Any]] = None

class FormatResponse(BaseModel):
    """Response model for code formatting."""
    formatted_code: str
    changes: List[Dict[str, Any]]

class AutocompleteRequest(BaseModel):
    """Request model for code autocompletion."""
    code: str
    language: str
    position: Dict[str, int]  # line and character
    context: Optional[Dict[str, Any]] = None

class AutocompleteResponse(BaseModel):
    """Response model for code autocompletion."""
    suggestions: List[Dict[str, Any]]
    trigger_characters: List[str]

class HoverRequest(BaseModel):
    """Request model for hover information."""
    code: str
    language: str
    position: Dict[str, int]  # line and character
    context: Optional[Dict[str, Any]] = None

class HoverResponse(BaseModel):
    """Response model for hover information."""
    contents: List[Dict[str, Any]]
    range: Optional[Dict[str, Any]] = None

class DefinitionRequest(BaseModel):
    """Request model for definition lookup."""
    code: str
    language: str
    position: Dict[str, int]  # line and character
    context: Optional[Dict[str, Any]] = None

class DefinitionResponse(BaseModel):
    """Response model for definition lookup."""
    locations: List[Dict[str, Any]]
    uri: Optional[str] = None

class AISuggestionRequest(BaseModel):
    """Request model for AI code suggestions."""
    code: str
    language: str
    context: Dict[str, Any]
    cursor_position: Dict[str, int]
    suggestion_type: str  # completion, documentation, bug_fix, test

class AISuggestionResponse(BaseModel):
    """Response model for AI code suggestions."""
    suggestions: List[Dict[str, Any]]
    confidence: float
    explanation: Optional[str] = None

class SessionRequest(BaseModel):
    """Request model for session management."""
    session_id: str
    action: str  # create, update, delete, undo, redo
    changes: Optional[List[Dict[str, Any]]] = None
    collaborators: Optional[List[str]] = None

class SessionResponse(BaseModel):
    """Response model for session management."""
    status: str
    session_id: str
    history: Optional[List[Dict[str, Any]]] = None
    collaborators: Optional[List[str]] = None

class CodeRequest(BaseModel):
    code: str
    language: str
    file_path: Optional[str] = None
    cursor_position: Optional[Dict[str, int]] = None
    context: Optional[Dict[str, Any]] = None

# Initialize services
language_server_manager = LanguageServerManager()
ai_assistant = AIAssistant()
session_manager = SessionManager()
editor_config = EditorConfig()

# Initialize language server manager and AI provider registry
language_server_manager = LanguageServerManager()
ai_provider = AIProviderRegistry()

@router.post("/lint", response_model=LintResponse)
async def lint_code(request: CodeRequest):
    """Lint code for errors and style issues."""
    try:
        # Try language server first
        if language_server_manager.has_server(request.language):
            result = await language_server_manager.lint(
                request.language,
                request.code,
                request.file_path
            )
            return LintResponse(**result)
        
        # Fallback to AI analysis
        result = await ai_provider.analyze_code(
            request.code,
            request.language,
            task="linting"
        )
        return LintResponse(**result)
    except Exception as e:
        logger.error(f"Error in lint_code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/format", response_model=FormatResponse)
async def format_code(request: CodeRequest):
    """Format code according to style guides."""
    try:
        # Try language server first
        if language_server_manager.has_server(request.language):
            result = await language_server_manager.format(
                request.language,
                request.code,
                request.file_path
            )
            return FormatResponse(**result)
        
        # Fallback to AI formatting
        result = await ai_provider.analyze_code(
            request.code,
            request.language,
            task="formatting"
        )
        return FormatResponse(**result)
    except Exception as e:
        logger.error(f"Error in format_code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/autocomplete", response_model=AutocompleteResponse)
async def get_autocomplete(request: CodeRequest):
    """Provide code autocompletion suggestions."""
    try:
        # Try language server first
        if language_server_manager.has_server(request.language):
            result = await language_server_manager.complete(
                request.language,
                request.code,
                request.cursor_position,
                request.file_path
            )
            return AutocompleteResponse(**result)
        
        # Fallback to AI completion
        result = await ai_provider.analyze_code(
            request.code,
            request.language,
            task="completion",
            cursor_position=request.cursor_position
        )
        return AutocompleteResponse(**result)
    except Exception as e:
        logger.error(f"Error in get_autocomplete: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hover", response_model=HoverResponse)
async def get_hover_info(request: CodeRequest):
    """Provide hover information for code elements."""
    try:
        # Try language server first
        if language_server_manager.has_server(request.language):
            result = await language_server_manager.hover(
                request.language,
                request.code,
                request.cursor_position,
                request.file_path
            )
            return HoverResponse(**result)
        
        # Fallback to AI hover
        result = await ai_provider.analyze_code(
            request.code,
            request.language,
            task="hover",
            cursor_position=request.cursor_position
        )
        return HoverResponse(**result)
    except Exception as e:
        logger.error(f"Error in get_hover_info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/definition", response_model=DefinitionResponse)
async def find_definition(request: CodeRequest):
    """Find definition locations for symbols."""
    try:
        # Try language server first
        if language_server_manager.has_server(request.language):
            result = await language_server_manager.definition(
                request.language,
                request.code,
                request.cursor_position,
                request.file_path
            )
            return DefinitionResponse(**result)
        
        # Fallback to AI definition finding
        result = await ai_provider.analyze_code(
            request.code,
            request.language,
            task="definition",
            cursor_position=request.cursor_position
        )
        return DefinitionResponse(**result)
    except Exception as e:
        logger.error(f"Error in find_definition: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/suggest", response_model=AISuggestionResponse)
async def get_ai_suggestions(request: AISuggestionRequest):
    """Get AI-powered code suggestions."""
    try:
        suggestions = await ai_assistant.get_code_suggestions(
            request.code,
            request.language,
            request.suggestion_type,
            request.context,
            request.cursor_position
        )
        
        return AISuggestionResponse(
            suggestions=suggestions,
            confidence=0.8,  # This should come from the AI model
            explanation="AI-generated suggestions based on context"
        )
    except Exception as e:
        logger.error(f"Error in get_ai_suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session", response_model=SessionResponse)
async def manage_session(request: SessionRequest):
    """Manage editor session."""
    try:
        if request.action == "create":
            session = await session_manager.create_session(
                request.session_id,
                request.collaborators
            )
        elif request.action == "update":
            session = await session_manager.update_session(
                request.session_id,
                request.changes
            )
        elif request.action == "delete":
            session = await session_manager.delete_session(request.session_id)
        elif request.action == "undo":
            session = await session_manager.undo(request.session_id)
        elif request.action == "redo":
            session = await session_manager.redo(request.session_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        return SessionResponse(
            status="success",
            session_id=session.id,
            history=session.history,
            collaborators=session.collaborators
        )
    except Exception as e:
        logger.error(f"Error in manage_session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_code(request: CodeRequest):
    """Perform AI-powered code analysis regardless of language."""
    try:
        # Combine language server and AI analysis
        analysis_results = []
        
        # Get language server analysis if available
        if language_server_manager.has_server(request.language):
            server_analysis = await language_server_manager.analyze(
                request.language,
                request.code,
                request.file_path
            )
            analysis_results.append(server_analysis)
        
        # Get AI analysis
        ai_analysis = await ai_provider.analyze_code(
            request.code,
            request.language,
            task="analysis",
            context=request.context
        )
        analysis_results.append(ai_analysis)
        
        # Merge and deduplicate results
        merged_analysis = CodeAnalyzer.merge_analyses(analysis_results)
        return AnalysisResponse(**merged_analysis)
    except Exception as e:
        logger.error(f"Error in analyze_code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Language support registration
SUPPORTED_LANGUAGES = {
    # Systems Programming
    "c": {"extensions": [".c", ".h"], "category": "systems"},
    "cpp": {"extensions": [".cpp", ".hpp", ".cc", ".hh"], "category": "systems"},
    "rust": {"extensions": [".rs"], "category": "systems"},
    "go": {"extensions": [".go"], "category": "systems"},
    
    # Web Development
    "javascript": {"extensions": [".js"], "category": "web"},
    "typescript": {"extensions": [".ts", ".tsx"], "category": "web"},
    "html": {"extensions": [".html", ".htm"], "category": "web"},
    "css": {"extensions": [".css", ".scss", ".sass"], "category": "web"},
    "php": {"extensions": [".php"], "category": "web"},
    
    # Mobile
    "swift": {"extensions": [".swift"], "category": "mobile"},
    "kotlin": {"extensions": [".kt", ".kts"], "category": "mobile"},
    "dart": {"extensions": [".dart"], "category": "mobile"},
    
    # Data Science
    "python": {"extensions": [".py"], "category": "data_science"},
    "r": {"extensions": [".r", ".R"], "category": "data_science"},
    "julia": {"extensions": [".jl"], "category": "data_science"},
    
    # Enterprise
    "java": {"extensions": [".java"], "category": "enterprise"},
    "csharp": {"extensions": [".cs"], "category": "enterprise"},
    
    # Functional
    "haskell": {"extensions": [".hs"], "category": "functional"},
    "scala": {"extensions": [".scala"], "category": "functional"},
    "clojure": {"extensions": [".clj"], "category": "functional"},
    "fsharp": {"extensions": [".fs"], "category": "functional"},
    
    # Scripting
    "ruby": {"extensions": [".rb"], "category": "scripting"},
    "perl": {"extensions": [".pl", ".pm"], "category": "scripting"},
    "bash": {"extensions": [".sh", ".bash"], "category": "scripting"},
    "powershell": {"extensions": [".ps1"], "category": "scripting"},
    
    # Database
    "sql": {"extensions": [".sql"], "category": "database"},
    "graphql": {"extensions": [".graphql", ".gql"], "category": "database"},
    
    # Infrastructure
    "terraform": {"extensions": [".tf"], "category": "infrastructure"},
    "cloudformation": {"extensions": [".yaml", ".yml", ".json"], "category": "infrastructure"},
    "kubernetes": {"extensions": [".yaml", ".yml"], "category": "infrastructure"},
    
    # Specialized
    "matlab": {"extensions": [".m"], "category": "specialized"},
    "fortran": {"extensions": [".f", ".f90", ".f95"], "category": "specialized"},
    "cobol": {"extensions": [".cbl", ".cob"], "category": "specialized"},
    "assembly": {"extensions": [".asm", ".s"], "category": "specialized"}
}

def get_language_from_extension(file_path: str) -> Optional[str]:
    """Determine language from file extension."""
    ext = Path(file_path).suffix.lower()
    for lang, info in SUPPORTED_LANGUAGES.items():
        if ext in info["extensions"]:
            return lang
    return None

def get_language_category(language: str) -> Optional[str]:
    """Get the category of a programming language."""
    return SUPPORTED_LANGUAGES.get(language, {}).get("category") 