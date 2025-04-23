from django.shortcuts import redirect
from django.contrib.auth.models import AnonymousUser

def login_or_admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated and (not hasattr(user, "username") or user.username != "admin"):
            return redirect("adam:login")
        return view_func(request, *args, **kwargs)
    return wrapper