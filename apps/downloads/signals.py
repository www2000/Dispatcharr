from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DownloadTask
from .tasks import download_file

@receiver(post_save, sender=DownloadTask)
def set_next_run_on_create(sender, instance, created, **kwargs):
    """Set the next run time when a task is first created"""
    if created and not instance.next_run:
        instance.update_next_run()
