# core/api_urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import UserAgentViewSet, StreamProfileViewSet, CoreSettingsViewSet, environment, get_csrf_token

router = DefaultRouter()
router.register(r'useragents', UserAgentViewSet, basename='useragent')
router.register(r'streamprofiles', StreamProfileViewSet, basename='streamprofile')
router.register(r'settings', CoreSettingsViewSet, basename='coresettings')

urlpatterns = [
    path('csrf/', get_csrf_token, name='csrf_token'),
    path('settings/env/', environment, name='token_refresh'),
    path('', include(router.urls)),
]
