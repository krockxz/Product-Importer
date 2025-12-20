from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('stats/', views.product_stats, name='product-stats'),
    path('', views.ProductListCreateView.as_view(), name='product-list-create'),
    path('<sku>/', views.ProductDetailView.as_view(), name='product-detail'),
]