# users/apps.py

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    AppConfig for the 'users' application.
    Sets the default auto field and verbose name for the app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'User Management'
