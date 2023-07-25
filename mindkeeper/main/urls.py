from django.urls import path, include
from .views import *


app_name = "main"

urlpatterns = [
    path('', IndexTemplateView.as_view(), name="index"),
    path('storage', storage, name="storage"),
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
    path('storage/del_theme/<int:theme_pk>', delete_theme, name="del_theme"),
    path('storage/del_card/<int:card_pk>', delete_card, name="del_card"),
    path('storage/global_search', global_search, name="global_search"),
    path('storage/global_search_json', global_search_ajax_json, name="global_search_ajax_json"),
    path('storage/local_search_ajax', local_search_ajax_json, name="local_search_ajax"),
    path('storage/<int:theme_pk>/like_theme', like_theme, name="like_theme"),
    path('storage/<int:card_pk>/like_card', like_card, name="like_card"),
    path('storage/add_comment_to_theme', add_comment_to_theme, name="add_comment_to_theme"),
    path('storage/add_comment_to_card', add_comment_to_card, name="add_comment_to_card"),
    path('storage/add_comment_to_card_comment', add_comment_to_card_comment, name="add_comment_to_card_comment"),
    path('storage/add_comment_to_theme_comment', add_comment_to_theme_comment, name="add_comment_to_theme_comment"),
    path('storage/<int:comment_pk>/del_comment_from_card', delete_comment_from_card, name='del_comment_from_card'),
    path('storage/<int:comment_pk>/del_comment_from_theme', delete_comment_from_theme, name='del_comment_from_theme'),
]


