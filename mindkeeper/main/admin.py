from django.contrib import admin
from .models import *


class ThemeInline(admin.TabularInline):
    model = Themes
    extra = 0


class CardInline(admin.TabularInline):
    model = Cards
    extra = 0


class CardAccessInline(admin.TabularInline):
    model = CardAccess
    extra = 0


class ThemeAccessInline(admin.TabularInline):
    model = ThemeAccess
    extra = 0
