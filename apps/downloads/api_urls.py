from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DownloadTaskViewSet, DownloadHistoryViewSet

app_name = 'downloads'

router = DefaultRouter()
router.register(r'tasks', DownloadTaskViewSet, basename='task')
router.register(r'history', DownloadHistoryViewSet, basename='history')

urlpatterns = router.urls
