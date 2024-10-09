from django.contrib import admin
from .models import IngestionAttempt
from .caching import TokenCache

admin.site.register(IngestionAttempt)
admin.site.register(TokenCache)
