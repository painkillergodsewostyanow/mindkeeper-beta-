from rest_framework.permissions import BasePermission

from main.models import Themes
from main.scripts import check_access


class CheckAccess(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            parent_theme_pk = request.data.get('parent_theme', None)

            if parent_theme_pk:

                parent_theme = Themes.objects.get(pk=parent_theme_pk)
                if request.user != parent_theme.user:
                    return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in ('PUT', 'PATCH', 'POST'):
            parent_theme_pk = request.data.get('parent_theme', None)
            if parent_theme_pk:
                parent_theme = Themes.objects.get(pk=parent_theme_pk)
                if not request.user != parent_theme.user:
                    return False
        print(check_access(request.user, obj, obj.users_with_access))
        return check_access(request.user, obj, obj.users_with_access)

