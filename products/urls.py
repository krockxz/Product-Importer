from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Product endpoints
    path('stats/', views.product_stats, name='product-stats'),
    path('info/', views.api_info, name='api-info'),
    path('', views.ProductListCreateView.as_view(), name='product-list-create'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),  # Changed from sku to pk for bulk delete
    path('bulk-delete/', views.bulk_delete_products, name='bulk-delete-products'),
    path('delete_all/', views.delete_all_products, name='delete-all-products'),

    # Upload endpoints
    path('upload/', views.upload_csv, name='upload-csv'),
    path('upload/status/<str:task_id>/', views.upload_status, name='upload-status'),

    # Webhook endpoints
    path('webhooks/', views.WebhookListCreateView.as_view(), name='webhook-list-create'),
    path('webhooks/<int:pk>/', views.WebhookDetailView.as_view(), name='webhook-detail'),
    path('webhooks/<int:pk>/test/', views.test_webhook, name='test-webhook'),
]