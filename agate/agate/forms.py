from django import forms

from .models import IngestionAttempt


class IngestionAttemptForm(forms.ModelForm):
    class Meta:
        model = IngestionAttempt
        exclude = ["created_at", "updated_at"]
