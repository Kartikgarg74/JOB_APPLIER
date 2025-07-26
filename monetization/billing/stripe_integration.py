import stripe
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import os
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class BillingConfig(BaseModel):
    stripe_secret_key: str
    stripe_publishable_key: str
    currency: str = "usd"
    webhook_secret: Optional[str] = None

class StripeBilling:
    """
    Handles Stripe billing integration for MCP services.
    """

    def __init__(self, config: BillingConfig):
        self.config = config
        stripe.api_key = config.stripe_secret_key
        self.currency = config.currency

    async def create_customer(self, email: str, name: str) -> str:
        """
        Create a new Stripe customer.

        Args:
            email: Customer email
            name: Customer name

        Returns:
            Stripe customer ID
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={"source": "mcp_service"}
            )
            logger.info(f"Created Stripe customer: {customer.id}")
            return customer.id
        except Exception as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise

    async def create_payment_intent(self, customer_id: str, amount: float, description: str) -> Dict[str, Any]:
        """
        Create a payment intent for immediate charging.

        Args:
            customer_id: Stripe customer ID
            amount: Amount in cents
            description: Payment description

        Returns:
            Payment intent data
        """
        try:
            payment_intent = stripe.PaymentIntent.create(
                customer=customer_id,
                amount=int(amount * 100),  # Convert to cents
                currency=self.currency,
                description=description,
                metadata={"service": "mcp"}
            )
            logger.info(f"Created payment intent: {payment_intent.id}")
            return {
                "id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "amount": amount,
                "status": payment_intent.status
            }
        except Exception as e:
            logger.error(f"Failed to create payment intent: {e}")
            raise

    async def charge_customer(self, customer_id: str, amount: float, description: str) -> Dict[str, Any]:
        """
        Charge a customer immediately.

        Args:
            customer_id: Stripe customer ID
            amount: Amount in dollars
            description: Charge description

        Returns:
            Charge data
        """
        try:
            charge = stripe.Charge.create(
                customer=customer_id,
                amount=int(amount * 100),  # Convert to cents
                currency=self.currency,
                description=description,
                metadata={"service": "mcp", "timestamp": datetime.now().isoformat()}
            )
            logger.info(f"Charged customer {customer_id}: ${amount} for {description}")
            return {
                "id": charge.id,
                "amount": amount,
                "status": charge.status,
                "created": charge.created
            }
        except Exception as e:
            logger.error(f"Failed to charge customer: {e}")
            raise

    async def create_subscription(self, customer_id: str, price_id: str) -> Dict[str, Any]:
        """
        Create a subscription for recurring billing.

        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID

        Returns:
            Subscription data
        """
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                metadata={"service": "mcp"}
            )
            logger.info(f"Created subscription: {subscription.id}")
            return {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end
            }
        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            raise

    async def create_usage_record(self, subscription_item_id: str, quantity: int, timestamp: int) -> Dict[str, Any]:
        """
        Create a usage record for metered billing.

        Args:
            subscription_item_id: Stripe subscription item ID
            quantity: Usage quantity
            timestamp: Unix timestamp

        Returns:
            Usage record data
        """
        try:
            usage_record = stripe.InvoiceItem.create(
                customer=subscription_item_id,
                amount=quantity,
                currency=self.currency,
                timestamp=timestamp
            )
            logger.info(f"Created usage record: {usage_record.id}")
            return {
                "id": usage_record.id,
                "amount": quantity,
                "timestamp": timestamp
            }
        except Exception as e:
            logger.error(f"Failed to create usage record: {e}")
            raise

    async def refund_charge(self, charge_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """
        Refund a charge.

        Args:
            charge_id: Stripe charge ID
            amount: Amount to refund (full amount if None)

        Returns:
            Refund data
        """
        try:
            refund_params = {"charge": charge_id}
            if amount:
                refund_params["amount"] = int(amount * 100)

            refund = stripe.Refund.create(**refund_params)
            logger.info(f"Refunded charge {charge_id}: ${amount or 'full'}")
            return {
                "id": refund.id,
                "amount": refund.amount / 100,
                "status": refund.status
            }
        except Exception as e:
            logger.error(f"Failed to refund charge: {e}")
            raise

    async def get_customer_balance(self, customer_id: str) -> Dict[str, Any]:
        """
        Get customer account balance.

        Args:
            customer_id: Stripe customer ID

        Returns:
            Balance information
        """
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return {
                "balance": customer.balance,
                "currency": customer.currency,
                "delinquent": customer.delinquent
            }
        except Exception as e:
            logger.error(f"Failed to get customer balance: {e}")
            raise

# Example usage and configuration
def get_stripe_config() -> BillingConfig:
    """
    Get Stripe configuration from environment variables.
    """
    return BillingConfig(
        stripe_secret_key=os.getenv("STRIPE_SECRET_KEY", ""),
        stripe_publishable_key=os.getenv("STRIPE_PUBLISHABLE_KEY", ""),
        webhook_secret=os.getenv("STRIPE_WEBHOOK_SECRET")
    )

# Example billing service
class MCPBillingService:
    """
    High-level billing service for MCP services.
    """

    def __init__(self):
        self.stripe = StripeBilling(get_stripe_config())

    async def charge_for_service(self, user_id: str, service: str, amount: float) -> bool:
        """
        Charge a user for using an MCP service.

        Args:
            user_id: User identifier
            service: Service name (e.g., "ats_scoring", "resume_parsing")
            amount: Amount to charge

        Returns:
            Success status
        """
        try:
            # In production, you would look up the customer_id from your database
            customer_id = f"cust_{user_id}"

            await self.stripe.charge_customer(
                customer_id=customer_id,
                amount=amount,
                description=f"MCP {service} service"
            )

            logger.info(f"Successfully charged user {user_id} ${amount} for {service}")
            return True

        except Exception as e:
            logger.error(f"Failed to charge user {user_id} for {service}: {e}")
            return False

    async def create_api_key_subscription(self, user_id: str, tier: str) -> Dict[str, Any]:
        """
        Create a subscription for API key usage.

        Args:
            user_id: User identifier
            tier: Subscription tier (basic, professional, enterprise)

        Returns:
            Subscription data
        """
        try:
            customer_id = f"cust_{user_id}"

            # Map tiers to Stripe price IDs
            price_mapping = {
                "basic": "price_basic_monthly",
                "professional": "price_professional_monthly",
                "enterprise": "price_enterprise_monthly"
            }

            price_id = price_mapping.get(tier, "price_basic_monthly")

            subscription = await self.stripe.create_subscription(
                customer_id=customer_id,
                price_id=price_id
            )

            logger.info(f"Created subscription for user {user_id} on {tier} tier")
            return subscription

        except Exception as e:
            logger.error(f"Failed to create subscription for user {user_id}: {e}")
            raise
