from rest_framework import serializers
from .models import DownloadTask, DownloadHistory
import logging
import re

logger = logging.getLogger(__name__)

class DownloadHistorySerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()

    class Meta:
        model = DownloadHistory
        fields = '__all__'

    def get_duration(self, obj):
        return obj.duration()

class DownloadTaskSerializer(serializers.ModelSerializer):
    latest_history = serializers.SerializerMethodField()

    class Meta:
        model = DownloadTask
        fields = '__all__'
        read_only_fields = [
            'status', 'last_run', 'next_run',
            'last_success', 'last_failure', 'created_at', 'updated_at'
        ]

    def get_latest_history(self, obj):
        latest = obj.history.order_by('-started_at').first()
        if latest:
            return DownloadHistorySerializer(latest).data
        return None

    def validate_url(self, value):
        """Custom URL validator that's more permissive than Django's URLValidator"""
        logger.debug(f"Validating URL: {value}")

        # Basic URL format checking - this is more permissive than Django's validator
        # Allow URLs with protocols like http://, https://, ftp://, etc.
        if not re.match(r'^[a-z0-9+.-]+://.*', value, re.IGNORECASE):
            # If no protocol specified, try prepending http://
            if not value.startswith('http://') and not value.startswith('https://'):
                value = 'http://' + value
                logger.debug(f"Added http:// protocol to URL: {value}")

        # Log the final URL
        logger.debug(f"Final URL after validation: {value}")
        return value

    def validate(self, attrs):
        # Log the incoming data to help with debugging
        logger.debug(f"DownloadTaskSerializer validate: {attrs}")

        # Validate download_type
        if 'download_type' in attrs and attrs['download_type'] not in dict(DownloadTask.TYPE_CHOICES):
            raise serializers.ValidationError({"download_type": f"Invalid download type. Choose from: {[t[0] for t in DownloadTask.TYPE_CHOICES]}"})

        # Validate frequency
        if 'frequency' in attrs and attrs['frequency'] not in dict(DownloadTask.FREQUENCY_CHOICES):
            raise serializers.ValidationError({"frequency": f"Invalid frequency. Choose from: {[f[0] for f in DownloadTask.FREQUENCY_CHOICES]}"})

        # Add more validation as needed for other fields
        return attrs
