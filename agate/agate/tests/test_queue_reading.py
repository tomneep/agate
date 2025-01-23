from django.test import TestCase
from unittest.mock import Mock
from agate.queue_reading.queue_reader import QueueReader
from agate.queue_reading.tracking_models import Project, ProjectSite
from agate.models import IngestionAttempt
from agate.message_retrieval_protocol import MessageRetrievalProtocol

inbound_matched_example = """{
   "uuid":"1fce0ac2-264c-4d43-9894-d4c8e525a20b",
   "site":"pluto",
   "run_index":"0",
   "run_id":"50e53165-a8b7-4c3a-b8cc-2986e653f379",
   "project":"synthscape",
   "platform":"illumina",
   "test_flag":true
}"""


class QueueReadingTestCase(TestCase):

    def test_calling_inbound_matched(self):

        self.assertEqual(IngestionAttempt.objects.count(), 0)

        retrieval: MessageRetrievalProtocol = Mock()
        retrieval.receive_batch = Mock(return_value=[])

        q = QueueReader(retrieval)
        q.update()

        retrieval.receive_batch.assert_any_call(exchange="inbound-matched")

    def test_inbound_matched_project_and_site_updates(self):

        self.assertEqual(IngestionAttempt.objects.count(), 0)
        self.assertEqual(Project.objects.count(), 0)
        self.assertEqual(ProjectSite.objects.count(), 0)

        message = Mock()
        message.body = inbound_matched_example

        retrieval: MessageRetrievalProtocol = Mock()

        def side_effect_func(exchange):
            if exchange == "inbound-matched":
                return [message]
            else:
                return []
        retrieval.receive_batch = Mock(side_effect=side_effect_func)
        retrieval.acknowledge_message = Mock()

        q = QueueReader(retrieval)
        q.update()

        retrieval.receive_batch.assert_any_call(exchange="inbound-matched")
        retrieval.acknowledge_message.assert_any_call(message)

        self.assertEqual(IngestionAttempt.objects.count(), 1)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(ProjectSite.objects.count(), 1)
        Project.objects.get(key="synthscape")
        ProjectSite.objects.get(key="synthscape-pluto")

        retrieval.receive_batch.assert_any_call(
            exchange="inbound-to_validate-synthscape")
        retrieval.receive_batch.assert_any_call(
            exchange="inbound-results-synthscape-pluto")

    def test_inbound_matched_injestion_attempt(self):

        self.assertEqual(IngestionAttempt.objects.count(), 0)

        message = Mock()
        message.body = inbound_matched_example

        retrieval: MessageRetrievalProtocol = Mock()

        def side_effect_func(exchange):
            if exchange == "inbound-matched":
                return [message]
            else:
                return []
        retrieval.receive_batch = Mock(side_effect=side_effect_func)
        retrieval.acknowledge_message = Mock()

        q = QueueReader(retrieval)
        q.update()

        retrieval.receive_batch.assert_any_call(exchange="inbound-matched")
        retrieval.acknowledge_message.assert_any_call(message)

        self.assertEqual(IngestionAttempt.objects.count(), 1)
        attempt = IngestionAttempt.objects.get(uuid="1fce0ac2-264c-4d43-9894-d4c8e525a20b")
        self.assertEqual(attempt.uuid, "1fce0ac2-264c-4d43-9894-d4c8e525a20b")
        self.assertEqual(attempt.name, "ToBeDecided")
        self.assertEqual(attempt.project, "synthscape")
        self.assertEqual(attempt.platform, "illumina")
        self.assertEqual(attempt.site, "pluto")
        self.assertEqual(attempt.run_index, "0")
        self.assertEqual(attempt.run_id, "50e53165-a8b7-4c3a-b8cc-2986e653f379")
        self.assertEqual(attempt.is_published, False)
        self.assertEqual(attempt.is_test_attempt, True)
        self.assertEqual(attempt.climb_id, "")
        self.assertEqual(attempt.error_message, "")
        self.assertEqual(attempt.status, IngestionAttempt.Status.METADATA)
        self.assertEqual(attempt.archived, False)
