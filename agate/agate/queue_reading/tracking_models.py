from django.db import models


class Project(models.Model):

    key = models.CharField(
        primary_key=True,
        unique=True,
        max_length=200,
    )


class ProjectSite(models.Model):

    key = models.CharField(
        primary_key=True,
        unique=True,
        max_length=200,
    )
