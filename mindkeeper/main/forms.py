from django import forms
from .models import *


class AddCardForm(forms.ModelForm):
    class Meta:
        model = Cards
        fields = ('image', 'is_private', 'title', 'content')


class AddThemeForm(forms.ModelForm):
    class Meta:
        model = Themes
        fields = ('image', 'is_private', 'title',)
