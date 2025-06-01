# users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
#from swaps.models import County, SubCounty, Ward # Import location models

class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds fields for full name, phone number, profile picture,
    school details, and current/desired swap locations.
    """
    # Personal Information
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True, unique=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # School Information
    SCHOOL_TYPE_CHOICES = [
        ('PRIMARY', 'Primary School'),
        ('JUNIOR_SECONDARY', 'Junior Secondary School'),
        ('SENIOR_SECONDARY', 'Senior Secondary School'),
        ('TERTIARY', 'Tertiary Institution'),
    ]
    school_type = models.CharField(max_length=50, choices=SCHOOL_TYPE_CHOICES, blank=True, null=True)
    subjects = models.TextField(
        blank=True,
        null=True,
        help_text="Comma-separated list of subjects you teach (e.g., Math, English, Kiswahili)"
    )

    # Current Location (Foreign Keys to location models)
    current_county = models.ForeignKey(
    'swaps.County',  # The 'to' model as a string
    on_delete=models.SET_NULL,  # What to do if the related County is deleted
    null=True,
    blank=True,
    related_name='current_users' # Optional: for reverse lookups
)
    current_subcounty = models.ForeignKey(
    'swaps.SubCounty',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='current_users'
)

    current_ward = models.ForeignKey(
    'swaps.Ward',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='current_users'
)


    # Desired Swap To Location (Foreign Keys to location models)
    swap_to_county = models.ForeignKey(
        'swaps.County',  # Use string reference
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users_swap_to_county'
    )
    swap_to_subcounty = models.ForeignKey(
        'swaps.SubCounty',  # Use string reference
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users_swap_to_subcounty'
    )
    swap_to_ward = models.ForeignKey(
        'swaps.Ward',  # Use string reference
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users_swap_to_ward'
    )

    # Profile Completion Status
    is_profile_complete = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        """
        Overrides save to automatically update is_profile_complete.
        A user's profile is considered complete if essential fields are filled.
        """
        # Define what constitutes a 'complete' profile
        if (self.full_name and self.phone_number and
            self.school_type and self.subjects and
            self.current_county and self.current_subcounty and self.current_ward and
            self.swap_to_county and self.swap_to_subcounty and self.swap_to_ward):
            self.is_profile_complete = True
        else:
            self.is_profile_complete = False
        super().save(*args, **kwargs)
