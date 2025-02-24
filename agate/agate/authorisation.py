import requests
from .caching import TokenCache
from core.settings import ONYX_DOMAIN
from datetime import timedelta
from django.utils import timezone
import json
import hashlib


def check_project_authorized(auth, project):
    """
    Boolean telling if a provided authorization token is valid to view a project

    The onyx API is queried to determine which projects the token is permitted to see.
    If the onyx response is not a 200, the token is invalid.
    Otherwise the list of projects is compared against the requested project
    """
    projects = _get_item(auth).projects_output
    for a in json.loads(projects)["data"]:
        if a["project"] == project:
            return True
    return False


def find_site(auth):
    """
    String telling which site a provided authorization token originates from

    The onyx API is queried to determine the profile of the token.
    If the onyx response is not a 200, the token is invalid, and the empty sting is returned.
    Otherwise site is returned
    """
    return _get_item(auth).site_output


def find_username_hash(auth):
    """
    String telling which site a provided authorization token originates from

    The onyx API is queried to determine the profile of the token.
    If the onyx response is not a 200, the token is invalid, and the empty sting is returned.
    Otherwise site is returned
    """
    return _get_item(auth).username_hash


def check_authorized(auth, site, project):
    """
    Boolean telling whether a provided authorization token BOTH
    + Originates from the site
    + Is authorized to view the project
    """
    return (find_site(auth) == site) and (check_project_authorized(auth, project))


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
        username_hash = ''
    else:
        site = r.json()["data"]["site"]
        username_hash = hashlib.sha256(r.json()["data"]["username"].encode("utf-8")).hexdigest()

    token_hash = hashlib.sha256(auth.encode("utf-8")).hexdigest()
    item = TokenCache(token_hash=token_hash, projects_output=projects, site_output=site, username_hash=username_hash)
    item.save()
    return item
