from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import RegisterUserForm
from .models import User


class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = 'users/registration/login.html'

    def get_success_url(self):
        return reverse_lazy('main:index')


def logout_user(request):
    logout(request)
    return redirect("main:index")


class RegistrationUser(CreateView):
    model = User
    template_name = 'users/registration/reg.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('users:login')
