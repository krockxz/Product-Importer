from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify


class Product(models.Model):
    """
    Product model for storing product information.
    SKU is stored in lowercase for case-insensitive uniqueness.
    """
    class ProductStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
    
    sku = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Stock Keeping Unit - must be unique"
    )
    name = models.CharField(
        max_length=255,
        help_text="Product name"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Product description"
    )
    active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether the product is active"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the product was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time when the product was last updated"
    )

    class Meta:
        db_table = 'products'
        indexes = [
            models.Index(fields=['sku'], name='idx_product_sku'),
            models.Index(fields=['active'], name='idx_product_active'),
            models.Index(fields=['sku', 'active'], name='idx_product_sku_active'),
        ]
        ordering = ['sku']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return f"{self.sku} - {self.name}"

    def save(self, *args, **kwargs):
        """Normalize SKU to lowercase before saving."""
        if self.sku:
            self.sku = self.sku.lower().strip()
        super().save(*args, **kwargs)

    def clean(self):
        """Validate the model data."""
        if self.sku:
            self.sku = self.sku.lower().strip()
        
        if not self.sku:
            raise ValidationError({'sku': 'SKU is required'})
        
        if not self.name:
            raise ValidationError({'name': 'Name is required'})


class Webhook(models.Model):
    """
    Webhook model for storing webhook endpoints.
    """
    class WebhookEventType(models.TextChoices):
        PRODUCT_CREATED = 'product.created', 'Product Created'
        PRODUCT_UPDATED = 'product.updated', 'Product Updated'

    url = models.URLField(
        max_length=500,
        help_text="Webhook endpoint URL"
    )
    event_type = models.CharField(
        max_length=50,
        choices=WebhookEventType.choices,
        help_text="Event type that triggers this webhook"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the webhook is active"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the webhook was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time when the webhook was last updated"
    )

    class Meta:
        db_table = 'webhooks'
        unique_together = ['url', 'event_type']
        indexes = [
            models.Index(fields=['event_type'], name='idx_webhook_event_type'),
            models.Index(fields=['is_active'], name='idx_webhook_is_active'),
            models.Index(fields=['event_type', 'is_active'], name='idx_webhook_event_active'),
        ]
        ordering = ['event_type', 'url']
        verbose_name = 'Webhook'
        verbose_name_plural = 'Webhooks'

    def __str__(self):
        return f"{self.event_type} -> {self.url}"