from django.contrib import admin
from .models import Product, Webhook


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model."""
    
    list_display = ['sku', 'name', 'active', 'created_at', 'updated_at']
    list_filter = ['active', 'created_at', 'updated_at']
    search_fields = ['sku', 'name', 'description']
    list_editable = ['active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('sku', 'name', 'description')
        }),
        ('Status', {
            'fields': ('active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['sku']
    
    def get_search_results(self, request, queryset, search_term):
        """Make SKU search case-insensitive."""
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            # Add case-insensitive SKU search
            queryset |= self.model.objects.filter(sku__icontains=search_term)
        return queryset, use_distinct


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    """Admin configuration for Webhook model."""
    
    list_display = ['event_type', 'url', 'is_active', 'created_at', 'updated_at']
    list_filter = ['event_type', 'is_active', 'created_at']
    search_fields = ['url']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Webhook Configuration', {
            'fields': ('url', 'event_type', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['event_type', 'url']