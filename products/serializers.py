from rest_framework import serializers
from .models import Product, Webhook


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.
    """
    
    class Meta:
        model = Product
        fields = [
            'sku',
            'name',
            'description',
            'active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'sku': {
                'help_text': 'Stock Keeping Unit - must be unique (case-insensitive)',
                'style': {'input_type': 'text'}
            },
            'name': {
                'help_text': 'Product name',
                'style': {'input_type': 'text'}
            },
            'description': {
                'help_text': 'Product description',
                'required': False,
                'allow_blank': True
            },
            'active': {
                'help_text': 'Whether the product is active'
            }
        }
    
    def validate_sku(self, value):
        """Validate SKU - convert to lowercase and check uniqueness."""
        if value:
            value = value.lower().strip()
        
        # Check if SKU already exists (case-insensitive)
        if Product.objects.filter(sku__iexact=value).exists():
            if self.instance and self.instance.sku.lower() == value:
                # Same product, allow update
                pass
            else:
                raise serializers.ValidationError(
                    "Product with this SKU already exists."
                )
        
        return value
    
    def create(self, validated_data):
        """Create a new product with normalized SKU."""
        validated_data['sku'] = validated_data.get('sku', '').lower().strip()
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update a product with normalized SKU."""
        if 'sku' in validated_data:
            validated_data['sku'] = validated_data['sku'].lower().strip()
        return super().update(instance, validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for product list views.
    """
    
    class Meta:
        model = Product
        fields = ['sku', 'name', 'active', 'created_at']
        read_only_fields = ['created_at']


class WebhookSerializer(serializers.ModelSerializer):
    """
    Serializer for the Webhook model.
    """
    
    class Meta:
        model = Webhook
        fields = [
            'id',
            'url',
            'event_type',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'url': {
                'help_text': 'Webhook endpoint URL'
            },
            'event_type': {
                'help_text': 'Event type that triggers this webhook'
            },
            'is_active': {
                'help_text': 'Whether the webhook is active'
            }
        }
    
    def validate(self, attrs):
        """Validate that the combination of url and event_type is unique."""
        url = attrs.get('url')
        event_type = attrs.get('event_type')
        
        if url and event_type:
            queryset = Webhook.objects.filter(url=url, event_type=event_type)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError(
                    "A webhook with this URL and event type already exists."
                )
        
        return attrs