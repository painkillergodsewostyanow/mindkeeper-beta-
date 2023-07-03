from django.contrib import admin
from .models import *

class ThemeInline(admin.TabularInline):
    model = Themes
    extra = 0


admin.site.register(Cards)
