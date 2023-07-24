from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.http import JsonResponse
from django.views.generic import TemplateView, UpdateView
from django.shortcuts import render, HttpResponseRedirect, redirect
from .forms import *
from django.urls import reverse
from .scripts import check_access


class IndexTemplateView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexTemplateView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['super_themes'] = Themes.get_super_themes_by_user(self.request.user)
            context['super_cards'] = Cards.get_super_cards_by_user(self.request.user)

        return context


@login_required
def storage(request):
    if request.GET.get('query', False):
        context = {

            'themes': set(list(Themes.objects.filter(title__icontains=request.GET['query'], user=request.user)) + list(
                Themes.objects.filter(sub_theme_to__in=Themes.objects.filter(title__icontains=request.GET['query'],
                                                                             user=request.user))) + list(
                Themes.objects.filter(title__icontains=request.GET['query'], user=request.user,
                                      sub_theme_to__isnull=True))),

            'cards': Cards.objects.filter(Q(title__icontains=request.GET['query']) |
                                          Q(content__icontains=request.GET['query']))
            .filter(user=request.user)

        }

    else:
        context = {

            "themes": Themes.get_super_themes_by_user(request.user),
            "cards": Cards.get_super_cards_by_user(request.user)

        }

    return render(request, "main/catalog.html", context)


def open_theme(request, theme):
    father_theme = theme
    theme = Themes.objects.filter(pk=theme).first()
    if request.user.is_authenticated:
        if not ThemeViews.objects.filter(obj=theme, user=request.user).first():
            ThemeViews.objects.create(obj=theme, user=request.user)

    context = {
        'father_theme': Themes.objects.filter(pk=father_theme).first(),
        "themes": Themes.objects.filter(sub_theme_to=theme),
        "cards": Cards.objects.filter(theme=theme)
    }

    if theme:
        if theme.is_private:
            if not check_access(request.user, to=theme, users_with_access=theme.users_with_access):
                context = {
                    'message': 'у вас нет доступа, запросить: # TODO()'  # TODO()
                }
    else:
        pass  # TODO(404)

    return render(request, "main/catalog.html", context)


def open_card(request, card):
    card = Cards.objects.filter(pk=card).first()
    if request.user.is_authenticated:
        if not CardViews.objects.filter(obj=card, user=request.user).first():
            CardViews.objects.create(obj=card, user=request.user)

    context = {'card': card}
    if card:
        if card.is_private:
            if not check_access(request.user, to=card, users_with_access=card.users_with_access):
                context = {
                    'message': 'у вас нет доступа, запросить: # TODO()'  # TODO()
                }
    else:
        pass  # TODO(404)

    return render(request, "main/card.html", context)


@login_required
def add_card_form(request, theme=None):
    theme = Themes.objects.filter(pk=theme).first()
    form = CardForm()
    if theme:
        if not check_access(request.user, theme):
            print('доступа нет')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('main:storage')))

        context = {'form': form, 'theme': theme.pk,
                   'action': 'Добавить карточку',
                   }

    else:
        context = {'form': form,
                   'action': 'Добавить карточку',
                   }

    return render(request, "main/add_card.html", context)


@login_required
def add_theme_form(request, theme=None):
    theme = Themes.objects.filter(pk=theme).first()
    form = ThemeForm()
    if theme:
        if not check_access(request.user, theme):
            print('доступа нет')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('main:storage')))

        context = {'form': form, 'theme': theme.pk,
                   'action': 'Добавить тему',
                   }

    else:
        context = {'form': form,
                   'action': 'Добавить тему',
                   }

    return render(request, "main/add_theme.html", context)


@login_required
def add_card(request):
    is_private = 'is_private' in request.POST
    theme = Themes.objects.get(pk=request.POST['theme']) if request.POST['theme'] else None
    image = request.FILES.get('image', None)

    card = Cards.objects.create(
        user=request.user,
        image=image,
        is_private=is_private,
        theme=theme,
        title=request.POST['title'], content=request.POST['content']
    )

    # TODO(Уведомить подписчиков)

    return redirect(reverse('main:open_card', kwargs={'card': card.pk}))


@login_required
def add_theme(request):
    is_private = 'is_private' in request.POST
    theme = Themes.objects.get(pk=request.POST['theme']) if request.POST['theme'] else None
    image = request.FILES.get('image', None)

    theme = Themes.objects.create(
        image=image,
        is_private=is_private,
        user=request.user,
        title=request.POST['title'],
        sub_theme_to=theme
    )

    # TODO(Уведомить подписчиков)

    return redirect(reverse('main:open_theme', kwargs={'theme': theme.pk}))


class UpdateWithCheckAccessOnGet(UpdateView):
    def get(self, request, *args, **kwargs):
        update_obj = self.get_object()
        if update_obj:
            if not check_access(request.user, update_obj):
                print('доступа нет')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('main:storage')))

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
        return reverse('main:open_theme', kwargs={'theme': self.kwargs['pk']})


@login_required
def delete_generic(request, model, object_pk):
    obj = model.objects.filter(pk=object_pk).first()
    if obj:
        if check_access(request.user, obj):
            obj.delete()
        else:
            print('Нет доступа')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('main:storage')))


def delete_theme(request, theme_pk):
    return delete_generic(request, Themes, theme_pk)


def delete_card(request, card_pk):
    return delete_generic(request, Cards, card_pk)


def delete_comment_from_card(request, comment_pk):
    return delete_generic(request, CardComments, comment_pk)


def delete_comment_from_theme(request, comment_pk):
    return delete_generic(request, ThemeComments, comment_pk)


@login_required
def like_generic(request, obj, model):
    like_obj = model.objects.filter(user=request.user, obj=obj).first()
    like_counter = model.objects.filter(obj=obj)

    if like_obj:
        like_obj.delete()
        print('Удаление')
        return JsonResponse({'like': like_counter.count()}, safe=False)

    model.objects.create(user=request.user, obj=obj)
    print('создание')

    return JsonResponse({'like': like_counter.count()}, safe=False)


# TODO(AJAX)
@login_required
def like_card(request, card_pk):
    obj = Cards.objects.filter(pk=card_pk).first()
    return like_generic(request, obj, CardLikes)


def like_theme(request, theme_pk):
    obj = Themes.objects.filter(pk=theme_pk).first()
    return like_generic(request, obj, ThemeLikes)


@login_required
def add_comment_generic(request, model, content, obj, sub_comment_to=None):
    if not content:
        print('Коментарий путсым быть не может')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('main:storage')))

    model.objects.create(user=request.user, content=content, obj=obj, sub_comment_to=sub_comment_to)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('main:storage')))


def add_comment_to_theme(request):
    theme = Themes.objects.get(pk=request.POST['theme']) if request.POST.get('theme') else None
    content = request.POST['content'] if request.POST['content'] else None
    return add_comment_generic(request, ThemeComments, content, theme)


def add_comment_to_card(request):
    card = Cards.objects.get(pk=request.POST['card']) if request.POST.get('card') else None
    content = request.POST['content'] if request.POST['content'] else None
    return add_comment_generic(request, CardComments, content, card)


def add_comment_to_card_comment(request):
    card = Cards.objects.get(pk=request.POST['obj']) if request.POST.get('obj') else None
    comment = CardComments.objects.get(pk=request.POST['comment']) if request.POST['comment'] else None
    content = request.POST['content'] if request.POST['content'] else None
    return add_comment_generic(request, CardComments, content, card, comment)


def add_comment_to_theme_comment(request):
    theme = Themes.objects.get(pk=request.POST['obj']) if request.POST.get('obj') else None
    comment = ThemeComments.objects.get(pk=request.POST['comment']) if request.POST['comment'] else None
    content = request.POST['content'] if request.POST['content'] else None
    return add_comment_generic(request, ThemeComments, content, theme, comment)


# SEARCH
def global_search(request):
    # TODO(Логика поиска)

    if request.GET.get('query', False):
        context = {
            'themes': Themes.objects.filter(title__icontains=request.GET['query'], is_private=False),

            'cards': Cards.objects.filter(
                Q(title__icontains=request.GET['query']) | Q(content__icontains=request.GET['query']))
            .filter(is_private=False)
        }
    else:
        # TODO(Предпочтения)
        context = {

            'themes': Themes.objects.filter(is_private=False)[:20],

            'cards': Cards.objects.filter(is_private=False)[:20]

        }
    return render(request, 'main/global_search.html', context)


def global_search_ajax_json(request):
    # TODO(Логика поиска)
    themes = list(Themes.objects.filter(title__icontains=request.GET['query'])
                  .filter(is_private=False)
                  .values('pk', 'image', 'title'))

    cards = list(Cards.objects.filter(
        Q(title__icontains=request.GET['query']) |
        Q(content__icontains=request.GET['query'])
    ).filter(is_private=False)
                 .distinct()
                 .values('pk', 'image', 'title'))

    return JsonResponse({'themes': themes, 'cards': cards}, safe=False)


def local_search_ajax_json(request):
    # TODO(Логика поиска)
    themes = list(Themes.objects.filter(title__icontains=request.GET['query'])
                  .values('pk', 'image', 'title'))

    cards = list(Cards.objects.filter(
        Q(title__icontains=request.GET['query']) |
        Q(content__icontains=request.GET['query'])
    )
                 .distinct()
                 .values('pk', 'image', 'title'))

    return JsonResponse({'themes': themes, 'cards': cards}, safe=False)
