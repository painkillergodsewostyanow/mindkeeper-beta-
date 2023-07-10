from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView, UpdateView
from django.shortcuts import render, HttpResponseRedirect, redirect
from .models import *
from .forms import *
from django.urls import reverse
from .scripts import check_access


class IndexTemplateView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexTemplateView, self).get_context_data()
        if self.request.user.is_authenticated:
            context['super_themes'] = Themes.get_super_themes_by_user(self.request.user)
        return context


@login_required
def super_theme_and_card_list_view(request):
    if request.user.is_authenticated:
        return render(request, "main/catalog.html", {
            "themes": Themes.get_super_themes_by_user(request.user),
            "cards": Cards.get_super_cards_by_user(request.user)
        })
    else:
        return render(request, "main/catalog.html")


# class SuperThemeListView(ListView):
#     model = Themes
#     template_name = "main/catalog.html"
#     context_object_name = "themes"
#
#     def get_queryset(self):
#         queryset = Themes.get_super_themes_by_user(user=self.request.user)
#         return queryset


@login_required
def open_theme(request, theme):
    father_theme = theme
    theme = Themes.objects.filter(pk=theme).first()

    context = {
        'father_theme': Themes.objects.filter(pk=father_theme).first,
        "themes": Themes.objects.filter(sub_theme_to=theme),
        "cards": Cards.objects.filter(theme=theme)
    }

    if theme:
        if theme.is_private:
            if not check_access(request.user, to=theme, users_with_access=theme.users_with_access()):
                context = {
                    'message': 'у вас нет доступа, запросить: # TODO()'  # TODO()
                }
    else:
        pass  # TODO(404)

    return render(request, "main/catalog.html", context)


@login_required
def open_card(request, card):
    card = Cards.objects.filter(pk=card).first()
    context = {'card': card}
    if card:
        if card.is_private:
            if not check_access(request.user, to=card, users_with_access=card.users_with_access()):
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
                   'HTTP_REFERER': request.META.get('HTTP_REFERER', '')}

    else:
        context = {'form': form,
                   'action': 'Добавить карточку',
                   'HTTP_REFERER': request.META.get('HTTP_REFERER', '')}

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
                   'HTTP_REFERER': request.META.get('HTTP_REFERER', '')}

    else:
        context = {'form': form,
                   'action': 'Добавить тему',
                   'HTTP_REFERER': request.META.get('HTTP_REFERER', '')}

    return render(request, "main/add_theme.html", context)


@login_required
def add_card(request):
    is_private = 'is_private' in request.POST
    theme = Themes.objects.get(pk=request.POST['theme']) if request.POST['theme'] else None
    image = request.FILES.get('image', None)

    Cards.objects.create(
        user=request.user,
        image=image,
        is_private=is_private,
        theme=theme,
        title=request.POST['title'], content=request.POST['content']
    )

    return HttpResponseRedirect(
        request.POST['HTTP_REFERER'] if request.POST['HTTP_REFERER'] else reverse('main:storage')
    )


@login_required
def add_theme(request):
    is_private = 'is_private' in request.POST
    theme = Themes.objects.get(pk=request.POST['theme']) if request.POST['theme'] else None
    image = request.FILES.get('image', None)

    Themes.objects.create(
        image=image,
        is_private=is_private,
        user=request.user,
        title=request.POST['title'],
        sub_theme_to=theme
    )

    return HttpResponseRedirect(
        request.POST['HTTP_REFERER'] if request.POST['HTTP_REFERER'] else reverse('main:storage')
    )


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
    # TODO(Глобальный динамический поиск)
    print(request.GET)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
