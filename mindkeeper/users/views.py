from django.shortcuts import get_object_or_404
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny

from users.models import Subscribes, User
from .serializers import CurrentUserSerializer, UsersSerializer
from djoser.views import UserViewSet
from rest_framework.response import Response


class CustomUserViewSet(UserViewSet):
    @action(["get", "put", "patch"], detail=False)
    def me(self, request, *args, **kwargs):
        if request.method == 'GET':
            return Response(CurrentUserSerializer(instance=request.user).data)

        else:
            return super(self.__class__, self).me(request, *args, **kwargs)

    @permission_classes([AllowAny])
    def retrieve(self, request, *args, **kwargs):
        return Response(CurrentUserSerializer(instance=get_object_or_404(User, pk=kwargs['id'])).data)

    @action(['GET'], detail=True)
    def users_s_subscribes(self, request, *args, **kwargs):
        return Response(UsersSerializer(get_object_or_404(User, pk=kwargs['id']).get_user_s_subscribes, many=True).data)

    @action(['GET'], detail=True)
    def users_s_subscribers(self, request, *args, **kwargs):
        return Response(UsersSerializer(get_object_or_404(User, pk=kwargs['id']).get_user_s_subscribers, many=True).data)

    @action(['POST'], detail=True)
    def subscribe(self, request, *args, **kwargs):
        author = User.objects.get(pk=kwargs['id'])
        subscribe = Subscribes.objects.filter(author=author, subscriber=request.user)

        if subscribe:
            subscribe.delete()
            return Response({'detail': 'Отписан'})

        Subscribes.objects.create(author=author, subscriber=request.user)

        return Response({'detail': 'Подписан'})
