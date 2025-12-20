from rest_framework import serializers
from .models import Product, Webhook


class ProductSerializer(serializers.ModelSerializer):
    """Product model serializer."""

    class Meta:
        model = Product
        fields = ['sku', 'name', 'description', 'active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_sku(self, value):
        """Validate SKU uniqueness (case-insensitive)."""
        if not value:
            return value

        value = value.lower().strip()
        qs = Product.objects.filter(sku__iexact=value)

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("Product with this SKU already exists.")

        return value


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight product list serializer."""

    class Meta:
        model = Product
        fields = ['sku', 'name', 'active', 'created_at']
        read_only_fields = ['created_at']


class WebhookSerializer(serializers.ModelSerializer):
    """Webhook model serializer."""

    class Meta:
        model = Webhook
        fields = ['id', 'url', 'event_type', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']