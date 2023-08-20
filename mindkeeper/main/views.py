from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, \
    ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from users.serializers import UsersSerializer
from .models import ThemeLikes, CardLikes, ThemeAccess, CardAccess
from .permissions import CheckCardAndThemesAccess, CheckCommentsAccess
from .serializers import *
from rest_framework.reverse import reverse
from django.conf import settings
from email_app.tasks import send_email


class IndexAPIView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            storage_preview = [
                {'themes': Themes.get_super_themes_by_user(request.user).values('title', 'pk')},
                {'cards': Cards.get_super_cards_by_user(request.user).values('title', 'pk')}
            ]
        else:
            storage_preview = 'login_required'

        authors = UsersSerializer(User.most_popular_authors(), many=True).data
        themes = ThemesSerializer(Themes.most_popular_theme(), many=True).data
        cards = CardsSerializer(Cards.most_popular_cards(), many=True).data

        most_popular = {

            'authors': authors,
            'themes': themes,
            'cards': cards

        }

        return Response({'storage_preview': storage_preview, 'most_popular': most_popular})


@api_view(('GET',))
@permission_classes([IsAuthenticated])
def storage_api_view(request):
    query = request.GET.get('query')

    if query:
        themes = Themes.objects.filter(user=request.user, search_vector=query)
        cards = Cards.objects.filter(user=request.user, search_vector=query)

        if not themes and not cards:
            return Response({'detail': 'совпадений не найденно'})

        else:
            return Response(
                {
                    'themes': ThemesSerializer(themes, many=True).data,
                    'cards': CardsSerializer(cards, many=True).data
                }
            )

    else:
        themes = Themes.get_super_themes_by_user(request.user)
        cards = Cards.get_super_cards_by_user(request.user)

        return Response(
            {
                'themes': ThemesSerializer(themes, many=True).data,
                'cards': CardsSerializer(cards, many=True).data
            }
        )


class ThemesViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = ThemesSerializer
    queryset = Themes.objects.all()
    permission_classes = (CheckCardAndThemesAccess,)

    def retrieve(self, request, *args, **kwargs):
        father_theme = get_object_or_404(Themes, pk=kwargs['pk'])
        request.user.has_perm(CheckCardAndThemesAccess, self.get_object())
        sub_themes = father_theme.get_sub_themes
        cards = father_theme.get_cards
        return Response(
            {
                'father_theme': ThemesSerializer(father_theme).data,
                'themes': ThemesSerializer(sub_themes, many=True).data,
                'cards': CardsSerializer(cards, many=True).data,
                'comments': ThemeCommentsSerializer(father_theme.comments, many=True).data
            }
        )

    @action(['GET'], detail=True)
    def who_likes(self, request, pk):
        request.user.has_perm(CheckCardAndThemesAccess, self.get_object())
        theme = get_object_or_404(Themes, pk=pk)
        like_objs = ThemeLikes.objects.filter(theme=theme)
        users = [like_obj.user for like_obj in like_objs]
        return Response({'users_who_likes': UsersSerializer(users, many=True).data})

    @action(['POST'], detail=True)
    def like(self, request, pk):
        theme = Themes.objects.filter(pk=pk).first()
        like_obj = ThemeLikes.objects.filter(user=request.user, theme=theme).first()
        like_counter = ThemeLikes.objects.filter(theme=theme)

        if like_obj:
            like_obj.delete()
            return Response({'like_count': like_counter.count()})

        ThemeLikes.objects.create(user=request.user, theme=theme)

        return Response({'like_count': like_counter.count()})


class CardsViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = CardsSerializer
    queryset = Cards.objects.all()
    permission_classes = (CheckCardAndThemesAccess,)

    def retrieve(self, request, *args, **kwargs):
        request.user.has_perm(CheckCardAndThemesAccess, self.get_object())
        card = get_object_or_404(Cards, pk=kwargs['pk'])
        return Response(
            {'card': CardsSerializer(card).data, 'comments': CardCommentsSerializer(card.comments, many=True).data})

    @action(['GET'], detail=True)
    def who_likes(self, request, pk):
        request.user.has_perm(CheckCardAndThemesAccess, self.get_object())
        card = get_object_or_404(Cards, pk=pk)
        like_objs = CardLikes.objects.filter(card=card)
        users = [like_obj.user for like_obj in like_objs]
        return Response({'users_who_likes': UsersSerializer(users, many=True).data})

    @action(['POST'], detail=True)
    def like(self, request, pk):
        card = Cards.objects.filter(pk=pk).first()
        like_obj = CardLikes.objects.filter(user=request.user, card=card).first()
        like_counter = CardLikes.objects.filter(card=card)

        if like_obj:
            like_obj.delete()
            return Response({'like_count': like_counter.count()})

        CardLikes.objects.create(user=request.user, card=card)

        return Response({'like_count': like_counter.count()})


class ThemesCommentsViewSet(ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin,
                            GenericViewSet):
    serializer_class = ThemeCommentsSerializer
    queryset = ThemeComments.objects.all()
    permission_classes = (CheckCommentsAccess,)


class CardsCommentsViewSet(ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin,
                           GenericViewSet):
    serializer_class = CardCommentsSerializer
    queryset = CardComments.objects.all()
    permission_classes = (CheckCommentsAccess,)


# ACCESS TO CARD/THEME
@api_view(('GET',))
@permission_classes([IsAuthenticated])
def request_access_to_theme_api(request, user_pk, theme_pk):
    theme = Themes.objects.filter(pk=theme_pk).first()
    link = f'{reverse("main:give_access_to_theme_api", args=[user_pk, theme_pk], request=request)}'
    user = request.user
    access = ThemeAccess.objects.filter(user=user, theme=theme)
    if access.exists():
        return Response({'detail': 'Доступ уже имеется'})

    send_email.delay({
        'subject': f"Пользователь {request.user.username} запрашивает доступ к теме {theme.title}",
        'recipient_list': [theme.user.email],
        'message': f"Пользователь {request.user.username} запрашивает доступ к теме {theme.title} \n"
                   f"что бы выдать доступ перейдите по ссылке: {link}",
    })

    return Response({'detail': 'Запрос успешно отправлен! '})


@api_view(('POST',))
@permission_classes([IsAuthenticated])
def give_access_to_theme_api(request, user_pk, theme_pk):
    user = User.objects.get(pk=user_pk)
    theme = Themes.objects.get(pk=theme_pk)
    access = ThemeAccess.objects.filter(user=user, theme=theme)
    if access.exists():
        return Response({'detail': 'Доступ уже имеется'})

    if not request.user == theme.user:
        return Response({'detail': 'Доступ может выдать только автор'})

    ThemeAccess.objects.create(user=user, theme=Themes.objects.get(pk=theme_pk))

    send_email.delay({

        'subject': f"Пользователь {theme.user.username} выдал вам доступ к теме {theme.title}",
        'recipient_list': [user.email],
        'message': f"Пользователь {theme.user.username} выдал вам доступ к теме {theme.title}",

    })

    return Response({'detail': 'Доступ успешно выдан!'})


@api_view(('POST',))
@permission_classes([IsAuthenticated])
def request_access_to_card_api(request, user_pk, card_pk):
    card = Cards.objects.filter(pk=card_pk).first()
    link = f'{settings.DOMAIN_NAME}{reverse("main:give_access_to_card_api", args=[user_pk, card_pk])}'
    user = request.user

    access = CardAccess.objects.filter(user=user, card=card.pk)
    if access.exists():
        return Response({'detail': 'Доступ уже имеется'})

    send_email.delay({
        'subject': f"Пользователь {request.user.username} запрашивает доступ к карточке {card.title}",
        'recipient_list': [card.user.email],
        'message': f"Пользователь {request.user.username} запрашивает доступ к карточке {card.title} \n"
                   f"что бы выдать доступ перейдите по ссылке: {link}",
    })

    return Response({'detail': 'Запрос успешно отправлен! '})


@api_view(('POST',))
@permission_classes([IsAuthenticated])
def give_access_to_card_api(request, user_pk, card_pk):
    user = User.objects.get(pk=user_pk)
    card = Cards.objects.get(pk=card_pk)

    access = CardAccess.objects.filter(user=user, card=card)
    if access.exists():
        return Response({'detail': 'Доступ уже имеется'})

    if not request.user == card.user:
        return Response({'detail': 'Доступ может выдать только автор'})

    CardAccess.objects.create(user=user, card=Cards.objects.get(pk=card_pk))

    send_email.delay({

        'subject': f"Пользователь {card.user.username} выдал вам доступ к карточке {card.title}",
        'recipient_list': [user.email],
        'message': f"Пользователь {card.user.username} выдал вам доступ к карточке {card.title}",

    })

    return Response({'detail': 'Доступ успешно выдан!'})


@api_view(['GET'])
def global_search_api(request):
    query = request.GET.get('query', False)
    if query:
        # Поиск по запросу
        themes = Themes.objects.filter(search_vector=query, is_private=False)[:6]
        cards = Cards.objects.filter(search_vector=query, is_private=False)[:6]
        authors = User.objects.filter(username__icontains=query, is_private=False)[:6]

    else:
        # TODO(ПРЕДПОЧТЕНИЯ)
        # если в запросе пустая строка
        themes = Themes.objects.filter(is_private=False)[:6]
        cards = Cards.objects.filter(is_private=False)[:6]
        authors = User.objects.filter(is_private=False)[:6]

    if not themes and not authors and not cards:
        return Response({'detail': 'Совпадений не найденно'})

    return Response({
        'themes': ThemesSerializer(themes, many=True).data,
        'cards': CardsSerializer(cards, many=True).data,
        'authors': UsersSerializer(authors, many=True).data
    })
