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
        return Themes.count_user_s_likes_received(obj) + Cards.count_user_s_likes_received(obj)

    def get_total_views(self, obj):
        return Themes.count_user_s_views_received(obj) + Cards.count_user_s_views_received(obj)

    def get_total_comments(self, obj):
        return Themes.count_user_s_comment_received(obj) + Cards.count_user_s_comment_received(obj)


class UsersSerializer(serializers.ModelSerializer):
    """ Для вывода preview пользователя
    (на главной в поиске и тд)  """

    class Meta:
        model = User
        fields = ('username', 'image', 'pk')
