from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group, Permission
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import json

from .models import User
from .serializers import UserSerializer, GroupSerializer, PermissionSerializer
from django.middleware.csrf import get_token

@csrf_exempt  # In production, consider CSRF protection strategies or ensure this endpoint is only accessible when no superuser exists.
def initialize_superuser(request):
    # If a superuser already exists, always indicate that
    if User.objects.filter(is_superuser=True).exists():
        return JsonResponse({"superuser_exists": True})

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
            email = data.get("email", "")
            if not username or not password:
                return JsonResponse({"error": "Username and password are required."}, status=400)
            # Create the superuser
            User.objects.create_superuser(username=username, password=password, email=email)
            return JsonResponse({"superuser_exists": True})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    # For GET requests, indicate no superuser exists
    return JsonResponse({"superuser_exists": False})

# 🔹 1) Authentication APIs
class AuthViewSet(viewsets.ViewSet):
    """Handles user login and logout"""

    @swagger_auto_schema(
        operation_description="Authenticate and log in a user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD)
            },
        ),
        responses={200: "Login successful", 400: "Invalid credentials"},
    )
    def login(self, request):
        """Logs in a user and returns user details"""
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return Response({
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "groups": list(user.groups.values_list('name', flat=True))
                }
            })
        return Response({"error": "Invalid credentials"}, status=400)

    @swagger_auto_schema(
        operation_description="Log out the current user",
        responses={200: "Logout successful"}
    )
    def logout(self, request):
        """Logs out the authenticated user"""
        logout(request)
        return Response({"message": "Logout successful"})


# 🔹 2) User Management APIs
class UserViewSet(viewsets.ModelViewSet):
    """Handles CRUD operations for Users"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a list of users",
        responses={200: UserSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Retrieve a specific user by ID")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Create a new user")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Update a user")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Delete a user")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# 🔹 3) Group Management APIs
class GroupViewSet(viewsets.ModelViewSet):
    """Handles CRUD operations for Groups"""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a list of groups",
        responses={200: GroupSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Retrieve a specific group by ID")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Create a new group")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Update a group")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Delete a group")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# 🔹 4) Permissions List API
@swagger_auto_schema(
    method='get',
    operation_description="Retrieve a list of all permissions",
    responses={200: PermissionSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_permissions(request):
    """Returns a list of all available permissions"""
    permissions = Permission.objects.all()
    serializer = PermissionSerializer(permissions, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_csrf_token(request):
    """
    Returns a CSRF token for clients to use in their requests.
    This endpoint does not require authentication.
    """
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})
