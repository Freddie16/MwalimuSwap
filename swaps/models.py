# swaps/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator

class County(models.Model):
    """Represents a county in Kenya."""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Counties"
        ordering = ['name']

    def __str__(self):
        return self.name

class SubCounty(models.Model):
    """Represents a sub-county within a specific County."""
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='subcounties')
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('county', 'name')
        verbose_name_plural = "Sub Counties"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.county.name})"

class Ward(models.Model):
    """Represents a ward within a specific SubCounty."""
    subcounty = models.ForeignKey(SubCounty, on_delete=models.CASCADE, related_name='wards')
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('subcounty', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.subcounty.name})"

class SwapRequest(models.Model):
    """Represents a teacher's request to swap schools."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'), # Initial status
        ('AWAITING_MATCH', 'Awaiting Match'), # Approved, looking for matches
        ('MATCH_FOUND', 'Match Found - Payment Required'), # Match found, awaiting payment to reveal details
        ('PAYMENT_PENDING', 'Payment Initiated'), # User initiated payment process
        ('COMPLETED', 'Completed & Details Revealed'), # Payment successful, details shown
        ('REJECTED', 'Rejected by Admin'),
        ('CANCELLED_BY_USER', 'Cancelled by User'),
        ('EXPIRED', 'Expired'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='swap_requests')
    
    # Desired swap location
    desired_county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, blank=True, related_name='desired_swaps')
    desired_subcounty = models.ForeignKey(SubCounty, on_delete=models.SET_NULL, null=True, blank=True, related_name='desired_swaps')
    desired_ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True, blank=True, related_name='desired_swaps')

    notes = models.TextField(blank=True, help_text="Any additional notes or preferences for the swap.")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Link to a matched swap request (for bilateral swaps)
    # This user initiated the request, matched_with is the other party's request
    matched_with_request = models.OneToOneField(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reverse_match_for_request',
        help_text="The other swap request this one is matched with."
    )
    
    # Indicates if payment to view matched_with_request user's details is complete
    payment_completed_for_match_reveal = models.BooleanField(default=False)
    # Timestamp when the match was made (and payment became due)
    match_found_at = models.DateTimeField(null=True, blank=True)


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Swap Request by {self.user.username} to {self.desired_county}, {self.desired_subcounty}"

    def can_view_match_details(self):
        return self.payment_completed_for_match_reveal and self.status == 'COMPLETED'

class Payment(models.Model):
    """Records payment transactions for revealing matched swap details."""
    PAYMENT_METHOD_CHOICES = [
        ('MPESA', 'M-Pesa'),
        ('PAYPAL', 'PayPal'),
        ('OTHER', 'Other'), # For future flexibility
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),       # Payment initiated but not confirmed
        ('COMPLETED', 'Completed'),   # Payment successful
        ('FAILED', 'Failed'),         # Payment failed
        ('REFUNDED', 'Refunded'),     # Payment was refunded
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, # Or SET_NULL if you want to keep payment records if user is deleted
        related_name='payments'
    )
    # Link to the swap request for which this payment is made
    swap_request = models.ForeignKey(
        SwapRequest,
        on_delete=models.SET_NULL, # Keep payment record even if swap request is deleted (or CASCADE)
        null=True,
        blank=True, # Should ideally not be blank if payment is for a swap
        related_name='payments'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Amount paid in KES"
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    
    # For M-Pesa
    mpesa_checkout_request_id = models.CharField(max_length=100, blank=True, null=True, help_text="M-Pesa Checkout Request ID for STK push")
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True, unique=True, help_text="M-Pesa transaction code (e.g., QBC123XYZ)")
    
    # For PayPal
    paypal_transaction_id = models.CharField(max_length=255, blank=True, null=True, unique=True, help_text="Transaction ID from PayPal")
    paypal_order_id = models.CharField(max_length=255, blank=True, null=True, unique=True, help_text="Order ID from PayPal")


    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True) # When payment record was created
    updated_at = models.DateTimeField(auto_now=True)   # When payment status was last updated
    paid_at = models.DateTimeField(null=True, blank=True) # Timestamp when payment was confirmed as COMPLETED

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment of {self.amount} KES by {self.user.username} via {self.payment_method} for Swap ID {self.swap_request_id or 'N/A'}"

    def save(self, *args, **kwargs):
        if self.status == 'COMPLETED' and not self.paid_at:
            self.paid_at = timezone.now()
        super().save(*args, **kwargs)

