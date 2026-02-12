from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
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


@api_view(["GET"])
def single_ingestion_attempt_response(request, uuid=""):
    obj = get_object_or_404(IngestionAttempt, uuid=uuid)

    auth = request.headers.get("Authorization")
    check_authorized(auth, obj.site, obj.project)
    serializer = IngestionSerializer(obj)
    return JsonResponse(serializer.data, safe=False)


@api_view(["GET"])
def archive_ingestion_attempt(request, uuid=""):
    obj = get_object_or_404(IngestionAttempt, uuid=uuid)

    auth = request.headers.get("Authorization")
    check_authorized(auth, obj.site, obj.project)
    obj.archived = True
    obj.save()
    return HttpResponse(status=status.HTTP_200_OK)


@api_view(["GET"])
def delete_ingestion_attempt(request, uuid=""):
    obj = get_object_or_404(IngestionAttempt, uuid=uuid)

    auth = request.headers.get("Authorization")
    check_authorized(auth, obj.site, obj.project)
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
    """Creates or replaces the target resource."""
    auth = request.headers.get("Authorization")
    # If we are updating an existing record, then we should return
    # status 200 (or possibly 204?), but if we are creating a new
    # record then we should return 201. See:
    # https://www.rfc-editor.org/rfc/rfc7231#section-4.3.4
    success_status = status.HTTP_200_OK
    try:
        instance = IngestionAttempt.objects.get(uuid=request.data.get('uuid'))
        if not check_authorized(auth, instance.site, instance.project):
            return HttpResponse('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
        form = IngestionAttemptForm(request.data, instance=instance)
    except IngestionAttempt.DoesNotExist:
        # IngestionAttempt doesn't exists, so we create a new one
        form = IngestionAttemptForm(request.data)
        success_status = status.HTTP_201_CREATED
    if form.is_valid():
        if not check_authorized(auth, form.instance.site, form.instance.project):
            return HttpResponse('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
        ingestion = form.save()
        return Response({"uuid": ingestion.uuid}, status=success_status)
    else:
        return HttpResponse(form.errors, status=status.HTTP_400_BAD_REQUEST)
