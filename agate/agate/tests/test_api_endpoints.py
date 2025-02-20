from rest_framework import status
from rest_framework.test import APITestCase
from agate.models import IngestionAttempt
from agate.caching import TokenCache
import hashlib

auth = "my_token"


class IngestionAttemptAPITests(APITestCase):

    def setUp(self):
        # Setup: Create some IngestionAttempt instances for testing
        IngestionAttempt.objects.create(uuid="user1",
                                        is_published=True,
                                        project="project",
                                        site="here",
                                        is_test_attempt=False)
        IngestionAttempt.objects.create(uuid="user2",
                                        is_published=True,
                                        project="project",
                                        site="here",
                                        is_test_attempt=False)

        TokenCache.objects.create(
            projects_output='{"data": [{"project":"project"}]}',
            site_output="here",
            token_hash=hashlib.sha256(auth.encode("utf-8")).hexdigest()
        )

    def test_unauthorized_access(self):
        # Test if the API correctly denies unauthorized access
        response = self.client.get('/ingestion/')
        print(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_ingestion_attempts(self):
        # Test if GET returns the list of ingestion attempts
        response = self.client.get('/ingestion/?project=project', HTTP_Authorization="my_token")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Expecting 2 ingestion attempts
        self.assertEqual(response.data['previous'], None)
        self.assertEqual(response.data['next'], None)

    def test_get_single_ingestion_attempt(self):
        # Test if GET returns the list of ingestion attempts
        response = self.client.get('/single/user1/', HTTP_Authorization="my_token")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['uuid'], 'user1')
        self.assertEqual(response.json()['project'], 'project')
        self.assertEqual(response.json()['site'], 'here')

    def test_archive_ingestion_attempt(self):
        IngestionAttempt.objects.create(uuid="user7",
                                        is_published=True,
                                        project="project",
                                        site="here",
                                        is_test_attempt=False)
        response = self.client.get('/single/user7/', HTTP_Authorization="my_token")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['archived'], False)
        response = self.client.get('/archive/user7/', HTTP_Authorization="my_token")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get('/single/user7/', HTTP_Authorization="my_token")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['archived'], True)
        # Ensure the object is deleted from the database
        self.assertEqual(IngestionAttempt.objects.filter(uuid="user7")[0].archived, True)

    def test_delete_ingestion_attempt(self):
        IngestionAttempt.objects.create(uuid="user4",
                                        is_published=True,
                                        project="project",
                                        site="here",
                                        is_test_attempt=False)
        response = self.client.get('/single/user4/', HTTP_Authorization="my_token")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['archived'], False)
        response = self.client.get('/delete/user4/', HTTP_Authorization="my_token")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get('/single/user4/', HTTP_Authorization="my_token")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
