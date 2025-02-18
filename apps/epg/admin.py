from django.contrib import admin
from .models import EPGSource, Program

@admin.register(EPGSource)
class EPGSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_type', 'is_active']
    list_filter = ['source_type', 'is_active']
    search_fields = ['name']

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_channel_tvg_id', 'start_time', 'end_time']
    list_filter = ['channel']
    search_fields = ['title', 'channel__channel_name']

    def get_channel_tvg_id(self, obj):
        return obj.channel.tvg_id if obj.channel else ''
    get_channel_tvg_id.short_description = 'Channel TVG ID'
    get_channel_tvg_id.admin_order_field = 'channel__tvg_id'
