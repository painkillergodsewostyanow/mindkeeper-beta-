from django.urls import path
from .views import *


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
    path('profile/verify_error/<int:user_pk>', verify_error, name="verify_error")
]
