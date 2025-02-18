from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from datetime import timedelta
from .models import Program, EPGSource
from .serializers import ProgramSerializer, EPGSourceSerializer
from .tasks import refresh_epg_data


# 🔹 1) EPG Source API (CRUD)
class EPGSourceViewSet(viewsets.ModelViewSet):
    """Handles CRUD operations for EPG sources"""
    queryset = EPGSource.objects.all()
    serializer_class = EPGSourceSerializer
    permission_classes = [IsAuthenticated]


# 🔹 2) Program API (CRUD)
class ProgramViewSet(viewsets.ModelViewSet):
    """Handles CRUD operations for EPG programs"""
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [IsAuthenticated]


# 🔹 3) EPG Grid View: Shows programs airing within the next 12 hours
class EPGGridAPIView(APIView):
    """Returns all programs airing in the next 12 hours"""

    @swagger_auto_schema(
        operation_description="Retrieve upcoming EPG programs within the next 12 hours",
        responses={200: ProgramSerializer(many=True)}
    )
    def get(self, request, format=None):
        now = timezone.now()
        twelve_hours_later = now + timedelta(hours=12)
        programs = Program.objects.select_related('channel').filter(
            start_time__gte=now, start_time__lte=twelve_hours_later
        )
        serializer = ProgramSerializer(programs, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


# 🔹 4) EPG Import View: Triggers an import of EPG data
class EPGImportAPIView(APIView):
    """Triggers an EPG data refresh"""

    @swagger_auto_schema(
        operation_description="Triggers an EPG data import",
        responses={202: "EPG data import initiated"}
    )
    def post(self, request, format=None):
        refresh_epg_data.delay()  # Trigger Celery task
        return Response({'success': True, 'message': 'EPG data import initiated.'}, status=status.HTTP_202_ACCEPTED)
