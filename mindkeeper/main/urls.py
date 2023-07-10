from django.urls import path
from .views import *


app_name = "main"

urlpatterns = [
    path('', IndexTemplateView.as_view(), name="index"),
    path('storage', super_theme_and_card_list_view, name="storage"),
    path('storage/theme/<int:theme>', open_theme, name="open_theme"),
    path('storage/theme/<int:theme>/card/<int:card>', open_card, name="open_card"),
    path('storage/card/<int:card>', open_card, name="open_card"),
    path('storage/theme/<int:theme>/add_card_form', add_card_form, name="add_card_form"),
    path('storage/add_card_form', add_card_form, name="add_card_form"),
    path('storage/add_card', add_card, name="add_card"),
    path('storage/add_theme_form', add_theme_form, name="add_theme_form"),
    path('storage/theme/<int:theme>/add_theme_form', add_theme_form, name="add_theme_form"),
    path('storage/add_theme', add_theme, name="add_theme"),
    path('storage/theme/<int:pk>/change_theme', EditTheme.as_view(), name='edit_theme'),
    path('storage/card/<int:pk>/change_theme', EditCard.as_view(), name='edit_card'),
    path('storage/del_theme/<int:theme>', del_theme, name="del_theme"),
    path('storage/del_card/<int:card>', del_card, name="del_card"),
    path('global_search', global_search, name="global_search"),
]


