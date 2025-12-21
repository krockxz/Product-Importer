"""Celery tasks for the products app."""
import logging
import os
from typing import Dict, List, Any

import pandas as pd
import requests
from celery import shared_task
from django.core.cache import cache
from django.db import transaction

from .models import Product

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 3600
CHUNK_SIZE = 1000
BATCH_SIZE = 500
PROGRESS_KEY = "import_progress_{}"


@shared_task(bind=True, name="products.import_products")
def import_products_task(self, file_path: str) -> Dict[str, Any]:
    """Import products from CSV file with progress tracking."""
    task_id = self.request.id
    cache.set(PROGRESS_KEY.format(task_id), 0, CACHE_TIMEOUT)

    if not os.path.exists(file_path):
        return _error_result(task_id, "File not found")

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            row_count = sum(1 for _ in f) - 1
    except Exception as e:
        return _error_result(task_id, f"Failed to read file: {e}")

    if row_count <= 0:
        return _error_result(task_id, "CSV file is empty")

    results = {"total_rows": row_count, "created": 0, "updated": 0, "errors": [], "task_id": task_id}
    processed = 0

    for chunk_df in pd.read_csv(
        file_path,
        chunksize=CHUNK_SIZE,
        encoding="utf-8",
        dtype=str
    ):
        try:
            created, updated = _process_chunk(chunk_df)
            results["created"] += created
            results["updated"] += updated
            processed += len(chunk_df)

            progress = min(int((processed / row_count) * 100), 99)
            cache.set(PROGRESS_KEY.format(task_id), progress, CACHE_TIMEOUT)
            logger.info(f"Progress: {progress}% ({processed}/{row_count})")

        except Exception as e:
            logger.error(f"Chunk processing failed: {e}", exc_info=True)
            results["errors"].append(str(e))
            break

    cache.set(PROGRESS_KEY.format(task_id), 100, CACHE_TIMEOUT)
    logger.info(f"Import complete: {results['created']} created, {results['updated']} updated")

    # Cleanup
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.warning(f"Failed to cleanup file: {e}")

    return results


def _process_chunk(chunk_df: pd.DataFrame) -> tuple[int, int]:
    """Process a single chunk using vectorized pandas operations."""
    # Clean data
    chunk_df = chunk_df.fillna("")
    chunk_df.columns = chunk_df.columns.str.lower()

    if missing := {"sku", "name"} - set(chunk_df.columns):
        raise ValueError(f"Missing required columns: {missing}")

    # Clean SKUs - vectorized
    chunk_df["sku"] = chunk_df["sku"].str.strip().str.lower()
    chunk_df = chunk_df[chunk_df["sku"] != ""]  # Remove empty SKUs

    if len(chunk_df) == 0:
        return 0, 0

    # Get existing SKUs for this chunk
    chunk_skus = chunk_df["sku"].tolist()
    existing_skus = set(Product.objects.filter(sku__in=chunk_skus).values_list("sku", flat=True))

    # Split into creates and updates
    create_mask = ~chunk_df["sku"].isin(existing_skus)
    to_create_df = chunk_df[create_mask].copy()
    to_update_df = chunk_df[~create_mask].copy()

    created = _bulk_create(to_create_df) if len(to_create_df) > 0 else 0
    updated = _bulk_update(to_update_df) if len(to_update_df) > 0 else 0

    return created, updated


def _bulk_create(df: pd.DataFrame) -> int:
    """Create products in bulk from DataFrame."""
    # Ensure we have the active column, fill with default if missing
    if "active" not in df.columns:
        df["active"] = "true"
    
    # Replace NaN with empty strings and prepare data
    df = df.fillna("").copy()
    df["name"] = df["name"].str.strip()
    df["description"] = df["description"].str.strip()
    df["description"] = df["description"].replace("", None)
    
    # Convert active to boolean - handle empty strings as True
    df["active"] = df["active"].str.strip().str.lower().replace("", "true")
    df["active"] = df["active"] == "true"

    products = [
        Product(
            sku=row.sku,
            name=row.name,
            description=row.description,
            active=row.active
        )
        for row in df.itertuples(index=False)
    ]

    with transaction.atomic():
        created = Product.objects.bulk_create(products, ignore_conflicts=True, batch_size=BATCH_SIZE)

    return len(created)


def _bulk_update(df: pd.DataFrame) -> int:
    """Update products in bulk from DataFrame."""
    # Ensure we have the active column, fill with default if missing
    if "active" not in df.columns:
        df["active"] = "true"
    
    # Replace NaN with empty strings and prepare data
    df = df.fillna("").copy()
    df["name"] = df["name"].str.strip()
    df["description"] = df["description"].str.strip()
    df["description"] = df["description"].replace("", None)
    
    # Convert active to boolean - handle empty strings as True
    df["active"] = df["active"].str.strip().str.lower().replace("", "true")
    df["active"] = df["active"] == "true"

    skus = df["sku"].tolist()
    existing_products = {p.sku: p for p in Product.objects.filter(sku__in=skus)}

    to_update = []
    for row in df.itertuples(index=False):
        if product := existing_products.get(row.sku):
            product.name = row.name
            product.description = row.description
            product.active = row.active
            to_update.append(product)

    if to_update:
        with transaction.atomic():
            Product.objects.bulk_update(to_update, ["name", "description", "active"], batch_size=BATCH_SIZE)

    return len(to_update)


def _error_result(task_id: str, message: str) -> Dict[str, Any]:
    """Return standardized error result."""
    logger.error(message)
    cache.set(PROGRESS_KEY.format(task_id), -1, CACHE_TIMEOUT)
    return {"total_rows": 0, "created": 0, "updated": 0, "errors": [message], "task_id": task_id}


@shared_task(name="products.get_import_progress")
def get_import_progress(task_id: str) -> Dict[str, Any]:
    """
    Get import progress from cache with fallback to Celery task state.
    
    Returns standard format: {'progress': int, 'status': str, 'message': str}
    """
    from celery.result import AsyncResult
    
    # Fast path: Check cache
    progress = cache.get(PROGRESS_KEY.format(task_id))
    if progress is not None:
        return _format_cache_status(progress)

    # Slow path: Check Celery state (cache expired or not started)
    try:
        return _get_celery_task_status(task_id)
    except Exception as e:
        logger.error(f"Failed to get task status for {task_id}: {e}")
        return {"progress": 0, "status": "error", "message": "Unable to fetch task status"}


def _format_cache_status(progress: int) -> Dict[str, Any]:
    """Format status from simple cache integer."""
    if progress == -1:
        return {"progress": 0, "status": "error", "message": "Import failed"}
    if progress == 100:
        return {"progress": 100, "status": "completed", "message": "Import complete"}
    return {"progress": progress, "status": "processing", "message": f"Processing: {progress}%"}


def _get_celery_task_status(task_id: str) -> Dict[str, Any]:
    """Resolve status from Celery AsyncResult."""
    from celery.result import AsyncResult
    result = AsyncResult(task_id)
    state = result.state

    if state == 'SUCCESS':
        res = result.result or {}
        return {
            "progress": 100,
            "status": "completed",
            "message": f"Import complete: {res.get('created', 0)} created, {res.get('updated', 0)} updated"
        }
    
    state_messages = {
        'PENDING': "Task queued",
        'STARTED': "Starting import...",
        'RETRY': "Retrying import...",
        'REVOKED': "Import cancelled",
    }
    
    if state == 'FAILURE':
        return {"progress": 0, "status": "failed", "message": f"Import failed: {result.info}"}
        
    return {
        "progress": 0,
        "status": "processing" if state in ['STARTED', 'RETRY'] else "failed" if state == 'REVOKED' else "pending",
        "message": state_messages.get(state, f"Task state: {state}")
    }


@shared_task(name="products.trigger_webhook", max_retries=3, autoretry_for=(Exception,), retry_backoff=True)
def trigger_webhook(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Trigger a webhook with the given payload."""
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Product-Importer-Webhook/1.0"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()

        logger.info(f"Webhook sent successfully to {url}, status: {response.status_code}")
        return {
            "success": True,
            "status_code": response.status_code,
            "response": response.text[:500]
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send webhook to {url}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }