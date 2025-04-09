from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import DownloadTask, DownloadHistory
from .serializers import DownloadTaskSerializer, DownloadHistorySerializer
from .tasks import download_file

class DownloadTaskViewSet(viewsets.ModelViewSet):
    queryset = DownloadTask.objects.all().order_by('-created_at')
    serializer_class = DownloadTaskSerializer

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
