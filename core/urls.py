from django.urls import path, include
from .views import settings_view

urlpatterns = [
    path('', settings_view, name='settings'),
    path('api/downloads/', include('apps.downloads.urls')),
]
