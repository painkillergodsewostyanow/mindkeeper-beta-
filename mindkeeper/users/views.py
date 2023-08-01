from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .forms import RegisterUserForm
from main.models import Themes, Cards
from users.models import Subscribes, User


class UserStatisticInContextMixin:
    def get_context_data(self, **kwargs):
        context = super(UserStatisticInContextMixin, self).get_context_data(**kwargs)
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

        context['subscribers'] = self.get_object().get_user_s_subscribers.count()
        context['subscribes'] = self.get_object().get_user_s_subscribes.count()

        return context


class UserDetailView(UserStatisticInContextMixin, DetailView):
    model = User
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        context['super_theme'] = Themes.get_super_themes_by_user(self.get_object()).filter(is_private=False)
        context['super_card'] = Cards.get_super_cards_by_user(self.get_object()).filter(is_private=False)
        context['is_request_user_subscribed'] = self.get_object().is_user_subscribed(self.request.user)
        # TODO(Самое популярное)

        return context


class UserUpdateView(UserStatisticInContextMixin, UpdateView, LoginRequiredMixin):
    model = User
    fields = (
        'image',
        'username',
        'email',
        'phone_number',
        'if_private'
    )
    template_name = 'users/my_profile.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('users:my_profile')


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


# TODO(AJAX)
@login_required
def subscribe(request, author_pk):
    print('ПОДПИСКА')
    author = User.objects.get(pk=author_pk)
    subscribe = Subscribes.objects.filter(author=author, subscriber=request.user)

    if subscribe:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    Subscribes.objects.create(author=author, subscriber=request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

# TODO(AJAX)
@login_required
def unsubscribe(request, author_pk):
    print('ОТПИСКА')
    author = User.objects.get(pk=author_pk)
    Subscribes.objects.filter(author=author, subscriber=request.user).delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
