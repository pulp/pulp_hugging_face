"""
Django app configuration for pulp_hugging_face.
"""

from django.apps import AppConfig


class PulpHuggingFaceAppConfig(AppConfig):
    """Django application config for pulp_hugging_face."""

    name = "pulp_hugging_face.app"
    label = "hugging_face"
    verbose_name = "Pulp Hugging Face"
