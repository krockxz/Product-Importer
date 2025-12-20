"""Django management command to import products from CSV."""
import os
import time
from django.core.management.base import BaseCommand, CommandError

from products.tasks import import_products_task, get_import_progress


class Command(BaseCommand):
    """Import products from a CSV file using Celery."""

    help = "Import products from a CSV file (async by default, use --sync for synchronous)"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument("file_path", help="Path to the CSV file")
        parser.add_argument("--sync", action="store_true", help="Run synchronously")

    def handle(self, *args, **options):
        """Execute the import command."""
        file_path = os.path.abspath(options["file_path"])

        if not os.path.exists(file_path):
            raise CommandError(f'File "{file_path}" does not exist')

        self.stdout.write(f'Starting import from: "{file_path}"')

        if options["sync"]:
            self._run_sync(file_path)
        else:
            self._run_async(file_path)

    def _run_sync(self, file_path: str):
        """Run import synchronously."""
        self.stdout.write("Running in synchronous mode...")
        result = import_products_task.apply(args=[file_path]).get()

        self.stdout.write(self.style.SUCCESS("\nImport completed!"))
        self.stdout.write(f"Total: {result['total_rows']}, Created: {result['created']}, Updated: {result['updated']}")

        if result["errors"]:
            self.stdout.write(self.style.ERROR(f"\nErrors: {len(result['errors'])}"))
            for error in result["errors"][:5]:
                self.stdout.write(f"  - {error}")

    def _run_async(self, file_path: str):
        """Run import asynchronously with progress monitoring."""
        task = import_products_task.delay(file_path)
        task_id = task.id

        self.stdout.write(f"Task started: {task_id}")
        self.stdout.write("Monitoring progress... (Ctrl+C to detach)")

        try:
            while True:
                progress_info = get_import_progress(task_id)
                status = progress_info["status"]

                if status in ("completed", "error"):
                    self._show_final_status(status)
                    break

                self._show_progress(progress_info["progress"])
                time.sleep(1)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING(f"\nImport continuing in background (task: {task_id})"))

    def _show_progress(self, progress: int):
        """Display progress bar."""
        bar = "█" * (progress // 2) + "-" * (50 - progress // 2)
        self.stdout.write(f"\r|{bar}| {progress}%", ending="")
        self.stdout.flush()

    def _show_final_status(self, status: str):
        """Display final status message."""
        if status == "completed":
            self.stdout.write(self.style.SUCCESS("\n✅ Import completed!"))
        else:
            self.stdout.write(self.style.ERROR("\n❌ Import failed!"))