# testing/views.py
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from core.client import EmpowerClient
from core.endpoints import Endpoint
from core.parsers import BaseParser
from .forms import FuseActionForm


class RawHtmlParser(BaseParser):
    """A simple parser that just returns the prettified HTML content."""
    def parse(self):
        return self.soup.prettify()

class TestingView(LoginRequiredMixin, View):
    template_name = 'testing/testing_page.html'
    form_class = FuseActionForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        result_html = None; error = None

        if form.is_valid():
            initial_fuseaction = form.cleaned_data.get('initial_fuseaction')
            token_name = form.cleaned_data.get('token_name')
            cfc_url = form.cleaned_data.get('cfc_url')
            cfc_method = form.cleaned_data.get('cfc_method')
            fuseaction = form.cleaned_data.get('fuseaction')
            payload_str = form.cleaned_data.get('payload', '')

            payload_dict = {}
            if payload_str:
                for line in payload_str.strip().split('\n'):
                    if '=' in line: key, value = line.split('=', 1); payload_dict[key.strip()] = value.strip()
            
            try:
                sis_password = request.session.get('sis_password')
                if not sis_password: raise Exception("SIS password not found in session. Please log out and log back in.")

                with EmpowerClient(request.user.username, sis_password) as client:
                    
                    if initial_fuseaction and token_name and cfc_url and cfc_method:
                        # --- This is the new two-step AJAX request ---
                        initial_endpoint = Endpoint(fuseaction=initial_fuseaction)
                        # We don't need to pass the token in the payload here, the client does it.
                        if 'token' in payload_dict:
                            del payload_dict['token']
                        result_html = client.ajax_post(initial_endpoint, token_name, cfc_url, cfc_method, payload_dict, RawHtmlParser)
                    elif fuseaction:
                        # This is a standard request
                        endpoint = Endpoint(fuseaction=fuseaction)
                        if payload_dict: result_html = client.post(endpoint, payload_dict, RawHtmlParser)
                        else: result_html = client.get(endpoint, RawHtmlParser)
                    else:
                        error = "You must provide either a Standard Fuseaction or all four AJAX fields."

            except Exception as e:
                error = f"An error occurred: {e}"

        context = {'form': form, 'result_html': result_html, 'error': error}
        return render(request, self.template_name, context)