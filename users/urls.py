# users/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

# Define the application namespace for the 'users' app
app_name = 'users'

urlpatterns = [
    # User authentication and registration
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('registration-success/', views.RegistrationSuccessView.as_view(),
         name='registration_success'),
    # Django's built-in LoginView and LogoutView are handled by 'accounts/' include in config/urls.py
    # You can remove these specific paths if you rely solely on django.contrib.auth.urls
    # path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # Password reset views (using Django's built-in views)
    path('password_reset/',
         auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # Profile completion steps
    path('complete-profile/step1/', views.CompleteProfileStep1View.as_view(),
         name='complete_profile_step1'),
    path('complete-profile/step2-school/', views.CompleteProfileStep2SchoolView.as_view(),
         name='complete_profile_step2'),
    path('complete-profile/step3-location/',
         views.CompleteProfileStep3LocationView.as_view(), name='complete_profile_step3'),
    path('complete-profile/step4-swap-to/',
         views.CompleteProfileStep4SwapToView.as_view(), name='complete_profile_step4'),

    # User profile and settings
    path('profile/', views.ProfileDetailView.as_view(), name='profile_detail'),
    # This path allows viewing a profile by primary key, useful for matched users
    path('profile/<int:pk>/', views.ProfileDetailView.as_view(), name='profile_detail_with_pk'),
    path('settings/', views.UserSettingsView.as_view(), name='user_settings'),

    # AJAX endpoints for dynamic forms (e.g., chained dropdowns)
    path('ajax/get-subcounties/', views.get_subcounties, name='get_subcounties'),
    path('ajax/get-wards/', views.get_wards, name='get_wards'),
]
