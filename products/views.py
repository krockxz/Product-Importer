"""API views for products."""
from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer, ProductListSerializer


class ProductListView(generics.ListCreateAPIView):
    """List and create products."""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Use list serializer for GET requests."""
        return ProductListSerializer if self.request.method == 'GET' else ProductSerializer

    def get_queryset(self):
        """Filter by active status and search term."""
        queryset = Product.objects.all()

        # Active filter
        if active := self.request.query_params.get('active'):
            queryset = queryset.filter(active=active.lower() == 'true')

        # Search filter
        if search := self.request.query_params.get('search'):
            queryset = queryset.filter(Q(sku__icontains=search) | Q(name__icontains=search))

        return queryset


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a product."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'sku'


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def product_stats(request):
    """Get product statistics."""
    stats = {
        'total': Product.objects.count(),
        'active': Product.objects.filter(active=True).count(),
        'inactive': Product.objects.filter(active=False).count(),
    }
    return Response({'data': stats})