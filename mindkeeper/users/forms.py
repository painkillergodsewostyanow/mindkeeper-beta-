from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User
from django import forms
from .tasks import send_verify_email


class UserForm(UserCreationForm):
    class Meta:
        model = User
        widgets = {
            'image': forms.FileInput()
        }
        fields = ('image', 'username', 'email', 'phone_number', 'is_private', 'is_receive_notifications')


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        widgets = {
            'image': forms.FileInput()
        }
        fields = ('image', 'username', 'email', 'phone_number', 'is_private', 'is_receive_notifications')


class UserAuthenticationForm(AuthenticationForm):

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username is not None and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if not self.user_cache.is_email_verified:
                send_verify_email.delay(self.user_cache.pk)
                raise ValidationError(
                    'Подтвердите почту',
                    code='invalid_login'
                )


            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
