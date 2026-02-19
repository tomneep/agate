from rest_framework import serializers
from .models import IngestionAttempt


class IngestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngestionAttempt
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]
