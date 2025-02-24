from django.contrib import admin
from .models import IngestionAttempt, IngestionAttemptArchived
from .caching import TokenCache
from .queue_reading.tracking_models import Project, ProjectSite

admin.site.register(IngestionAttempt)
admin.site.register(IngestionAttemptArchived)
admin.site.register(TokenCache)
admin.site.register(Project)
admin.site.register(ProjectSite)
