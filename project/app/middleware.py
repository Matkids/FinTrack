from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile


class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code executed for each request before the view is called
        response = self.get_response(request)

        # Code executed for each request/response after the view is called

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip middleware for admin, login, and logout pages
        if request.path.startswith('/admin/') or request.path in ['/login/', '/logout/']:
            return None
            
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return redirect('login')
            
        # If user doesn't have a profile, redirect to login (they might not be properly set up)
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return redirect('login')
            
        # The role-based restrictions will be handled in individual views
        # This middleware ensures that all authenticated users have a valid profile
        return None


def role_required(allowed_roles):
    """
    Decorator to restrict access based on user role
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
                
            try:
                user_role = request.user.userprofile.role
            except UserProfile.DoesNotExist:
                return redirect('login')
                
            if user_role not in allowed_roles:
                return HttpResponseForbidden("You don't have permission to access this page.")
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator