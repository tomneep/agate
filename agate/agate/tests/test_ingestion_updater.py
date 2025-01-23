import json
from django.test import TestCase
from agate.queue_reading.ingestion_updater import IngestionUpdater, IngestionAttempt

inbound_matched_example = """{
   "uuid":"00e37b53-7c0f-4fd5-9515-cd1b00ec4818",
   "site":"synthscape",
   "run_index":"0",
   "run_id":"97abbef9-20b7-441f-b929-886c602059e6",
   "project":"synthscape",
   "platform":"illumina",
   "test_flag":true
}"""

inbound_to_validate_example = """{
  "uuid": "00e37b53-7c0f-4fd5-9515-cd1b00ec4818",
  "site": "wales",
  "run_index": "11",
  "run_id": "a11598f1-56af-44fb-8906-a48aa6a2638c",
  "project": "mscape",
  "platform": "ont",
  "test_flag": false,
  "validate": true,
  "onyx_test_create_status": true,
  "biosample_id": "Pos_Control_160524"
}"""

inbound_results_example = """{
  "uuid": "00e37b53-7c0f-4fd5-9515-cd1b00ec4818",
  "site": "house",
  "run_index": "0",
  "run_id": "90c53bb2-92bb-40a6-b975-c195fae96279",
  "project": "synthscape",
  "platform": "illumina",
  "test_flag": true,
  "validate": false,
  "onyx_test_create_errors": {
    "site": [
      "Site with code=house does not exist."
    ],
    "iso_region": [
      "Select a valid choice. Perhaps you meant: GB-FAL"
    ]
  }
}"""

inbound_results_passed_example = """{
  "uuid": "00e37b53-7c0f-4fd5-9515-cd1b00ec4818",
  "site": "paris",
  "run_index": "11",
  "run_id": "0e324158-b7a6-4dc1-9891-b63a16f4db5b",
  "project": "mscape",
  "platform": "ont",
  "test_flag": false,
  "validate": true,
  "onyx_test_create_status": true,
  "rerun": false,
  "scylla_version": "v1.3.2",
  "climb_id": "A-GH3A9993FAKE",
  "onyx_create_status": true,
  "created": true,
  "published": true
}"""

inbound_new_artifact_example = """{
  "publish_timestamp": 1729590886133615000,
  "climb_id": "C-D4A3833C93",
  "run_id": "R-CD31FB0258",
  "run_index": "RI-09859F9CE7",
  "biosample_id": "B-B94686E620",
  "site": "gosh",
  "platform": "ont",
  "match_uuid": "21913b43-8b1e-42ac-90d6-d3eb7d3dd5ea",
  "project": "mscape"
}"""


class IngestionCreateTestCase(TestCase):

    def test_inbound_matched(self):

        self.assertEqual(IngestionAttempt.objects.count(), 0)

        data = json.loads(inbound_matched_example)
        IngestionUpdater.update(data, "inbound-matched")

        self.assertEqual(IngestionAttempt.objects.count(), 1)
        attempt = IngestionAttempt.objects.get(uuid="00e37b53-7c0f-4fd5-9515-cd1b00ec4818")
        self.assertEqual(attempt.uuid, "00e37b53-7c0f-4fd5-9515-cd1b00ec4818")
        self.assertEqual(attempt.name, "ToBeDecided")
        self.assertEqual(attempt.project, "synthscape")
        self.assertEqual(attempt.platform, "illumina")
        self.assertEqual(attempt.site, "synthscape")
        self.assertEqual(attempt.run_index, "0")
        self.assertEqual(attempt.run_id, "97abbef9-20b7-441f-b929-886c602059e6")
        self.assertEqual(attempt.is_published, False)
        self.assertEqual(attempt.is_test_attempt, True)
        self.assertEqual(attempt.climb_id, "")
        self.assertEqual(attempt.error_message, "")
        self.assertEqual(attempt.status, IngestionAttempt.Status.METADATA)
        self.assertEqual(attempt.archived, False)

    def test_to_validate(self):

        self.assertEqual(IngestionAttempt.objects.count(), 0)

        data = json.loads(inbound_to_validate_example)
        IngestionUpdater.update(data, "inbound-to-validate")

        self.assertEqual(IngestionAttempt.objects.count(), 1)
        attempt = IngestionAttempt.objects.get(uuid="00e37b53-7c0f-4fd5-9515-cd1b00ec4818")
        self.assertEqual(attempt.uuid, "00e37b53-7c0f-4fd5-9515-cd1b00ec4818")
        self.assertEqual(attempt.name, "ToBeDecided")
        self.assertEqual(attempt.project, "mscape")
        self.assertEqual(attempt.platform, "ont")
        self.assertEqual(attempt.site, "wales")
        self.assertEqual(attempt.run_index, "11")
        self.assertEqual(attempt.run_id, "a11598f1-56af-44fb-8906-a48aa6a2638c")
        self.assertEqual(attempt.is_published, False)
        self.assertEqual(attempt.is_test_attempt, False)
        self.assertEqual(attempt.climb_id, "")
        self.assertEqual(attempt.error_message, "")
        self.assertEqual(attempt.status, IngestionAttempt.Status.VALIDATION)
        self.assertEqual(attempt.archived, False)

    def test_inbound_results(self):

        self.assertEqual(IngestionAttempt.objects.count(), 0)

        data = json.loads(inbound_results_example)
        IngestionUpdater.update(data, "inbound-results")

        self.assertEqual(IngestionAttempt.objects.count(), 1)
        attempt = IngestionAttempt.objects.get(uuid="00e37b53-7c0f-4fd5-9515-cd1b00ec4818")
        self.assertEqual(attempt.uuid, "00e37b53-7c0f-4fd5-9515-cd1b00ec4818")
        self.assertEqual(attempt.name, "ToBeDecided")
        self.assertEqual(attempt.project, "synthscape")
        self.assertEqual(attempt.platform, "illumina")
        self.assertEqual(attempt.site, "house")
        self.assertEqual(attempt.run_index, "0")
        self.assertEqual(attempt.run_id, "90c53bb2-92bb-40a6-b975-c195fae96279")
        self.assertEqual(attempt.is_published, False)
        self.assertEqual(attempt.is_test_attempt, True)
        self.assertEqual(attempt.climb_id, "")
        self.assertEqual(attempt.error_message,
                         ("{'site': ['Site with code=house does not exist.'], "
                          "'iso_region': ['Select a valid choice. Perhaps you meant: GB-FAL']}")
                         )
        self.assertEqual(attempt.status, IngestionAttempt.Status.VALIDATIONFAIL)
        self.assertEqual(attempt.archived, False)

    def test_results_passed(self):

        self.assertEqual(IngestionAttempt.objects.count(), 0)

        data = json.loads(inbound_results_passed_example)
        IngestionUpdater.update(data, "inbound-results")

        self.assertEqual(IngestionAttempt.objects.count(), 1)
        attempt = IngestionAttempt.objects.get(uuid="00e37b53-7c0f-4fd5-9515-cd1b00ec4818")
        self.assertEqual(attempt.uuid, "00e37b53-7c0f-4fd5-9515-cd1b00ec4818")
        self.assertEqual(attempt.name, "ToBeDecided")
        self.assertEqual(attempt.project, "mscape")
        self.assertEqual(attempt.platform, "ont")
        self.assertEqual(attempt.site, "paris")
        self.assertEqual(attempt.run_index, "11")
        self.assertEqual(attempt.run_id, "0e324158-b7a6-4dc1-9891-b63a16f4db5b")
        self.assertEqual(attempt.is_published, True)
        self.assertEqual(attempt.is_test_attempt, False)
        self.assertEqual(attempt.climb_id, "A-GH3A9993FAKE")
        self.assertEqual(attempt.error_message, "")
        self.assertEqual(attempt.status, IngestionAttempt.Status.SUCCESS)
        self.assertEqual(attempt.archived, False)


class IngestionUpdateTestCase(TestCase):
    def setUp(self):
        IngestionAttempt.objects.create(
            uuid="00e37b53-7c0f-4fd5-9515-cd1b00ec4818",
            is_published=False,
            is_test_attempt=False)

    def test_ingestion_attempt_created(self):
        self.assertEqual(IngestionAttempt.objects.count(), 1)
        attempt = IngestionAttempt.objects.get(uuid="00e37b53-7c0f-4fd5-9515-cd1b00ec4818")
        self.assertEqual(attempt.uuid, "00e37b53-7c0f-4fd5-9515-cd1b00ec4818")
        self.assertEqual(attempt.name, "")
        self.assertEqual(attempt.project, "")
        self.assertEqual(attempt.platform, "")
        self.assertEqual(attempt.site, "")
        self.assertEqual(attempt.run_index, "")
        self.assertEqual(attempt.run_id, "")
        self.assertEqual(attempt.is_published, False)
        self.assertEqual(attempt.is_test_attempt, False)
        self.assertEqual(attempt.climb_id, "")
        self.assertEqual(attempt.error_message, "")
        self.assertEqual(attempt.status, IngestionAttempt.Status.UNSTARTED)
        self.assertEqual(attempt.archived, False)

    def test_inbound_matched(self):

        self.assertEqual(IngestionAttempt.objects.count(), 1)

        data = json.loads(inbound_matched_example)
        IngestionUpdater.update(data, "inbound-matched")

        self.assertEqual(IngestionAttempt.objects.count(), 1)
        attempt = IngestionAttempt.objects.get(uuid="00e37b53-7c0f-4fd5-9515-cd1b00ec4818")
        self.assertEqual(attempt.uuid, "00e37b53-7c0f-4fd5-9515-cd1b00ec4818")
        self.assertEqual(attempt.name, "ToBeDecided")
        self.assertEqual(attempt.project, "synthscape")
        self.assertEqual(attempt.platform, "illumina")
        self.assertEqual(attempt.site, "synthscape")
        self.assertEqual(attempt.run_index, "0")
        self.assertEqual(attempt.run_id, "97abbef9-20b7-441f-b929-886c602059e6")
        self.assertEqual(attempt.is_published, False)
        self.assertEqual(attempt.is_test_attempt, True)
        self.assertEqual(attempt.climb_id, "")
        self.assertEqual(attempt.error_message, "")
        self.assertEqual(attempt.status, IngestionAttempt.Status.METADATA)
        self.assertEqual(attempt.archived, False)

    def test_to_validate(self):

        self.assertEqual(IngestionAttempt.objects.count(), 1)

        data = json.loads(inbound_to_validate_example)
        IngestionUpdater.update(data, "inbound-to-validate")

        self.assertEqual(IngestionAttempt.objects.count(), 1)
        attempt = IngestionAttempt.objects.get(uuid="00e37b53-7c0f-4fd5-9515-cd1b00ec4818")
        self.assertEqual(attempt.uuid, "00e37b53-7c0f-4fd5-9515-cd1b00ec4818")
        self.assertEqual(attempt.name, "ToBeDecided")
        self.assertEqual(attempt.project, "mscape")
        self.assertEqual(attempt.platform, "ont")
        self.assertEqual(attempt.site, "wales")
        self.assertEqual(attempt.run_index, "11")
        self.assertEqual(attempt.run_id, "a11598f1-56af-44fb-8906-a48aa6a2638c")
        self.assertEqual(attempt.is_published, False)
        self.assertEqual(attempt.is_test_attempt, False)
        self.assertEqual(attempt.climb_id, "")
        self.assertEqual(attempt.error_message, "")
        self.assertEqual(attempt.status, IngestionAttempt.Status.VALIDATION)
        self.assertEqual(attempt.archived, False)

    def test_inbound_results(self):

        self.assertEqual(IngestionAttempt.objects.count(), 1)

        data = json.loads(inbound_results_example)
        IngestionUpdater.update(data, "inbound-results")

        self.assertEqual(IngestionAttempt.objects.count(), 1)
        attempt = IngestionAttempt.objects.get(uuid="00e37b53-7c0f-4fd5-9515-cd1b00ec4818")
        self.assertEqual(attempt.uuid, "00e37b53-7c0f-4fd5-9515-cd1b00ec4818")
        self.assertEqual(attempt.name, "ToBeDecided")
        self.assertEqual(attempt.project, "synthscape")
        self.assertEqual(attempt.platform, "illumina")
        self.assertEqual(attempt.site, "house")
        self.assertEqual(attempt.run_index, "0")
        self.assertEqual(attempt.run_id, "90c53bb2-92bb-40a6-b975-c195fae96279")
        self.assertEqual(attempt.is_published, False)
        self.assertEqual(attempt.is_test_attempt, True)
        self.assertEqual(attempt.climb_id, "")
        self.assertEqual(attempt.error_message,
                         "{'site': ['Site with code=house does not exist.'], \
'iso_region': ['Select a valid choice. Perhaps you meant: GB-FAL']}")
        self.assertEqual(attempt.status, IngestionAttempt.Status.VALIDATIONFAIL)
        self.assertEqual(attempt.archived, False)

    def test_results_passed(self):

        self.assertEqual(IngestionAttempt.objects.count(), 1)

        data = json.loads(inbound_results_passed_example)
        IngestionUpdater.update(data, "inbound-results")

        self.assertEqual(IngestionAttempt.objects.count(), 1)
        attempt = IngestionAttempt.objects.get(uuid="00e37b53-7c0f-4fd5-9515-cd1b00ec4818")
        self.assertEqual(attempt.uuid, "00e37b53-7c0f-4fd5-9515-cd1b00ec4818")
        self.assertEqual(attempt.name, "ToBeDecided")
        self.assertEqual(attempt.project, "mscape")
        self.assertEqual(attempt.platform, "ont")
        self.assertEqual(attempt.site, "paris")
        self.assertEqual(attempt.run_index, "11")
        self.assertEqual(attempt.run_id, "0e324158-b7a6-4dc1-9891-b63a16f4db5b")
        self.assertEqual(attempt.is_published, True)
        self.assertEqual(attempt.is_test_attempt, False)
        self.assertEqual(attempt.climb_id, "A-GH3A9993FAKE")
        self.assertEqual(attempt.error_message, "")
        self.assertEqual(attempt.status, IngestionAttempt.Status.SUCCESS)
        self.assertEqual(attempt.archived, False)
