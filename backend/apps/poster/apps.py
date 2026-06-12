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
        import os
        import sys

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

        # For gunicorn/uwsgi/worker/runapscheduler: RUN_MAIN is not set,
        # but we skip the runserver guard above and start the scheduler directly.

        from .scheduler import start_scheduler
        try:
            start_scheduler()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to start scheduler: {e}")
