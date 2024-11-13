from django.test import TestCase
from unittest.mock import Mock
from agate.queue_reading.queue_reader import QueueReader
from agate.queue_reading.tracking_models import Project, ProjectSite
from agate.models import IngestionAttempt
from agate.message_retrieval_protocol import MessageRetrievalProtocol

inbound_matched_example = """{
   "uuid":"4d35e1bf-44f9-4901-a8c6-b4751746a722",
   "site":"bham",
   "raw_site":"synthscape.ukhsa",
   "uploaders":[
      "bryn-synthscape-ukhsa"
   ],
   "match_timestamp":1727098664533980741,
   "artifact":"synthscape|0|92274db4-3535-47db-b6f6-151354597142",
   "run_index":"0",
   "run_id":"92274db4-3535-47db-b6f6-151354597142",
   "project":"synthscape",
   "platform":"illumina",
   "files":{
      ".1.fastq.gz":{
         "uri":"s3://synthscape-synthscape.ukhsa-illumina-test/synthscape.0.92274db4-3535-47db-b6f6-151354597142.1.fastq.gz",
         "etag":"f667f435136e91b986254d735cee1c13",
         "key":"synthscape.0.92274db4-3535-47db-b6f6-151354597142.1.fastq.gz",
         "submitter":"bryn-synthscape-ukhsa",
         "parsed_fname":{
            "project":"synthscape",
            "run_index":"0",
            "run_id":"92274db4-3535-47db-b6f6-151354597142",
            "direction":"1",
            "ftype":"fastq",
            "gzip":"gz"
         }
      },
      ".2.fastq.gz":{
         "uri":"s3://synthscape-synthscape.ukhsa-illumina-test/synthscape.0.92274db4-3535-47db-b6f6-151354597142.2.fastq.gz",
         "etag":"de2fed484dcad68d50ec6673df6b3670",
         "key":"synthscape.0.92274db4-3535-47db-b6f6-151354597142.2.fastq.gz",
         "submitter":"bryn-synthscape-ukhsa",
         "parsed_fname":{
            "project":"synthscape",
            "run_index":"0",
            "run_id":"92274db4-3535-47db-b6f6-151354597142",
            "direction":"2",
            "ftype":"fastq",
            "gzip":"gz"
         }
      },
      ".csv":{
         "uri":"s3://synthscape-synthscape.ukhsa-illumina-test/synthscape.0.92274db4-3535-47db-b6f6-151354597142.csv",
         "etag":"714c18df9c62b30f70443219467fcba1",
         "key":"synthscape.0.92274db4-3535-47db-b6f6-151354597142.csv",
         "submitter":"bryn-synthscape-ukhsa",
         "parsed_fname":{
            "project":"synthscape",
            "run_index":"0",
            "run_id":"92274db4-3535-47db-b6f6-151354597142",
            "ftype":"csv"
         }
      }
   },
   "test_flag":true
}"""


class QueueReadingTestCase(TestCase):

    def test_calling_inbound_matched(self):

        self.assertEqual(IngestionAttempt.objects.count(), 0)

        retrieval = Mock()
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

        retrieval = Mock()

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
        ProjectSite.objects.get(key="synthscape-bham")

        retrieval.receive_batch.assert_any_call(
            exchange="inbound-to_validate-synthscape")
        retrieval.receive_batch.assert_any_call(
            exchange="inbound-results-synthscape-bham")

    def test_inbound_matched_injestion_attempt(self):

        self.assertEqual(IngestionAttempt.objects.count(), 0)

        message = Mock()
        message.body = inbound_matched_example

        retrieval = Mock()

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
        attempt = IngestionAttempt.objects.get(uuid="4d35e1bf-44f9-4901-a8c6-b4751746a722")
        self.assertEqual(attempt.uuid, "4d35e1bf-44f9-4901-a8c6-b4751746a722")
        self.assertEqual(attempt.name, "ToBeDecided")
        self.assertEqual(attempt.project, "synthscape")
        self.assertEqual(attempt.platform, "illumina")
        self.assertEqual(attempt.site, "bham")
        self.assertEqual(attempt.run_index, "0")
        self.assertEqual(attempt.run_id, "92274db4-3535-47db-b6f6-151354597142")
        self.assertEqual(attempt.is_published, False)
        self.assertEqual(attempt.is_test_attempt, True)
        self.assertEqual(attempt.climb_id, "")
        self.assertEqual(attempt.error_message, "")
        self.assertEqual(attempt.status, IngestionAttempt.Status.METADATA)
        self.assertEqual(attempt.archived, False)
