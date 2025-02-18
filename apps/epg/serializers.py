from rest_framework import serializers
from .models import Program, EPGSource
from apps.channels.models import Channel

class EPGSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EPGSource
        fields = ['id', 'name', 'source_type', 'url', 'api_key', 'is_active']


class ProgramSerializer(serializers.ModelSerializer):
    channel = serializers.SerializerMethodField()

    def get_channel(self, obj):
        return {"id": obj.channel.id, "name": obj.channel.name} if obj.channel else None

    class Meta:
        model = Program
        fields = ['id', 'channel', 'title', 'description', 'start_time', 'end_time']
