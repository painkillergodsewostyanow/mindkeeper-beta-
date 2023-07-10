from django.http import HttpResponseRedirect
from django.urls import reverse


def check_access(user, to=None,  users_with_access=None):
    if to:
        if to.user != user:
            return False

    if users_with_access:
        if user not in users_with_access:
            return False

    return True
