# ai_assistant/forms.py

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field

class ChatMessageForm(forms.Form):
    """
    Form for user input in the AI Chatbot.
    """
    message = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={'placeholder': 'Type your message here...', 'class': 'w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
        max_length=500
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False # Hide labels for a cleaner chat input
        self.helper.layout = Layout(
            Field('message'),
            Submit('submit', 'Send', css_class='btn btn-primary ml-2 px-6 py-3 rounded-md')
        )
