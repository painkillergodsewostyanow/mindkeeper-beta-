from .models import User
from django.db.models import Q
from rest_framework.exceptions import AuthenticationFailed
from .tasks import send_verify_email


class AuthByUsernameOrEmailBackends(object):
    supports_object_permissions = True
    supports_anonymous_user = False
    supports_inactive_user = False

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, request, username, password):
        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
        except User.DoesNotExist:
            return None

        if user:
            if not user.is_email_verified:

                send_verify_email.delay(user.pk)

                raise AuthenticationFailed(
                    'Подтвердите почту, письмо отправленно автоматически'
                )

        return user if user.check_password(password) else None

