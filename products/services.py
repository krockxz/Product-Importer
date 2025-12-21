"""Service layer for webhook operations."""
import logging
from typing import List, Dict, Any, Optional

from django.db import transaction
from django.utils import timezone

from .models import Product, Webhook
from .models import Product, Webhook

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for managing webhook operations."""

    @staticmethod
    def trigger_webhooks_for_products(products: List[Product], created: bool = True) -> None:
        """
        Trigger webhooks for a list of products (bulk operation).

        This method is optimized for bulk operations like CSV imports,
        where triggering individual webhooks for each product would be inefficient.

        Args:
            products: List of Product instances
            created: True if these are newly created products, False if updated
        """
        if not products:
            return

        event_type = "product.created" if created else "product.updated"

        # Group webhooks by event type to minimize database queries
        webhooks = Webhook.objects.filter(
            event_type=event_type,
            is_active=True
        )

        if not webhooks:
            logger.debug(f"No active webhooks found for event: {event_type}")
            return

        # Trigger a webhook task for each webhook with all products
        for webhook in webhooks:
            payload = {
                "event": event_type,
                "timestamp": timezone.now().isoformat(),
                "products": [
                    {
                        "sku": product.sku,
                        "name": product.name,
                        "description": product.description,
                        "active": product.active,
                        "created_at": product.created_at.isoformat(),
                        "updated_at": product.updated_at.isoformat(),
                    }
                    for product in products
                ],
                "count": len(products)
            }

            logger.info(
                f"Triggering bulk webhook {webhook.url} for {len(products)} products "
                f"(event: {event_type})"
            )
            from .tasks import trigger_webhook
            trigger_webhook.delay(webhook.url, payload)

    @staticmethod
    def trigger_webhook_for_product(product: Product, created: bool = True) -> None:
        """
        Trigger webhooks for a single product.

        This is a convenience method that uses the signal handler's logic
        but can be called directly when needed.

        Args:
            product: The Product instance
            created: True if this is a newly created product, False if updated
        """
        event_type = "product.created" if created else "product.updated"

        webhooks = Webhook.objects.filter(
            event_type=event_type,
            is_active=True
        )

        if not webhooks:
            return

        payload = {
            "event": event_type,
            "sku": product.sku,
            "name": product.name,
            "description": product.description,
            "active": product.active,
            "created_at": product.created_at.isoformat(),
            "updated_at": product.updated_at.isoformat(),
            "timestamp": timezone.now().isoformat()
        }

        for webhook in webhooks:
            logger.info(f"Triggering webhook {webhook.url} for product {product.sku}")
            from .tasks import trigger_webhook
            trigger_webhook.delay(webhook.url, payload)

    @staticmethod
    def test_webhook(webhook_url: str, event_type: str = "product.created") -> Dict[str, Any]:
        """
        Test a webhook by sending a sample payload.

        Args:
            webhook_url: The URL to test
            event_type: The event type to simulate

        Returns:
            Result of the webhook test
        """
        sample_payload = {
            "event": event_type,
            "sku": "TEST-SKU-123",
            "name": "Test Product",
            "description": "This is a test product for webhook validation",
            "active": True,
            "created_at": timezone.now().isoformat(),
            "updated_at": timezone.now().isoformat(),
            "timestamp": timezone.now().isoformat(),
            "test": True
        }

        from .tasks import trigger_webhook
        return trigger_webhook(webhook_url, sample_payload)