# swaps/admin.py
from datetime import timezone
from django.contrib import admin
from .models import County, SubCounty, Ward, SwapRequest, Payment # Removed SubscriptionPlan, UserSubscription

@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(SubCounty)
class SubCountyAdmin(admin.ModelAdmin):
    list_display = ('name', 'county')
    list_filter = ('county',)
    search_fields = ('name', 'county__name')

@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ('name', 'subcounty', 'get_county')
    list_filter = ('subcounty__county', 'subcounty')
    search_fields = ('name', 'subcounty__name', 'subcounty__county__name')

    @admin.display(description='County', ordering='subcounty__county__name')
    def get_county(self, obj):
        return obj.subcounty.county.name

@admin.register(SwapRequest)
class SwapRequestAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'status', 'desired_county', 'desired_subcounty',
        'desired_ward', 'created_at', 'get_matched_with_user',
        'payment_completed_for_match_reveal', 'match_found_at'
    )
    list_filter = ('status', 'desired_county', 'payment_completed_for_match_reveal', 'created_at')
    search_fields = (
        'user__username', 'user__first_name', 'user__last_name', 'notes',
        'desired_county__name', 'desired_subcounty__name',
        'desired_ward__name', 'matched_with_request__user__username'
    )
    raw_id_fields = ('user', 'matched_with_request')
    date_hierarchy = 'created_at'
    actions = ['mark_as_completed_and_paid']

    @admin.display(description='Matched With User', ordering='matched_with_request__user__username')
    def get_matched_with_user(self, obj):
        if obj.matched_with_request:
            return obj.matched_with_request.user.username
        return "-"

    @admin.action(description="Mark selected requests as 'Completed & Details Revealed' (simulate payment)")
    def mark_as_completed_and_paid(self, request, queryset):
        updated_count = queryset.update(
            status='COMPLETED',
            payment_completed_for_match_reveal=True,
            match_found_at=timezone.now() # Or preserve existing if already set
        )
        for req in queryset: # Also update reverse match if applicable
            if req.matched_with_request:
                req.matched_with_request.status = 'COMPLETED'
                req.matched_with_request.payment_completed_for_match_reveal = True
                req.matched_with_request.save()
        self.message_user(request, f"{updated_count} swap requests marked as completed and paid.")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'swap_request_id_link', 'amount', 'payment_method', 'status',
        'mpesa_receipt_number', 'paypal_transaction_id', 'paid_at', 'created_at'
    )
    list_filter = ('payment_method', 'status', 'created_at', 'paid_at')
    search_fields = (
        'user__username', 'swap_request__id',
        'mpesa_receipt_number', 'paypal_transaction_id', 'mpesa_checkout_request_id', 'paypal_order_id'
    )
    raw_id_fields = ('user', 'swap_request')
    date_hierarchy = 'created_at'
    readonly_fields = ('paid_at', 'created_at', 'updated_at')

    @admin.display(description='Swap Request ID', ordering='swap_request__id')
    def swap_request_id_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        if obj.swap_request:
            link = reverse("admin:swaps_swaprequest_change", args=[obj.swap_request.id])
            return format_html('<a href="{}">{}</a>', link, obj.swap_request.id)
        return "N/A"

    def get_queryset(self, request):
        # Prefetch related user and swap_request for efficiency
        return super().get_queryset(request).select_related('user', 'swap_request')

