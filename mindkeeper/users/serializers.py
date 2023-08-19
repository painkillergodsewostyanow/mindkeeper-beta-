from rest_framework import serializers

from .models import User


class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'image', 'email', 'last_login', 'total_like', 'total_comments', 'total_views', 'total_subscribers',
                  'total_subscribes')


class UsersSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'image', 'pk')
