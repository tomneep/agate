from django.db import models


class IngestionAttempt(models.Model):
    class Status(models.TextChoices):
        UNSTARTED = "US", ("Unstarted")
        METADATA = "MD", ("Awaiting metadata checks")
        VALIDATION = "VD", ("Awaiting validation Checks")
        METADATAFAIL = "FM", ("Metadata checks fail")
        VALIDATIONFAIL = "FV", ("Validation checks fail")
        SUCCESS = "SU", ("Success")

    uuid = models.CharField(
        primary_key=True,
        unique=True,
        max_length=200,
        default='',
    )

    name = models.CharField(
        null=True,
        blank=True,
        max_length=200,
        default='',
    )

    project = models.CharField(
        max_length=200,
        default='',
    )

    platform = models.CharField(
        null=True,
        blank=True,
        max_length=200,
        default='',
    )

    site = models.CharField(
        max_length=200,
        default='',
    )

    run_index = models.CharField(
        null=True,
        blank=True,
        max_length=200,
        default='',
    )

    run_id = models.CharField(
        null=True,
        blank=True,
        max_length=200,
        default='',
    )

    is_published = models.BooleanField()

    is_test_attempt = models.BooleanField()

    climb_id = models.CharField(
        null=True,
        blank=True,
        max_length=200,
        default='',
    )

    error_message = models.CharField(
        null=True,
        blank=True,
        max_length=600,
        default='',
    )

    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.UNSTARTED,
    )

    archived = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
