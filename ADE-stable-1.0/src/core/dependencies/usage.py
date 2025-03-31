from typing import AsyncGenerator
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient

from src.core.services.usage_tracking import UsageTrackingService
from src.storage.document.repositories import UsageRepository, UserRepository
from src.core.providers.registry import ProviderRegistry
from src.core.dependencies.database import get_database
from src.core.dependencies.providers import get_provider_registry
from src.core.dependencies.users import get_user_repository

async def get_usage_repository(
    db: AsyncIOMotorClient = Depends(get_database)
) -> AsyncGenerator[UsageRepository, None]:
    """Get usage repository instance"""
    repository = UsageRepository(db.client, db.name)
    yield repository

async def get_usage_tracking_service(
    usage_repository: UsageRepository = Depends(get_usage_repository),
    user_repository: UserRepository = Depends(get_user_repository),
    provider_registry: ProviderRegistry = Depends(get_provider_registry)
) -> AsyncGenerator[UsageTrackingService, None]:
    """Get usage tracking service instance"""
    service = UsageTrackingService(
        usage_repository=usage_repository,
        user_repository=user_repository,
        provider_registry=provider_registry
    )
    yield service 