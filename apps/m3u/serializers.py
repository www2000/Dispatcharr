from rest_framework import serializers
from .models import M3UAccount, M3UFilter, ServerGroup


class M3UFilterSerializer(serializers.ModelSerializer):
    """Serializer for M3U Filters"""

    class Meta:
        model = M3UFilter
        fields = ['id', 'filter_type', 'regex_pattern', 'exclude']


class M3UAccountSerializer(serializers.ModelSerializer):
    """Serializer for M3U Account"""
    filters = M3UFilterSerializer(many=True, read_only=True)

    class Meta:
        model = M3UAccount
        fields = ['id', 'name', 'server_url', 'uploaded_file', 'server_group', 
                  'max_streams', 'is_active', 'created_at', 'updated_at', 'filters']


class ServerGroupSerializer(serializers.ModelSerializer):
    """Serializer for Server Group"""

    class Meta:
        model = ServerGroup
        fields = ['id', 'name']
