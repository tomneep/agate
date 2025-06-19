from django.core import serializers
from django.http import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from .models import IngestionAttempt
from .forms import IngestionAttemptForm
import requests
from .authorisation import check_project_authorized, find_site, check_authorized
from core.settings import ONYX_DOMAIN

from .serializers import IngestionSerializer
from .pagination import MyCursorPagination
from rest_framework.generics import ListAPIView


class IngestionAPIView(ListAPIView):
    queryset = IngestionAttempt.objects.all()
    serializer_class = IngestionSerializer
    pagination_class = MyCursorPagination

    def get_queryset(self):
        auth = self.request.headers.get("Authorization")
        project_name = self.request.query_params.get("project", None)
        return IngestionAttempt.objects.filter(project=project_name, site=find_site(auth), archived=False)

    def list(self, request, *args, **kwargs):
        auth = request.headers.get("Authorization")
        project_name = request.query_params.get("project", None)
        if (project_name is None) or (not check_project_authorized(auth, project_name)):
            return HttpResponse('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
        return super().list(request, *args, **kwargs)


def single_ingestion_attempt_response(request, uuid=""):
    try:
        obj = IngestionAttempt.objects.get(uuid=uuid)
    except IngestionAttempt.DoesNotExist:
        return HttpResponse('Not found', status=status.HTTP_404_NOT_FOUND)

    auth = request.headers.get("Authorization")
    if not check_authorized(auth, obj.site, obj.project):
        return HttpResponse('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
    data = serializers.serialize('json', obj)
    return JsonResponse(data, safe=False)


def archive_ingestion_attempt(request, uuid=""):
    try:
        obj = IngestionAttempt.objects.get(uuid=uuid)
    except IngestionAttempt.DoesNotExist:
        return HttpResponse('Not found', status=status.HTTP_404_NOT_FOUND)

    auth = request.headers.get("Authorization")
    if not check_authorized(auth, obj.site, obj.project):
        return HttpResponse('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
    obj.archived = True
    obj.save()
    return HttpResponse(status=status.HTTP_200_OK)


def delete_ingestion_attempt(request, uuid=""):

    try:
        obj = IngestionAttempt.objects.get(uuid=uuid)
    except IngestionAttempt.DoesNotExist:
        return HttpResponse('Not found', status=status.HTTP_404_NOT_FOUND)

    auth = request.headers.get("Authorization")
    if not check_authorized(auth, obj.site, obj.project):
        return HttpResponse('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
    obj.delete()
    return HttpResponse(status=status.HTTP_200_OK)


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


@api_view(["PUT"])
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
