from django.urls import path
from .views import *


app_name = "users"

urlpatterns = [
    path('storage', MyStorageListView.as_view(), name="storage"),
    path('storage/card/<int:id>', CardDetailView.as_view(), name="card")
]

