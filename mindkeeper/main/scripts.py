from rest_framework.response import Response
from django.conf import settings


def check_access(user, to=None, users_with_access=None):
    if users_with_access:
        if user in users_with_access:
            return True

    if to:
        if to.user == user:
            return True

    return False
