
import requests
import os
from .caching import cache
from core.settings import ONYX_DOMAIN

@cache(time_to_live =3600)
def check_project_authorized(auth, project):
    route = f"{ONYX_DOMAIN}/projects"
    headers = {"Authorization":auth}
    r= requests.get(route, headers=headers)
    if (not r.status_code ==200): return False
    for a in r.json()["data"]:
        if a["project"] == project: return True
    return False


@cache(time_to_live =3600)
def find_site(auth):
    route = f"{ONYX_DOMAIN}/accounts/profile"
    headers = {"Authorization":auth}
    r= requests.get(route, headers=headers)
    if (not r.status_code ==200): return ''
    return r.json()["data"]["site"]



@cache
def check_authorized(auth, site, project):
    return (find_site(auth) == site) and (check_project_authorized( auth, project))