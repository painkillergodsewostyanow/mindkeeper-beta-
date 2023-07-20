from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import RegisterUserForm
from .models import User
from main.models import Themes, Cards


class UserUpdateView(UpdateView):
    model = User
    fields = (
        'image',
        'username',
        'email',
        'phone_number',
        'if_private'
    )
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        context['total_likes_received'] = Themes.count_user_s_likes_received(self.request.user) + \
                                          Cards.count_user_s_likes_received(self.request.user)

        context['total_views_received'] = Themes.count_user_s_views_received(self.request.user) + \
                                          Cards.count_user_s_views_received(self.request.user)

        context['total_comments_received'] = Themes.count_user_s_comment_received(self.request.user) + \
                                             Cards.count_user_s_comment_received(self.request.user)

        context['total_likes_verb'] = Themes.count_user_s_likes_placed(self.request.user) + \
                                      Cards.count_user_s_likes_placed(self.request.user)

        context['total_views_verb'] = Themes.count_user_s_views_placed(self.request.user) + \
                                      Cards.count_user_s_views_placed(self.request.user)

        context['total_comments_verb'] = Themes.count_user_s_comment_placed(self.request.user) + \
                                         Cards.count_user_s_comment_placed(self.request.user)

        return context


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
