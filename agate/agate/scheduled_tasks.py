from apscheduler.schedulers.background import BackgroundScheduler
import logging
import os
from .queue_reader import QueueReader
from varys import Varys

_scheduler = BackgroundScheduler()

_queue_reader = QueueReader(projects=['mscape'], project_sites=['mscape-bham'])

open('varys_test.log', 'w').close()

_varys_client = Varys(
    config_path="varys_config.cfg",
    profile="test",
    logfile="varys_test.log",
    log_level="DEBUG",
    auto_acknowledge=False,
)


def test_task():
    _queue_reader.update(_varys_client)


def start_scheduler():
    """Start our background scheduler."""
    if not (os.environ.get('UWSGI_ORIGINAL_PROC_NAME') or os.environ.get('RUN_MAIN')):
        # UWSGI_ORIGINAL_PROC_NAME => we're running under uwsgi
        # RUN_MAIN => we're in the development server, and the main process
        # Otherwise, don't start the scheduler.
        return

    _scheduler.add_job(test_task, 'interval', seconds=20)
    _scheduler.start()
    logging.info("Started background scheduler")
