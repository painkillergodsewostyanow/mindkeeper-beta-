from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('image', 'username', 'email', 'phone_number', 'if_private')