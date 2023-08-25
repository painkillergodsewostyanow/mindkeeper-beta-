from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from main.models import Themes, Cards
from main.scripts import check_access


class CheckCardAndThemesAccess(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            parent_theme_pk = request.data.get('parent_theme', None)
            if not request.user.is_authenticated:
                return False

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

        if obj.is_private:
            return check_access(request.user, obj, obj.users_with_access)
        return True


class CheckCommentsAccess(BasePermission):
    def has_permission(self, request, view):

        if request.method == 'POST':
            if request.data.get('theme', False):
                return not get_object_or_404(Themes, pk=request.data['theme']).is_private

            if request.data.get('card', False):
                return not get_object_or_404(Cards, pk=request.data['card']).is_private

        return True

    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True

        if request.method in ('PUT', 'PATCH'):
            return obj.user == request.user

        if request.method == "DELETE":
            return request.user == obj.user

        return True
