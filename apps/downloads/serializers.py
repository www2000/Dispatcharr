from rest_framework import serializers
from .models import DownloadTask, DownloadHistory

class DownloadHistorySerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()

    class Meta:
        model = DownloadHistory
        fields = [
            'id', 'started_at', 'completed_at', 'status',
            'file_size', 'download_speed', 'error_message',
            'saved_path', 'duration'
        ]

    def get_duration(self, obj):
        return obj.duration()

class DownloadTaskSerializer(serializers.ModelSerializer):
    latest_history = serializers.SerializerMethodField()

    class Meta:
        model = DownloadTask
        fields = [
            'id', 'name', 'url', 'download_type', 'frequency',
            'cron_expression', 'hour', 'minute', 'day_of_week',
            'day_of_month', 'status', 'last_run', 'next_run',
            'last_success', 'last_failure', 'custom_filename',
            'is_active', 'created_at', 'updated_at', 'user_agent',
            'custom_headers', 'latest_history'
        ]

    def get_latest_history(self, obj):
        latest = obj.history.order_by('-started_at').first()
        if latest:
            return DownloadHistorySerializer(latest).data
        return None
