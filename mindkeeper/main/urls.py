from django.urls import path, include
from rest_framework.routers import SimpleRouter
from users.views import CustomUserViewSet
from .views import *

app_name = "main"

themes_router = SimpleRouter()
cards_router = SimpleRouter()
themes_comments_router = SimpleRouter()
cards_comments_router = SimpleRouter()
users_router = SimpleRouter()
themes_router.register('themes', ThemesViewSet)
cards_router.register('cards', CardsViewSet)
themes_comments_router.register('themes_comments', ThemesCommentsViewSet)
cards_comments_router.register('cards_comments', CardsCommentsViewSet)
users_router.register('users', CustomUserViewSet)

urlpatterns = [
    path('api/v1/index', IndexAPIView.as_view()),
    path('api/v1/auth/', include('djoser.urls')),
    path('api/v1/auth/', include('djoser.urls.authtoken')),
    path('api/v1/storage', storage_api_view),
    path('api/v1/', include(themes_router.urls)),
    path('api/v1/', include(cards_router.urls)),
    path('api/v1/', include(themes_comments_router.urls)),
    path('api/v1/', include(cards_comments_router.urls)),
    path('api/v1/', include(users_router.urls)),
    path('', IndexTemplateView.as_view(), name="index"),
    path('storage', storage, name="storage"),
    path('storage/theme/<int:parent_theme>', open_theme, name="open_theme"),
    path('storage/card/<int:card>', open_card, name="open_card"),
    path('storage/parent_theme/<int:parent_theme>/add_card_form', AddCardView.as_view(), name="add_card_form"),
    path('storage/add_card_form', AddCardView.as_view(), name="add_card_form"),
    path('storage/add_card', AddCardView.as_view(), name="add_card"),
    path('storage/add_theme_form', AddThemeView.as_view(), name="add_theme_form"),
    path('storage/parent_theme/<int:parent_theme>/add_theme_form', AddThemeView.as_view(), name="add_theme_form"),
    path('storage/add_theme', AddThemeView.as_view(), name="add_theme"),
    path('storage/parent_theme/<int:pk>/change_theme', EditTheme.as_view(), name='edit_theme'),
    path('storage/card/<int:pk>/change_card', EditCard.as_view(), name='edit_card'),
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
    path('storage/edit_card_comment/<int:comment_pk>', edit_card_comment, name="edit_card_comment"),
    path('storage/edit_theme_comment/<int:comment_pk>', edit_theme_comment, name="edit_theme_comment"),
    path('storage/request_access_to_theme/<int:user_pk>/to/<int:theme_pk>', request_access_to_theme,
         name="request_access_to_theme"),
    path('storage/request_access_to_card/<int:user_pk>/to/<int:card_pk>', request_access_to_card,
         name="request_access_to_card"),
    path('storage/give_access_to_theme/<int:user_pk>/to/<int:theme_pk>', give_access_to_theme,
         name="give_access_to_theme"),
    path('storage/give_access_to_card/<int:user_pk>/to/<int:card_pk>', give_access_to_card,
         name="give_access_to_card"),

    path('storage/parent_theme/<int:theme_pk>/who_like', show_users_who_like_theme_list, name="show_who_like_theme"),
    path('storage/card/<int:card_pk>/who_like', show_users_who_like_card_list, name="show_who_like_card"),

]
