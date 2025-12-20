"""API views for products."""
import os
import tempfile
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Product, Webhook
from .serializers import ProductSerializer, ProductListSerializer, WebhookSerializer
from .tasks import import_products_task, get_import_progress


# Constants
PAGE_SIZE = 100
MAX_PAGE_SIZE = 1000


class ProductPagination(PageNumberPagination):
    """Standard pagination for products."""
    page_size = PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = MAX_PAGE_SIZE


def error_response(message: str, code: str, http_status: int = status.HTTP_400_BAD_REQUEST):
    """Create a standardized error response."""
    return Response({'error': {'message': message, 'code': code}}, status=http_status)


def success_response(data: dict, http_status: int = status.HTTP_200_OK):
    """Create a standardized success response."""
    return Response({'data': data}, status=http_status)


def get_filtered_products(queryset, params):
    """Apply filters to product queryset."""
    # Active filter
    if active := params.get('active'):
        queryset = queryset.filter(active=active.lower() == 'true')

    # Search filter
    if search := params.get('search'):
        queryset = queryset.filter(Q(sku__icontains=search) | Q(name__icontains=search))

    return queryset


class ProductListCreateView(generics.ListCreateAPIView):
    """List and create products."""
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ProductPagination

    def get_serializer_class(self):
        return ProductListSerializer if self.request.method == 'GET' else ProductSerializer

    def get_queryset(self):
        return get_filtered_products(Product.objects.all(), self.request.query_params)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a product."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'sku'


class WebhookMixin:
    """Common configuration for webhook views."""
    queryset = Webhook.objects.all()
    serializer_class = WebhookSerializer
    permission_classes = [permissions.IsAuthenticated]


class WebhookListCreateView(WebhookMixin, generics.ListCreateAPIView):
    """List and create webhooks."""
    pass


class WebhookDetailView(WebhookMixin, generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a webhook."""
    pass


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_csv(request):
    """Upload CSV file for import."""
    if 'file' not in request.FILES:
        return error_response('No file provided', 'NO_FILE')

    file = request.FILES['file']
    if not file.name.lower().endswith('.csv'):
        return error_response('File must be a CSV', 'INVALID_FILE_TYPE')

    # Save to temp file
    with tempfile.NamedTemporaryFile(mode='wb+', suffix='.csv', delete=False) as temp_file:
        for chunk in file.chunks():
            temp_file.write(chunk)
        temp_file_path = temp_file.name

    try:
        task = import_products_task.delay(temp_file_path)
        return success_response({
            'task_id': task.id,
            'message': 'Import started'
        }, status.HTTP_202_ACCEPTED)
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        return error_response(f'Failed to start import: {str(e)}', 'TASK_START_FAILED',
                             status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def upload_status(request, task_id):
    """Get import status by task_id."""
    try:
        progress_info = get_import_progress(task_id)

        # Determine status code
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR if progress_info['status'] == 'error' \
                     else status.HTTP_200_OK if progress_info['status'] == 'completed' \
                     else status.HTTP_202_ACCEPTED

        return success_response({
            'task_id': task_id,
            'progress': progress_info['progress'],
            'status': progress_info['status'],
            'message': progress_info['message']
        }, status_code)

    except Exception as e:
        return error_response(f'Failed to get status: {str(e)}', 'STATUS_CHECK_FAILED',
                             status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_all_products(request):
    """Delete all products (requires confirmation)."""
    if not request.data.get('confirmed'):
        return error_response(
            'Include {"confirmed": true} to delete all products',
            'CONFIRMATION_REQUIRED'
        )

    count = Product.objects.count()
    if count == 0:
        return success_response({'message': 'No products to delete', 'deleted_count': 0})

    try:
        deleted_count, _ = Product.objects.all().delete()
        return success_response({
            'message': f'Deleted {deleted_count} products',
            'deleted_count': deleted_count
        })
    except Exception as e:
        return error_response(f'Failed to delete products: {str(e)}', 'DELETE_FAILED',
                             status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def product_stats(request):
    """Get product statistics."""
    return success_response({
        'total': Product.objects.count(),
        'active': Product.objects.filter(active=True).count(),
        'inactive': Product.objects.filter(active=False).count(),
    })