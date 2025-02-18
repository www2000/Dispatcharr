from django.core.management.base import BaseCommand
from apps.channels.models import Stream, Channel, ChannelGroup
from apps.m3u.models import M3UAccount

class Command(BaseCommand):
    help = "Delete all Channels, Streams, M3Us from the database (example)."

    def handle(self, *args, **kwargs):
        # Delete all Streams
        stream_count = Stream.objects.count()
        Stream.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {stream_count} Streams."))

        # Or delete Channels:
        channel_count = Channel.objects.count()
        Channel.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {channel_count} Channels."))

        # If you have M3UAccount:
        m3u_count = M3UAccount.objects.count()
        M3UAccount.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {m3u_count} M3U accounts."))

        self.stdout.write(self.style.SUCCESS("Successfully deleted the requested objects."))
