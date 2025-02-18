from django.urls import path
from .views import EPGDashboardView

app_name = 'epg_dashboard'

urlpatterns = [
    path('dashboard/', EPGDashboardView.as_view(), name='epg_dashboard'),
]
