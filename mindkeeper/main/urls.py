from django.urls import path
from .views import *


app_name = "main"

urlpatterns = [
    path('', IndexTemplateView.as_view(), name="index"),
]

