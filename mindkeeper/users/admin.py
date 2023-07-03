from django.contrib import admin
from users.models import *
from main.admin import ThemeInline


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = (ThemeInline,)



