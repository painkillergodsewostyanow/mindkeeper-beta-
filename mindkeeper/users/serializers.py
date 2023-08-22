from rest_framework import serializers

from main.models import Themes, Cards
from .models import User


class CurrentUserSerializer(serializers.ModelSerializer):
    """ Для вывода станицы конкретного
    пользователя (расширенная инфа) """

    class Meta:
        model = User
        fields = (
            'username',
            'image',
            'email',
            'last_login',
            'total_like',
            'total_comments',
            'total_views',
            'total_subscribers',
            'total_subscribes'
        )


class UsersSerializer(serializers.ModelSerializer):
    """ Для вывода preview пользователя
    (на главной в поиске и тд)  """

    class Meta:
        model = User
        fields = ('username', 'image', 'pk')
