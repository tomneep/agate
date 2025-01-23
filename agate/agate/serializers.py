from rest_framework import serializers
from .models import IngestionAttempt


class IngestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngestionAttempt
        exclude = ''
