import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from decimal import Decimal

from src.storage.document.repositories import UsageRepository, UserRepository
from src.core.services.usage_tracking import UsageTrackingService
from src.core.providers.registry import ProviderRegistry
from src.config.usage import USAGE_TRACKING_SETTINGS
from src.core.dependencies.database import get_database
from src.core.dependencies.providers import get_provider_registry
from src.core.dependencies.users import get_user_repository

logger = logging.getLogger(__name__)

class BillingTask:
    """Background task for handling billing calculations and invoice generation"""
    
    def __init__(self):
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        self.service: Optional[UsageTrackingService] = None
    
    async def start(self):
        """Start the billing task"""
        if self.is_running:
            return
        
        # Initialize service
        db = await anext(get_database())
        usage_repository = UsageRepository(db.client, db.name)
        user_repository = await anext(get_user_repository())
        provider_registry = await anext(get_provider_registry())
        
        self.service = UsageTrackingService(
            usage_repository=usage_repository,
            user_repository=user_repository,
            provider_registry=provider_registry
        )
        
        self.is_running = True
        self.task = asyncio.create_task(self._run())
        logger.info("Billing task started")
    
    async def stop(self):
        """Stop the billing task"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Billing task stopped")
    
    async def _run(self):
        """Run the billing task"""
        while self.is_running:
            try:
                if not self.service:
                    raise RuntimeError("Usage tracking service not initialized")
                
                # Check if it's time to generate invoices (e.g., at the start of each month)
                if datetime.utcnow().day == 1:
                    await self._generate_invoices()
                
                # Wait before next check
                await asyncio.sleep(3600)  # Check every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in billing task: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    async def _generate_invoices(self):
        """Generate invoices for all users"""
        try:
            # Get all users
            users = await self.service.user_repository.find({})
            
            # Get usage for the previous month
            now = datetime.utcnow()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            for user in users:
                try:
                    # Get usage summary for the month
                    summary = await self.service.get_user_usage_summary(
                        user.id,
                        start_date=start_of_month,
                        end_date=end_of_month
                    )
                    
                    # Get tier config
                    tier_config = self.service.tier_configs[user.billing_tier]
                    
                    # Calculate charges
                    charges = await self._calculate_charges(summary, tier_config)
                    
                    # Generate invoice
                    invoice = await self._create_invoice(
                        user,
                        start_of_month,
                        end_of_month,
                        charges
                    )
                    
                    # Store invoice
                    await self._store_invoice(invoice)
                    
                    # Send invoice to user
                    await self._send_invoice(invoice)
                    
                    logger.info(f"Generated invoice for user {user.id}")
                    
                except Exception as e:
                    logger.error(f"Error generating invoice for user {user.id}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error generating invoices: {str(e)}")
    
    async def _calculate_charges(
        self,
        summary: any,
        tier_config: any
    ) -> Dict[str, Decimal]:
        """Calculate charges for usage"""
        charges = {
            "base_fee": Decimal(str(tier_config.monthly_price)),
            "usage_charges": Decimal("0.0"),
            "overage_charges": Decimal("0.0"),
            "total": Decimal("0.0")
        }
        
        # Calculate usage charges
        for usage_type, limit in tier_config.quota_limits.items():
            current_usage = summary.usage_by_type.get(usage_type, 0)
            
            if current_usage <= limit:
                # Within quota, no additional charges
                continue
            
            # Calculate overage
            overage = current_usage - limit
            
            # Get overage rate from tier config
            overage_rate = Decimal(str(tier_config.overage_rates.get(usage_type, "0.0")))
            
            # Calculate overage charge
            overage_charge = Decimal(str(overage)) * overage_rate
            
            charges["overage_charges"] += overage_charge
        
        # Calculate total
        charges["total"] = (
            charges["base_fee"] +
            charges["usage_charges"] +
            charges["overage_charges"]
        )
        
        return charges
    
    async def _create_invoice(
        self,
        user: any,
        start_date: datetime,
        end_date: datetime,
        charges: Dict[str, Decimal]
    ) -> Dict:
        """Create an invoice document"""
        return {
            "id": f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{user.id}",
            "user_id": user.id,
            "billing_tier": user.billing_tier,
            "period_start": start_date,
            "period_end": end_date,
            "charges": charges,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "due_date": (end_date + timedelta(days=30)).date(),
            "paid_at": None,
            "payment_method": user.payment_method,
            "billing_address": user.billing_address,
            "items": [
                {
                    "description": "Base subscription fee",
                    "amount": charges["base_fee"],
                    "quantity": 1
                },
                {
                    "description": "Usage charges",
                    "amount": charges["usage_charges"],
                    "quantity": 1
                },
                {
                    "description": "Overage charges",
                    "amount": charges["overage_charges"],
                    "quantity": 1
                }
            ]
        }
    
    async def _store_invoice(self, invoice: Dict):
        """Store invoice in database"""
        # TODO: Implement invoice storage
        pass
    
    async def _send_invoice(self, invoice: Dict):
        """Send invoice to user"""
        # TODO: Implement invoice sending (email, etc.)
        pass 