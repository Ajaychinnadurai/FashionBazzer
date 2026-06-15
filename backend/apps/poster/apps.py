"""
Poster app configuration for FashionBazzer.
Initializes the automation scheduler when Django starts.
"""
from django.apps import AppConfig


class PosterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.poster'
    verbose_name = 'Posting & Automation'

    def ready(self):
        """
        Start the automation scheduler when Django is ready.
        Called once when Django starts (dev server, gunicorn, or worker).
        """
        import logging
        import os
        import sys

        logger = logging.getLogger(__name__)

        # Never start scheduler during management commands that touch the DB
        # or during Django's first-pass setup (before the autoreloader kicks in)
        skip_commands = {'migrate', 'makemigrations', 'collectstatic',
                         'createsuperuser', 'flush', 'sqlflush', 'sqlmigrate',
                         'showmigrations', 'test', 'shell', 'dbshell'}

        argv = ' '.join(sys.argv) if hasattr(sys, 'argv') else ''

        # Skip for excluded management commands
        for cmd in skip_commands:
            if f' {cmd}' in argv or argv.startswith(cmd):
                return

        # For dev server (runserver): only start on the second pass (RUN_MAIN=true)
        # The dev server loads the app twice; the first pass doesn't have RUN_MAIN set.
        run_once = os.environ.get('RUN_MAIN', None)
        if 'runserver' in argv:
            if run_once != 'true':
                return
            # Dev server: start scheduler in background
            import threading
            def _start_lazy():
                from .scheduler import start_scheduler
                try:
                    start_scheduler()
                except Exception as e:
                    logger.error(f"Failed to start scheduler: {e}")
            threading.Thread(target=_start_lazy, daemon=True).start()
            return

        # gunicorn/web process: check if we should run scheduler in web process
        if os.environ.get('RUN_SCHEDULER_IN_WEB', 'False').lower() in ('true', '1', 'yes'):
            import threading
            def _start_lazy_web():
                from .scheduler import start_scheduler
                try:
                    start_scheduler()
                except Exception as e:
                    logger.error(f"Failed to start scheduler in web process: {e}")
            threading.Thread(target=_start_lazy_web, daemon=True).start()
            logger.info("Scheduler started in background thread of web process (RUN_SCHEDULER_IN_WEB is enabled).")
            return

        # Otherwise, don't start the scheduler in the web process.
        logger.info(
            "Scheduler not started in web process. "
            "Run 'python manage.py run_scheduler' in a separate worker."
        )
