# testing/apps.py
from django.apps import AppConfig

class TestingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'testing'

    def ready(self):
        # This code runs once when the app is ready.
        from core.widgets import register, Widget
        from .widgets import fetch_testing_widget_data

        register(
            Widget(
                name='SIS Tester',
                # We can reuse a common permission. 'auth.view_user' is a safe default for authenticated users.
                permission_codename='auth.view_user',
                template_name='testing/testing_dashboard_widget.html',
                fetch_data_func=fetch_testing_widget_data
            )
        )