# swaps/urls.py
from django.urls import path
from . import views

# Define the application namespace for the 'swaps' app
app_name = 'swaps'

urlpatterns = [
    # Dashboard URL (if it resides in the swaps app, as indicated by base.html)
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # Swap Request management
    path('request/create/', views.SwapRequestCreateView.as_view(), name='swap_request_create'),
    path('request/list/', views.SwapListView.as_view(), name='swap_list'),
    path('request/<int:pk>/', views.SwapDetailView.as_view(), name='swap_detail'),
    path('request/<int:pk>/update/', views.SwapRequestUpdateView.as_view(), name='swap_request_update'),
    path('request/<int:pk>/delete/', views.SwapRequestDeleteView.as_view(), name='swap_request_delete'),

    # Admin view for all swap requests
    path('admin/requests/', views.AdminSwapListView.as_view(), name='admin_swap_list'),

    # Payment related URLs
    # Initiate payment after a match is made
    path('payment/initiate/<int:swap_request_id>/', views.InitiateConnectionPaymentView.as_view(), name='initiate_connection_payment'),
    # Page to show payment is pending (e.g., waiting for M-Pesa STK push)
    path('payment/pending/<int:payment_id>/', views.PaymentPendingView.as_view(), name='payment_pending'),
    # Generic success and failure pages after payment attempts
    path('payment/success/', views.PaymentSuccessView.as_view(), name='payment_success'),
    path('payment/failed/', views.PaymentFailedView.as_view(), name='payment_failed'),

    # Payment Gateway Callbacks/Webhooks (These need to be publicly accessible HTTPS endpoints)
    # M-Pesa callback URL for confirming transactions
    path('payments/mpesa/callback/', views.mpesa_payment_callback, name='mpesa_payment_callback'),
    # PayPal webhook/IPN listener for transaction notifications
    path('payments/paypal/webhook/', views.paypal_payment_webhook, name='paypal_payment_webhook'),
    # Mock PayPal approval URL (for development/testing purposes)
    path('payments/paypal/mock-approval/', views.mock_paypal_approval, name='mock_paypal_approval'),

    # Billing history page for users
    path('billing/', views.BillingHistoryView.as_view(), name='billing'),

    # AJAX endpoints for dynamic forms (e.g., chained dropdowns)
    path('ajax/get-subcounties/', views.get_subcounties, name='ajax_get_subcounties'),
    path('ajax/get-wards/', views.get_wards, name='ajax_get_wards'),
]
