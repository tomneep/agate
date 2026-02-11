import hashlib

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from agate.caching import TokenCache
from agate.models import IngestionAttempt

auth = "my_token"


class IngestionAttemptAPITests(APITestCase):
    def setUp(self):
        # Setup: Create some IngestionAttempt instances for testing
        IngestionAttempt.objects.create(
            uuid="user1",
            is_published=True,
            project="project",
            site="here",
            is_test_attempt=False,
        )
        IngestionAttempt.objects.create(
            uuid="user2",
            is_published=True,
            project="project",
            site="here",
            is_test_attempt=False,
        )

        TokenCache.objects.create(
            projects_output='{"data": [{"project":"project"}]}',
            site_output="here",
            token_hash=hashlib.sha256(auth.encode("utf-8")).hexdigest(),
        )

        # Setup dummy Http Auth
        self.client.credentials(HTTP_AUTHORIZATION=auth)

    def test_unauthorized_access(self):
        # Test if the API correctly denies unauthorized access
        response = self.client.get(reverse("agate:ingestion"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_ingestion_attempts(self):
        # Test if GET returns the list of ingestion attempts
        response = self.client.get(
            reverse("agate:ingestion"), data={"project": "project"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Expecting 2 ingestion attempts (see setUp)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertIsNone(response.data["previous"])
        self.assertIsNone(response.data["next"])

    def test_get_single_ingestion_attempt(self):
        # Test if GET returns the list of ingestion attempts
        response = self.client.get(reverse("agate:single", args=["user1"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["uuid"], "user1")
        self.assertEqual(response.json()["project"], "project")
        self.assertEqual(response.json()["site"], "here")

    def test_archive_ingestion_attempt(self):
        IngestionAttempt.objects.create(
            uuid="user7",
            is_published=True,
            project="project",
            site="here",
            is_test_attempt=False,
        )

        # Check the object exists and is not archived
        response = self.client.get(reverse("agate:single", args=["user7"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.json()["archived"])

        # Archive the project
        response = self.client.get(reverse("agate:archive", args=["user7"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the object exists and is archived
        response = self.client.get(reverse("agate:single", args=["user7"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["archived"])

        # Ensure the object has been archived in the database
        self.assertTrue(IngestionAttempt.objects.filter(uuid="user7")[0].archived)

    def test_delete_ingestion_attempt(self):
        IngestionAttempt.objects.create(
            uuid="user4",
            is_published=True,
            project="project",
            site="here",
            is_test_attempt=False,
        )
        # Check that we can retrieve the object and that it isn't archived
        response = self.client.get(reverse("agate:single", args=["user4"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.json()["archived"])

        # Now delete the object
        response = self.client.get(reverse("agate:delete", args=["user4"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that we can no longer find it (because it has been deleted)
        response = self.client.get(reverse("agate:single", args=["user4"]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_ingestion_attempt_replace_success(self):
        """Test getting an existing record and modifying some field of it."""
        response = self.client.get(reverse("agate:single", args=["user1"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Modify the data slightly and update it
        data = response.json()
        data["run_index"] = 1
        response = self.client.put(reverse("agate:update"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_ingestion_attempt_new_success(self):
        """Test putting a new record (by copying an existing field and changing the UUID."""
        response = self.client.get(reverse("agate:single", args=["user1"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Use exactly the same data but change the uuid so we are creating a new
        # record
        data = response.json()
        data["uuid"] = "user9"
        response = self.client.put(reverse("agate:update"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_ingestion_attempt_bad_data(self):
        """Test that putting bad data returns status code 400."""
        response = self.client.put(reverse("agate:update"), {"bad": "data"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
