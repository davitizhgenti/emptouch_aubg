# testing/urls.py
from django.urls import path
from .views import TestingView

urlpatterns = [
    path('', TestingView.as_view(), name='testing_page'),
]