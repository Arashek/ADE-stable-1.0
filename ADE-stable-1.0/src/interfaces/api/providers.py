"""Provider Registry API endpoints with authentication."""
from fastapi import APIRouter, Depends, HTTPException, status, Security
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from src.core.models.provider_registry import ModelCapability, ProviderRegistry
from src.interfaces.api.auth import User, UserRole, has_role, get_current_active_user

# Create router
router = APIRouter(
    prefix="/providers",
    tags=["providers"]
)

# Models
class ProviderRequest(BaseModel):
    """Request model for registering a provider."""
    provider_type: str = Field(..., description="Type of the provider (e.g., 'openai', 'anthropic')")
    api_key: str = Field(..., description="API key for the provider")
    model_map: Optional[Dict[str, str]] = Field(None, description="Mapping of model names to provider-specific model IDs")
    default_parameters: Optional[Dict[str, Any]] = Field(None, description="Default parameters for the provider")
    description: Optional[str] = Field(None, description="Description of the provider")
    rate_limit: Optional[int] = Field(None, description="Rate limit for the provider (requests per minute)")

class ProviderResponse(BaseModel):
    """Response model for provider information."""
    provider_id: str = Field(..., description="Unique identifier for the provider")
    provider_type: str = Field(..., description="Type of the provider")
    available_models: List[str] = Field(..., description="List of available models")
    capabilities: List[str] = Field(..., description="List of provider capabilities")
    is_active: bool = Field(..., description="Whether the provider is active")
    description: Optional[str] = Field(None, description="Description of the provider")
    rate_limit: Optional[int] = Field(None, description="Rate limit for the provider")
    created_at: datetime = Field(..., description="When the provider was registered")
    updated_at: datetime = Field(..., description="When the provider was last updated")

class ProviderUpdateRequest(BaseModel):
    """Request model for updating a provider."""
    api_key: Optional[str] = Field(None, description="New API key for the provider")
    model_map: Optional[Dict[str, str]] = Field(None, description="Updated model mapping")
    default_parameters: Optional[Dict[str, Any]] = Field(None, description="Updated default parameters")
    description: Optional[str] = Field(None, description="Updated description")
    rate_limit: Optional[int] = Field(None, description="Updated rate limit")
    is_active: Optional[bool] = Field(None, description="Whether to activate/deactivate the provider")

# Provider registry instance
provider_registry = ProviderRegistry()

# Routes with RBAC
@router.post("/", response_model=ProviderResponse)
async def register_provider(
    request: ProviderRequest,
    current_user: User = Security(has_role([UserRole.ADMIN]))
):
    """
    Register a new provider (Admin only)
    
    This endpoint allows administrators to register new AI providers with the system.
    The provider will be validated and tested before being registered.
    """
    try:
        provider = provider_registry.register_provider(
            provider_type=request.provider_type,
            api_key=request.api_key,
            model_map=request.model_map,
            default_parameters=request.default_parameters,
            description=request.description,
            rate_limit=request.rate_limit
        )
        
        return {
            "provider_id": provider.provider_id,
            "provider_type": provider.provider_type,
            "available_models": provider.list_available_models(),
            "capabilities": [c.value for c in provider.get_capabilities()],
            "is_active": provider.is_active(),
            "description": provider.description,
            "rate_limit": provider.rate_limit,
            "created_at": provider.created_at,
            "updated_at": provider.updated_at
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register provider: {str(e)}"
        )

@router.get("/", response_model=List[ProviderResponse])
async def list_providers(
    current_user: User = Depends(get_current_active_user),
    include_inactive: bool = False
):
    """
    List all registered providers (Any authenticated user)
    
    Args:
        include_inactive: Whether to include inactive providers in the response
    """
    try:
        providers = provider_registry.list_providers(include_inactive=include_inactive)
        return [
            {
                "provider_id": provider.provider_id,
                "provider_type": provider.provider_type,
                "available_models": provider.list_available_models(),
                "capabilities": [c.value for c in provider.get_capabilities()],
                "is_active": provider.is_active(),
                "description": provider.description,
                "rate_limit": provider.rate_limit,
                "created_at": provider.created_at,
                "updated_at": provider.updated_at
            }
            for provider in providers
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list providers: {str(e)}"
        )

@router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(
    provider_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get provider by ID (Any authenticated user)"""
    try:
        provider = provider_registry.get_provider(provider_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provider with ID {provider_id} not found"
            )
        
        return {
            "provider_id": provider.provider_id,
            "provider_type": provider.provider_type,
            "available_models": provider.list_available_models(),
            "capabilities": [c.value for c in provider.get_capabilities()],
            "is_active": provider.is_active(),
            "description": provider.description,
            "rate_limit": provider.rate_limit,
            "created_at": provider.created_at,
            "updated_at": provider.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get provider: {str(e)}"
        )

@router.put("/{provider_id}", response_model=ProviderResponse)
async def update_provider(
    provider_id: str,
    request: ProviderUpdateRequest,
    current_user: User = Security(has_role([UserRole.ADMIN]))
):
    """Update a provider (Admin only)"""
    try:
        provider = provider_registry.get_provider(provider_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provider with ID {provider_id} not found"
            )
        
        # Update provider fields
        if request.api_key is not None:
            provider.api_key = request.api_key
        if request.model_map is not None:
            provider.model_map = request.model_map
        if request.default_parameters is not None:
            provider.default_parameters = request.default_parameters
        if request.description is not None:
            provider.description = request.description
        if request.rate_limit is not None:
            provider.rate_limit = request.rate_limit
        if request.is_active is not None:
            provider.is_active = request.is_active
        
        # Save changes
        provider_registry.update_provider(provider)
        
        return {
            "provider_id": provider.provider_id,
            "provider_type": provider.provider_type,
            "available_models": provider.list_available_models(),
            "capabilities": [c.value for c in provider.get_capabilities()],
            "is_active": provider.is_active(),
            "description": provider.description,
            "rate_limit": provider.rate_limit,
            "created_at": provider.created_at,
            "updated_at": provider.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update provider: {str(e)}"
        )

@router.delete("/{provider_id}")
async def delete_provider(
    provider_id: str,
    current_user: User = Security(has_role([UserRole.ADMIN]))
):
    """Delete a provider (Admin only)"""
    try:
        success = provider_registry.unregister_provider(provider_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provider with ID {provider_id} not found"
            )
        
        return {"message": f"Provider {provider_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete provider: {str(e)}"
        )

@router.get("/capabilities/")
async def list_capabilities(
    current_user: User = Depends(get_current_active_user)
):
    """List all available model capabilities (Any authenticated user)"""
    try:
        capabilities = [capability.value for capability in ModelCapability]
        return {"capabilities": capabilities}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list capabilities: {str(e)}"
        )

@router.get("/{provider_id}/test")
async def test_provider(
    provider_id: str,
    current_user: User = Security(has_role([UserRole.ADMIN]))
):
    """Test a provider's connection and capabilities (Admin only)"""
    try:
        provider = provider_registry.get_provider(provider_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provider with ID {provider_id} not found"
            )
        
        # Test the provider
        test_results = provider_registry.test_provider(provider_id)
        
        return {
            "provider_id": provider_id,
            "success": test_results["success"],
            "message": test_results["message"],
            "capabilities_tested": test_results["capabilities_tested"],
            "errors": test_results.get("errors", [])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test provider: {str(e)}"
        )

@router.get("/health")
async def provider_health():
    """Health check for Provider Registry.
    
    Returns:
        Dict containing:
        - status: Overall health status (healthy/degraded/unhealthy)
        - total_providers: Total number of registered providers
        - active_providers: Number of active providers
        - provider_types: List of unique provider types
        - timestamp: Current timestamp
        - error: Error message if status is unhealthy
    """
    try:
        # Get all providers
        providers = provider_registry.list_providers()
        
        # Get active providers
        active_providers = [p for p in providers if p.is_initialized]
        
        # Get unique provider types
        provider_types = list(set(p.provider_type for p in providers))
        
        # Determine health status
        if not providers:
            status = "degraded"
        elif not active_providers:
            status = "degraded"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "total_providers": len(providers),
            "active_providers": len(active_providers),
            "provider_types": provider_types,
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "providers_by_type": {
                    provider_type: len([p for p in providers if p.provider_type == provider_type])
                    for provider_type in provider_types
                },
                "capabilities": list(set(
                    capability for p in providers
                    for capability in p.capabilities_scores.keys()
                ))
            }
        }
    except Exception as e:
        logger.error(f"Provider health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        } 