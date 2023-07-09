from django.db import models

from users.models import User


class Themes(models.Model):
    image = models.ImageField(upload_to="themes_image", blank=True)
    is_private = models.BooleanField(default=False)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="Автор")
    title = models.CharField(max_length=255, verbose_name="Название")
    sub_theme_to = models.ForeignKey(to="self", on_delete=models.CASCADE, blank=True, null=True, verbose_name="Подтема для")

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"

    def __str__(self):
        return f"{self.title}"

    @staticmethod
    def get_super_themes_by_user(user):
        return Themes.objects.filter(user=user, sub_theme_to__isnull=True)

    def users_with_access(self):
        lst_users_with_access = []
        for row in ThemeAccess.objects.filter(theme=self).values('user'):
            lst_users_with_access.append(User.objects.get(pk=row['user']))
        return lst_users_with_access

    def get_sub_themes(self):
        return Themes.objects.filter(sub_theme_to=self)

    def get_cards(self):
        return Cards.objects.filter(theme=self)


class Cards(models.Model):
    # TODO(Возможность выдавать доступ определенным людям)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="Автор")
    image = models.ImageField(upload_to="card_image", blank=True)
    is_private = models.BooleanField(default=False)
    theme = models.ForeignKey(to=Themes, on_delete=models.CASCADE, verbose_name="Тема",
                              blank=True, null=True,
                              )
    title = models.CharField(max_length=255, verbose_name="Название")
    content = models.TextField(verbose_name="Контент")

    class Meta:
        verbose_name = "Карточка"
        verbose_name_plural = "Карточки"

    def __str__(self):
        return f"{self.theme}, {self.title}"

    @staticmethod
    def get_super_cards_by_user(user):
        return Cards.objects.filter(user=user, theme__isnull=True)

    def users_with_access(self):
        lst_users_with_access = []
        for row in CardAccess.objects.filter(card=self).values('user'):
            lst_users_with_access.append(User.objects.get(pk=row['user']))
        return lst_users_with_access


class CardAccess(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    card = models.ForeignKey(to=Cards, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Доступ к карточке'
        verbose_name_plural = 'Доступ к карточкам'

    def __str__(self):
        return f"{self.user}->{self.card}"


class ThemeAccess(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    theme = models.ForeignKey(to=Themes, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Доступ к теме'
        verbose_name_plural = 'Доступ к темам'

    def __str__(self):
        return f"{self.user}->{self.theme}"
