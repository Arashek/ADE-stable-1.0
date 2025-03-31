from fastapi import APIRouter
from .learning_endpoints import router as learning_router

# Create main router
router = APIRouter()

# Include learning endpoints
router.include_router(learning_router) 