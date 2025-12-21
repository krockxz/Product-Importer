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
        fields = ['id', 'sku', 'name', 'active', 'created_at']
        read_only_fields = ['id', 'created_at']


class WebhookSerializer(serializers.ModelSerializer):
    """Webhook model serializer with event_types array support."""
    event_types = serializers.SerializerMethodField()

    class Meta:
        model = Webhook
        fields = ['id', 'url', 'event_type', 'event_types', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'event_type': {'write_only': True}  # Only used for writes
        }

    def get_event_types(self, obj):
        """Convert single event_type to array for frontend compatibility."""
        return [obj.event_type]

    def to_internal_value(self, data):
        """Handle frontend sending event_types as array."""
        # Convert event_types array to single event_type for the model
        if 'event_types' in data and isinstance(data['event_types'], list) and data['event_types']:
            data['event_type'] = data['event_types'][0]
            data.pop('event_types', None)
        return super().to_internal_value(data)