from celery import shared_task
from .models import EPGSource, Program
from apps.channels.models import Channel
from django.utils import timezone
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from django.db import transaction

@shared_task
def refresh_epg_data():
    active_sources = EPGSource.objects.filter(is_active=True)
    for source in active_sources:
        if source.source_type == 'xmltv':
            fetch_xmltv(source)
        elif source.source_type == 'schedules_direct':
            fetch_schedules_direct(source)
    return "EPG data refreshed."

def fetch_xmltv(source):
    try:
        response = requests.get(source.url, timeout=30)
        response.raise_for_status()
        root = ET.fromstring(response.content)

        with transaction.atomic():
            for programme in root.findall('programme'):
                start_time = parse_xmltv_time(programme.get('start'))
                stop_time = parse_xmltv_time(programme.get('stop'))
                channel_tvg_id = programme.get('channel')

                title = programme.findtext('title', default='No Title')
                desc = programme.findtext('desc', default='')

                # Find or create the channel
                try:
                    channel = Channel.objects.get(tvg_id=channel_tvg_id)
                except Channel.DoesNotExist:
                    # Optionally, skip programs for unknown channels
                    continue

                # Create or update the program
                Program.objects.update_or_create(
                    channel=channel,
                    title=title,
                    start_time=start_time,
                    end_time=stop_time,
                    defaults={'description': desc}
                )
    except Exception as e:
        # Log the error appropriately
        print(f"Error fetching XMLTV from {source.name}: {e}")

def fetch_schedules_direct(source):
    try:
        # need to add a setting for api url.

        api_url = ''
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {source.api_key}',
        }

        # Fetch subscriptions (channels)
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        subscriptions = response.json()

        # Fetch schedules for each subscription
        for sub in subscriptions:
            channel_tvg_id = sub.get('stationID')
            # Fetch schedules
            # Need to add schedules direct url
            schedules_url = f"/schedules/{channel_tvg_id}"
            sched_response = requests.get(schedules_url, headers=headers, timeout=30)
            sched_response.raise_for_status()
            schedules = sched_response.json()

            with transaction.atomic():
                try:
                    channel = Channel.objects.get(tvg_id=channel_tvg_id)
                except Channel.DoesNotExist:
                    # skip programs for unknown channels
                    continue

                for sched in schedules.get('schedules', []):
                    title = sched.get('title', 'No Title')
                    desc = sched.get('description', '')
                    start_time = parse_schedules_direct_time(sched.get('startTime'))
                    end_time = parse_schedules_direct_time(sched.get('endTime'))

                    Program.objects.update_or_create(
                        channel=channel,
                        title=title,
                        start_time=start_time,
                        end_time=end_time,
                        defaults={'description': desc}
                    )

    except Exception as e:
        # Log the error appropriately
        print(f"Error fetching Schedules Direct data from {source.name}: {e}")

def parse_xmltv_time(time_str):
    # XMLTV time format: '20250130120000 +0000'
    dt = datetime.strptime(time_str[:14], '%Y%m%d%H%M%S')
    tz_sign = time_str[15]
    tz_hours = int(time_str[16:18])
    tz_minutes = int(time_str[18:20])
    if tz_sign == '+':
        dt = dt - timedelta(hours=tz_hours, minutes=tz_minutes)
    elif tz_sign == '-':
        dt = dt + timedelta(hours=tz_hours, minutes=tz_minutes)
    return timezone.make_aware(dt, timezone=timezone.utc)

def parse_schedules_direct_time(time_str):
    # Schedules Direct time format: ISO 8601, e.g., '2025-01-30T12:00:00Z'
    dt = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ')
    return timezone.make_aware(dt, timezone=timezone.utc)
