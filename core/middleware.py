from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import JsonResponse
import re

class CustomCsrfMiddleware(MiddlewareMixin):
    """Custom middleware to handle CSRF for specific API endpoints"""

    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Check if the request is for API endpoints we want to exempt
        api_paths = [
            r'^/api/accounts/auth/',
            r'^/api/downloads/',  # Exempting all downloads endpoints
            r'^/api/epg/data/',
            r'^/api/core/csrf/',
        ]

        # Skip CSRF checks for specified paths
        request_path = request.path
        for path_pattern in api_paths:
            if re.match(path_pattern, request_path):
                return None

        # For all other paths, let Django's CSRF protection work normally
        return None
