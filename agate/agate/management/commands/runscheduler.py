import logging
from threading import Event

from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run the APscheduler background scheduler"

    def handle(self, *args, **options):
        logger.info("Starting Scheduler")
        # This waits forever (or until the process is stopped), which
        # we want to do while the scheduler runs in the background
        try:
            Event().wait()
        except KeyboardInterrupt:
            logger.info("Scheduler shutting down")
