# ai_assistant/apps.py

from django.apps import AppConfig


class AiAssistantConfig(AppConfig):
    """
    AppConfig for the 'ai_assistant' application.
    Sets the default auto field and verbose name for the app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_assistant'
    verbose_name = 'AI Assistant'
