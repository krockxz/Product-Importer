from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Product, Webhook


class ProductModelTest(TestCase):
    """Test cases for Product model."""
    
    def setUp(self):
        """Set up test data."""
        self.product = Product.objects.create(
            sku='TEST-001',
            name='Test Product',
            description='A test product',
            active=True
        )
    
    def test_product_creation(self):
        """Test that product can be created."""
        self.assertEqual(self.product.sku, 'test-001')  # Should be lowercase
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.description, 'A test product')
        self.assertTrue(self.product.active)
    
    def test_sku_normalization(self):
        """Test that SKU is normalized to lowercase."""
        product = Product.objects.create(
            sku='MIXED-Case-SKU',
            name='Another Test Product'
        )
        self.assertEqual(product.sku, 'mixed-case-sku')
    
    def test_sku_uniqueness(self):
        """Test that SKU must be unique."""
        with self.assertRaises(Exception):
            Product.objects.create(
                sku='test-001',  # Same as setUp product
                name='Duplicate SKU Product'
            )
    
    def test_case_insensitive_sku_uniqueness(self):
        """Test that SKU uniqueness is case-insensitive."""
        with self.assertRaises(Exception):
            Product.objects.create(
                sku='TEST-001',  # Different case but same SKU
                name='Case Insensitive Duplicate'
            )
    
    def test_product_str_representation(self):
        """Test string representation of product."""
        expected = f"{self.product.sku} - {self.product.name}"
        self.assertEqual(str(self.product), expected)


class WebhookModelTest(TestCase):
    """Test cases for Webhook model."""
    
    def setUp(self):
        """Set up test data."""
        self.webhook = Webhook.objects.create(
            url='https://example.com/webhook',
            event_type=Webhook.WebhookEventType.PRODUCT_CREATED,
            is_active=True
        )
    
    def test_webhook_creation(self):
        """Test that webhook can be created."""
        self.assertEqual(self.webhook.url, 'https://example.com/webhook')
        self.assertEqual(
            self.webhook.event_type,
            Webhook.WebhookEventType.PRODUCT_CREATED
        )
        self.assertTrue(self.webhook.is_active)
    
    def test_webhook_str_representation(self):
        """Test string representation of webhook."""
        expected = f"{self.webhook.event_type} -> {self.webhook.url}"
        self.assertEqual(str(self.webhook), expected)
    
    def test_unique_webhook_constraint(self):
        """Test that webhook URL and event_type combination must be unique."""
        with self.assertRaises(Exception):
            Webhook.objects.create(
                url='https://example.com/webhook',  # Same URL
                event_type=Webhook.WebhookEventType.PRODUCT_CREATED  # Same event
            )
    
    def test_different_event_types_allowed(self):
        """Test that same URL with different event types is allowed."""
        webhook = Webhook.objects.create(
            url='https://example.com/webhook',
            event_type=Webhook.WebhookEventType.PRODUCT_UPDATED
        )
        self.assertEqual(
            webhook.event_type,
            Webhook.WebhookEventType.PRODUCT_UPDATED
        )