"""Custom authentication for admin access."""
import os
from functools import wraps
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse


def get_admin_password():
    """Get admin password from environment."""
    password = os.environ.get('ADMIN_PASSWORD')
    if not password:
        raise ValueError("ADMIN_PASSWORD environment variable is not set")
    return password


def require_admin(view_func):
    """Decorator to require admin authentication."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_admin'):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.path.startswith('/api/'):
                return JsonResponse({'error': 'Authentication required'}, status=401)
            return HttpResponseRedirect(reverse('login') + f'?next={request.path}')
        return view_func(request, *args, **kwargs)
    return wrapper


def require_admin_api(view_func):
    """Decorator for API endpoints that require admin authentication."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check session authentication
        if request.session.get('is_admin'):
            return view_func(request, *args, **kwargs)
        
        # Check Authorization header (for bash script)
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            try:
                if token == get_admin_password():
                    return view_func(request, *args, **kwargs)
            except ValueError:
                pass
        
        return JsonResponse({'error': 'Authentication required'}, status=401)
    return wrapper
