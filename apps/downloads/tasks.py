import os
import time
import logging
import requests
from celery import shared_task
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import DownloadTask, DownloadHistory
from core.utils import acquire_task_lock, release_task_lock

logger = logging.getLogger(__name__)

def send_status_update(task_id, status, progress=None, speed=None, error=None):
    """Send WebSocket update for download task status"""
    channel_layer = get_channel_layer()
    message = {
        "type": "download_status",
        "task_id": str(task_id),
        "status": status
    }

    if progress is not None:
        message["progress"] = progress

    if speed is not None:
        message["speed"] = speed

    if error is not None:
        message["error"] = str(error)

    async_to_sync(channel_layer.group_send)(
        'updates',
        {
            'type': 'update',
            'data': message
        }
    )

@shared_task
def download_file(task_id):
    """Download a file based on the task configuration"""
    if not acquire_task_lock(f'download_task_{task_id}', task_id):
        logger.info(f"Task already running for download_task_{task_id}")
        return f"Task already running for task_id={task_id}."

    try:
        task = DownloadTask.objects.get(id=task_id, is_active=True)
    except DownloadTask.DoesNotExist:
        release_task_lock(f'download_task_{task_id}', task_id)
        return f"DownloadTask with ID={task_id} not found or inactive."

    # Create history record
    history = DownloadHistory.objects.create(
        task=task,
        status='downloading'
    )

    # Update task status
    task.status = 'downloading'
    task.last_run = timezone.now()
    task.save(update_fields=['status', 'last_run'])

    # Ensure download directory exists
    os.makedirs(task.download_path, exist_ok=True)

    output_path = task.get_full_path()
    temp_path = f"{output_path}.tmp"

    # Prepare headers
    headers = {
        'User-Agent': task.user_agent
    }

    if task.custom_headers:
        headers.update(task.custom_headers)

    # Download file with progress tracking
    try:
        start_time = time.time()

        with requests.get(task.url, headers=headers, stream=True) as response:
            response.raise_for_status()

            # Get content length if available
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            last_update_time = start_time
            update_interval = 1.0  # Update status every second

            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Update status periodically
                        current_time = time.time()
                        if current_time - last_update_time >= update_interval:
                            elapsed = current_time - start_time
                            speed = downloaded / elapsed if elapsed > 0 else 0

                            # Calculate progress if content length is known
                            progress = None
                            if total_size > 0:
                                progress = int((downloaded / total_size) * 100)

                            send_status_update(
                                task_id=task.id,
                                status='downloading',
                                progress=progress,
                                speed=speed
                            )
                            last_update_time = current_time

        # Rename temp file to final name
        os.replace(temp_path, output_path)

        # Record successful download
        elapsed = time.time() - start_time
        download_speed = downloaded / elapsed if elapsed > 0 else 0

        # Update history record
        history.status = 'success'
        history.completed_at = timezone.now()
        history.file_size = downloaded
        history.download_speed = download_speed
        history.saved_path = output_path
        history.save()

        # Update task status
        task.status = 'success'
        task.last_success = timezone.now()
        task.update_next_run()
        task.save(update_fields=['status', 'last_success', 'next_run'])

        # Send final status update
        send_status_update(
            task_id=task.id,
            status='success',
            speed=download_speed
        )

        logger.info(f"Download successful for task {task.name} (ID: {task_id})")
        return f"Download successful for task {task_id}"

    except Exception as e:
        logger.error(f"Download failed for task {task.name} (ID: {task_id}): {str(e)}")

        # Clean up temp file if it exists
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as clean_error:
                logger.error(f"Error cleaning up temp file: {str(clean_error)}")

        # Update history record
        history.status = 'failed'
        history.completed_at = timezone.now()
        history.error_message = str(e)
        history.save()

        # Update task status
        task.status = 'failed'
        task.last_failure = timezone.now()
        task.update_next_run()
        task.save(update_fields=['status', 'last_failure', 'next_run'])

        # Send error status
        send_status_update(
            task_id=task.id,
            status='failed',
            error=str(e)
        )

        return f"Download failed for task {task_id}: {str(e)}"

    finally:
        release_task_lock(f'download_task_{task_id}', task_id)


@shared_task
def check_scheduled_downloads():
    """Check for downloads that need to be scheduled based on next_run time"""
    now = timezone.now()

    # Get all active tasks that are due to run
    due_tasks = DownloadTask.objects.filter(
        is_active=True,
        next_run__lte=now,
        status__in=['idle', 'scheduled', 'success', 'failed']  # Don't reschedule if already downloading
    )

    for task in due_tasks:
        # Update status and schedule download
        task.status = 'scheduled'
        task.save(update_fields=['status'])

        # Schedule download
        download_file.delay(str(task.id))

        logger.info(f"Scheduled download for task {task.name} (ID: {task.id})")

    return f"Checked for scheduled downloads: {due_tasks.count()} tasks scheduled"
