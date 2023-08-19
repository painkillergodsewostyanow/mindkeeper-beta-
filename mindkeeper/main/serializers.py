from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from users.models import User
from .models import Themes, Cards, CardComments, ThemeComments


class ThemesSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Themes
        fields = ('pk', 'image', 'user', 'title', 'is_private', 'parent_theme', 'likes', 'views', 'count_comments')


class CardsSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Cards
        fields = ('pk', 'image', 'user', 'title', 'is_private', 'parent_theme', 'likes', 'views', 'count_comments')


class AuthorsSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = User
        fields = ('pk', 'image', 'username')


class CardCommentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CardComments
        fields = '__all__'
        extra_kwargs = {'user': {'required': False}}

    def create(self, validated_data):
        request = self.context.get("request")

        comment = CardComments()
        comment.user = request.user
        comment.content = self.validated_data['content']
        comment.sub_comment_to = self.validated_data.get('sub_comment_to', None)
        comment.card = self.validated_data['card']
        comment.sub_comment_to = self.validated_data.get('sub_comment_to', None)
        comment.save()

        return comment


class ThemeCommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThemeComments
        fields = '__all__'
        extra_kwargs = {'user': {'required': False}}

    def create(self, validated_data):
        request = self.context.get("request")

        comment = ThemeComments()
        comment.user = request.user
        comment.content = self.validated_data['content']
        comment.sub_comment_to = self.validated_data.get('sub_comment_to', None)
        comment.theme = self.validated_data['theme']
        comment.sub_comment_to = self.validated_data.get('sub_comment_to', None)
        comment.save()

        return comment

