from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import LoginView
from main.tasks import send_notification
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.core.exceptions import ValidationError
from main.tasks import send_notification
from django.shortcuts import redirect, HttpResponseRedirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .forms import UserForm, UserUpdateForm, UserAuthenticationForm
from main.models import Themes, Cards
from users.models import Subscribes, User
from .tasks import send_verify_email
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings


# User
class UserStatisticInContextMixin:
    def get_context_data(self, **kwargs):
        if self.get_object():
            context = super(UserStatisticInContextMixin, self).get_context_data(**kwargs)

            context['total_likes_received'] = Themes.count_user_s_likes_received(self.get_object()) + \
                                              Cards.count_user_s_likes_received(self.get_object())

            context['total_views_received'] = Themes.count_user_s_views_received(self.get_object()) + \
                                              Cards.count_user_s_views_received(self.get_object())

            context['total_comments_received'] = Themes.count_user_s_comment_received(self.get_object()) + \
                                                 Cards.count_user_s_comment_received(self.get_object())

            context['total_likes_verb'] = Themes.count_user_s_likes_placed(self.get_object()) + \
                                          Cards.count_user_s_likes_placed(self.get_object())

            context['total_views_verb'] = Themes.count_user_s_views_placed(self.get_object()) + \
                                          Cards.count_user_s_views_placed(self.get_object())

            context['total_comments_verb'] = Themes.count_user_s_comment_placed(self.get_object()) + \
                                             Cards.count_user_s_comment_placed(self.get_object())

            context['subscribers_count'] = self.get_object().get_user_s_subscribers.count()
            context['subscribes_count'] = self.get_object().get_user_s_subscribes.count()
            context['subscribers_prev'] = self.get_object().get_user_s_subscribers[:10]
            # TODO(отсортировать по популярности)

            context['subscribes_prev'] = self.get_object().get_user_s_subscribes[:10]

            return context


class UserDetailView(UserStatisticInContextMixin, DetailView):
    model = User
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        context['super_theme'] = Themes.get_super_themes_by_user(self.get_object()).filter(is_private=False)
        context['super_card'] = Cards.get_super_cards_by_user(self.get_object()).filter(is_private=False)
        context['is_request_user_subscribed'] = self.get_object().is_user_subscribed(
            self.request.user) if self.request.user.is_authenticated else False

        return context


class UserUpdateView(UserStatisticInContextMixin, UpdateView, LoginRequiredMixin):
    form_class = UserUpdateForm
    template_name = 'users/my_profile.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('users:my_profile')

    def post(self, request, *args, **kwargs):
        old_user_email = self.request.user.email
        post = super(UserUpdateView, self).post(request, *args, **kwargs)

        if self.request.POST['email'] != old_user_email:
            user = request.user
            user.is_email_verified = False
            user.save()
            send_verify_email.delay(user.pk)
            logout(self.request)
            return redirect("main:index")

        return post


def del_user(request):
    request.user.delete()
    return redirect(reverse('main:index'))


# Auth
class RegistrationUser(View):
    template_name = 'users/registration/reg.html'
    form_class = UserForm

    def get(self, request):
        context = {
            'form': self.form_class()
        }

        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            send_verify_email.delay(user.pk)
            return redirect('users:confirm_your_email')

        return render(request, self.template_name, {'form': form})


class UserLoginUser(LoginView):
    form_class = UserAuthenticationForm
    template_name = 'users/registration/login.html'

    def get_success_url(self):
        return reverse_lazy('main:index')


class ConfirmEmailTemplateView(TemplateView):
    template_name = 'users/registration/confirm_your_email.html'


class EmailVerify(View):
    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)
        if user is not None and default_token_generator.check_token(user, token):
            user.is_email_verified = True
            user.save()
            login(request, user)
            return redirect(reverse('main:index'))
        return redirect(reverse('users:verify_error', args={user.pk}))

    @staticmethod
    def get_user(uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            user = None

        return user


def verify_error(request, user_pk):
    send_verify_email.delay(user_pk)
    return render(request, 'users/registration/verify_error.html')


def logout_user(request):
    logout(request)
    return redirect("main:index")


# ResetPassword
def password_reset_request_view(request):
    password_reset_form = PasswordResetForm()
    if request.method == 'POST':
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            email = password_reset_form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except Exception:
                user = False
                print('Пользователя с такой почтой не существует')
                # TODO(ВЫВЕСТИ ОШИБКУ ФОРМЫ)

            if user:
                if not user.is_email_verified:
                    raise ValidationError(
                        'Подтвердите почту',
                        code='invalid_login'
                    )

                subject = 'Запрос на сброс пароля'
                context = {

                    'domain': settings.DOMAIN_NAME,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user)

                }
                msg = render_to_string('users/registration/password_reset/password_reset_email.html', context)
                email_data = {
                    "subject": subject,
                    "message": msg,
                    "from_email": settings.EMAIL_HOST_USER,
                    "recipient_list": [user.email]
                }

                send_notification.delay(email_data)

                return redirect('users:password_reset_done')

    return render(request, 'users/registration/password_reset/password_reset.html', {'form': password_reset_form})


@login_required
def subscribe(request, author_pk):
    author = User.objects.get(pk=author_pk)
    subscribe = Subscribes.objects.filter(author=author, subscriber=request.user)

    if subscribe:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    if author.is_receive_notifications:
        email_data = {

            'subject': f'Пользователь {request.user.username} подписался на ваши обновления...',
            'recipient_list': [author.email],
            'message': f'Пользователь {request.user.username} подписался на ваши обновления...',

        }
    else:
        email_data = None

    send_notification.delay(email_data)

    Subscribes.objects.create(author=author, subscriber=request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def unsubscribe(request, author_pk):
    author = User.objects.get(pk=author_pk)
    Subscribes.objects.filter(author=author, subscriber=request.user).delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
