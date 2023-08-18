import requests
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.response import Response
from users.models import User
from .models import Themes, Cards, CardComments, ThemeComments
from .scripts import check_access


class ThemesSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Themes
        fields = ('pk', 'image', 'user', 'title', 'parent_theme', 'likes', 'views', 'count_comments')


class CardsSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Cards
        fields = ('pk', 'image', 'user', 'title', 'parent_theme', 'likes', 'views', 'count_comments')


class AuthorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'image', 'username')


class CardCommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardComments
        fields = '__all__'


class ThemeCommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThemeComments
        fields = '__all__'
