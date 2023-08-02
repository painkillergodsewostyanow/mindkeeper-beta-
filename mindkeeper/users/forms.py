from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms


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