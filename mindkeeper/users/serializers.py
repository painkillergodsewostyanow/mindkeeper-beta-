from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from main.models import Themes, Cards
from .models import User


class CurrentUserSerializer(serializers.ModelSerializer):
    """ Для вывода станицы конкретного
    пользователя (расширенная инфа) """

    total_likes = SerializerMethodField(method_name='get_total_likes')
    total_comments = SerializerMethodField(method_name='get_total_comments')
    total_views = SerializerMethodField(method_name='get_total_views')
    
    class Meta:
        model = User
        fields = (
            'username',
            'image',
            'email',
            'last_login',
            'total_likes',
            'total_comments',
            'total_views',
            'total_subscribers',
            'total_subscribes'
        )

    def get_total_likes(self, obj):
        theme_likes = Themes.count_user_s_likes_received(obj)
        card_likes = Cards.count_user_s_likes_received(obj)
        return theme_likes if theme_likes is not None else 0 + card_likes if card_likes is not None else 0

    def get_total_views(self, obj):
        theme_views = Themes.count_user_s_views_received(obj)
        card_views = Cards.count_user_s_views_received(obj)
        return theme_views if theme_views is not None else 0 + card_views if card_views is not None else 0

    def get_total_comments(self, obj):
        theme_comments = Themes.count_user_s_comment_received(obj)
        card_comments = Cards.count_user_s_comment_received(obj)
        return theme_comments if theme_comments is not None else 0 + card_comments if card_comments is not None else 0


class UsersSerializer(serializers.ModelSerializer):
    """ Для вывода preview пользователя
    (на главной в поиске и тд)  """

    class Meta:
        model = User
        fields = ('username', 'image', 'pk')
