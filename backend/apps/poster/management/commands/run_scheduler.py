"""
Management command to start the FashionBazzer automation scheduler.
Runs as a long-lived process (Render worker service).
"""
import logging
import time
from django.core.management.base import BaseCommand
from django.db import connection

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Start the FashionBazzer APScheduler and keep it running."

    def handle(self, *args, **options):
        self.stdout.write("Starting FashionBazzer scheduler worker...")

        from apps.poster.scheduler import start_scheduler

        try:
            scheduler = start_scheduler()
            self.stdout.write(self.style.SUCCESS(
                "Scheduler started! 11 jobs registered. "
                "Press Ctrl+C to stop."
            ))

            # Keep the process alive — the scheduler runs in background threads.
            # Poll every 60s and verify the DB connection is still alive.
            try:
                while True:
                    time.sleep(60)
                    # Keep the DB connection healthy
                    connection.ensure_connection()
            except KeyboardInterrupt:
                self.stdout.write("\nShutting down scheduler...")
                if scheduler.running:
                    scheduler.shutdown(wait=False)
                self.stdout.write(self.style.SUCCESS("Scheduler stopped."))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to start scheduler: {e}"))
            raise
