# core/forms.py
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Username",
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your SIS username', 'autofocus': True})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
  
        self.helper = FormHelper()
        # This explicitly tells Crispy NOT to render the <form> tag itself.
        self.helper.form_tag = False 
        # The layout no longer includes a submit button.
        self.helper.layout = Layout(
            'username',
            'password'
        )