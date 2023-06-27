from django.views.generic import ListView, DetailView
from .models import *


class MyStorageSuperThemeListView(ListView):
    model = Themes
    template_name = "users/catalog.html"

    def get_queryset(self):
        queryset = self.request.user.get_super_themes
        return queryset


class MyStorageListView(ListView):
    ...
    # TODO(углубление в темы а не только superTheme)


class CardDetailView(DetailView):
    model = Cards
    template_name = "users/card.html"
    pk_url_kwarg = "id"
    context_object_name = "card"

    # TODO(фильтрация по авторизованному пользователю)

