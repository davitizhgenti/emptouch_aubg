# core/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import DashboardView, CustomLoginView

urlpatterns = [
    # The root URL now points to the dashboard. LoginRequiredMixin will handle redirection.
    path('', DashboardView.as_view(), name='dashboard'),
    
    # Our new custom login URL
    path('login/', CustomLoginView.as_view(), name='login'),
    
    # We can use Django's built-in LogoutView. 'next_page' sends them to our login screen after logout.
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]