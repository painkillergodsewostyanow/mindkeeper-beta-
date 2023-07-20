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


# class SuperThemeListView(ListView):
#     model = Themes
#     template_name = "main/catalog.html"
#     context_object_name = "themes"
#
#     def get_queryset(self):
#         queryset = Themes.get_super_themes_by_user(user=self.request.user)
#         return queryset


def open_theme(request, theme):
    father_theme = theme
    theme = Themes.objects.filter(pk=theme).first()
    if request.user.is_authenticated:
        if not ThemeViews.objects.filter(theme=theme, user=request.user).first():
            ThemeViews.objects.create(theme=theme, user=request.user)

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
        if not CardViews.objects.filter(card=card, user=request.user).first():
            CardViews.objects.create(card=card, user=request.user)

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

    return redirect(reverse('main:open_theme', kwargs={'theme': theme.pk}))


class EditCard(UpdateView):
    model = Cards
    form_class = CardForm
    template_name = 'main/change_card.html'

    def get_success_url(self):
        return reverse('main:storage')

    def post(self, request, *args, **kwargs):
        card = Cards.objects.get(pk=kwargs['pk'])
        if card:
            if not check_access(request.user, card):
                print('доступа нет')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('main:storage')))

        post = super(EditCard, self).post(request, *args, **kwargs)
        return post


class EditTheme(UpdateView):
    model = Themes
    form_class = ThemeForm
    template_name = 'main/change_theme.html'

    def get_success_url(self):
        return reverse('main:storage')

    def post(self, request, *args, **kwargs):
        theme = Themes.objects.get(pk=kwargs['pk'])
        if theme:
            if not check_access(request.user, theme):
                print('доступа нет')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('main:storage')))

        post = super(EditTheme, self).post(request, *args, **kwargs)
        return post


@login_required
def del_theme(request, theme):
    theme = Themes.objects.filter(pk=theme).first()

    if theme:
        if check_access(request.user, theme):
            theme.delete()
        else:
            print("Нет доступа")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('main:storage')))


@login_required
def del_card(request, card):
    card = Cards.objects.filter(pk=card).first()
    if card:
        if check_access(request.user, card):
            card.delete()
        else:
            print("Нет доступа")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('main:storage')))


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


# TODO(AJAX)
@login_required
def card_like(request, card_pk):
    card = Cards.objects.filter(pk=card_pk).first()
    like_obj = CardLikes.objects.filter(user=request.user, card=card)
    if like_obj.exists():
        like_obj.delete()
        print('удаление')
        return JsonResponse({'like': CardLikes.objects.filter(card=card_pk).count()}, safe=False)

    print('создание')
    CardLikes.objects.create(user=request.user, card=card)
    return JsonResponse({'like': CardLikes.objects.filter(card=card_pk).count()}, safe=False)


# TODO(AJAX)
@login_required
def theme_like(request, theme_pk):
    theme = Themes.objects.filter(pk=theme_pk).first()
    like_obj = ThemeLikes.objects.filter(user=request.user, theme=theme)
    if like_obj.exists():
        like_obj.delete()
        print('удаление')
        return JsonResponse({'like': ThemeLikes.objects.filter(theme=theme_pk).count()}, safe=False)

    print('создание')
    ThemeLikes.objects.create(user=request.user, theme=theme)
    return JsonResponse({'like': ThemeLikes.objects.filter(theme=theme_pk).count()}, safe=False)


# TODO(AJAX)
@login_required
def add_comment_to_theme(request):
    theme = Themes.objects.get(pk=request.POST['theme'])
    content = request.POST['content'] if request.POST['content'] else None
    if not content:
        print('Коментарий путсым быть не может')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('main:storage')))

    ThemeComments.objects.create(user=request.user, content=content, theme=theme)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('main:storage')))


@login_required
def del_comment_from_theme(request, comment_pk):
    comment = ThemeComments.objects.filter(pk=comment_pk).first()
    if comment.user == request.user:
        comment.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('main:storage')))
    print('Нет доступа')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('main:storage')))


@login_required
def add_comment_to_card(request):
    card = Cards.objects.get(pk=request.POST['card'])
    content = request.POST['content'] if request.POST['content'] else None
    if not content:
        print('Коментарий путсым быть не может')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('main:storage')))

    CardComments.objects.create(user=request.user, content=content, card=card)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('main:storage')))


@login_required
def del_comment_from_card(request, comment_pk):
    comment = CardComments.objects.filter(pk=comment_pk).first()
    if comment.user == request.user:
        comment.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('main:storage')))
    print('Нет доступа')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('main:storage')))
