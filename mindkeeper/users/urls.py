from django.urls import path
from .views import *


app_name = "users"

urlpatterns = [
    path('login/', LoginUser.as_view(), name="login"),
    path('logout/', logout_user, name='logout'),
    path('registration', RegistrationUser.as_view(), name="reg"),
    path('profile/<int:pk>', UserUpdateView.as_view(), name="profile")
]
