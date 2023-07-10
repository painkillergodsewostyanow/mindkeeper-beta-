from django import forms
from .models import *


class CardForm(forms.ModelForm):
    class Meta:
        model = Cards
        fields = ('image', 'is_private', 'title', 'content')


class ThemeForm(forms.ModelForm):
    class Meta:
        model = Themes
        fields = ('image', 'is_private', 'title',)
