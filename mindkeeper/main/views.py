from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView
from django.shortcuts import render, HttpResponseRedirect, redirect
from .models import *
from .forms import *


class IndexTemplateView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexTemplateView, self).get_context_data()
        if self.request.user.is_authenticated:
            context['themes'] = Themes.get_super_themes_by_user(self.request.user)
        return context

# TODO(сделать дать возможность делать темы и карты приватными)
# TODO(сделать что бы показывались только карточки пользователя в профиле)


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
def open_user_theme(request, theme):
    # TODO(if is_private)
    context = {
        'theme': Themes.objects.filter(pk=theme).first,
        "themes": Themes.objects.filter(sub_theme_to=theme).filter(user=request.user),
        "cards": Cards.objects.filter(theme=theme)
    }

    return render(request, "main/catalog.html", context)


@login_required
def open_user_card(request, card,):
    # TODO(if is_private)
    context = {
        "card": Cards.objects.filter(pk=card).first
    }

    return render(request, "main/card.html", context)


@login_required
def add_card_form(request, theme=None):
    form = AddCardForm()
    return render(request, "main/add_card.html", {'form': form, 'theme': theme,
                                                    'action': 'Добавить карточку',
                                                    })


@login_required
def add_theme_form(request, theme=None):
    form = AddThemeForm()
    return render(request, "main/add_theme.html", {'form': form, 'theme': theme, 'action': 'Добавить тему'})


@login_required
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


@login_required
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


@login_required
def del_theme(request, theme):
    theme = Themes.objects.filter(pk=theme).first()
    if theme:
        theme.delete()

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def del_card(request, card):
    card = Cards.objects.filter(pk=card).first()
    if card:
        card.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def global_search(request):
    # TODO()
    print(request.GET)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
