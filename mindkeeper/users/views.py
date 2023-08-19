from rest_framework.decorators import action

from main.tasks import send_notification
from users.models import Subscribes, User
from .serializers import CurrentUserSerializer, UsersSerializers
from djoser.views import UserViewSet
from rest_framework.response import Response


class CustomUserViewSet(UserViewSet):
    @action(["get", "put", "patch"], detail=False)
    def me(self, request, *args, **kwargs):
        if request.method == 'GET':
            return Response(CurrentUserSerializer(instance=request.user).data)

        else:
            return super(self.__class__, self).me(request, *args, **kwargs)

    @action(['GET'], detail=False)
    def users_s_subscribes(self, request, *args, **kwargs):
        return Response(UsersSerializers(request.user.get_user_s_subscribes, many=True).data)

    @action(['GET'], detail=False)
    def users_s_subscribers(self, request, *args, **kwargs):
        return Response(UsersSerializers(request.user.get_user_s_subscribers, many=True).data)

    @action(['POST'], detail=False)
    def subscribe(self, request, *args, **kwargs):
        author = User.objects.get(pk=request.data['author_pk'])
        subscribe = Subscribes.objects.filter(author=author, subscriber=request.user)

        if subscribe:
            subscribe.delete()
            return Response({'detail': 'Отписан'})

        if author.is_receive_notifications:
            email_data = {

                'subject': f'Пользователь {request.user.username} подписался на ваши обновления...',
                'recipient_list': [author.email],
                'message': f'Пользователь {request.user.username} подписался на ваши обновления...',

            }
        else:
            email_data = None

        send_notification.delay(email_data)

        Subscribes.objects.create(author=author, subscriber=request.user)
        return Response({'detail': 'Подписан'})
