from apscheduler.schedulers.background import BackgroundScheduler
import logging
import os
from .queue_reading.queue_reader import QueueReader
from datetime import timedelta
from django.utils import timezone
from .caching import TokenCache
from .models import IngestionAttempt
from core.settings import MESSAGE_RETRIEVAL

_scheduler = BackgroundScheduler()

_queue_reader = QueueReader(MESSAGE_RETRIEVAL)


def queue_retrieve_task():
    """
    Task to read the queues and update ingestion attempts accordingly
    """
    _queue_reader.update()


def clear_old_tokens_task():
    """
    Task which will delete TokenCache objects if they were created more than 2 hours ago.
    """
    logging.debug("token clear task")
    TokenCache.objects.filter(created_at__lte=timezone.now()-timedelta(hours=2)).delete()


def clear_old_archived_ingest_attempts_task():
    """
    Task which will delete IngestionAttempt objects either if
    + they have been archived and unmodified for a day
    + they have been unmodified for 28 days
    """
    logging.debug("ingestion clear task")
    IngestionAttempt.objects.filter(archived=True,  updated_at__lte=timezone.now()-timedelta(days=1)).delete()
    IngestionAttempt.objects.filter(updated_at__lte=timezone.now()-timedelta(days=28)).delete()


def start_scheduler():
    """Start our background scheduler."""
    if not (os.environ.get('UWSGI_ORIGINAL_PROC_NAME') or os.environ.get('RUN_MAIN')):
        # UWSGI_ORIGINAL_PROC_NAME => we're running under uwsgi
        # RUN_MAIN => we're in the development server, and the main process
        # Otherwise, don't start the scheduler.
        return

    _scheduler.add_job(queue_retrieve_task, 'interval', seconds=20)
    _scheduler.add_job(clear_old_tokens_task, 'interval', hours=23)
    # _scheduler.add_job(clear_old_archived_ingest_attempts_task, 'interval', hours=23)
    _scheduler.start()
    logging.info("Started background scheduler")
