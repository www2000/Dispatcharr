from django.db import models
from django.utils import timezone
from apps.channels.models import Channel


class EPGSource(models.Model):
    SOURCE_TYPE_CHOICES = [
        ('xmltv', 'XMLTV URL'),
        ('schedules_direct', 'Schedules Direct API'),
    ]
    name = models.CharField(max_length=255, unique=True)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES)
    url = models.URLField(blank=True, null=True)  # For XMLTV
    api_key = models.CharField(max_length=255, blank=True, null=True)  # For Schedules Direct
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Program(models.Model):
    channel = models.ForeignKey('channels.Channel', on_delete=models.CASCADE, related_name="programs")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.title} ({self.start_time} - {self.end_time})"
