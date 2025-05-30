# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView # For serving a simple home page

urlpatterns = [
    # Django Admin URL
    path('admin/', admin.site.urls),
    # Home page URL
    # This will serve the templates/home.html file
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    # Include URLs from the 'users' app
    # All URLs starting with 'users/' will be handled by users.urls
    path('users/', include('users.urls', namespace='users')), # Added namespace='users'
    # Include URLs for Django's built-in authentication views
    # This will handle login, logout, password reset, etc., using Django's default views
    # We will customize templates for these in templates/registration/
    path('accounts/', include('django.contrib.auth.urls')),
    # Include URLs from the 'swaps' app
    # All URLs starting with 'swaps/' will be handled by swaps.urls
    path('swaps/', include('swaps.urls', namespace='swaps')), # Ensure this also has a namespace
    # Include URLs from the 'ai_assistant' app
    # All URLs starting with 'ai-assistant/' will be handled by ai_assistant.urls
    path('ai-assistant/', include('ai_assistant.urls', namespace='ai_assistant')),

]

# Serve static and media files during development
# In production, these should be served by a web server (e.g., Nginx, Apache)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
