"""Celery tasks for the products app."""
import logging
import os
from typing import Dict, List, Any

import pandas as pd
from celery import shared_task
from django.core.cache import cache
from django.db import transaction

from .models import Product

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 3600  # 1 hour
CHUNK_SIZE = 1000
BATCH_SIZE = 500
PROGRESS_KEY = "import_progress_{}"


@shared_task(bind=True, name="products.import_products")
def import_products_task(self, file_path: str) -> Dict[str, Any]:
    """
    Import products from a CSV file using pandas for memory efficiency.

    Args:
        file_path: Path to the CSV file

    Returns:
        Import statistics with counts and any errors
    """
    task_id = self.request.id
    cache.set(PROGRESS_KEY.format(task_id), 0, CACHE_TIMEOUT)

    # Validate file exists
    if not os.path.exists(file_path):
        return _error_result(file_path, task_id, "File not found")

    # Count rows for progress tracking
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            row_count = sum(1 for _ in f) - 1  # Subtract header
    except Exception as e:
        return _error_result(file_path, task_id, f"Failed to read file: {e}")

    if row_count <= 0:
        return _error_result(file_path, task_id, "CSV file is empty")

    results = {"total_rows": row_count, "created": 0, "updated": 0, "errors": [], "task_id": task_id}

    # Get existing SKUs for upsert logic
    existing_skus = set(Product.objects.values_list("sku", flat=True))

    # Process CSV in chunks
    processed = 0
    for chunk_df in pd.read_csv(
        file_path,
        chunksize=CHUNK_SIZE,
        encoding="utf-8",
        dtype=str,
        usecols=lambda x: x.lower() in {"sku", "name", "description", "active"}  # Only load needed columns
    ):
        try:
            created, updated, errors = _process_chunk(chunk_df, existing_skus)
            results["created"] += created
            results["updated"] += updated
            results["errors"].extend(errors)
            processed += len(chunk_df)

            # Update progress
            progress = int((processed / row_count) * 100)
            cache.set(PROGRESS_KEY.format(task_id), progress, CACHE_TIMEOUT)

        except Exception as e:
            results["errors"].append(f"Chunk processing failed: {e}")
            break

    # Finalize
    cache.set(PROGRESS_KEY.format(task_id), 100, CACHE_TIMEOUT)
    logger.info(f"Import complete: {results['created']} created, {results['updated']} updated")

    return results


def _process_chunk(chunk_df: pd.DataFrame, existing_skus: set) -> tuple[int, int, List[str]]:
    """Process a single chunk of CSV data."""
    # Clean data
    chunk_df = chunk_df.fillna("")
    chunk_df.columns = chunk_df.columns.str.str.lower()

    # Validate required columns once
    required = {"sku", "name"}
    if missing := required - set(chunk_df.columns):
        raise ValueError(f"Missing columns: {missing}")

    # Separate creates and updates
    to_create = []
    to_update = []

    for _, row in chunk_df.iterrows():
        sku = str(row["sku"]).strip().lower()
        if not sku:
            continue

        product_data = {
            "sku": sku,
            "name": str(row["name"]).strip(),
            "description": str(row.get("description", "")).strip() or None,
            "active": str(row.get("active", "true")).strip().lower() == "true",
        }

        if sku in existing_skus:
            to_update.append(product_data)
        else:
            to_create.append(product_data)
            existing_skus.add(sku)

    # Bulk operations
    created = _bulk_create(to_create) if to_create else 0
    updated = _bulk_update(to_update) if to_update else 0

    return created, updated, []


def _bulk_create(products_data: List[Dict[str, Any]]) -> int:
    """Create products in bulk."""
    if not products_data:
        return 0

    products = [
        Product(
            sku=data["sku"],
            name=data["name"],
            description=data["description"],
            active=data["active"],
        )
        for data in products_data
    ]

    with transaction.atomic():
        return Product.objects.bulk_create(products, ignore_conflicts=True, batch_size=BATCH_SIZE).__len__()


def _bulk_update(products_data: List[Dict[str, Any]]) -> int:
    """Update products in bulk."""
    if not products_data:
        return 0

    skus = [d["sku"] for d in products_data]
    product_map = {p.sku: p for p in Product.objects.filter(sku__in=skus)}

    to_update = []
    for data in products_data:
        if p := product_map.get(data["sku"]):
            p.name = data["name"]
            p.description = data["description"]
            p.active = data["active"]
            to_update.append(p)

    if to_update:
        with transaction.atomic():
            Product.objects.bulk_update(to_update, ["name", "description", "active"], batch_size=BATCH_SIZE)

    return len(to_update)


def _error_result(file_path: str, task_id: str, message: str) -> Dict[str, Any]:
    """Return a standardized error result."""
    logger.error(f"{message}: {file_path}")
    cache.set(PROGRESS_KEY.format(task_id), -1, CACHE_TIMEOUT)
    return {"total_rows": 0, "created": 0, "updated": 0, "errors": [message], "task_id": task_id}


@shared_task(name="products.get_import_progress")
def get_import_progress(task_id: str) -> Dict[str, Any]:
    """Get import progress from cache."""
    progress = cache.get(PROGRESS_KEY.format(task_id))

    if progress is None:
        return {"progress": 0, "status": "pending", "message": "Task not found"}
    if progress == -1:
        return {"progress": 0, "status": "error", "message": "Import failed"}
    if progress == 100:
        return {"progress": 100, "status": "completed", "message": "Complete"}

    return {"progress": progress, "status": "processing", "message": f"Progress: {progress}%"}