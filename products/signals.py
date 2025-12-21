"""Django signals for the products app."""
import logging
from typing import Dict, Any

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from .models import Product, Webhook
from .tasks import trigger_webhook

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Product)
def product_post_save(sender, instance: Product, created: bool, **kwargs) -> None:
    """
    Handle product creation/update events and trigger webhooks.

    This signal is triggered after a Product is saved. It queries for active
    webhooks matching the event type and triggers them asynchronously.

    Args:
        sender: The model class (Product)
        instance: The Product instance that was saved
        created: Boolean indicating if this was a new record
        **kwargs: Additional signal arguments
    """
    # Determine the event type
    event_type = "product.created" if created else "product.updated"

    # Skip webhook triggering during bulk operations to avoid excessive calls
    # during CSV imports. The import task can handle bulk webhook triggering
    # separately if needed.
    if getattr(instance, "_skip_webhooks", False):
        return

    # Query active webhooks for this event type
    webhooks = Webhook.objects.filter(
        event_type=event_type,
        is_active=True
    )

    if not webhooks.exists():
        logger.debug(f"No active webhooks found for event: {event_type}")
        return

    # Prepare the payload
    payload = _prepare_webhook_payload(instance, event_type)

    # Trigger webhooks asynchronously
    for webhook in webhooks:
        logger.info(f"Triggering webhook {webhook.url} for product {instance.sku}")
        trigger_webhook.delay(webhook.url, payload)


def _prepare_webhook_payload(product: Product, event_type: str) -> Dict[str, Any]:
    """
    Prepare the webhook payload for a product event.

    Args:
        product: The Product instance
        event_type: The event type (product.created or product.updated)

    Returns:
        Dictionary containing the webhook payload
    """
    return {
        "event": event_type,
        "sku": product.sku,
        "name": product.name,
        "description": product.description,
        "active": product.active,
        "created_at": product.created_at.isoformat(),
        "updated_at": product.updated_at.isoformat(),
        "timestamp": transaction.atomic()  # Use atomic operation for timestamp consistency
    }