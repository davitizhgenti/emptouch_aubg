# core/views.py
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string

from .forms import LoginForm
from .network import HttpClient
from .exceptions import AuthenticationError
from .widgets import WIDGET_REGISTRY


class CustomLoginView(View):
    template_name = 'core/login.html'
    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username').lower()
            password = form.cleaned_data.get('password')
            
            try:
                client = HttpClient(username, password)
                if client._login():
                    user, created = User.objects.get_or_create(username=username)
                    if created or not user.check_password(password):
                        user.set_password(password)
                        user.save()
                    
                    login(request, user)

                    # --- THIS IS THE FIX ---
                    # Store the plain-text password in the user's session.
                    # Django's session middleware will handle encryption.
                    request.session['sis_password'] = password
                    
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Invalid credentials. Please try again.')

            except AuthenticationError as e:
                messages.error(request, f"A network error occurred: {e}")
            finally:
                if 'client' in locals():
                    client.close()

        return render(request, self.template_name, {'form': form})


class DashboardView(LoginRequiredMixin, View):
    """
    Displays the main dashboard by pre-rendering all visible widgets into HTML strings.
    """
    template_name = 'core/dashboard.html'

    def get(self, request, *args, **kwargs):
        rendered_widgets = []
        user = request.user

        for widget_config in WIDGET_REGISTRY:
            if user.has_perm(widget_config.permission_codename):
                context_data = {}
                try:
                    fetched_data = widget_config.fetch_data_func(user)
                    if isinstance(fetched_data, dict):
                        context_data = fetched_data
                except Exception as e:
                    context_data['error'] = f"Could not load widget data: {e}"

                try:
                    widget_html = render_to_string(widget_config.template_name, context_data)
                    rendered_widgets.append(widget_html)
                except Exception as e:
                    error_html = f'<div class="alert alert-danger">Error rendering widget: {widget_config.name}</div>'
                    rendered_widgets.append(error_html)

        context = {
            'rendered_widgets': rendered_widgets
        }
        return render(request, self.template_name, context)