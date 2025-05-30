# ai_assistant/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone

class AIChatMessage(models.Model):
    """
    Stores messages exchanged in the AI Chatbot.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_chat_messages')
    message_type = models.CharField(max_length=10, choices=[('USER', 'User'), ('AI', 'AI')])
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name = "AI Chat Message"
        verbose_name_plural = "AI Chat Messages"

    def __str__(self):
        return f"{self.user.username} ({self.message_type}): {self.content[:50]}..."

class SmartMatchLog(models.Model):
    """
    Logs AI-generated smart matching suggestions for users.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='smart_match_logs')
    # Store the prompt sent to the AI for matching
    prompt = models.TextField(help_text="The input prompt or user profile data sent to the AI for matching.")
    # Store the raw response from the AI
    ai_response = models.TextField(help_text="The raw JSON or text response received from the AI.")
    # Store parsed suggestions (e.g., list of suggested swap requests or schools)
    # This could be a JSONField if using PostgreSQL, but for SQLite, store as Text and parse in Python
    suggestions_data = models.TextField(blank=True, null=True,
                                        help_text="Parsed smart matching suggestions (e.g., JSON string of schools/requests).")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Smart Match Log"
        verbose_name_plural = "Smart Match Logs"

    def __str__(self):
        return f"Smart Match for {self.user.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
