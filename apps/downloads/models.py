import os
from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

# Default download paths - can be overridden in settings
DEFAULT_EPG_PATH = os.path.join(settings.MEDIA_ROOT, 'downloaded_epg')
DEFAULT_M3U_PATH = os.path.join(settings.MEDIA_ROOT, 'downloaded_m3u')
DEFAULT_CUSTOM_PATH = os.path.join(settings.MEDIA_ROOT, 'downloaded_custom')

class DownloadTask(models.Model):
    """Model for scheduled download tasks"""
    TYPE_CHOICES = (
        ('epg', 'EPG'),
        ('m3u', 'M3U'),
        ('custom', 'Custom'),
    )

    FREQUENCY_CHOICES = (
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom Schedule'),
    )

    STATUS_CHOICES = (
        ('idle', 'Idle'),
        ('scheduled', 'Scheduled'),
        ('downloading', 'Downloading'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    # Change URLField to TextField to accept any string without validation
    url = models.TextField(max_length=2048)
    download_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)

    # For custom schedule (stored as cron expression)
    cron_expression = models.CharField(max_length=100, blank=True, null=True)

    # For simple schedules
    hour = models.IntegerField(default=0)  # 0-23
    minute = models.IntegerField(default=0)  # 0-59
    day_of_week = models.IntegerField(null=True, blank=True)  # 0-6 (Monday-Sunday)
    day_of_month = models.IntegerField(null=True, blank=True)  # 1-31

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='idle')
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    last_success = models.DateTimeField(null=True, blank=True)
    last_failure = models.DateTimeField(null=True, blank=True)

    # Custom filename (optional, will use original filename if empty)
    custom_filename = models.CharField(max_length=255, blank=True)

    # Task control
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Headers for download request
    user_agent = models.CharField(max_length=500, blank=True, default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    custom_headers = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.name} ({self.download_type})"

    @property
    def download_path(self):
        """Get the appropriate download directory based on type"""
        if self.download_type == 'epg':
            return getattr(settings, 'EPG_DOWNLOAD_PATH', DEFAULT_EPG_PATH)
        elif self.download_type == 'm3u':
            return getattr(settings, 'M3U_DOWNLOAD_PATH', DEFAULT_M3U_PATH)
        else:  # custom
            return getattr(settings, 'CUSTOM_DOWNLOAD_PATH', DEFAULT_CUSTOM_PATH)

    def get_output_filename(self):
        """Get the filename to save the downloaded file as"""
        if self.custom_filename:
            return self.custom_filename

        # Extract filename from URL
        url_filename = os.path.basename(self.url.split('?')[0])
        if not url_filename:
            # Generate a filename if we can't extract one
            extension = '.xml' if self.download_type == 'epg' else '.m3u' if self.download_type == 'm3u' else ''
            return f"{self.download_type}_{self.id}{extension}"
        return url_filename

    def get_full_path(self):
        """Get the full path for the downloaded file"""
        return os.path.join(self.download_path, self.get_output_filename())

    def update_next_run(self):
        """Calculate and set the next run time based on frequency"""
        now = timezone.now()

        if self.frequency == 'hourly':
            next_run = now.replace(minute=self.minute, second=0, microsecond=0)
            if next_run <= now:
                next_run = next_run + timezone.timedelta(hours=1)

        elif self.frequency == 'daily':
            next_run = now.replace(hour=self.hour, minute=self.minute, second=0, microsecond=0)
            if next_run <= now:
                next_run = next_run + timezone.timedelta(days=1)

        elif self.frequency == 'weekly' and self.day_of_week is not None:
            # Calculate days until next occurrence
            current_weekday = now.weekday()
            days_ahead = (self.day_of_week - current_weekday) % 7
            if days_ahead == 0 and now.time() >= timezone.datetime.time(self.hour, self.minute):
                days_ahead = 7

            next_run = now.replace(hour=self.hour, minute=self.minute, second=0, microsecond=0)
            next_run = next_run + timezone.timedelta(days=days_ahead)

        elif self.frequency == 'monthly' and self.day_of_month is not None:
            # Get the next month occurrence
            if now.day > self.day_of_month or (now.day == self.day_of_month and
                                              now.time() >= timezone.datetime.time(self.hour, self.minute)):
                # Move to next month
                if now.month == 12:
                    next_run = now.replace(year=now.year+1, month=1, day=min(self.day_of_month, 31),
                                          hour=self.hour, minute=self.minute, second=0, microsecond=0)
                else:
                    next_run = now.replace(month=now.month+1, day=min(self.day_of_month, 31),
                                          hour=self.hour, minute=self.minute, second=0, microsecond=0)
            else:
                next_run = now.replace(day=self.day_of_month, hour=self.hour, minute=self.minute,
                                      second=0, microsecond=0)
        else:
            # Default: run in one hour if we can't determine schedule
            next_run = now + timezone.timedelta(hours=1)

        self.next_run = next_run
        self.save(update_fields=['next_run'])
        return next_run

    class Meta:
        app_label = 'downloads'


class DownloadHistory(models.Model):
    """Model for tracking download history and details"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(DownloadTask, on_delete=models.CASCADE, related_name='history')

    # Timing information
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Status information
    status = models.CharField(max_length=20, choices=DownloadTask.STATUS_CHOICES, default='downloading')
    file_size = models.BigIntegerField(null=True, blank=True)  # in bytes
    download_speed = models.FloatField(null=True, blank=True)  # in bytes/second

    # Error tracking
    error_message = models.TextField(blank=True)

    # File information
    saved_path = models.CharField(max_length=512, blank=True)

    def __str__(self):
        return f"{self.task.name} - {self.started_at}"

    def duration(self):
        """Calculate download duration in seconds"""
        if not self.completed_at:
            return None

        duration = (self.completed_at - self.started_at).total_seconds()
        return duration

    class Meta:
        app_label = 'downloads'
        verbose_name_plural = 'Download histories'
