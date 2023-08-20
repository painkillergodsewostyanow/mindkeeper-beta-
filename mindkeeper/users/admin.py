from main.admin import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = (ThemeInline, CardInline, CardCommentsInline, ThemeCommentsInline, CardAccessInline, ThemeAccessInline)



