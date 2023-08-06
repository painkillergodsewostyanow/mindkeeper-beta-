from django.http import JsonResponse
from django.conf import settings


def check_access(user, to=None,  users_with_access=None):
    if getattr(to, 'obj', False):
        if to.obj.user == user:
            return True
        return False

    if users_with_access:
        if user in users_with_access:
            return True

    if to :
        if to.user == user:
            return True

    return False


def ajax_login_required(func):

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"authenticated": False, "login_url": settings.LOGIN_URL}, safe=False)
        return func(request, *args, **kwargs)

    return wrapper


