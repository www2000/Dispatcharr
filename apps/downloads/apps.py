from django.apps import AppConfig


class DownloadsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.downloads'

    def ready(self):
        import apps.downloads.signals
