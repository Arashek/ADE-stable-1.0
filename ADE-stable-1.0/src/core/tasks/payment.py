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

class PaymentTask:
    """Background task for handling payment processing"""
    
    def __init__(self):
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        self.service: Optional[UsageTrackingService] = None
    
    async def start(self):
        """Start the payment task"""
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
        logger.info("Payment task started")
    
    async def stop(self):
        """Stop the payment task"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Payment task stopped")
    
    async def _run(self):
        """Run the payment task"""
        while self.is_running:
            try:
                if not self.service:
                    raise RuntimeError("Usage tracking service not initialized")
                
                # Process pending payments
                await self._process_pending_payments()
                
                # Process failed payments
                await self._process_failed_payments()
                
                # Wait before next check
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in payment task: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    async def _process_pending_payments(self):
        """Process pending payments"""
        try:
            # Get pending invoices
            pending_invoices = await self._get_pending_invoices()
            
            for invoice in pending_invoices:
                try:
                    # Get user
                    user = await self.service.user_repository.get_by_id(invoice["user_id"])
                    if not user:
                        logger.error(f"User not found for invoice {invoice['id']}")
                        continue
                    
                    # Process payment
                    success = await self._process_payment(invoice, user)
                    
                    if success:
                        # Update invoice status
                        await self._update_invoice_status(invoice["id"], "paid")
                        logger.info(f"Successfully processed payment for invoice {invoice['id']}")
                    else:
                        # Update invoice status
                        await self._update_invoice_status(invoice["id"], "failed")
                        logger.error(f"Failed to process payment for invoice {invoice['id']}")
                    
                except Exception as e:
                    logger.error(f"Error processing payment for invoice {invoice['id']}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error processing pending payments: {str(e)}")
    
    async def _process_failed_payments(self):
        """Process failed payments"""
        try:
            # Get failed invoices
            failed_invoices = await self._get_failed_invoices()
            
            for invoice in failed_invoices:
                try:
                    # Get user
                    user = await self.service.user_repository.get_by_id(invoice["user_id"])
                    if not user:
                        logger.error(f"User not found for invoice {invoice['id']}")
                        continue
                    
                    # Check if we should retry
                    if not await self._should_retry_payment(invoice):
                        continue
                    
                    # Process payment
                    success = await self._process_payment(invoice, user)
                    
                    if success:
                        # Update invoice status
                        await self._update_invoice_status(invoice["id"], "paid")
                        logger.info(f"Successfully processed retry payment for invoice {invoice['id']}")
                    else:
                        # Update retry count
                        await self._increment_retry_count(invoice["id"])
                        logger.error(f"Failed to process retry payment for invoice {invoice['id']}")
                    
                except Exception as e:
                    logger.error(f"Error processing retry payment for invoice {invoice['id']}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error processing failed payments: {str(e)}")
    
    async def _get_pending_invoices(self) -> List[Dict]:
        """Get pending invoices"""
        # TODO: Implement getting pending invoices from database
        return []
    
    async def _get_failed_invoices(self) -> List[Dict]:
        """Get failed invoices"""
        # TODO: Implement getting failed invoices from database
        return []
    
    async def _process_payment(self, invoice: Dict, user: any) -> bool:
        """Process payment for an invoice"""
        try:
            # TODO: Implement actual payment processing
            # This would integrate with a payment processor like Stripe
            
            # For now, simulate payment processing
            await asyncio.sleep(1)  # Simulate API call
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}")
            return False
    
    async def _update_invoice_status(self, invoice_id: str, status: str):
        """Update invoice status"""
        # TODO: Implement updating invoice status in database
        pass
    
    async def _should_retry_payment(self, invoice: Dict) -> bool:
        """Check if we should retry payment"""
        # TODO: Implement retry logic based on invoice retry count and other factors
        return True
    
    async def _increment_retry_count(self, invoice_id: str):
        """Increment retry count for an invoice"""
        # TODO: Implement incrementing retry count in database
        pass 