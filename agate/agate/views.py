from django.core import serializers
from django.http import JsonResponse, HttpResponse
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from .models import IngestionAttempt
from .forms import IngestionAttemptForm
import requests
from .authorisation import check_project_authorized, find_site, check_authorized
from core.settings import ONYX_DOMAIN


def ingestion_attempt_response(request, project=""):
    auth = request.headers.get("Authorization")
    if (not check_project_authorized(auth, project)):
        return HttpResponse('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
    objs = IngestionAttempt.objects.filter(project=project, site=find_site(auth),
                                           archived=False).order_by('created_at')
    data = serializers.serialize('json', objs)
    return JsonResponse(data, safe=False)


def projects(request):
    route = f"{ONYX_DOMAIN}/projects"
    headers = {"Authorization": request.headers.get("Authorization")}
    r = requests.get(route, headers=headers)
    return HttpResponse(r, status=r.status_code)


def profile(request):
    route = f"{ONYX_DOMAIN}/accounts/profile"
    headers = {"Authorization": request.headers.get("Authorization")}
    r = requests.get(route, headers=headers)
    return HttpResponse(r, status=r.status_code)


@csrf_exempt
def update_ingestion_attempt(request):
    if request.method == 'PUT':
        auth = request.headers.get("Authorization")
        try:
            instance = IngestionAttempt.objects.get(uuid=request.PUT['uuid'])
            if (not check_authorized(auth, instance.site, instance.project)):
                return HttpResponse('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
            form = IngestionAttemptForm(request.PUT, instance=instance)
        except IngestionAttempt.DoesNotExist:
            # IngestionAttempt doesn't exists, so we create a new one
            form = IngestionAttemptForm(request.PUT)
        if form.is_valid():
            if (not check_authorized(auth, form.instance.site, form.instance.project)):
                return HttpResponse('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
            ingestion = form.save()
            return HttpResponse(ingestion.uuid, status=status.HTTP_201_CREATED)
        else:
            return HttpResponse(form.errors, status=status.HTTP_400_BAD_REQUEST)
