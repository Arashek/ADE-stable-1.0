"""Main FastAPI application."""
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from prometheus_client import make_asgi_app
from prometheus_fastapi_instrumentator import Instrumentator
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path

# Import application components
from src.interfaces.api.providers import router as providers_router
from src.core.models.provider_registry import ProviderRegistry
from src.storage.document.repositories import ProviderRepository
from src.utils.encryption import get_encryption_key
from src.core.middleware.usage_tracking import UsageTrackingMiddleware
from src.core.dependencies.usage import get_usage_tracking_service
from src.core.dependencies.providers import get_provider_registry
from src.interfaces.api import usage, providers, auth
from src.config.settings import get_settings
from src.core.tasks.usage_cleanup import UsageCleanupTask
from src.core.tasks.usage_summary import UsageSummaryTask
from src.core.tasks.quota_monitor import QuotaMonitorTask
from src.core.tasks.metrics_update import MetricsUpdateTask
from src.core.tasks.billing import BillingTask
from src.core.tasks.payment import PaymentTask

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ade-main")

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="ADE Platform",
    description="AI Development Environment Platform",
    version="0.1.0",
)

# Initialize MongoDB client
mongodb_client = AsyncIOMotorClient(settings.MONGODB_URI)
database = str(settings.MONGODB_DATABASE)  # Ensure database name is a string
provider_repository = ProviderRepository(client=mongodb_client, database=database)

# Initialize provider registry
provider_registry = ProviderRegistry(provider_repository)

# Initialize background tasks
usage_cleanup_task = UsageCleanupTask()
usage_summary_task = UsageSummaryTask()
quota_monitor_task = QuotaMonitorTask()
metrics_update_task = MetricsUpdateTask()
billing_task = BillingTask()
payment_task = PaymentTask()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
Instrumentator().instrument(app).expose(app)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(providers.router, prefix="/api/providers", tags=["providers"])
app.include_router(usage.router, prefix="/api/usage", tags=["usage"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        # Get provider registry from dependency
        provider_registry = get_provider_registry()
        
        # Initialize provider registry
        await provider_registry.load_providers_from_database()
        logger.info("Provider registry initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize provider registry: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background tasks on application shutdown"""
    await usage_cleanup_task.stop()
    await usage_summary_task.stop()
    await quota_monitor_task.stop()
    await metrics_update_task.stop()
    await billing_task.stop()
    await payment_task.stop()

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to ADE Platform"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check provider registry health
        total_providers = len(provider_registry.providers)
        active_providers = sum(1 for p in provider_registry.providers.values() if p.is_initialized)
        provider_types = set(p.provider_type for p in provider_registry.providers.values())
        
        return {
            "status": "healthy" if active_providers > 0 else "degraded",
            "total_providers": total_providers,
            "active_providers": active_providers,
            "provider_types": list(provider_types),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler()
        ]
    )
    
    # Create logger for this module
    logger = logging.getLogger(__name__)
    logger.info("Starting ADE Platform API Server")
    
    return logger

if __name__ == "__main__":
    import uvicorn
    setup_logging()
    uvicorn.run(app, host="0.0.0.0", port=8000)