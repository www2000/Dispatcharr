from django.contrib import admin
from .models import DownloadTask, DownloadHistory

@admin.register(DownloadTask)
class DownloadTaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'download_type', 'frequency', 'status', 'last_run', 'next_run', 'is_active')
    list_filter = ('download_type', 'frequency', 'status', 'is_active')
    search_fields = ('name', 'url')
    readonly_fields = ('last_run', 'next_run', 'last_success', 'last_failure')
    fieldsets = (
        (None, {
            'fields': ('name', 'url', 'download_type', 'is_active')
        }),
        ('Schedule', {
            'fields': ('frequency', 'cron_expression', 'hour', 'minute', 'day_of_week', 'day_of_month')
        }),
        ('Status', {
            'fields': ('status', 'last_run', 'next_run', 'last_success', 'last_failure')
        }),
        ('Advanced', {
            'fields': ('custom_filename', 'user_agent', 'custom_headers'),
            'classes': ('collapse',)
        }),
    )

@admin.register(DownloadHistory)
class DownloadHistoryAdmin(admin.ModelAdmin):
    list_display = ('task', 'started_at', 'completed_at', 'status', 'file_size', 'download_speed')
    list_filter = ('status', 'started_at')
    search_fields = ('task__name',)
    readonly_fields = ('task', 'started_at', 'completed_at', 'status', 'file_size', 'download_speed', 'error_message', 'saved_path')
