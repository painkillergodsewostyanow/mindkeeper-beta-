from django.urls import path
from .views import *


app_name = "users"

urlpatterns = [
    path('login/', LoginUser.as_view(), name="login"),
    path('logout/', logout_user, name='logout'),
    path('registration', RegistrationUser.as_view(), name="reg"),
    path('my_profile', UserUpdateView.as_view(), name="my_profile"),
    path('profile/<int:pk>', UserDetailView.as_view(), name="profile"),
    path('profile/<int:author_pk>/subscribe', subscribe, name="subscribe"),
    path('profile/<int:author_pk>/unsubscribe', unsubscribe, name="unsubscribe")
]
