from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from users.models import User
from .models import Themes, Cards, CardComments, ThemeComments


class ThemesSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Themes
        fields = ('pk', 'user', 'title', 'is_private', 'parent_theme', 'likes', 'views', 'count_comments')


class CardsSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Cards
        fields = ('pk', 'user', 'title', 'is_private', 'parent_theme', 'likes', 'views', 'count_comments')


class CardCommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardComments
        fields = '__all__'
        extra_kwargs = {'user': {'required': False}}

    def create(self, validated_data):
        request = self.context.get("request")

        sub_comment_to = validated_data.get('sub_comment_to', None)
        comment = CardComments()
        comment.user = request.user
        comment.content = self.validated_data['content']
        comment.sub_comment_to = sub_comment_to

        if sub_comment_to:
            comment.card = get_object_or_404(CardComments, pk=sub_comment_to).card

        else:
            comment.card = validated_data['card']

        comment.save()

        return comment


class ThemeCommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThemeComments
        fields = '__all__'
        extra_kwargs = {'user': {'required': False}}

    def create(self, validated_data):
        request = self.context.get("request")

        sub_comment_to = validated_data.get('sub_comment_to', None)
        comment = ThemeComments()
        comment.user = request.user
        comment.content = self.validated_data['content']
        comment.sub_comment_to = sub_comment_to

        if sub_comment_to:
            comment.theme = get_object_or_404(ThemeComments, pk=sub_comment_to).theme

        else:
            comment.theme = validated_data['theme']

        comment.save()

        return comment
