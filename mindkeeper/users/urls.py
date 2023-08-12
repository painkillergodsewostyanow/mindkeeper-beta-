from django.urls import path
from .views import *
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView, \
    PasswordChangeView

app_name = "users"

urlpatterns = [
    path('login/', UserLoginUser.as_view(), name="login"),
    path('logout/', logout_user, name='logout'),
    path('registration', RegistrationUser.as_view(), name="reg"),
    path('my_profile', UserUpdateView.as_view(), name="my_profile"),
    path('profile/<int:pk>', UserDetailView.as_view(), name="profile"),
    path('profile/<int:author_pk>/subscribe', subscribe, name="subscribe"),
    path('profile/<int:author_pk>/unsubscribe', unsubscribe, name="unsubscribe"),
    path('profile/delete_user', del_user, name="delete_user"),
    path('profile/confirm_your_email', ConfirmEmailTemplateView.as_view(), name="confirm_your_email"),
    path('verify_email/<uidb64>/<token>', EmailVerify.as_view(), name="verify_email"),
    path('profile/verify_error/<int:user_pk>', verify_error, name="verify_error"),

    path('profile/password_reset', password_reset_request_view, name='password_reset'),

    path('profile/password_reset/done/',
         PasswordResetDoneView.as_view(template_name='users/registration/password_reset/password_reset_done.html'),
         name="password_reset_done"),

    path('profile/reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='users/registration/password_reset/password_reset_form.html',
                                          success_url=reverse_lazy('users:login')), name='password_reset_confirm'),

    path('profile/<int:user_pk>/subscribers', show_users_who_subscribes_list, name="show_subscribers"),
    path('profile/<int:user_pk>/subscribes', show_user_s_subscribes_list, name="show_subscribes"),

    path('my_profile/password_change/',
         PasswordChangeView.as_view(template_name='users/registration/password_change_view.html',
                                    success_url=reverse_lazy('users:password_change_done')),
         name="password_change"),

    path('my_profile/password_change/done/', password_change_done, name='password_change_done')

]
