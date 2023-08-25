
from rest_framework import serializers
from .models import Themes, Cards, CardComments, ThemeComments


class ThemesSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    count_likes = serializers.IntegerField(read_only=True)
    count_comments = serializers.IntegerField(read_only=True)
    count_views = serializers.IntegerField(read_only=True)

    class Meta:
        model = Themes
        fields = ('pk', 'user', 'title', 'is_private', 'parent_theme', 'count_likes', 'count_comments', 'count_views', 'comments', 'sub_themes', 'sub_cards')
        extra_kwargs = {'comments': {'required': False}, 'sub_themes': {'required': False}, 'sub_cards': {'required': False}}


class CardsSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    count_likes = serializers.IntegerField(read_only=True)
    count_comments = serializers.IntegerField(read_only=True)
    count_views = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cards
        fields = ('pk', 'user', 'title', 'is_private', 'count_likes', 'count_comments', 'count_views', 'comments')
        extra_kwargs = {'comments': {'required': False}}


class CardCommentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CardComments
        fields = '__all__'
        extra_kwargs = {'user': {'required': False}}


class ThemeCommentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ThemeComments
        fields = '__all__'
        extra_kwargs = {'user': {'required': False}}

