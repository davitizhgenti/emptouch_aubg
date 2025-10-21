# testing/forms.py
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field


class FuseActionForm(forms.Form):
    # AJAX FIELDS
    initial_fuseaction = forms.CharField(label="Initial Fuseaction (to get token)", required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g., WEBSRQ14'}))
    token_name = forms.CharField(label="Token Field Name", required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g., token'}))
    cfc_url = forms.CharField(label="AJAX URL (.cfc)", required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g., https://.../courseCatalog.cfc'}))
    cfc_method = forms.CharField(label="AJAX Method", required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g., GetCataList'}))
    
    # Standard Fields
    fuseaction = forms.CharField(label="Standard Fuseaction (for GET/POST)", required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g., student.main'}))
    payload = forms.CharField(label="Payload (one key=value per line)", required=False, widget=forms.Textarea(attrs={'rows': 5}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'initial_fuseaction',
            'token_name',
            'cfc_url',
            'cfc_method',
            'fuseaction',
            Field('payload', css_class='font-monospace'),
            Submit('submit', 'Execute Request', css_class='btn-success w-100 mt-3')
        )