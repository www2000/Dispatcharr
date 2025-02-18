from django.contrib import admin
from django.utils.html import format_html
from .models import M3UAccount, M3UFilter, ServerGroup

class M3UFilterInline(admin.TabularInline):
    model = M3UFilter
    extra = 1
    verbose_name = "M3U Filter"
    verbose_name_plural = "M3U Filters"

@admin.register(M3UAccount)
class M3UAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'server_url', 'server_group', 'max_streams', 'is_active', 'uploaded_file_link', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'server_url', 'server_group__name')
    inlines = [M3UFilterInline]
    actions = ['activate_accounts', 'deactivate_accounts']

    def uploaded_file_link(self, obj):
        if obj.uploaded_file:
            return format_html("<a href='{}' target='_blank'>Download M3U</a>", obj.uploaded_file.url)
        return "No file uploaded"
    uploaded_file_link.short_description = "Uploaded File"

    @admin.action(description='Activate selected accounts')
    def activate_accounts(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Deactivate selected accounts')
    def deactivate_accounts(self, request, queryset):
        queryset.update(is_active=False)

@admin.register(M3UFilter)
class M3UFilterAdmin(admin.ModelAdmin):
    list_display = ('m3u_account', 'filter_type', 'regex_pattern', 'exclude')
    list_filter = ('filter_type', 'exclude')
    search_fields = ('regex_pattern',)
    ordering = ('m3u_account',)

@admin.register(ServerGroup)
class ServerGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
