# This app only includes basic TemplateView generic views.
# These are included in urls.py, within the urlpatterns array.
# This is why this views.py file is empty.


from django.core import serializers
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from .models import *
from .forms import *
import os
import requests
from .authorisation import *


def ingestion_attempt_response(request, project=""):
    auth = request.headers.get("Authorization")
    if (not check_project_authorized(auth, project)):
        return HttpResponse('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
    objs = IngestionAttempt.objects.filter(project=project, site=find_site(auth), archived=False).order_by('created_at')
    data = serializers.serialize('json', objs)
    return JsonResponse(data, safe=False)


def projects(request):
    route = f"{ONYX_DOMAIN}/projects"
    headers = {"Authorization": request.headers.get("Authorization")}
    r = requests.get(route, headers=headers)
    if (not r.status_code == 200): return HttpResponse(r, status=r.status_code)
    return HttpResponse(r)


def profile(request):
    route = f"{ONYX_DOMAIN}/accounts/profile"
    headers = {"Authorization": request.headers.get("Authorization")}
    r = requests.get(route, headers=headers)
    if (not r.status_code == 200): return HttpResponse(r, status=r.status_code)
    return HttpResponse(r)


@csrf_exempt
def create_ingestion_attempt(request):
    if request.method == 'POST':
        auth = request.headers.get("Authorization")
        form = IngestionAttemptForm(request.POST)
        if form.is_valid():
            if (not check_authorized(request, form.instance.site, form.instance.project)):
                return HttpResponse('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
            # create a new `IngestionAttempt` and save it to the db
            ingestion = form.save()
            return HttpResponse(ingestion.uuid, status=status.HTTP_201_CREATED)
        else:
            return HttpResponse(form.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def update_ingestion_attempt(request):
    if request.method == 'POST':
        auth = request.headers.get("Authorization")
        try:
            instance = IngestionAttempt.objects.get(uuid=request.POST['uuid'])
            if (not check_authorized(auth, instance.site, instance.project)):
                return HttpResponse('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
            form = IngestionAttemptForm(request.POST, instance=instance)
        except IngestionAttempt.DoesNotExist:
            # IngestionAttempt doesn't exists, so we create a new one
            form = IngestionAttemptForm(request.POST)
        if form.is_valid():
            if (not check_authorized(auth, form.instance.site, form.instance.project)):
                return HttpResponse('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
            ingestion = form.save()
            return HttpResponse(ingestion.uuid, status=status.HTTP_201_CREATED)
        else:
            return HttpResponse(form.errors, status=status.HTTP_400_BAD_REQUEST)
