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
    path('api/v1/global_search', global_search_api),

    path('api/v1/request_access_to/themes/<int:theme_pk>/to/users/<int:user_pk>', request_access_to_theme_api),
    path('api/v1/give_access_to/themes/<int:theme_pk>/to/users/<int:user_pk>', give_access_to_theme_api,
         name='give_access_to_theme_api'),

    path('api/v1/request_access_to/cards/<int:card_pk>/to/users/<int:user_pk>', request_access_to_card_api),
    path('api/v1/give_access_to/cards/<int:card_pk>/to/users/<int:user_pk>', give_access_to_card_api,
         name='give_access_to_card_api'),

]
