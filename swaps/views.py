from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
    TemplateView, FormView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt # For payment callbacks, use with caution
from django.conf import settings # Import settings
from .models import SwapRequest, Payment, County, SubCounty, Ward
from .forms import SwapRequestForm, ConnectionPaymentForm # Updated PaymentForm
import json # For potential JSON responses or logging
# import requests # For making HTTP requests to payment gateways if not using SDKs
# from decimal import Decimal # For precise amount handling

# --- Helper Functions/Classes (Placeholder for actual payment gateway logic) ---
def initiate_mpesa_stk_push(user, amount, phone_number, swap_request_id):
    """
    Placeholder: Initiates M-Pesa STK Push.
    In a real app, this would call Safaricom Daraja API.
    """
    print(f"Attempting M-Pesa STK Push for KES {amount} to {phone_number} for Swap ID: {swap_request_id}")
    # Example: Generate a CheckoutRequestID
    checkout_request_id = \
        f"ws_CO_{timezone.now().strftime('%Y%m%d%H%M%S')}_{swap_request_id}"

    # Simulate API call success/failure
    # response_code = "0" # Success
    response_code = "1" # Failure example

    if response_code == "0":
        return True, checkout_request_id, "STK Push initiated successfully. Check your phone."
    else:
        return False, None, "Failed to initiate M-Pesa STK Push. Please try again."

def create_paypal_order(user, amount, swap_request_id):
    """
    Placeholder: Creates a PayPal order and returns approval URL.
    In a real app, this would use PayPal SDK or API.
    """
    print(f"Creating PayPal order for KES {amount} for Swap ID: {swap_request_id}")
    # Simulate PayPal order creation
    # This would typically involve converting KES to USD/EUR if PayPal account is not KES based
    paypal_order_id = \
        f"PAYPAL_ORDER_{timezone.now().strftime('%Y%m%d%H%M%S')}_{swap_request_id}"
    # This would be the URL PayPal provides to redirect the user for payment approval
    approval_url = \
        f"/payments/paypal/mock-approval/?order_id={paypal_order_id}&swap_id={swap_request_id}"

    return True, paypal_order_id, approval_url, "PayPal order created. Redirecting..."

# --- Core Views ---
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'swaps/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Check if the user has a profile before accessing it
        user_profile = None
        if hasattr(user, 'profile'):
            user_profile = user.profile
        context['user_profile'] = user_profile # Add user_profile to context

        # Get active swap request for the current user
        user_swap_request = SwapRequest.objects.filter(
            user=user
        ).exclude(
            status__in=['COMPLETED', 'CANCELLED_BY_USER', 'REJECTED', 'EXPIRED']
        ).first()

        context['user_swap_request'] = user_swap_request

        potential_matches_info = []
        if user_swap_request and user_swap_request.matched_with_request:
            match = user_swap_request.matched_with_request
            can_view_details = \
                user_swap_request.can_view_match_details()

            # Check if the other party has also paid (for mutual reveal)
            # This logic might need adjustment based on your exact reveal rules
            other_party_paid = False
            if match.matched_with_request == user_swap_request: # Ensure the match is reciprocal
                other_party_paid = match.can_view_match_details()
            potential_matches_info.append({
                'matched_request_id': match.id,
                'matched_user_id': match.user.id, # Only for internal reference before payment
                'desired_location_of_match': f"{match.desired_ward or match.desired_subcounty or match.desired_county or 'N/A'}",
                'status_of_your_request':
                    user_swap_request.get_status_display(),
                'payment_required': user_swap_request.status ==
                    'MATCH_FOUND',
                'can_view_details': can_view_details,
                'other_party_paid': other_party_paid, # Info if the other user has paid
                'payment_url':
                    reverse_lazy('swaps:initiate_connection_payment',
                                 kwargs={'swap_request_id': user_swap_request.id}) if
                    user_swap_request.status == 'MATCH_FOUND' else None,
                'matched_user_details': match.user if can_view_details
                    else None # Securely pass details
            })
        context['potential_matches_info'] = potential_matches_info

        # For general match counts (simplified)
        context['county_match_count'] = 0 # Replace with actual logic if needed
        context['subcounty_match_count'] = 0
        context['ward_match_count'] = 0
        context['alternative_match_count'] = 0

        if user_swap_request and user_swap_request.status == 'AWAITING_MATCH' and user_profile:
            # Basic count for demonstration
            if user_swap_request.desired_county and user_profile.current_county:
                context['county_match_count'] = \
                    SwapRequest.objects.filter(
                        status='AWAITING_MATCH',
                        # Example: people who want to come to user's current county
                        desired_county=user_profile.current_county,
                        # And are in user's desired county
                        user__profile__current_county=user_swap_request.desired_county
                    ).exclude(user=user).count()
        return context

class SwapRequestCreateView(LoginRequiredMixin, CreateView):
    model = SwapRequest
    form_class = SwapRequestForm
    template_name = 'swaps/swap_request_form.html'

    def get_success_url(self):
        return reverse_lazy('swaps:swap_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = 'AWAITING_MATCH' # Or 'PENDING' if admin approval is first
        messages.success(self.request, "Your swap request has been submitted successfully!")
        return super().form_valid(form)

class SwapRequestUpdateView(LoginRequiredMixin, UserPassesTestMixin,
                            UpdateView):
    model = SwapRequest
    form_class = SwapRequestForm
    template_name = 'swaps/swap_request_form.html'
    success_url = reverse_lazy('swaps:swap_list')

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user and obj.status not in \
            ['COMPLETED', 'EXPIRED']

    def form_valid(self, form):
        messages.success(self.request, "Your swap request has been updated successfully!")
        return super().form_valid(form)

class SwapRequestDeleteView(LoginRequiredMixin, UserPassesTestMixin,
                            DeleteView):
    model = SwapRequest
    template_name = 'swaps/swap_confirm_delete.html'
    success_url = reverse_lazy('swaps:swap_list')

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user and obj.status not in \
            ['COMPLETED', 'EXPIRED']

    def form_valid(self, form):
        # Instead of full delete, mark as cancelled
        swap_request = self.get_object()
        swap_request.status = 'CANCELLED_BY_USER'
        swap_request.save()

        # If it was matched, also update the other request's status if necessary
        if swap_request.matched_with_request:
            other_request = swap_request.matched_with_request
            if other_request.matched_with_request == swap_request: # check reciprocity
                other_request.matched_with_request = None
                other_request.status = 'AWAITING_MATCH' # Or other appropriate status
                other_request.match_found_at = None
                other_request.payment_completed_for_match_reveal = \
                    False
                other_request.save()
            swap_request.matched_with_request = None
            swap_request.save()
        messages.success(self.request, "Your swap request has been cancelled.")
        return redirect(self.success_url)

class SwapListView(LoginRequiredMixin, ListView):
    model = SwapRequest
    template_name = 'swaps/swap_list.html'
    context_object_name = 'swap_requests'
    paginate_by = 10

    def get_queryset(self):
        return \
            SwapRequest.objects.filter(user=self.request.user).order_by('-created_at')

class SwapDetailView(LoginRequiredMixin, UserPassesTestMixin,
                     DetailView):
    model = SwapRequest
    template_name = 'swaps/swap_detail.html'
    context_object_name = 'swap_request'

    def test_func(self):
        # User can view their own request, or if it's a completed match, they can view the other side.
        obj = self.get_object()
        if obj.user == self.request.user:
            return True
        # Check if this is the "other side" of a completed match the current user paid for
        try:
            related_request = \
                SwapRequest.objects.get(user=self.request.user,
                                        matched_with_request=obj, status='COMPLETED')
            return related_request.can_view_match_details()
        except SwapRequest.DoesNotExist:
            return False
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        swap_request = self.get_object()

        # If this is the user's own request and it's matched & payment is required
        if swap_request.user == self.request.user and \
            swap_request.status == 'MATCH_FOUND':
            context['payment_url'] = \
                reverse('swaps:initiate_connection_payment', kwargs={'swap_request_id':
                                                                         swap_request.id})
            context['show_payment_prompt'] = True
            context['matched_partner_request'] = \
                swap_request.matched_with_request
        elif swap_request.user == self.request.user and \
            swap_request.can_view_match_details() and \
            swap_request.matched_with_request:
            context['show_match_details'] = True
            context['matched_partner_request'] = \
                swap_request.matched_with_request
            context['matched_partner_user'] = \
                swap_request.matched_with_request.user
        # If the current user is viewing the *other* person's request *after paying*
        elif swap_request.user != self.request.user:
            try:
                # Find the current user's request that is matched with this one
                user_own_request = \
                    SwapRequest.objects.get(user=self.request.user,
                                            matched_with_request=swap_request)
                if user_own_request.can_view_match_details():
                    context['show_match_details'] = True
                    context['matched_partner_request'] = swap_request # This is the other person's request
                    context['matched_partner_user'] = swap_request.user # This is the other person
            except SwapRequest.DoesNotExist:
                pass # No direct match found from current user's perspective
        return context

class AdminSwapListView(LoginRequiredMixin, UserPassesTestMixin,
                        ListView):
    model = SwapRequest
    template_name = 'swaps/admin_swap_list.html' # Ensure this template exists
    context_object_name = 'all_swap_requests'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        queryset = SwapRequest.objects.all().select_related(
            'user', 'desired_county', 'desired_subcounty',
            'desired_ward', 'matched_with_request__user'
        ).order_by('-created_at')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset

# --- Payment Views ---
class InitiateConnectionPaymentView(LoginRequiredMixin, FormView):
    template_name = 'swaps/initiate_connection_payment.html'
    form_class = ConnectionPaymentForm

    def dispatch(self, request, *args, **kwargs):
        self.swap_request_id = self.kwargs.get('swap_request_id')
        self.swap_request = get_object_or_404(SwapRequest,
                                              id=self.swap_request_id, user=request.user)
        if self.swap_request.status != 'MATCH_FOUND':
            messages.error(request, "Payment is not currently required or already processed for this swap.")
            return redirect('swaps:dashboard')
        if not self.swap_request.matched_with_request:
            messages.error(request, "No match found for this swap request to pay for.")
            return redirect('swaps:dashboard')

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['swap_request_id'] = self.swap_request_id
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['swap_request'] = self.swap_request
        context['payment_amount'] = settings.CONNECTION_PAYMENT_AMOUNT
        context['matched_with_user_identifier'] = f"User ID {self.swap_request.matched_with_request.user.id}" # Generic identifier
        return context

    def form_valid(self, form):
        payment_method = form.cleaned_data['payment_method']
        mpesa_phone_number = \
            form.cleaned_data.get('mpesa_phone_number')
        user = self.request.user
        amount = settings.CONNECTION_PAYMENT_AMOUNT
        # Create a PENDING payment record
        payment, created = Payment.objects.update_or_create(
            swap_request=self.swap_request,
            user=user,
            defaults={
                'amount': amount,
                'payment_method': payment_method,
                'status': 'PENDING',
                # Clear previous gateway IDs if re-attempting
                'mpesa_checkout_request_id': None,
                'mpesa_receipt_number': None,
                'paypal_order_id': None,
                'paypal_transaction_id': None,
            }
        )
        self.swap_request.status = 'PAYMENT_PENDING'
        self.swap_request.save()
        if payment_method == 'MPESA':
            if not mpesa_phone_number: # Should be caught by form validation but double check
                messages.error(self.request, "M-Pesa phone number is required.")
                return self.form_invalid(form)
            # Placeholder for M-Pesa STK Push
            success, mpesa_checkout_id, message = \
                initiate_mpesa_stk_push(
                    user, amount, mpesa_phone_number, self.swap_request.id
                )
            if success:
                payment.mpesa_checkout_request_id = mpesa_checkout_id
                payment.save()
                messages.info(self.request, message)
                # Redirect to a page that tells user to check their phone, or just dashboard
                return redirect('swaps:payment_pending',
                                payment_id=payment.id)
            else:
                payment.status = 'FAILED'
                payment.save()
                self.swap_request.status = 'MATCH_FOUND' # Revert status
                self.swap_request.save()
                messages.error(self.request, f"M-Pesa Error: {message}")
                return self.form_invalid(form)
        elif payment_method == 'PAYPAL':
            # Placeholder for PayPal order creation
            success, paypal_order_id, approval_url, message = \
                create_paypal_order(
                    user, amount, self.swap_request.id
                )
            if success:
                payment.paypal_order_id = paypal_order_id
                payment.save()
                messages.info(self.request, message)
                return redirect(approval_url) # Redirect to PayPal
            else:
                payment.status = 'FAILED'
                payment.save()
                self.swap_request.status = 'MATCH_FOUND' # Revert status
                self.swap_request.save()
                messages.error(self.request, f"PayPal Error: {message}")
                return self.form_invalid(form)

        return redirect('swaps:dashboard') # Fallback

class PaymentPendingView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'swaps/payment_pending.html' # User waits here, or gets instructions
    context_object_name = 'payment'
    pk_url_kwarg = 'payment_id'

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any specific instructions based on payment method
        if context['payment'].payment_method == 'MPESA':
            context['instruction_message'] = "An M-Pesa STK Push has been sent to your phone. Please enter your M-Pesa PIN to complete the payment."
        # Add more context if needed
        return context

@csrf_exempt # IMPORTANT: Secure this properly in production (e.g., verify sender IP, use signature)
@require_POST
def mpesa_payment_callback(request):
    """
    Placeholder: M-Pesa Daraja API will POST to this URL.
    This needs to be a publicly accessible HTTPS endpoint.
    """
    # callback_data = json.loads(request.body)
    # print("M-Pesa Callback Received:", callback_data)

    # --- PRODUCTION LEVEL PROCESSING ---
    # 1. Validate the source of the request (Safaricom IP, signature if available)
    # 2. Parse callback_data:
    # - Body.stkCallback.ResultCode (0 for success)
    # - Body.stkCallback.ResultDesc
    # - Body.stkCallback.CheckoutRequestID
    # - Body.stkCallback.CallbackMetadata.Item (contains Amount, MpesaReceiptNumber, TransactionDate, PhoneNumber)

    # Example of how you might process (highly simplified):
    # checkout_request_id = callback_data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
    # result_code = callback_data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
    # try:
    # payment = Payment.objects.get(mpesa_checkout_request_id=checkout_request_id, status='PENDING')
    # except Payment.DoesNotExist:
    # return HttpResponseBadRequest("Payment record not found or already processed.")
    # if result_code == 0: # Success
    # metadata = callback_data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {}).get('Item', [])
    # receipt_number = next((item['Value'] for item in metadata if item['Name'] == 'MpesaReceiptNumber'), None)

    # payment.status = 'COMPLETED'
    # payment.mpesa_receipt_number = receipt_number
    # payment.paid_at = timezone.now()
    # payment.save()
    # swap_request = payment.swap_request
    # swap_request.payment_completed_for_match_reveal = True
    # swap_request.status = 'COMPLETED'
    # swap_request.save()

    # # Also update the other side of the match if it's a reciprocal match
    # if swap_request.matched_with_request and \
    # swap_request.matched_with_request.matched_with_request == swap_request:
    # # If you have a rule that the other side also gets revealed/notified
    # pass # Potentially send notification or update their status if needed
    # # Send notification to user
    # # messages.success(payment.user, "Your M-Pesa payment was successful!") # Cannot use messages framework here directly
    # else: # Failed or cancelled
    # payment.status = 'FAILED'
    # payment.save()
    # if payment.swap_request:
    # payment.swap_request.status = 'MATCH_FOUND' # Revert to allow retry
    # payment.swap_request.save()

    # Acknowledge receipt to M-Pesa
    # return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
    print("M-Pesa callback received (placeholder processing)")
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Callback received by placeholder."})

@csrf_exempt # IMPORTANT: Secure this (e.g., verify PayPal IPN message)
@require_POST # Or GET depending on PayPal setup (IPN is POST)
def paypal_payment_webhook(request):
    """
    Placeholder: PayPal IPN or Webhook will POST here.
    This needs to be a publicly accessible HTTPS endpoint.
    """
    # raw_post_data = request.body.decode('utf-8')
    # print("PayPal Webhook/IPN Received:", raw_post_data)
    # --- PRODUCTION LEVEL PROCESSING ---
    # 1. Verify the IPN/Webhook message with PayPal to ensure it's genuine.
    # 2. Parse the data:
    # - payment_status (e.g., 'Completed')
    # - txn_id (transaction ID)
    # - custom (often used to pass your internal order/payment ID, e.g., Payment.pk or SwapRequest.pk)
    # - mc_gross (amount)
    # - mc_currency
    # Example (highly simplified):
    # payment_status = request.POST.get('payment_status')
    # paypal_order_id_from_custom_field = request.POST.get('custom') # Assuming you pass your Payment.paypal_order_id here
    # txn_id = request.POST.get('txn_id')
    # try:
    # # It's better to identify payment by paypal_order_id you stored
    # payment = Payment.objects.get(paypal_order_id=paypal_order_id_from_custom_field, status='PENDING')
    # except Payment.DoesNotExist:
    # return HttpResponseBadRequest("Payment record not found or already processed.")
    # if payment_status == 'Completed':
    # payment.status = 'COMPLETED'
    # payment.paypal_transaction_id = txn_id
    # payment.paid_at = timezone.now()
    # payment.save()
    # swap_request = payment.swap_request
    # swap_request.payment_completed_for_match_reveal = True
    # swap_request.status = 'COMPLETED'
    # swap_request.save()

    # # Notify user
    # else: # Other statuses like 'Failed', 'Pending', 'Denied'
    # payment.status = 'FAILED' # Or map to appropriate status
    # payment.save()
    # if payment.swap_request:
    # payment.swap_request.status = 'MATCH_FOUND'
    # payment.swap_request.save()

    # Acknowledge receipt to PayPal (empty 200 OK for webhooks, specific response for IPN)
    # return HttpResponse(status=200)
    print("PayPal webhook/IPN received (placeholder processing)")
    return HttpResponse(status=200)

class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'swaps/payment_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        swap_request_id = self.request.GET.get('swap_request_id')
        if swap_request_id:
            try:
                swap_request = \
                    SwapRequest.objects.get(id=swap_request_id, user=self.request.user,
                                            status='COMPLETED')
                context['swap_request'] = swap_request
                context['message'] = "Your payment was successful! You can now view the details of your matched partner."
            except SwapRequest.DoesNotExist:
                context['message'] = "Payment processed. Swap details will be available shortly."
        else:
            context['message'] = "Your payment was successful!"
        return context

class PaymentFailedView(LoginRequiredMixin, TemplateView):
    template_name = 'swaps/payment_failed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        swap_request_id = self.request.GET.get('swap_request_id')
        context['message'] = "Your payment failed or was cancelled."
        if swap_request_id:
            context['retry_url'] = \
                reverse_lazy('swaps:initiate_connection_payment',
                             kwargs={'swap_request_id': swap_request_id})
        return context

class BillingHistoryView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'swaps/billing.html'
    context_object_name = 'payments'
    paginate_by = 10

    def get_queryset(self):
        return \
            Payment.objects.filter(user=self.request.user).select_related('swap_request').order_by('-created_at')

# --- AJAX Endpoints (Keep these as they are useful for forms) ---
@require_GET
def get_subcounties(request):
    county_id = request.GET.get('county_id')
    subcounties_data = []
    if county_id:
        try:
            county = County.objects.get(id=county_id)
            subcounties_data = list(county.subcounties.values('id', 'name'))
        except County.DoesNotExist:
            pass
    return JsonResponse({'subcounties': subcounties_data})

@require_GET
def get_wards(request):
    subcounty_id = request.GET.get('subcounty_id')
    wards_data = []
    if subcounty_id:
        try:
            subcounty = SubCounty.objects.get(id=subcounty_id)
            wards_data = list(subcounty.wards.values('id', 'name'))
        except SubCounty.DoesNotExist:
            pass
    return JsonResponse({'wards': wards_data})

# Removed get_plan_price as subscription plans are removed.
# Mock PayPal Approval (for testing redirect flow without actual PayPal)
def mock_paypal_approval(request):
    order_id = request.GET.get('order_id')
    swap_id = request.GET.get('swap_id')
    # In a real scenario, PayPal would call your webhook.
    # Here, we simulate a successful payment and redirect.
    if order_id and swap_id:
        try:
            payment = Payment.objects.get(paypal_order_id=order_id,
                                          swap_request_id=swap_id, status='PENDING')
            payment.status = 'COMPLETED'
            payment.paypal_transaction_id = \
                f"MOCK_TXN_{timezone.now().strftime('%Y%m%d%H%M%S')}"
            payment.paid_at = timezone.now()
            payment.save()
            swap_request = payment.swap_request
            swap_request.payment_completed_for_match_reveal = True
            swap_request.status = 'COMPLETED'
            swap_request.save()
            messages.success(request, "Mock PayPal Payment Successful!")
            return redirect(reverse('swaps:payment_success') +
                            f"?swap_request_id={swap_id}")
        except Payment.DoesNotExist:
            messages.error(request, "Mock PayPal: Payment record not found.")
            return redirect(reverse('swaps:payment_failed') +
                            f"?swap_request_id={swap_id}")
    messages.error(request, "Mock PayPal: Invalid parameters.")
    return redirect('swaps:dashboard')
