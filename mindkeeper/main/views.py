from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView, UpdateView
from django.shortcuts import render, HttpResponseRedirect, redirect
from rest_framework.decorators import api_view
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, \
    ListModelMixin

from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from users.serializers import UsersSerializers
from .permissions import CheckCardAndThemesAccess, CheckCommentsAccess
from .serializers import *
from .forms import *
from django.urls import reverse, reverse_lazy
from .scripts import check_access, ajax_or_api_login_required
from django.conf import settings
from main.tasks import send_notification
from django.contrib.auth.mixins import LoginRequiredMixin


class IndexAPIView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            storage_preview = [
                {'themes': Themes.get_super_themes_by_user(request.user).values('title', 'pk')},
                {'cards': Cards.get_super_cards_by_user(request.user).values('title', 'pk')}
            ]
        else:
            storage_preview = 'login_required'

        authors = UsersSerializers(User.most_popular_authors(), many=True).data
        themes = ThemesSerializer(Themes.most_popular_theme(), many=True).data
        cards = CardsSerializer(Cards.most_popular_cards(), many=True).data

        most_popular = {

            'authors': authors,
            'themes': themes,
            'cards': cards

        }

        return Response({'storage_preview': storage_preview, 'most_popular': most_popular})


class IndexTemplateView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexTemplateView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['super_themes'] = Themes.get_super_themes_by_user(self.request.user)
            context['super_cards'] = Cards.get_super_cards_by_user(self.request.user)

        context['most_popular_authors'] = User.most_popular_authors()
        context['most_popular_themes'] = Themes.most_popular_theme()
        context['most_popular_cards'] = Cards.most_popular_cards()

        return context


@api_view(('GET',))
@ajax_or_api_login_required
def storage_api_view(request):
    query = request.GET.get('query')

    if query:
        themes = Themes.objects.filter(user=request.user, search_vector=query)
        cards = Cards.objects.filter(search_vector=query, user=request.user)

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


@login_required
def storage(request):
    query = request.GET.get('query')

    if query:
        themes = Themes.objects.filter(user=request.user, title__icontains=query)

        cards = Cards.objects.filter(title__icontains=query, user=request.user)

        if not themes and not cards:
            context = {

                'message': "По данному запросу совпадени не найденно"

            }

        else:

            context = {

                'themes': themes,
                'cards': cards

            }

        return render(request, "main/catalog.html", context)

    else:
        themes = Themes.get_super_themes_by_user(request.user)
        cards = Cards.get_super_cards_by_user(request.user)

        context = {

            'themes': themes,
            'cards': cards

        }

    return render(request, "main/catalog.html", context)


class ThemesViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = ThemesSerializer
    queryset = Themes.objects.all()
    permission_classes = (CheckCardAndThemesAccess, )

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


class CardsViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = CardsSerializer
    queryset = Cards.objects.all()
    permission_classes = (CheckCardAndThemesAccess, )

    def retrieve(self, request, *args, **kwargs):
        request.user.has_perm(CheckCardAndThemesAccess, self.get_object())
        card = get_object_or_404(Cards, pk=kwargs['pk'])
        return Response({'card': CardsSerializer(card).data, 'comments': CardCommentsSerializer(card.comments, many=True).data})


class ThemesCommentsViewSet(ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = ThemeCommentsSerializer
    queryset = ThemeComments.objects.all()
    permission_classes = (CheckCommentsAccess, )


class CardsCommentsViewSet(ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = CardCommentsSerializer
    queryset = CardComments.objects.all()
    permission_classes = (CheckCommentsAccess,)


def open_theme(request, theme):
    father_theme = theme
    theme = Themes.objects.filter(pk=theme).first()

    if theme:

        if request.user.is_authenticated:
            if not ThemeViews.objects.filter(obj=theme, user=request.user).first():
                ThemeViews.objects.create(obj=theme, user=request.user)

        if theme.is_private:
            if check_access(request.user, theme, theme.users_with_access):
                context = {
                    'father_theme': Themes.objects.filter(pk=father_theme).first(),
                    "themes": Themes.objects.filter(sub_theme_to=theme),
                    "cards": Cards.objects.filter(theme=theme)
                }

            else:
                context = {
                    'request_access_link': f'{settings.DOMAIN_NAME}{reverse_lazy("main:request_access_to_theme", kwargs={"user_pk": request.user.pk, "theme_pk": theme.pk})}'
                }
        else:
            context = {
                'father_theme': Themes.objects.filter(pk=father_theme).first(),
                "themes": Themes.objects.filter(sub_theme_to=theme),
                "cards": Cards.objects.filter(theme=theme)
            }

        return render(request, "main/catalog.html", context)
    else:
        ...
        # TODO(404)


def open_card(request, card):
    card = Cards.objects.filter(pk=card).first()
    if card:
        if request.user.is_authenticated:
            if not CardViews.objects.filter(obj=card, user=request.user).first():
                CardViews.objects.create(obj=card, user=request.user)

        if card.is_private:
            if check_access(request.user, card, card.users_with_access):
                context = {'card': card}

            else:
                context = {
                    'request_access_link': f'{settings.DOMAIN_NAME}{reverse_lazy("main:request_access_to_card", kwargs={"user_pk": request.user.pk, "card_pk": card.pk})}'
                }
        else:
            context = {'card': card}

        return render(request, "main/card.html", context)
    else:
        ...
        # TODO(404)


class AddCardView(View, LoginRequiredMixin):
    def get(self, request, theme=None):
        theme = Themes.objects.filter(pk=theme).first()
        form = CardForm

        if theme:
            if not check_access(request.user, theme):
                print('доступа нет')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            context = {'form': form, 'parent_theme': theme.pk}

        else:
            context = {'form': form}

        return render(request, "main/add_card.html", context)

    def post(self, request):
        is_private = 'is_private' in request.POST
        theme = Themes.objects.get(pk=request.POST['parent_theme']) if request.POST['parent_theme'] else None
        image = request.FILES.get('image')

        card = Cards.objects.create(
            user=request.user,
            image=image,
            is_private=is_private,
            theme=theme,
            title=request.POST['title'],
            content=request.POST['content']
        )
        if not is_private:
            if request.user.get_user_s_subscribers:
                subscribers = request.user.get_user_s_subscribers
                subscribers_email = [sub.subscriber.email for sub in subscribers if
                                     sub.subscriber.is_receive_notifications]

                email_data = {
                    'subject': f'У {request.user.username} новая карточка! {request.POST["title"]}',
                    'recipient_list': subscribers_email,
                    'message': f'У {request.user.username} новая карточка! {request.POST["title"]}\n'
                               f'это сообщение пришло вам так как вы подписанны на {request.user.username}\n'
                               f'если вы хотите отменить рассылку #TODO()'
                }

                send_notification.delay(email_data)

        return redirect(reverse('main:open_card', kwargs={'card': card.pk}))


class AddThemeView(View, LoginRequiredMixin):
    def get(self, request, theme=None):
        theme = Themes.objects.filter(pk=theme).first()
        form = ThemeForm
        if theme:
            if not check_access(request.user, theme):
                print('доступа нет')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            context = {'form': form, 'parent_theme': theme.pk}

        else:
            context = {'form': form}

        return render(request, "main/add_theme.html", context)

    def post(self, request):
        is_private = 'is_private' in request.POST
        theme = Themes.objects.get(pk=request.POST['parent_theme']) if request.POST['parent_theme'] else None
        image = request.FILES.get('image')

        theme = Themes.objects.create(
            image=image,
            is_private=is_private,
            user=request.user,
            title=request.POST['title'],
            sub_theme_to=theme
        )
        if not is_private:
            if request.user.get_user_s_subscribers:
                subscribers = request.user.get_user_s_subscribers
                subscribers_email = [sub.subscriber.email for sub in subscribers if
                                     sub.subscriber.is_receive_notifications]

                email_data = {
                    'subject': f'У {request.user.username} новая тема! {request.POST["title"]}',
                    'recipient_list': subscribers_email,
                    'message': f'У {request.user.username} новая тема! {request.POST["title"]}\n'
                               f'это сообщение пришло вам так как вы подписанны на {request.user.username}\n'
                               f'если вы хотите отменить рассылку #TODO()'
                }

                send_notification.delay(email_data)

        return redirect(reverse('main:open_theme', kwargs={'parent_theme': theme.pk}))


# UPDATE/EDIT
class UpdateWithCheckAccessOnGet(UpdateView):
    def get(self, request, *args, **kwargs):
        update_obj = self.get_object()
        if update_obj:
            if not check_access(request.user, update_obj):
                print('доступа нет')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        get = super(UpdateWithCheckAccessOnGet, self).get(request, *args, **kwargs)
        return get


class EditCard(UpdateWithCheckAccessOnGet):
    model = Cards
    form_class = CardForm
    template_name = 'main/change_card.html'

    def get_success_url(self):
        return reverse('main:open_card', kwargs={'card': self.kwargs['pk']})


class EditTheme(UpdateWithCheckAccessOnGet):
    model = Themes
    form_class = ThemeForm
    template_name = 'main/change_theme.html'

    def get_success_url(self):
        return reverse('main:open_theme', kwargs={'parent_theme': self.kwargs['pk']})


def edit_card_comment(request, comment_pk):
    new_content = request.POST['content']
    comment = CardComments.objects.get(pk=comment_pk)
    comment.content = new_content
    comment.save()
    return JsonResponse({'updated_comment': {'pk': comment.pk, 'content': comment.content}})


def edit_theme_comment(request, comment_pk):
    new_content = request.POST['content']
    comment = ThemeComments.objects.get(pk=comment_pk)
    comment.content = new_content
    comment.save()
    return JsonResponse({'updated_comment': {'pk': comment.pk, 'content': comment.content}})


# DELETE
def delete_generic(request, obj, json_answer):
    if check_access(request.user, obj):
        obj.delete()
    else:
        print('Нет доступа')

    return JsonResponse({'deleted_objs': json_answer}, safe=False)


def delete_theme(request, theme_pk):
    obj = Themes.objects.get(pk=theme_pk)
    json_theme = [{'pk': obj.pk}]

    return delete_generic(request, obj, json_theme)


def delete_card(request, card_pk):
    obj = Cards.objects.get(pk=card_pk)
    json_card = [{'pk': obj.pk}]

    return delete_generic(request, obj, json_card)


def delete_comment_from_card(request, comment_pk):
    obj = CardComments.objects.get(pk=comment_pk)
    return delete_generic(request, obj, {'pk': obj.pk})


def delete_comment_from_theme(request, comment_pk):
    obj = ThemeComments.objects.get(pk=comment_pk)
    return delete_generic(request, obj, {'pk': obj.pk})


# LIKES
@ajax_or_api_login_required
def like_generic(request, obj, model, email_data=None):
    like_obj = model.objects.filter(user=request.user, obj=obj).first()
    like_counter = model.objects.filter(obj=obj)

    if like_obj:
        like_obj.delete()
        return JsonResponse({'like': like_counter.count()}, safe=False)

    if email_data:
        if request.user.email in email_data['recipient_list']:
            email_data['recipient_list'].remove(obj.user.email)

        send_notification.delay(email_data)

    model.objects.create(user=request.user, obj=obj)
    return JsonResponse({'like': like_counter.count()}, safe=False)


def like_card(request, card_pk):
    obj = Cards.objects.filter(pk=card_pk).first()

    if obj.user.is_receive_notifications:
        email_data = {

            'subject': f"ваша карточка {obj.title} понравилась {request.user.username}",
            'recipient_list': [obj.user.email],
            'message': f"ваша карточка {obj.title} понравилась {request.user.username}"

        }
    else:
        email_data = None

    return like_generic(request, obj, CardLikes, email_data)


def like_theme(request, theme_pk):
    obj = Themes.objects.filter(pk=theme_pk).first()

    if obj.user.is_receive_notifications:
        email_data = {

            'subject': f"ваша тема {obj.title} понравилась {request.user.username}",
            'recipient_list': [obj.user.email],
            'from_email': settings.EMAIL_HOST_USER,
            'message': f"ваша карточка {obj.title} понравилась {request.user.username}"

        }
    else:
        email_data = None

    return like_generic(request, obj, ThemeLikes, email_data)


# COMMENTS ANSWERS
@ajax_or_api_login_required
def add_comment_generic(request, model, content, obj, sub_comment_to=None, email_data=None):
    if not content:
        print('Коментарий путсым быть не может')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if email_data:
        if request.user.email in email_data['recipient_list']:
            email_data['recipient_list'].remove(request.user.email)

        send_notification.delay(email_data)

    comment = model.objects.create(user=request.user, content=content, obj=obj, sub_comment_to=sub_comment_to)

    comment_json = {'pk': comment.pk, 'content': comment.content,
                    'user': {'pk': comment.user.pk, 'username': comment.user.username},
                    'sub_comment_to': {'pk': sub_comment_to.pk,
                                       'user': sub_comment_to.user.username} if sub_comment_to else None,
                    'request_user': request.user.pk}

    return JsonResponse(
        {'comment': comment_json}, safe=False)


def add_comment_to_theme(request):
    theme = Themes.objects.get(pk=request.POST.get('parent_theme')) if request.POST.get('parent_theme') else None
    content = request.POST['content'] if request.POST['content'] else None
    if theme.user.is_receive_notifications:
        email_data = {
            'subject': f'Пользователь {request.user.username} оставил коментарий вашей теме {theme.title}...',
            'recipient_list': [theme.user.email],
            'message': f'Пользователь {request.user.username} оставил коментарий вашей карточке {theme.title}... \n'
                       f'{content}',
        }
    else:
        email_data = None

    return add_comment_generic(request, ThemeComments, content, theme, email_data=email_data)


def add_comment_to_card(request):
    card = Cards.objects.get(pk=request.POST.get('card')) if request.POST.get('card') else None
    content = request.POST['content'] if request.POST['content'] else None
    email_data = None
    if card.user.is_receive_notifications:
        email_data = {
            'subject': f'Пользователь {request.user.username} оставил коментарий вашей карточке {card.title}...',
            'recipient_list': [card.user.email],
            'message': f'Пользователь {request.user.username} оставил коментарий вашей карточке {card.title}... \n'
                       f'{content}',
        }

    return add_comment_generic(request, CardComments, content, card, email_data=email_data)


def add_comment_to_card_comment(request):
    card = Cards.objects.get(pk=request.POST.get('obj')) if request.POST.get('obj') else None
    comment = CardComments.objects.get(pk=request.POST['comment'][8:]) if request.POST['comment'] else None
    content = request.POST['content'] if request.POST['content'] else None
    if comment.user.is_receive_notifications:
        email_data = {
            'subject': f'Пользователь {request.user.username} ответил на ваш коментарий {comment.content[:10]}...',
            'recipient_list': [comment.user.email],
            'from_email': settings.EMAIL_HOST_USER,
            'message': f'Пользователь {request.user.username} ответил на ваш коментарий {comment.content[:10]}... \n'
                       f'{content}',
        }
    else:
        email_data = None

    return add_comment_generic(request, CardComments, content, card, comment, email_data=email_data)


def add_comment_to_theme_comment(request):
    theme = Themes.objects.get(pk=request.POST.get('obj')) if request.POST.get('obj') else None
    comment = ThemeComments.objects.get(pk=request.POST['comment'][8:]) if request.POST['comment'] else None
    content = request.POST['content'] if request.POST['content'] else None
    if comment.user.is_receive_notifications:
        email_data = {
            'subject': f'Пользователь {request.user.username} ответил на ваш коментарий {comment.content[:10]}...',
            'recipient_list': [comment.user.email],
            'from_email': settings.EMAIL_HOST_USER,
            'message': f'Пользователь {request.user.username} ответил на ваш коментарий {comment.content[:10]}... \n'
                       f'{content}',
        }
    else:
        email_data = None

    return add_comment_generic(request, ThemeComments, content, theme, comment, email_data=email_data)


# ACCESS TO CARD/THEME
def request_access_to_theme(request, user_pk, theme_pk):
    theme = Themes.objects.filter(pk=theme_pk).first()
    link = f'{settings.DOMAIN_NAME}{reverse("main:give_access_to_theme", kwargs={"user_pk": user_pk, "theme_pk": theme_pk})}'

    user = request.user
    access = ThemeAccess.objects.filter(user=user, theme=theme)
    if access.exists():
        return redirect(reverse('main:open_theme', kwargs={'parent_theme': theme_pk}))

    send_notification.delay({
        'subject': f"Пользователь {request.user.username} запрашивает доступ к теме {theme.title}",
        'recipient_list': [theme.user.email],
        'message': f"Пользователь {request.user.username} запрашивает доступ к теме {theme.title} \n"
                   f"что бы выдать доступ перейдите по ссылке: {link}",
    })

    return redirect(reverse('main:index'))


def give_access_to_theme(request, user_pk, theme_pk):
    user = User.objects.get(pk=user_pk)
    theme = Themes.objects.get(pk=theme_pk)

    access = ThemeAccess.objects.filter(user=user, theme=theme)
    if access.exists():
        print('доступ уже есть')
        return redirect(reverse('main:open_theme', kwargs={'parent_theme': theme_pk}))

    ThemeAccess.objects.create(user=user, theme=Themes.objects.get(pk=theme_pk))

    send_notification.delay({

        'subject': f"Пользователь {theme.user.username} выдал вам доступ к теме {theme.title}",
        'recipient_list': [user.email],
        'message': f"Пользователь {theme.user.username} выдал вам доступ к теме {theme.title}",

    })

    return redirect(reverse('main:index'))


def request_access_to_card(request, user_pk, card_pk):
    card = Cards.objects.filter(pk=card_pk).first()
    link = f'{settings.DOMAIN_NAME}{reverse("main:give_access_to_card", kwargs={"user_pk": user_pk, "card_pk": card_pk})}'
    user = request.user

    access = CardAccess.objects.filter(user=user, card=card.pk)
    if access.exists():
        return redirect(reverse('main:open_card', kwargs={'card': card_pk}))

    send_notification.delay({
        'subject': f"Пользователь {request.user.username} запрашивает доступ к карточке {card.title}",
        'recipient_list': [card.user.email],
        'message': f"Пользователь {request.user.username} запрашивает доступ к карточке {card.title} \n"
                   f"что бы выдать доступ перейдите по ссылке: {link}",
    })

    return redirect(reverse('main:index'))


def give_access_to_card(request, user_pk, card_pk):
    user = User.objects.get(pk=user_pk)
    card = Cards.objects.get(pk=card_pk)

    access = CardAccess.objects.filter(user=user, card=card)
    if access.exists():
        return redirect(reverse('main:open_card', kwargs={'card': card_pk}))

    CardAccess.objects.create(user=user, card=Cards.objects.get(pk=card_pk))

    send_notification.delay({

        'subject': f"Пользователь {card.user.username} выдал вам доступ к карточке {card.title}",
        'recipient_list': [user.email],
        'message': f"Пользователь {card.user.username} выдал вам доступ к карточке {card.title}",

    })
    return redirect(reverse('main:index'))


def show_users_list_generic(request, title, users, if_users_is_empty):
    context = {
        'title': title,
        'users': users,
        'if_users_is_empty': if_users_is_empty
    }

    return render(request, 'main/users_list_view.html', context)


def show_users_who_like_theme_list(request, theme_pk):
    users = [User.objects.get(pk=obj.user.pk) for obj in ThemeLikes.objects.filter(obj=theme_pk)]
    return show_users_list_generic(request, f'Кому понравилась тема {Themes.objects.get(pk=theme_pk).title}', users,
                                   'Станте первым кому понравиться тема')


def show_users_who_like_card_list(request, card_pk):
    users = [User.objects.get(pk=obj.user.pk) for obj in CardLikes.objects.filter(obj=card_pk)]
    return show_users_list_generic(request, f'Кому понравилась карточка {Cards.objects.get(pk=card_pk).title}', users,
                                   'Станте первым кому понравиться карточка')


# SEARCH
def global_search(request):
    # TODO(Логика поиска)
    query = request.GET.get('query')
    if query:

        cards = Cards.objects.filter(search_vector=query).filter(is_private=False)[:6]
        themes = Themes.objects.filter(search_vector=query, is_private=False)[:6]
        authors = User.objects.filter(username__icontains=query)[:6]

        if not cards and not themes and not authors:
            context = {

                'massage': "По данному запросу совпадени не найденно"

            }

        else:
            context = {
                'themes': themes,
                'cards': cards,
                'authors': authors
            }

        return render(request, 'main/global_search.html', context)

    else:
        # TODO(Предпочтения)
        context = {

            'themes': Themes.objects.filter(is_private=False, sub_theme_to__isnull=True)[:20],

            'cards': Cards.objects.filter(is_private=False, theme__isnull=True)[:20],

            'authors': User.objects.filter(is_private=False)[:20],

        }
    return render(request, 'main/global_search.html', context)


def global_search_ajax_json(request):
    # TODO(Логика поиска)
    query = request.GET['query']
    if query:
        # Поиск по запросу
        themes = Themes.objects.filter(search_vector=query, is_private=False)[:6]

        cards = Cards.objects.filter(search_vector=query).filter(is_private=False)[:6]

        authors = User.objects.filter(username__icontains=query)[:6]

    else:

        # TODO(ПРЕДПОЧТЕНИЯ)
        # если в запросе пустая строка
        themes = Themes.objects.filter(is_private=False, sub_theme_to__isnull=True)[:20],

        cards = Cards.objects.filter(is_private=False, theme__isnull=True)[:20],

        authors = User.objects.filter(is_private=False)[:20],

    themes_json = list()
    cards_json = list()
    authors_json = list()
    for card in cards:
        cards_json.append(
            {
                'pk': card.pk,
                'image': card.image.url if card.image else "",
                'title': card.title,
                'likes': card.likes,
                'views': card.views,
                'comments': card.count_comments
            }
        )

    for theme in themes:
        themes_json.append(
            {
                'pk': theme.pk,
                'image': theme.image.url if theme.image else "",
                'title': theme.title,
                'likes': theme.likes,
                'views': theme.views,
                'comments': theme.count_comments
            }
        )

    for author in authors:
        authors_json.append(
            {
                'pk': author.pk,
                'username': author.username,
                'image': author.image.url if author.image else "",
                'subscribers_count': author.get_user_s_subscribers_count
            }
        )
    return JsonResponse({'themes': themes_json, 'cards': cards_json, 'authors': authors_json}, safe=False)


def local_search_ajax_json(request):
    # TODO(Логика поиска)
    query = request.GET['query']
    if query:
        # Поиск по запросу
        themes = Themes.objects.filter(search_vector=query, user=request.user)
        cards = Cards.objects.filter(search_vector=query).filter(is_private=False)[:6]

    else:
        # Если в запросе пустая строка
        themes = Themes.get_super_themes_by_user(request.user)
        cards = Cards.get_super_cards_by_user(request.user)

    themes_json = list()
    cards_json = list()
    for card in cards:
        cards_json.append(
            {'pk': card.pk, 'image': card.image.url if card.image else "", 'title': card.title, 'likes': card.likes,
             'views': card.views, 'comments': card.count_comments})

    for theme in themes:
        themes_json.append({'pk': theme.pk, 'image': theme.image.url if theme.image else "", 'title': theme.title,
                            'likes': theme.likes, 'views': theme.views, 'comments': theme.count_comments})

    return JsonResponse({'themes': themes_json, 'cards': cards_json}, safe=False)
