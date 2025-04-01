"""
Visual Perception MCP for Windsurf

This specialized agent provides vision capabilities to understand and analyze
content displayed in preview windows, enabling better debugging and assistance.
"""

import base64
import io
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Union

import cv2
import numpy as np
import pytesseract
from fastapi import APIRouter, Depends, HTTPException, Request
from PIL import Image
from pydantic import BaseModel

from backend.services.agent_coordinator import AgentCoordinator
from backend.services.memory.memory_service import MemoryService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure pytesseract path (adjust as needed for Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Models
class ScreenshotRequest(BaseModel):
    """Request model for screenshot analysis."""
    image_data: str  # Base64 encoded image
    context: Optional[Dict] = None

class ScreenshotAnalysisResult(BaseModel):
    """Response model for screenshot analysis."""
    text_content: str
    ui_elements: List[Dict]
    error_messages: Optional[List[str]] = None
    status_messages: Optional[List[str]] = None
    recognized_state: str
    timestamp: str

class VisualPerceptionMCP:
    """
    Visual Perception MCP that provides vision capabilities to understand
    content displayed in preview windows.
    """
    
    def __init__(self, memory_service: MemoryService = None, agent_coordinator: AgentCoordinator = None):
        """Initialize the Visual Perception MCP."""
        self.memory_service = memory_service
        self.agent_coordinator = agent_coordinator
        self.router = self._create_router()
        logger.info("Visual Perception MCP initialized")
    
    def _create_router(self) -> APIRouter:
        """Create and configure the API router for this MCP."""
        router = APIRouter(prefix="/api/mcp/visual", tags=["Visual Perception MCP"])
        
        @router.post("/analyze", response_model=ScreenshotAnalysisResult)
        async def analyze_screenshot(request: ScreenshotRequest):
            """Analyze a screenshot from a preview window."""
            try:
                # Process the screenshot
                result = self.process_screenshot(request.image_data, request.context)
                
                # Store the analysis in memory for future reference
                if self.memory_service:
                    self.memory_service.store_perception_data(result)
                
                return result
            except Exception as e:
                logger.error(f"Error analyzing screenshot: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error analyzing screenshot: {str(e)}")
        
        @router.get("/status")
        async def get_status():
            """Get the status of the Visual Perception MCP."""
            return {
                "status": "active",
                "capabilities": ["text_recognition", "ui_element_detection", "error_detection"],
                "last_updated": datetime.now().isoformat()
            }
        
        return router
    
    def process_screenshot(self, image_data: str, context: Optional[Dict] = None) -> ScreenshotAnalysisResult:
        """
        Process a screenshot and extract information from it.
        
        Args:
            image_data: Base64 encoded image data
            context: Optional context information about the screenshot
            
        Returns:
            ScreenshotAnalysisResult with extracted information
        """
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to OpenCV format for processing
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Extract text using OCR
            text_content = pytesseract.image_to_string(image)
            
            # Detect UI elements (simplified version)
            ui_elements = self._detect_ui_elements(cv_image)
            
            # Detect error messages (red text or typical error patterns)
            error_messages = self._detect_error_messages(cv_image, text_content)
            
            # Detect status messages
            status_messages = self._detect_status_messages(text_content)
            
            # Determine the recognized state
            recognized_state = self._determine_state(text_content, ui_elements, error_messages)
            
            return ScreenshotAnalysisResult(
                text_content=text_content,
                ui_elements=ui_elements,
                error_messages=error_messages,
                status_messages=status_messages,
                recognized_state=recognized_state,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"Error processing screenshot: {str(e)}")
            raise
    
    def _detect_ui_elements(self, image: np.ndarray) -> List[Dict]:
        """
        Detect UI elements in the image.
        
        This is a simplified implementation that would be expanded with more
        sophisticated computer vision techniques in a production system.
        """
        # Convert to grayscale for processing
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect edges
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        ui_elements = []
        for i, contour in enumerate(contours):
            # Filter out very small contours
            if cv2.contourArea(contour) < 100:
                continue
                
            x, y, w, h = cv2.boundingRect(contour)
            ui_elements.append({
                "id": f"element_{i}",
                "type": "unknown",
                "bounds": {
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h)
                }
            })
        
        return ui_elements
    
    def _detect_error_messages(self, image: np.ndarray, text_content: str) -> List[str]:
        """
        Detect error messages in the image based on color and text patterns.
        """
        error_messages = []
        
        # Look for common error keywords in the text
        error_keywords = ["error", "exception", "failed", "warning", "invalid", "not found"]
        lines = text_content.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in error_keywords):
                error_messages.append(line.strip())
        
        # Additional image processing could be done here to detect red text
        # This would involve color filtering and more sophisticated OCR
        
        return error_messages
    
    def _detect_status_messages(self, text_content: str) -> List[str]:
        """
        Detect status messages in the text content.
        """
        status_messages = []
        
        # Look for common status keywords
        status_keywords = ["success", "completed", "running", "started", "loading", "ready"]
        lines = text_content.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in status_keywords):
                status_messages.append(line.strip())
        
        return status_messages
    
    def _determine_state(self, text_content: str, ui_elements: List[Dict], error_messages: List[str]) -> str:
        """
        Determine the overall state of the application based on the analyzed content.
        """
        # Check for blank or empty page
        if not text_content.strip() and not ui_elements:
            return "blank_page"
        
        # Check for error state
        if error_messages:
            return "error_state"
        
        # Check for loading state
        if "loading" in text_content.lower():
            return "loading"
        
        # Check for login page
        if any(keyword in text_content.lower() for keyword in ["login", "sign in", "username", "password"]):
            return "login_page"
        
        # Default to normal state if we have UI elements
        if ui_elements:
            return "normal_state"
        
        return "unknown_state"

# Router factory function for FastAPI integration
def get_visual_perception_router(
    memory_service: MemoryService = None,
    agent_coordinator: AgentCoordinator = None
) -> APIRouter:
    """Create and return the Visual Perception MCP router."""
    mcp = VisualPerceptionMCP(memory_service, agent_coordinator)
    return mcp.router
