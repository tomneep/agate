from django.urls import path, re_path
from django.views.generic import TemplateView
from . import views

app_name = 'agate'
urlpatterns = [
    path('', TemplateView.as_view(template_name="agate/coming-soon.html"), name='comingsoon'),
    path('cookies/', TemplateView.as_view(template_name="agate/cookies.html"), name='cookies'),
    path("ingestion/<str:project>/", views.ingestion_attempt_response),
    path("profile/", views.profile),
    path("projects/", views.projects),
    path("add/", views.create_ingestion_attempt),
    path("update/", views.update_ingestion_attempt),
]
