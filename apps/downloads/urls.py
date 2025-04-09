from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DownloadTaskViewSet, DownloadHistoryViewSet

router = DefaultRouter()
router.register(r'tasks', DownloadTaskViewSet)
router.register(r'history', DownloadHistoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
