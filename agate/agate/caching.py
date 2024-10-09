from django.db import models


class TokenCache(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    token_hash = models.CharField(
        max_length=200,
    )

    site_output = models.CharField(
        max_length=100,
    )

    projects_output = models.CharField(
        max_length=500,
    )
