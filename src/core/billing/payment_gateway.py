from typing import Optional, Dict, Any
from datetime import datetime
import stripe
import paypalrestsdk
from pydantic import BaseModel
from ..auth.pricing_tiers import pricing_manager
from ..storage.usage_tracking import usage_tracker

class PaymentMethod(BaseModel):
    """Represents a payment method"""
    id: str
    type: str
    last4: Optional[str] = None
    brand: Optional[str] = None
    expiry_month: Optional[int] = None
    expiry_year: Optional[int] = None

class Invoice(BaseModel):
    """Represents a billing invoice"""
    id: str
    amount: float
    currency: str = "usd"
    status: str
    date: datetime
    payment_method: PaymentMethod
    subscription_id: Optional[str] = None

class PaymentGateway:
    """Handles payment processing and subscription management"""
    
    def __init__(self, stripe_secret_key: str, paypal_client_id: str, paypal_secret: str):
        self.stripe = stripe
        self.stripe.api_key = stripe_secret_key
        
        paypalrestsdk.configure({
            "mode": "sandbox",  # Change to "live" for production
            "client_id": paypal_client_id,
            "client_secret": paypal_secret
        })
    
    def create_customer(self, email: str, name: Optional[str] = None) -> str:
        """Create a new customer in Stripe"""
        customer = self.stripe.Customer.create(
            email=email,
            name=name
        )
        return customer.id
    
    def add_payment_method(self, customer_id: str, payment_method_id: str) -> PaymentMethod:
        """Add a payment method to a customer"""
        # Attach payment method to customer
        self.stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer_id
        )
        
        # Set as default payment method
        self.stripe.Customer.modify(
            customer_id,
            invoice_settings={
                "default_payment_method": payment_method_id
            }
        )
        
        # Get payment method details
        payment_method = self.stripe.PaymentMethod.retrieve(payment_method_id)
        return PaymentMethod(
            id=payment_method.id,
            type=payment_method.type,
            last4=payment_method.card.last4 if payment_method.type == "card" else None,
            brand=payment_method.card.brand if payment_method.type == "card" else None,
            expiry_month=payment_method.card.exp_month if payment_method.type == "card" else None,
            expiry_year=payment_method.card.exp_year if payment_method.type == "card" else None
        )
    
    def create_subscription(
        self,
        customer_id: str,
        tier_name: str,
        trial_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a new subscription"""
        tier = pricing_manager.get_tier(tier_name)
        if not tier:
            raise ValueError(f"Invalid tier: {tier_name}")
        
        # Create Stripe subscription
        subscription_data = {
            "customer": customer_id,
            "items": [{"price": self._get_stripe_price_id(tier)}],
            "payment_behavior": "default_incomplete",
            "expand": ["latest_invoice.payment_intent"],
        }
        
        if trial_days:
            subscription_data["trial_period_days"] = trial_days
        
        subscription = self.stripe.Subscription.create(**subscription_data)
        
        return {
            "subscription_id": subscription.id,
            "client_secret": subscription.latest_invoice.payment_intent.client_secret,
            "status": subscription.status
        }
    
    def update_subscription(self, subscription_id: str, tier_name: str) -> Dict[str, Any]:
        """Update an existing subscription"""
        tier = pricing_manager.get_tier(tier_name)
        if not tier:
            raise ValueError(f"Invalid tier: {tier_name}")
        
        subscription = self.stripe.Subscription.retrieve(subscription_id)
        
        # Update subscription with new price
        updated_subscription = self.stripe.Subscription.modify(
            subscription_id,
            items=[{
                "id": subscription.items.data[0].id,
                "price": self._get_stripe_price_id(tier),
                "prorate": True
            }]
        )
        
        return {
            "subscription_id": updated_subscription.id,
            "status": updated_subscription.status
        }
    
    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a subscription"""
        subscription = self.stripe.Subscription.delete(subscription_id)
        return {
            "subscription_id": subscription.id,
            "status": subscription.status
        }
    
    def get_invoice(self, invoice_id: str) -> Invoice:
        """Get invoice details"""
        invoice = self.stripe.Invoice.retrieve(invoice_id)
        return Invoice(
            id=invoice.id,
            amount=invoice.amount_paid / 100,  # Convert from cents to dollars
            currency=invoice.currency,
            status=invoice.status,
            date=datetime.fromtimestamp(invoice.created),
            payment_method=PaymentMethod(
                id=invoice.payment_intent.payment_method,
                type=invoice.payment_intent.payment_method_types[0]
            ),
            subscription_id=invoice.subscription
        )
    
    def get_billing_history(self, customer_id: str) -> list[Invoice]:
        """Get billing history for a customer"""
        invoices = self.stripe.Invoice.list(
            customer=customer_id,
            limit=100
        )
        return [self.get_invoice(invoice.id) for invoice in invoices.data]
    
    def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        try:
            event = self.stripe.Webhook.construct_event(
                payload,
                signature,
                self.stripe_webhook_secret
            )
            
            if event.type == "invoice.payment_succeeded":
                return self._handle_successful_payment(event.data.object)
            elif event.type == "invoice.payment_failed":
                return self._handle_failed_payment(event.data.object)
            elif event.type == "customer.subscription.updated":
                return self._handle_subscription_updated(event.data.object)
            
            return {"status": "ignored"}
            
        except Exception as e:
            raise ValueError(f"Invalid webhook payload: {str(e)}")
    
    def _handle_successful_payment(self, invoice: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful payment webhook"""
        subscription_id = invoice.get("subscription")
        if subscription_id:
            # Update usage limits based on new subscription
            subscription = self.stripe.Subscription.retrieve(subscription_id)
            tier_name = self._get_tier_name_from_price_id(subscription.items.data[0].price.id)
            usage_tracker.update_tier(subscription.metadata.get("user_id"), tier_name)
        
        return {"status": "success"}
    
    def _handle_failed_payment(self, invoice: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed payment webhook"""
        # Implement retry logic and notification system
        return {"status": "failed"}
    
    def _handle_subscription_updated(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription update webhook"""
        tier_name = self._get_tier_name_from_price_id(subscription.items.data[0].price.id)
        usage_tracker.update_tier(subscription.metadata.get("user_id"), tier_name)
        return {"status": "updated"}
    
    def _get_stripe_price_id(self, tier) -> str:
        """Get Stripe price ID for a tier"""
        # In production, this would map tier names to Stripe price IDs
        # stored in a configuration or database
        price_ids = {
            "free": "price_free",
            "professional": "price_professional",
            "team": "price_team",
            "enterprise": "price_enterprise"
        }
        return price_ids.get(tier.name.lower())
    
    def _get_tier_name_from_price_id(self, price_id: str) -> str:
        """Get tier name from Stripe price ID"""
        # In production, this would map Stripe price IDs to tier names
        # stored in a configuration or database
        tier_names = {
            "price_free": "free",
            "price_professional": "professional",
            "price_team": "team",
            "price_enterprise": "enterprise"
        }
        return tier_names.get(price_id, "free")

# Global instance for use throughout the application
payment_gateway = PaymentGateway(
    stripe_secret_key="your_stripe_secret_key",
    paypal_client_id="your_paypal_client_id",
    paypal_secret="your_paypal_secret"
) 