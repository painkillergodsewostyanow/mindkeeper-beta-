from django.contrib import admin
from users.models import *


class ThemeInline(admin.TabularInline):
    model = Themes
    extra = 0


admin.site.register(Cards)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = (ThemeInline,)



