from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from uuid import uuid4

from src.storage.document.models.usage import (
    UsageRecord,
    UserUsageSummary,
    BillingTierConfig,
    UsageType,
    BillingTier
)
from src.storage.document.repositories import UsageRepository, UserRepository
from src.core.providers.registry import ProviderRegistry
from src.utils.metrics import track_usage_metrics

logger = logging.getLogger(__name__)

class UsageTrackingService:
    """Service for tracking and managing usage of AI providers"""
    
    def __init__(
        self,
        usage_repository: UsageRepository,
        user_repository: UserRepository,
        provider_registry: ProviderRegistry
    ):
        self.usage_repository = usage_repository
        self.user_repository = user_repository
        self.provider_registry = provider_registry
        
        # Default tier configurations
        self.tier_configs = {
            BillingTier.FREE: BillingTierConfig(
                tier=BillingTier.FREE,
                monthly_price=0.0,
                quota_limits={
                    "text_generation": 1000,
                    "code_generation": 500,
                    "embedding": 1000,
                    "vision": 100,
                    "audio": 100
                },
                features=["basic_ai_features", "standard_support"],
                priority=1,
                rate_limits={"requests_per_minute": 10}
            ),
            BillingTier.STANDARD: BillingTierConfig(
                tier=BillingTier.STANDARD,
                monthly_price=49.99,
                quota_limits={
                    "text_generation": 10000,
                    "code_generation": 5000,
                    "embedding": 10000,
                    "vision": 1000,
                    "audio": 1000
                },
                features=["basic_ai_features", "standard_support", "priority_routing"],
                priority=2,
                rate_limits={"requests_per_minute": 60}
            ),
            BillingTier.PREMIUM: BillingTierConfig(
                tier=BillingTier.PREMIUM,
                monthly_price=149.99,
                quota_limits={
                    "text_generation": 100000,
                    "code_generation": 50000,
                    "embedding": 100000,
                    "vision": 10000,
                    "audio": 10000
                },
                features=["basic_ai_features", "premium_support", "priority_routing", "custom_models"],
                priority=3,
                rate_limits={"requests_per_minute": 300}
            )
        }
    
    async def record_usage(
        self,
        user_id: str,
        provider: str,
        model: str,
        usage_type: UsageType,
        tokens_used: int,
        cost: float,
        status: str,
        project_id: Optional[str] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> UsageRecord:
        """Record a new usage event"""
        try:
            # Create usage record
            record = UsageRecord(
                id=str(uuid4()),
                user_id=user_id,
                project_id=project_id,
                provider=provider,
                model=model,
                usage_type=usage_type,
                tokens_used=tokens_used,
                cost=cost,
                status=status,
                error_message=error_message,
                metadata=metadata or {}
            )
            
            # Save to database
            await self.usage_repository.create(record)
            
            # Update user summary
            await self._update_user_summary(user_id, record)
            
            # Track metrics
            track_usage_metrics(record)
            
            return record
            
        except Exception as e:
            logger.error(f"Error recording usage: {str(e)}")
            raise
    
    async def get_user_usage_summary(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> UserUsageSummary:
        """Get usage summary for a user"""
        try:
            # Get user's current tier
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                raise ValueError(f"User not found: {user_id}")
            
            # Get usage records for the period
            query = {"user_id": user_id}
            if start_date:
                query["timestamp"] = {"$gte": start_date}
            if end_date:
                query["timestamp"] = {"$lte": end_date}
            
            records = await self.usage_repository.find(query)
            
            # Calculate summary
            summary = UserUsageSummary(
                user_id=user_id,
                billing_tier=user.billing_tier,
                quota_limits=self.tier_configs[user.billing_tier].quota_limits
            )
            
            for record in records:
                summary.total_tokens += record.tokens_used
                summary.total_cost += record.cost
                
                # Update usage by type
                summary.usage_by_type[record.usage_type] = \
                    summary.usage_by_type.get(record.usage_type, 0) + record.tokens_used
                
                # Update usage by provider
                summary.usage_by_provider[record.provider] = \
                    summary.usage_by_provider.get(record.provider, 0) + record.tokens_used
                
                # Update usage by model
                summary.usage_by_model[record.model] = \
                    summary.usage_by_model.get(record.model, 0) + record.tokens_used
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting usage summary: {str(e)}")
            raise
    
    async def check_quota_limits(
        self,
        user_id: str,
        usage_type: UsageType,
        tokens: int
    ) -> bool:
        """Check if a user has exceeded their quota limits"""
        try:
            # Get user's current tier
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                raise ValueError(f"User not found: {user_id}")
            
            # Get tier config
            tier_config = self.tier_configs[user.billing_tier]
            
            # Get current usage for the month
            start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            summary = await self.get_user_usage_summary(user_id, start_date=start_of_month)
            
            # Check quota limits
            current_usage = summary.usage_by_type.get(usage_type, 0)
            quota_limit = tier_config.quota_limits.get(usage_type.value, 0)
            
            return (current_usage + tokens) <= quota_limit
            
        except Exception as e:
            logger.error(f"Error checking quota limits: {str(e)}")
            raise
    
    async def _update_user_summary(self, user_id: str, record: UsageRecord) -> None:
        """Update the user's usage summary with a new record"""
        try:
            # Get current summary
            summary = await self.get_user_usage_summary(user_id)
            
            # Update summary with new record
            summary.total_tokens += record.tokens_used
            summary.total_cost += record.cost
            summary.last_updated = datetime.utcnow()
            
            # Update usage by type
            summary.usage_by_type[record.usage_type] = \
                summary.usage_by_type.get(record.usage_type, 0) + record.tokens_used
            
            # Update usage by provider
            summary.usage_by_provider[record.provider] = \
                summary.usage_by_provider.get(record.provider, 0) + record.tokens_used
            
            # Update usage by model
            summary.usage_by_model[record.model] = \
                summary.usage_by_model.get(record.model, 0) + record.tokens_used
            
            # Save updated summary
            await self.usage_repository.update_summary(user_id, summary)
            
        except Exception as e:
            logger.error(f"Error updating user summary: {str(e)}")
            raise 