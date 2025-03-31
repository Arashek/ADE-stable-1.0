import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import application components
from src.interfaces.api.api import app as api_app
from src.interfaces.api.auth import router as auth_router
from src.interfaces.api.protected import router as protected_router
from src.storage.document.init_db import init_database

# Configure logging
logger = logging.getLogger("ade-api")

# Create FastAPI app
app = FastAPI(
    title="ADE Platform API",
    description="API for the ADE Platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(protected_router, prefix="/protected", tags=["protected"])
app.include_router(api_app)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Initializing application...")
    
    # Initialize database
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://mongodb:27017/ade")
    db_init_success = await init_database(mongodb_uri)
    
    if not db_init_success:
        logger.warning("Database initialization failed, some features may not work properly")
    else:
        logger.info("Database initialization completed successfully")

@app.get("/")
async def root():
    return {"message": "Welcome to ADE Platform API"} 