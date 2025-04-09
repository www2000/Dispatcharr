# core/api_views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import UserAgent, StreamProfile, CoreSettings
from .serializers import UserAgentSerializer, StreamProfileSerializer, CoreSettingsSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from drf_yasg.utils import swagger_auto_schema
import socket
import requests
import os
from django.middleware.csrf import get_token
from django.http import JsonResponse
from rest_framework.permissions import AllowAny

class UserAgentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows user agents to be viewed, created, edited, or deleted.
    """
    queryset = UserAgent.objects.all()
    serializer_class = UserAgentSerializer

class StreamProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows stream profiles to be viewed, created, edited, or deleted.
    """
    queryset = StreamProfile.objects.all()
    serializer_class = StreamProfileSerializer

class CoreSettingsViewSet(viewsets.ModelViewSet):
    """
    API endpoint for editing core settings.
    This is treated as a singleton: only one instance should exist.
    """
    queryset = CoreSettings.objects.all()
    serializer_class = CoreSettingsSerializer

@swagger_auto_schema(
    method='get',
    operation_description="Endpoint for environment details",
    responses={200: "Environment variables"}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def environment(request):
    public_ip = None
    local_ip = None
    country_code = None
    country_name = None

    # 1) Get the public IP
    try:
        r = requests.get("https://api64.ipify.org?format=json", timeout=5)
        r.raise_for_status()
        public_ip = r.json().get("ip")
    except requests.RequestException as e:
        public_ip = f"Error: {e}"

    # 2) Get the local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # connect to a “public” address so the OS can determine our local interface
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        local_ip = f"Error: {e}"

    # 3) If we got a valid public_ip, fetch geo info from ipapi.co
    if public_ip and "Error" not in public_ip:
        try:
            geo = requests.get(f"https://ipapi.co/{public_ip}/json/", timeout=5).json()
            # ipapi returns fields like country_code, country_name, etc.
            country_code = geo.get("country_code", "")  # e.g. "US"
            country_name = geo.get("country_name", "")  # e.g. "United States"
        except requests.RequestException as e:
            country_code = None
            country_name = None

    return Response({
        'authenticated': True,
        'public_ip': public_ip,
        'local_ip': local_ip,
        'country_code': country_code,
        'country_name': country_name,
        'env_mode': "dev" if os.getenv('DISPATCHARR_ENV') == "dev" else "prod",
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def get_csrf_token(request):
    """
    Returns a CSRF token for clients to use in their requests.
    This endpoint does not require authentication.
    """
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})
