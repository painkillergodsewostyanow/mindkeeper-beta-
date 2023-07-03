from django.views.generic import TemplateView, ListView
from django.shortcuts import render, HttpResponseRedirect, redirect
from .models import *
from .forms import *


class IndexTemplateView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexTemplateView, self).get_context_data()
        context['themes'] = Themes.get_super_themes_by_user(self.request.user)
        return context

# TODO(сделать дать возможность делать темы и карты приватными)
# TODO(сделать что бы показывались только карточки пользователя в профиле)


def super_theme_and_card_list_view(request):
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
    # TODO(if is_private)
    context = {
        'theme': Themes.objects.filter(pk=theme).first,
        "themes": Themes.objects.filter(sub_theme_to=theme).filter(user=request.user),
        "cards": Cards.objects.filter(theme=theme)
    }

    return render(request, "main/catalog.html", context)


def open_card(request, card,):
    # TODO(if is_private)
    context = {
        "card": Cards.objects.filter(pk=card).first
    }

    return render(request, "main/card.html", context)


def add_card_form(request, theme=None):
    form = AddCardForm()
    return render(request, "main/add_card.html", {'form': form, 'theme': theme,
                                                    'action': 'Добавить карточку',
                                                    })


def add_theme_form(request, theme=None):
    form = AddThemeForm()
    return render(request, "main/add_theme.html", {'form': form, 'theme': theme, 'action': 'Добавить тему'})


def add_card(request):
    is_private = 'is_private' in request.POST
    theme = Themes.objects.get(pk=request.POST['theme']) if request.POST['theme'] != 'None' else None
    image = request.FILES.get('image', None)
    Cards.objects.create(
        user=request.user,
        image=image,
        is_private=is_private,
        theme=theme,
        title=request.POST['title'], content=request.POST['content']
    )

    # TODO(редиректить обратно)
    return redirect('main:index')


def add_theme(request):
    is_private = 'is_private' in request.POST
    theme = Themes.objects.get(pk=request.POST['theme']) if request.POST['theme'] != 'None' else None
    image = request.FILES.get('image', None)
    Themes.objects.create(
        image=image,
        is_private=is_private,
        user=request.user,
        title=request.POST['title'],
        sub_theme_to=theme
    )
    return redirect('main:index')


def del_theme(request, theme):
    theme = Themes.objects.filter(pk=theme).first()
    if theme:
        theme.delete()

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def del_card(request, card):
    card = Cards.objects.filter(pk=card).first()
    if card:
        card.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
