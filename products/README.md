# Products App

This app handles product management and webhooks for the Product Importer system.

## Models

### Product Model

The Product model stores product information with the following fields:

- **sku** (CharField, unique, indexed): Stock Keeping Unit
  - Automatically converted to lowercase for case-insensitive uniqueness
  - Maximum length: 100 characters
  - Indexed for fast lookups
  
- **name** (CharField): Product name
  - Maximum length: 255 characters
  
- **description** (TextField, optional): Product description
  - Can be null or blank
  
- **active** (BooleanField, default=True, indexed): Product status
  - Indicates whether the product is active
  - Indexed for filtering
  
- **created_at** (DateTimeField): Auto-populated creation timestamp
- **updated_at** (DateTimeField): Auto-populated update timestamp

**Indexes:**
- idx_product_sku (on sku)
- idx_product_active (on active)
- idx_product_sku_active (composite on sku and active)

### Webhook Model

The Webhook model stores webhook endpoints for event notifications:

- **url** (URLField): Webhook endpoint URL
  - Maximum length: 500 characters
  
- **event_type** (CharField, choices): Event type that triggers the webhook
  - Options: 'product.created', 'product.updated'
  
- **is_active** (BooleanField, default=True): Webhook status
  
- **created_at** (DateTimeField): Auto-populated creation timestamp
- **updated_at** (DateTimeField): Auto-populated update timestamp

**Constraints:**
- Unique combination of url and event_type

**Indexes:**
- idx_webhook_event_type (on event_type)
- idx_webhook_is_active (on is_active)
- idx_webhook_event_active (composite on event_type and is_active)

## API Endpoints

### Product API

All endpoints require authentication (Basic Auth or Session Auth).

#### List/Create Products
- **URL**: `/api/products/`
- **Methods**: 
  - `GET`: List all products (supports pagination)
  - `POST`: Create a new product
  
**Query Parameters (GET)**:
- `active` (boolean): Filter by active status
- `search` (string): Search by SKU or name (case-insensitive)

**Example POST Request**:
```json
{
  "sku": "PROD-123",
  "name": "Product Name",
  "description": "Product description",
  "active": true
}
```

#### Product Detail
- **URL**: `/api/products/<sku>/`
- **Methods**:
  - `GET`: Retrieve product by SKU (case-insensitive)
  - `PUT`: Update product
  - `PATCH`: Partially update product
  - `DELETE`: Delete product

**Note**: SKU lookup is case-insensitive. The SKU will be automatically converted to lowercase.

#### Product Statistics
- **URL**: `/api/products/stats/`
- **Method**: `GET`
- **Response**: Product statistics

**Example Response**:
```json
{
  "total_products": 100,
  "active_products": 75,
  "inactive_products": 25,
  "active_percentage": 75.0
}
```

## Serializers

### ProductSerializer
- Handles full CRUD operations for Product model
- Automatically normalizes SKU to lowercase
- Validates SKU uniqueness (case-insensitive)

### ProductListSerializer
- Lightweight serializer for list views
- Excludes description and updated_at fields for better performance

### WebhookSerializer
- Handles CRUD operations for Webhook model
- Validates unique constraint on url and event_type combination

## Testing

Run tests with:
```bash
docker exec product_importer_web python manage.py test products -v 2
```

## Usage Examples

### Creating a Product
```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46YWRtaW4xMjM=" \
  -d '{
    "sku": "ELEC-001",
    "name": "Smartphone",
    "description": "Latest smartphone model",
    "active": true
  }'
```

### Getting a Product
```bash
# SKU lookup is case-insensitive
curl http://localhost:8000/api/products/ELEC-001/ \
  -H "Authorization: Basic YWRtaW46YWRtaW4xMjM="
```

### Searching Products
```bash
curl "http://localhost:8000/api/products/?search=phone" \
  -H "Authorization: Basic YWRtaW46YWRtaW4xMjM="
```

### Filtering by Active Status
```bash
curl "http://localhost:8000/api/products/?active=false" \
  -H "Authorization: Basic YWRtaW46YWRtaW4xMjM="
```

## Notes

- All SKU values are stored and compared in lowercase
- The SKU field has a unique constraint enforced at the database level
- Timestamp fields are automatically managed
- The API supports pagination for list views