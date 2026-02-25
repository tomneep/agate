import json
from datetime import timedelta
from unittest.mock import Mock, patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from agate.authorisation import check_authorized, check_project_authorized, find_site
from core.local_settings import ONYX_DOMAIN


class AuthTestCase(TestCase):

    @staticmethod
    def mock_onyx_request(url, *args, **kwargs):

        if url == f"{ONYX_DOMAIN}/projects":
            response = Mock()
            response.status_code = 200
            response.text = json.dumps({"data": [{"project": "test_project"}]})
            return response

        if url == f"{ONYX_DOMAIN}/accounts/profile":
            response = Mock()
            response.status_code = 200
            response.json.return_value = {"data": {"site": "test_site"}}
            return response

        raise ValueError(f"Unexpected URL: {url}")

    def test_good_requests(self):

        with patch("requests.get", side_effect=self.mock_onyx_request) as mocked:
            auth = "token"
            site = find_site(auth)
            self.assertEqual(site, "test_site")
            # `requests.get` should now have been called twice (once
            # for projects and once for profile)
            self.assertEqual(mocked.call_count, 2)

            check_project_authorized(auth, "test_project")
            # `requests.get` should still have only been called twice,
            # since there is a token cache that stores the results
            self.assertEqual(mocked.call_count, 2)

            # Check both project and site together
            check_authorized(auth, "test_site", "test_project")
            # `requests.get` should still have only been called twice,
            # since there is a token cache that stores the results
            self.assertEqual(mocked.call_count, 2)

            # A request to a project that we don't have access to
            # should raise PermissionDenied
            with self.assertRaises(PermissionDenied):
                check_project_authorized(auth, "bad_project")
            # And here too, it should still only be twice
            self.assertEqual(mocked.call_count, 2)

            # Go into the future 2 hours!
            fixed_dt = timezone.now() + timedelta(hours=2)
            with patch("django.utils.timezone.now", return_value=fixed_dt):
                find_site(auth)

            # Now that we've gone into the future two hours, the cache
            # becomes invalidated (after 1 hour) and so two new calls
            # should be made to `requests.get`
            self.assertEqual(mocked.call_count, 4)
