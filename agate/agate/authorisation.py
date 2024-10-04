import requests
from .caching import cache
from core.settings import ONYX_DOMAIN


@cache(time_to_live=3600)
def check_project_authorized(auth, project):
    """
    Boolean telling if a provided authorization token is valid to view a project

    The onyx API is queried to determine which projects the token is permitted to see.
    If the onyx response is not a 200, the token is invalid.
    Otherwise the list of projects is compared against the requested project

    The result is cached (with the decorator) for a period to reduce repeated requests to the onyx API
    """
    route = f"{ONYX_DOMAIN}/projects"
    headers = {"Authorization": auth}
    r = requests.get(route, headers=headers)
    if (not r.status_code == 200):
        return False
    for a in r.json()["data"]:
        if a["project"] == project:
            return True
    return False


@cache(time_to_live=3600)
def find_site(auth):
    """
    String telling which site a provided authorization token originates from

    The onyx API is queried to determine the profile of the token.
    If the onyx response is not a 200, the token is invalid, and the empty sting is returned.
    Otherwise site is returned

    The result is cached (with the decorator) for a period to reduce repeated requests to the onyx API
    """
    route = f"{ONYX_DOMAIN}/accounts/profile"
    headers = {"Authorization": auth}
    r = requests.get(route, headers=headers)
    if (not r.status_code == 200):
        return ''
    return r.json()["data"]["site"]


@cache
def check_authorized(auth, site, project):
    """
    Boolean telling whether a provided authorization token BOTH
    + Originates from the site
    + Is authorized to view the project

    The result is cached (with the decorator) for a period because it is expected that the same user will make regular
    calls, each of which would otherwise need re-validation
    """
    return (find_site(auth) == site) and (check_project_authorized(auth, project))
