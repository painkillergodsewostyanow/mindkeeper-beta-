from django_summernote.widgets import SummernoteWidget
from django import forms
from .models import *


class CardForm(forms.ModelForm):
    class Meta:
        widgets = {
            'content': SummernoteWidget(attrs={'class': 'summernote_class'}),
            'image': forms.FileInput()
        }
        model = Cards
        fields = ('image', 'is_private', 'title', 'content')


class ThemeForm(forms.ModelForm):
    class Meta:
        model = Themes
        widgets = {
            'image': forms.FileInput()
        }
        fields = ('image', 'is_private', 'title',)
