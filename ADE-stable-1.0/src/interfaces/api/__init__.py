from .app import app
from .auth import router as auth_router
from .providers import router as providers_router
from .usage import router as usage_router
from .protected import router as protected_router

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(providers_router, prefix="/providers", tags=["providers"])
app.include_router(usage_router, prefix="/usage", tags=["usage"])
app.include_router(protected_router, prefix="/protected", tags=["protected"])

__all__ = [
    'app'
]


