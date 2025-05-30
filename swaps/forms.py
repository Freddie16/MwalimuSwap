# swaps/forms.py
from django import forms
from .models import SwapRequest, Payment, County, SubCounty, Ward
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML
from django.urls import reverse_lazy
from django.conf import settings # Import settings

class SwapRequestForm(forms.ModelForm):
    """Form for creating and updating SwapRequest instances."""
    desired_county = forms.ModelChoiceField(
        queryset=County.objects.all().order_by('name'),
        empty_label="Select a County",
        required=True,
        label="Desired County"
    )
    desired_subcounty = forms.ModelChoiceField(
        queryset=SubCounty.objects.none(), # Will be populated via JavaScript
        empty_label="Select a Sub-county",
        required=False,
        label="Desired Sub-county"
    )
    desired_ward = forms.ModelChoiceField(
        queryset=Ward.objects.none(), # Will be populated via JavaScript
        empty_label="Select a Ward",
        required=False,
        label="Desired Ward"
    )

    class Meta:
        model = SwapRequest
        fields = ['desired_county', 'desired_subcounty', 'desired_ward', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Any specific preferences or reasons for the swap?'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h3 class="text-xl font-semibold mb-4">Where do you want to swap to?</h3>'),
            Field('desired_county', css_class='form-control rounded-md'),
            Field('desired_subcounty', css_class='form-control rounded-md'),
            Field('desired_ward', css_class='form-control rounded-md'),
            Field('notes', css_class='form-control rounded-md'),
            Submit('submit', 'Submit Swap Request', css_class='btn btn-primary w-full rounded-md mt-4')
        )
        
        # If form has data (POST request), populate the querysets based on submitted values
        if 'desired_county' in self.data:
            try:
                county_id = int(self.data.get('desired_county'))
                self.fields['desired_subcounty'].queryset = SubCounty.objects.filter(
                    county_id=county_id
                ).order_by('name')
            except (ValueError, TypeError):
                pass  # Invalid input, ignore
        elif self.instance.pk and self.instance.desired_county:
            # If editing existing instance, populate based on saved values
            self.fields['desired_subcounty'].queryset = self.instance.desired_county.subcounties.all().order_by('name')

        if 'desired_subcounty' in self.data:
            try:
                subcounty_id = int(self.data.get('desired_subcounty'))
                self.fields['desired_ward'].queryset = Ward.objects.filter(
                    subcounty_id=subcounty_id
                ).order_by('name')
            except (ValueError, TypeError):
                pass  # Invalid input, ignore
        elif self.instance.pk and self.instance.desired_subcounty:
            # If editing existing instance, populate based on saved values
            self.fields['desired_ward'].queryset = self.instance.desired_subcounty.wards.all().order_by('name')

    def clean_desired_subcounty(self):
        subcounty = self.cleaned_data.get('desired_subcounty')
        county = self.cleaned_data.get('desired_county')
        
        if subcounty and county:
            # Verify that the subcounty belongs to the selected county
            if subcounty.county != county:
                raise forms.ValidationError("Selected subcounty does not belong to the selected county.")
        
        return subcounty

    def clean_desired_ward(self):
        ward = self.cleaned_data.get('desired_ward')
        subcounty = self.cleaned_data.get('desired_subcounty')
        
        if ward and subcounty:
            # Verify that the ward belongs to the selected subcounty
            if ward.subcounty != subcounty:
                raise forms.ValidationError("Selected ward does not belong to the selected subcounty.")
        
        return ward


class ConnectionPaymentForm(forms.ModelForm):
    """
    Form for initiating payment for a connection.
    The amount is fixed. User chooses payment method.
    """
    payment_method = forms.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES[:-1], # Exclude 'OTHER' for direct user choice
        widget=forms.RadioSelect,
        required=True,
        label="Choose Payment Method"
    )
    
    # M-Pesa phone number field for STK Push
    mpesa_phone_number = forms.CharField(
        max_length=15,
        required=False, # Required only if M-Pesa is chosen, handled in view/JS
        label="M-Pesa Phone Number (e.g., 2547XXXXXXXX)",
        widget=forms.TextInput(attrs={'placeholder': '254712345678'})
    )

    class Meta:
        model = Payment
        fields = ['payment_method', 'mpesa_phone_number'] # Amount is set in the view

    def __init__(self, *args, **kwargs):
        self.swap_request_id = kwargs.pop('swap_request_id', None)
        super().__init__(*args, **kwargs)
        self.fields['mpesa_phone_number'].widget.attrs['class'] = 'form-control rounded-md'
        
        self.helper = FormHelper()
        self.helper.form_tag = False # We will render the form tag manually in the template
        self.helper.layout = Layout(
            HTML(f"""
                <div class="mb-4 p-4 border border-gray-300 rounded-md bg-gray-50">
                    <h4 class="text-lg font-semibold">Payment for Connection</h4>
                    <p class="text-gray-700">You are about to pay <strong>KSh {settings.CONNECTION_PAYMENT_AMOUNT}</strong> to view the details of your matched swap partner.</p>
                </div>
            """),
            Field('payment_method', css_class='mb-3'),
            # Conditional M-Pesa phone number field (can be shown/hidden with JS)
            HTML("""
                <div id="mpesa-phone-number-field" class="mb-3" style="display: none;">
            """),
            Field('mpesa_phone_number'),
            HTML("""
                </div>
            """),
            # Placeholder for PayPal button or M-Pesa STK push button
            # Submit button will be handled by specific payment gateway logic in the template/JS
        )

    def clean_mpesa_phone_number(self):
        phone_number = self.cleaned_data.get('mpesa_phone_number')
        payment_method = self.cleaned_data.get('payment_method')
        if payment_method == 'MPESA' and not phone_number:
            raise forms.ValidationError("M-Pesa phone number is required for M-Pesa payments.")
        if phone_number and not phone_number.startswith('254'):
             raise forms.ValidationError("Phone number must start with 254.")
        if phone_number and len(phone_number) != 12 : # 254 + 9 digits
             raise forms.ValidationError("Phone number must be 12 digits long (e.g. 254712345678).")
        return phone_number