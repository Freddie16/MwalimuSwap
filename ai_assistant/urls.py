# ai_assistant/urls.py

from django.urls import path
from . import views
app_name = 'ai_assistant'

urlpatterns = [
    # AI Chatbot UI
    path('chatbot/', views.ChatbotView.as_view(), name='ai_assistant_chatbot'),

    # Smart Matching Suggestions
    path('smart-matches/', views.SmartMatchSuggestionsView.as_view(), name='ai_assistant_smart_matches'),
]
