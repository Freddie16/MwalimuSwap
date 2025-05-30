# ai_assistant/admin.py

import json
from django.contrib import admin
from .models import AIChatMessage, SmartMatchLog

@admin.register(AIChatMessage)
class AIChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_type', 'content', 'timestamp')
    list_filter = ('message_type', 'timestamp')
    search_fields = ('user__username', 'content')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

@admin.register(SmartMatchLog)
class SmartMatchLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'display_suggestions_count')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'prompt', 'ai_response')
    readonly_fields = ('timestamp', 'prompt', 'ai_response', 'suggestions_data')
    date_hierarchy = 'timestamp'

    def display_suggestions_count(self, obj):
        try:
            data = json.loads(obj.suggestions_data)
            return len(data)
        except (json.JSONDecodeError, TypeError):
            return 0
    display_suggestions_count.short_description = 'Suggestions Count'
