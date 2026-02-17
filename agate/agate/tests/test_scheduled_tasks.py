import json
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from agate.models import IngestionAttempt
from agate.scheduled_tasks import start_scheduler, clear_old_archived_ingest_attempts_task
from agate.queue_reading.ingestion_updater import IngestionUpdater
from agate.tests.test_ingestion_updater import inbound_matched_example


class SchedulerTestCase(TestCase):

    @patch("agate.scheduled_tasks._scheduler")
    def test_start_scheduler(self, scheduler):
        with patch.dict("os.environ", {"RUN_MAIN": "True"}):
            start_scheduler()
        # Check that we have added something to the scheduler
        scheduler.add_job.assert_called()
        # Check that we started the scheduler
        scheduler.start.assert_called()

    def test_with_data(self):

        self.assertEqual(IngestionAttempt.objects.count(), 0)
        data = json.loads(inbound_matched_example)
        IngestionUpdater.update(data, "inbound-matched")
        # We should now have an entry
        self.assertEqual(IngestionAttempt.objects.count(), 1)

        clear_old_archived_ingest_attempts_task()
        # We should still have an entry, since it was just added
        self.assertEqual(IngestionAttempt.objects.count(), 1)

        # Back to the future
        fixed_dt = timezone.now() + timedelta(days=30)
        with patch("django.utils.timezone.now", return_value=fixed_dt):
            clear_old_archived_ingest_attempts_task()

        # Under the current rules, this should have now been deleted
        self.assertEqual(IngestionAttempt.objects.count(), 0)
