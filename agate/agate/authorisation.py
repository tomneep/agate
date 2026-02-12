import requests
from .caching import TokenCache
from core.settings import ONYX_DOMAIN
from datetime import timedelta
from django.utils import timezone
import json
import hashlib
from rest_framework.exceptions import PermissionDenied


def check_project_authorized(auth, project):
    """
    Check if the user is allowed to view this project.

    Returns True if a provided authorization token is valid to view a project,
    otherwise raises a `PermissionDenied` exception.

    The onyx API is queried to determine which projects the token is permitted to see.
    If the onyx response is not a 200, the token is invalid.
    Otherwise the list of projects is compared against the requested project
    """
    projects = _get_item(auth).projects_output
    for a in json.loads(projects)["data"]:
        if a["project"] == project:
            return True
    raise PermissionDenied("Not authorised to view this project")


def find_site(auth):
    """
    String telling which site a provided authorization token originates from

    The onyx API is queried to determine the profile of the token.
    If the onyx response is not a 200, the token is invalid, and the empty sting is returned.
    Otherwise site is returned
    """
    return _get_item(auth).site_output


def check_authorized(auth, site, project):
    """
    Boolean telling whether a provided authorization token BOTH
    + Originates from the site
    + Is authorized to view the project
    """
    if find_site(auth) != site:
        raise PermissionDenied("Not authorised to view this site")
    return check_project_authorized(auth, project)


def _get_item(auth):

    time_one_hour_ago = timezone.now() - timedelta(hours=1)
    try:
        token_hash = hashlib.sha256(auth.encode("utf-8")).hexdigest()
        item = TokenCache.objects.get(token_hash=token_hash)
        if item.created_at < time_one_hour_ago:
            item.delete()
        else:
            return item
    except TokenCache.DoesNotExist:
        pass
    return _populate_entry(auth)


def _populate_entry(auth):

    route = f"{ONYX_DOMAIN}/projects"
    headers = {"Authorization": auth}
    r = requests.get(route, headers=headers)
    if (not r.status_code == 200):
        projects = ''
    else:
        projects = r.text

    route = f"{ONYX_DOMAIN}/accounts/profile"
    headers = {"Authorization": auth}
    r = requests.get(route, headers=headers)
    if (not r.status_code == 200):
        site = ''
    else:
        site = r.json()["data"]["site"]

    token_hash = hashlib.sha256(auth.encode("utf-8")).hexdigest()
    item = TokenCache(token_hash=token_hash, projects_output=projects, site_output=site)
    item.save()
    return item
