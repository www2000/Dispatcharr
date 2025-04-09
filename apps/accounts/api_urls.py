from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    AuthViewSet, UserViewSet, GroupViewSet,
    list_permissions, initialize_superuser, get_csrf_token
)
from rest_framework_simplejwt import views as jwt_views

app_name = 'accounts'

# 🔹 Register ViewSets with a Router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'groups', GroupViewSet, basename='group')

# 🔹 Custom Authentication Endpoints
auth_view = AuthViewSet.as_view({
    'post': 'login'
})

logout_view = AuthViewSet.as_view({
    'post': 'logout'
})

# 🔹 Define API URL patterns
urlpatterns = [
    # Authentication
    path('auth/login/', auth_view, name='user-login'),
    path('auth/logout/', logout_view, name='user-logout'),
    path('csrf/', get_csrf_token, name='csrf-token'),

    # Superuser API
    path('initialize-superuser/', initialize_superuser, name='initialize_superuser'),

    # Permissions API
    path('permissions/', list_permissions, name='list-permissions'),

    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]

# 🔹 Include ViewSet routes
urlpatterns += router.urls
