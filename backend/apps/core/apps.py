import os
import sys
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'

    def ready(self):
        # Pre-load models in background or worker if requested
        # Lazy singleton fallback in ServiceRegistry ensures models load once on first access
        pass
