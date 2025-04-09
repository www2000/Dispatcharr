from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import DownloadTask, DownloadHistory
from .serializers import DownloadTaskSerializer, DownloadHistorySerializer
from .tasks import download_file
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging

logger = logging.getLogger(__name__)

class DownloadTaskViewSet(viewsets.ModelViewSet):
    """ViewSet for managing download tasks"""
    queryset = DownloadTask.objects.all().order_by('-created_at')
    serializer_class = DownloadTaskSerializer
    permission_classes = [IsAuthenticated]

    # Explicitly handle POST method with better error handling
    def create(self, request, *args, **kwargs):
        logger.debug(f"DownloadTask create - POST data: {request.data}")
        try:
            # If URL is present in data, log it for debugging
            if 'url' in request.data:
                logger.info(f"Received URL: {request.data['url']}")

            return super().create(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"DownloadTask create error: {str(e)}")

            # Create a more user-friendly error message
            error_msg = str(e)
            if 'url' in str(e) and 'Enter a valid URL' in str(e):
                error_msg = "The URL format is invalid. Please provide a complete URL including the protocol (e.g., http:// or https://)"

            return Response(
                {"detail": f"Error creating download task: {error_msg}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Also enhance update method
    def update(self, request, *args, **kwargs):
        logger.debug(f"DownloadTask update - data: {request.data}")
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"DownloadTask update error: {str(e)}")
            return Response(
                {"detail": f"Error updating download task: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def trigger(self, request, pk=None):
        """Manually trigger a download task"""
        task = self.get_object()

        if task.status == 'downloading':
            return Response({'error': 'Task is already downloading'}, status=status.HTTP_400_BAD_REQUEST)

        # Update task status to scheduled
        task.status = 'scheduled'
        task.save(update_fields=['status'])

        # Schedule the download task
        download_file.delay(str(task.id))

        return Response({'status': 'download scheduled'})

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get download history for a specific task"""
        task = self.get_object()
        history = task.history.all().order_by('-started_at')

        page = self.paginate_queryset(history)
        if page is not None:
            serializer = DownloadHistorySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = DownloadHistorySerializer(history, many=True)
        return Response(serializer.data)

class DownloadHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DownloadHistory.objects.all().order_by('-started_at')
    serializer_class = DownloadHistorySerializer
