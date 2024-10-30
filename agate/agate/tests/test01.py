
from django.test import TestCase
from agate.models import IngestionAttempt    


class IngestionAttemptTestCase(TestCase):
    def setUp(self):
        IngestionAttempt.objects.create(uuid="a")

    def test_ingestion_attempt_created(self):
        attempt = IngestionAttempt.objects.get(uuid="a")
        self.assertEqual(attempt.uuid, "a")
