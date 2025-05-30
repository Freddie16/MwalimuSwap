# users/views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .forms import (
    CustomUserCreationForm,
    CustomUserChangeForm,
    ProfileStep1Form,
    ProfileStep2SchoolForm,
    ProfileStep3LocationForm,
    ProfileStep4SwapToForm
)
from .models import CustomUser
from swaps.models import County, SubCounty, Ward, SwapRequest, Payment # Ensure Payment and SwapRequest are imported
import json
from users.forms import SUBJECT_CHOICES
from django.db.models import Q
from django.views.decorators.http import require_GET

class SignUpView(SuccessMessageMixin, CreateView):
    """
    View for user registration, extending Django's UserCreationForm.
    Uses CustomUserCreationForm and redirects to registration success page.
    """
    form_class = CustomUserCreationForm
    # Corrected success_url to use the 'users' namespace
    success_url = reverse_lazy('users:registration_success')
    template_name = 'registration/signup.html'
    success_message = "Your account has been created successfully! Please complete your profile."

    def form_valid(self, form):
        response = super().form_valid(form)
        # Send a message to the new user (e.g., via Django messages framework)
        messages.success(self.request, f"Welcome, {self.object.username}! Please complete your profile.")
        return response

class RegistrationSuccessView(TemplateView):
    """
    Simple view to display a success message after registration.
    """
    template_name = 'users/registration_success.html'

class ProfileDetailView(LoginRequiredMixin, DetailView):
    """
    View to display a user's profile.
    If viewing another user's profile, access is restricted unless payment is made for the
    connection.
    """
    model = CustomUser
    template_name = 'users/profile_detail.html'
    context_object_name = 'user_profile'

    def get_object(self, queryset=None):
        # Determine which user's profile to display
        if 'pk' in self.kwargs:
            # If a PK is provided, attempt to fetch that user
            profile_owner = get_object_or_404(CustomUser, pk=self.kwargs['pk'])
            # If the requested profile is not the current logged-in user's profile,
            # restrict access unless the user has paid for the connection
            if profile_owner != self.request.user:
                # Check for a completed payment associated with a matched swap request
                # where the current user is one party and profile_owner is the other.
                user_paid_for_connection = Payment.objects.filter(
                    user=self.request.user,
                    swap_request__in=SwapRequest.objects.filter(
                        Q(user=self.request.user, matched_with__user=profile_owner) |
                        Q(user=profile_owner, matched_with__user=self.request.user)
                    ),
                    status='COMPLETED'
                ).exists()
                if not user_paid_for_connection:
                    messages.warning(self.request, "You need to pay to view this teacher's profile details.")
                    # Redirect to the dashboard (or a payment initiation page)
                    return redirect(reverse_lazy('swaps:dashboard')) # Changed to swaps:dashboard
            return profile_owner
        else:
            # If no PK, display the current logged-in user's profile
            return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data needed for the profile detail page
        return context

class UserSettingsView(LoginRequiredMixin, UpdateView):
    """
    View for users to update their account settings.
    Uses CustomUserChangeForm (though we might use specific forms for different
    sections).
    """
    model = CustomUser
    form_class = CustomUserChangeForm # Using the comprehensive change form
    template_name = 'users/user_settings.html' # You might want a dedicated settings template
    # Corrected success_url to use the 'users' namespace
    success_url = reverse_lazy('users:user_settings') # Redirect back to settings page
    context_object_name = 'user_profile'

    def get_object(self):
        """
        Ensures that only the logged-in user can update their own profile.
        """
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Your profile has been updated successfully!")
        return super().form_valid(form)

class CompleteProfileStep1View(LoginRequiredMixin, UpdateView):
    """
    First step of the multi-step profile completion.
    Collects full name and phone number.
    """
    model = CustomUser
    form_class = ProfileStep1Form
    template_name = 'users/complete_profile_step1.html'
    # Corrected success_url to use the 'users' namespace
    success_url = reverse_lazy('users:complete_profile_step2') # Next step in the process

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.info(self.request, "Step 1 complete. Now for school details!")
        return super().form_valid(form)

class CompleteProfileStep2SchoolView(LoginRequiredMixin, UpdateView):
    """
    Second step of the multi-step profile completion.
    Collects school type and subjects.
    """
    model = CustomUser
    form_class = ProfileStep2SchoolForm
    template_name = 'users/complete_profile_step2_school.html'
    # Corrected success_url to use the 'users' namespace
    success_url = reverse_lazy('users:complete_profile_step3')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.info(self.request, "Step 2 complete. Let's get your current location!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subject_json'] = json.dumps(SUBJECT_CHOICES) # JSON-safe
        return context

class CompleteProfileStep3LocationView(LoginRequiredMixin, UpdateView):
    """
    Third step of the multi-step profile completion.
    Collects current county, subcounty, and ward.
    """
    model = CustomUser
    form_class = ProfileStep3LocationForm
    template_name = 'users/complete_profile_step3_location.html'
    # Corrected success_url to use the 'users' namespace
    success_url = reverse_lazy('users:complete_profile_step4')

    def get_object(self):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['counties'] = County.objects.all().order_by('name')
        return kwargs

    def form_valid(self, form):
        messages.info(self.request, "Step 3 complete. Finally, where do you want to swap to?")
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Profile Step 3 form is invalid:", form.errors)
        messages.error(self.request, "There were errors in your location information. Please correct them.")
        return self.render_to_response(self.get_context_data(form=form))
    
class CompleteProfileStep4SwapToView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileStep4SwapToForm
    template_name = 'users/complete_profile_step4_swap_to.html'
    # Corrected success_url to use the 'swaps' namespace for dashboard
    success_url = reverse_lazy('swaps:dashboard')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_profile_complete = True
        user.save()
        messages.success(self.request, "Profile completed successfully! Welcome to your dashboard.")
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form is invalid:", form.errors)
        messages.error(self.request, "There was an issue completing your profile.")
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

@require_GET
def get_subcounties(request):
    county_id = request.GET.get('county_id')
    if not county_id:
        return JsonResponse({'error': 'County ID is required'}, status=400)
    try:
        subcounties = SubCounty.objects.filter(county_id=county_id).values('id', 'name')
        return JsonResponse({'subcounties': list(subcounties)})
    except County.DoesNotExist:
        return JsonResponse({'error': 'County not found'}, status=404)

@require_GET
def get_wards(request):
    subcounty_id = request.GET.get('subcounty_id')
    if not subcounty_id:
        return JsonResponse({'error': 'Subcounty ID is required'}, status=400)
    try:
        wards = Ward.objects.filter(subcounty_id=subcounty_id).values('id', 'name')
        return JsonResponse({'wards': list(wards)})
    except SubCounty.DoesNotExist:
        return JsonResponse({'error': 'Subcounty not found'}, status=404)
