import json
from django.test import TestCase
from agate.queue_reading.ingestion_updater import IngestionUpdater, IngestionAttempt

inbound_matched_example = """{
   "uuid":"4d35e1bf-44f9-4901-a8c6-b4751746a722",
   "site":"synthscape",
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

inbound_to_validate_example = """{
  "uuid": "4d35e1bf-44f9-4901-a8c6-b4751746a722",
  "site": "gosh",
  "raw_site": "gosh.mscape",
  "uploaders": [
    "bryn-gosh-mscape"
  ],
  "match_timestamp": 1729590295622335200,
  "artifact": "mscape|11|0e324158-b7a6-4dc1-9891-b63a16f4db5b",
  "run_index": "11",
  "run_id": "0e324158-b7a6-4dc1-9891-b63a16f4db5b",
  "project": "mscape",
  "platform": "ont",
  "files": {
    ".csv": {
      "uri": "s3://mscape-gosh.mscape-ont-prod/mscape.11.0e324158-b7a6-4dc1-9891-b63a16f4db5b.csv",
      "etag": "1db51024e42066aa2735fa2e6425f296",
      "key": "mscape.11.0e324158-b7a6-4dc1-9891-b63a16f4db5b.csv",
      "submitter": "bryn-gosh-mscape",
      "parsed_fname": {
        "project": "mscape",
        "run_index": "11",
        "run_id": "0e324158-b7a6-4dc1-9891-b63a16f4db5b",
        "ftype": "csv"
      }
    },
    ".fastq.gz": {
      "uri": "s3://mscape-gosh.mscape-ont-prod/mscape.11.0e324158-b7a6-4dc1-9891-b63a16f4db5b.fastq.gz",
      "etag": "8ef29ded2e7a6712072768fd6cf9ce4f-31",
      "key": "mscape.11.0e324158-b7a6-4dc1-9891-b63a16f4db5b.fastq.gz",
      "submitter": "bryn-gosh-mscape",
      "parsed_fname": {
        "project": "mscape",
        "run_index": "11",
        "run_id": "0e324158-b7a6-4dc1-9891-b63a16f4db5b",
        "ftype": "fastq",
        "gzip": "gz"
      }
    }
  },
  "test_flag": false,
  "validate": true,
  "onyx_test_create_status": true,
  "biosample_id": "Pos_Control_160524"
}"""

inbound_results_example = """{
  "uuid": "4d35e1bf-44f9-4901-a8c6-b4751746a722",
  "site": "synthscape",
  "raw_site": "synthscape.ukhsa",
  "uploaders": [
    "bryn-synthscape-ukhsa"
  ],
  "match_timestamp": 1727098664533980700,
  "artifact": "synthscape|0|92274db4-3535-47db-b6f6-151354597142",
  "run_index": "0",
  "run_id": "92274db4-3535-47db-b6f6-151354597142",
  "project": "synthscape",
  "platform": "illumina",
  "files": {
    ".1.fastq.gz": {
      "uri": 
      "s3://synthscape-synthscape.ukhsa-illumina-test/synthscape.0.92274db4-3535-47db-b6f6-151354597142.1.fastq.gz",
      "etag": "f667f435136e91b986254d735cee1c13",
      "key": "synthscape.0.92274db4-3535-47db-b6f6-151354597142.1.fastq.gz",
      "submitter": "bryn-synthscape-ukhsa",
      "parsed_fname": {
        "project": "synthscape",
        "run_index": "0",
        "run_id": "92274db4-3535-47db-b6f6-151354597142",
        "direction": "1",
        "ftype": "fastq",
        "gzip": "gz"
      }
    },
    ".2.fastq.gz": {
      "uri": 
      "s3://synthscape-synthscape.ukhsa-illumina-test/synthscape.0.92274db4-3535-47db-b6f6-151354597142.2.fastq.gz",
      "etag": "de2fed484dcad68d50ec6673df6b3670",
      "key": "synthscape.0.92274db4-3535-47db-b6f6-151354597142.2.fastq.gz",
      "submitter": "bryn-synthscape-ukhsa",
      "parsed_fname": {
        "project": "synthscape",
        "run_index": "0",
        "run_id": "92274db4-3535-47db-b6f6-151354597142",
        "direction": "2",
        "ftype": "fastq",
        "gzip": "gz"
      }
    },
    ".csv": {
      "uri": "s3://synthscape-synthscape.ukhsa-illumina-test/synthscape.0.92274db4-3535-47db-b6f6-151354597142.csv",
      "etag": "714c18df9c62b30f70443219467fcba1",
      "key": "synthscape.0.92274db4-3535-47db-b6f6-151354597142.csv",
      "submitter": "bryn-synthscape-ukhsa",
      "parsed_fname": {
        "project": "synthscape",
        "run_index": "0",
        "run_id": "92274db4-3535-47db-b6f6-151354597142",
        "ftype": "csv"
      }
    }
  },
  "test_flag": true,
  "validate": false,
  "onyx_test_create_errors": {
    "site": [
      "Site with code=synthscape does not exist."
    ],
    "iso_region": [
      "Select a valid choice. Perhaps you meant: GB-FAL"
    ]
  }
}"""

inbound_results_passed_example = """{
  "uuid": "4d35e1bf-44f9-4901-a8c6-b4751746a722",
  "site": "gosh",
  "raw_site": "gosh.mscape",
  "uploaders": [
    "bryn-gosh-mscape"
  ],
  "match_timestamp": 1729590295622335200,
  "artifact": "mscape|11|0e324158-b7a6-4dc1-9891-b63a16f4db5b",
  "run_index": "11",
  "run_id": "0e324158-b7a6-4dc1-9891-b63a16f4db5b",
  "project": "mscape",
  "platform": "ont",
  "files": {
    ".csv": {
      "uri": "s3://mscape-gosh.mscape-ont-prod/mscape.11.0e324158-b7a6-4dc1-9891-b63a16f4db5b.csv",
      "etag": "1db51024e42066aa2735fa2e6425f296",
      "key": "mscape.11.0e324158-b7a6-4dc1-9891-b63a16f4db5b.csv",
      "submitter": "bryn-gosh-mscape",
      "parsed_fname": {
        "project": "mscape",
        "run_index": "11",
        "run_id": "0e324158-b7a6-4dc1-9891-b63a16f4db5b",
        "ftype": "csv"
      }
    },
    ".fastq.gz": {
      "uri": "s3://mscape-gosh.mscape-ont-prod/mscape.11.0e324158-b7a6-4dc1-9891-b63a16f4db5b.fastq.gz",
      "etag": "8ef29ded2e7a6712072768fd6cf9ce4f-31",
      "key": "mscape.11.0e324158-b7a6-4dc1-9891-b63a16f4db5b.fastq.gz",
      "submitter": "bryn-gosh-mscape",
      "parsed_fname": {
        "project": "mscape",
        "run_index": "11",
        "run_id": "0e324158-b7a6-4dc1-9891-b63a16f4db5b",
        "ftype": "fastq",
        "gzip": "gz"
      }
    }
  },
  "test_flag": false,
  "validate": true,
  "onyx_test_create_status": true,
  "biosample_id": "Pos_Control_160524",
  "rerun": false,
  "scylla_version": "v1.3.2",
  "anonymised_biosample_id": "B-B94686E620",
  "anonymised_run_id": "R-CD31FB0258",
  "climb_id": "C-D4A3833C93",
  "anonymised_run_index": "RI-09859F9CE7",
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
        attempt = IngestionAttempt.objects.get(uuid="4d35e1bf-44f9-4901-a8c6-b4751746a722")
        self.assertEqual(attempt.uuid, "4d35e1bf-44f9-4901-a8c6-b4751746a722")
        self.assertEqual(attempt.name, "ToBeDecided")
        self.assertEqual(attempt.project, "synthscape")
        self.assertEqual(attempt.platform, "illumina")
        self.assertEqual(attempt.site, "synthscape")
        self.assertEqual(attempt.run_index, "0")
        self.assertEqual(attempt.run_id, "92274db4-3535-47db-b6f6-151354597142")
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
        attempt = IngestionAttempt.objects.get(uuid="4d35e1bf-44f9-4901-a8c6-b4751746a722")
        self.assertEqual(attempt.uuid, "4d35e1bf-44f9-4901-a8c6-b4751746a722")
        self.assertEqual(attempt.name, "ToBeDecided")
        self.assertEqual(attempt.project, "mscape")
        self.assertEqual(attempt.platform, "ont")
        self.assertEqual(attempt.site, "gosh")
        self.assertEqual(attempt.run_index, "11")
        self.assertEqual(attempt.run_id, "0e324158-b7a6-4dc1-9891-b63a16f4db5b")
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
        attempt = IngestionAttempt.objects.get(uuid="4d35e1bf-44f9-4901-a8c6-b4751746a722")
        self.assertEqual(attempt.uuid, "4d35e1bf-44f9-4901-a8c6-b4751746a722")
        self.assertEqual(attempt.name, "ToBeDecided")
        self.assertEqual(attempt.project, "synthscape")
        self.assertEqual(attempt.platform, "illumina")
        self.assertEqual(attempt.site, "synthscape")
        self.assertEqual(attempt.run_index, "0")
        self.assertEqual(attempt.run_id, "92274db4-3535-47db-b6f6-151354597142")
        self.assertEqual(attempt.is_published, False)
        self.assertEqual(attempt.is_test_attempt, True)
        self.assertEqual(attempt.climb_id, "")
        self.assertEqual(attempt.error_message,
                         ("{'site': ['Site with code=synthscape does not exist.'], "
                          "'iso_region': ['Select a valid choice. Perhaps you meant: GB-FAL']}")
                         )
        self.assertEqual(attempt.status, IngestionAttempt.Status.VALIDATIONFAIL)
        self.assertEqual(attempt.archived, False)

    def test_results_passed(self):

        self.assertEqual(IngestionAttempt.objects.count(), 0)

        data = json.loads(inbound_results_passed_example)
        IngestionUpdater.update(data, "inbound-results")

        self.assertEqual(IngestionAttempt.objects.count(), 1)
        attempt = IngestionAttempt.objects.get(uuid="4d35e1bf-44f9-4901-a8c6-b4751746a722")
        self.assertEqual(attempt.uuid, "4d35e1bf-44f9-4901-a8c6-b4751746a722")
        self.assertEqual(attempt.name, "ToBeDecided")
        self.assertEqual(attempt.project, "mscape")
        self.assertEqual(attempt.platform, "ont")
        self.assertEqual(attempt.site, "gosh")
        self.assertEqual(attempt.run_index, "11")
        self.assertEqual(attempt.run_id, "0e324158-b7a6-4dc1-9891-b63a16f4db5b")
        self.assertEqual(attempt.is_published, True)
        self.assertEqual(attempt.is_test_attempt, False)
        self.assertEqual(attempt.climb_id, "C-D4A3833C93")
        self.assertEqual(attempt.error_message, "")
        self.assertEqual(attempt.status, IngestionAttempt.Status.SUCCESS)
        self.assertEqual(attempt.archived, False)


class IngestionUpdateTestCase(TestCase):
    def setUp(self):
        IngestionAttempt.objects.create(
            uuid="4d35e1bf-44f9-4901-a8c6-b4751746a722",
            is_published=False,
            is_test_attempt=False)

    def test_ingestion_attempt_created(self):
        self.assertEqual(IngestionAttempt.objects.count(), 1)
        attempt = IngestionAttempt.objects.get(uuid="4d35e1bf-44f9-4901-a8c6-b4751746a722")
        self.assertEqual(attempt.uuid, "4d35e1bf-44f9-4901-a8c6-b4751746a722")
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
        attempt = IngestionAttempt.objects.get(uuid="4d35e1bf-44f9-4901-a8c6-b4751746a722")
        self.assertEqual(attempt.uuid, "4d35e1bf-44f9-4901-a8c6-b4751746a722")
        self.assertEqual(attempt.name, "ToBeDecided")
        self.assertEqual(attempt.project, "synthscape")
        self.assertEqual(attempt.platform, "illumina")
        self.assertEqual(attempt.site, "synthscape")
        self.assertEqual(attempt.run_index, "0")
        self.assertEqual(attempt.run_id, "92274db4-3535-47db-b6f6-151354597142")
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
        attempt = IngestionAttempt.objects.get(uuid="4d35e1bf-44f9-4901-a8c6-b4751746a722")
        self.assertEqual(attempt.uuid, "4d35e1bf-44f9-4901-a8c6-b4751746a722")
        self.assertEqual(attempt.name, "ToBeDecided")
        self.assertEqual(attempt.project, "mscape")
        self.assertEqual(attempt.platform, "ont")
        self.assertEqual(attempt.site, "gosh")
        self.assertEqual(attempt.run_index, "11")
        self.assertEqual(attempt.run_id, "0e324158-b7a6-4dc1-9891-b63a16f4db5b")
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
        attempt = IngestionAttempt.objects.get(uuid="4d35e1bf-44f9-4901-a8c6-b4751746a722")
        self.assertEqual(attempt.uuid, "4d35e1bf-44f9-4901-a8c6-b4751746a722")
        self.assertEqual(attempt.name, "ToBeDecided")
        self.assertEqual(attempt.project, "synthscape")
        self.assertEqual(attempt.platform, "illumina")
        self.assertEqual(attempt.site, "synthscape")
        self.assertEqual(attempt.run_index, "0")
        self.assertEqual(attempt.run_id, "92274db4-3535-47db-b6f6-151354597142")
        self.assertEqual(attempt.is_published, False)
        self.assertEqual(attempt.is_test_attempt, True)
        self.assertEqual(attempt.climb_id, "")
        self.assertEqual(attempt.error_message,
                         "{'site': ['Site with code=synthscape does not exist.'], \
'iso_region': ['Select a valid choice. Perhaps you meant: GB-FAL']}")
        self.assertEqual(attempt.status, IngestionAttempt.Status.VALIDATIONFAIL)
        self.assertEqual(attempt.archived, False)

    def test_results_passed(self):

        self.assertEqual(IngestionAttempt.objects.count(), 1)

        data = json.loads(inbound_results_passed_example)
        IngestionUpdater.update(data, "inbound-results")

        self.assertEqual(IngestionAttempt.objects.count(), 1)
        attempt = IngestionAttempt.objects.get(uuid="4d35e1bf-44f9-4901-a8c6-b4751746a722")
        self.assertEqual(attempt.uuid, "4d35e1bf-44f9-4901-a8c6-b4751746a722")
        self.assertEqual(attempt.name, "ToBeDecided")
        self.assertEqual(attempt.project, "mscape")
        self.assertEqual(attempt.platform, "ont")
        self.assertEqual(attempt.site, "gosh")
        self.assertEqual(attempt.run_index, "11")
        self.assertEqual(attempt.run_id, "0e324158-b7a6-4dc1-9891-b63a16f4db5b")
        self.assertEqual(attempt.is_published, True)
        self.assertEqual(attempt.is_test_attempt, False)
        self.assertEqual(attempt.climb_id, "C-D4A3833C93")
        self.assertEqual(attempt.error_message, "")
        self.assertEqual(attempt.status, IngestionAttempt.Status.SUCCESS)
        self.assertEqual(attempt.archived, False)
