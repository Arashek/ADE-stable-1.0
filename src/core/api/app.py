from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .rest_endpoints import router as rest_router
from .websocket_endpoints import router as websocket_router
from .github_endpoints import router as github_router
from .github_auth import router as github_auth_router

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
app.include_router(rest_router, prefix="/api")
app.include_router(websocket_router, prefix="/api")
app.include_router(github_router, prefix="/api")
app.include_router(github_auth_router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "ADE Platform API",
        "version": "1.0.0",
        "status": "active",
        "websocket_endpoint": "/api/ws",
        "github_endpoints": {
            "repositories": "/api/github/repos",
            "auth": "/api/github/auth"
        }
    } 