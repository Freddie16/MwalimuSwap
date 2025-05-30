# swaps/apps.py

from django.apps import AppConfig


class SwapsConfig(AppConfig):
    """
    AppConfig for the 'swaps' application.
    Sets the default auto field and verbose name for the app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'swaps'
    verbose_name = 'Swap Management'
