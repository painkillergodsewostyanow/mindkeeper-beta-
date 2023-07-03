from django.db import models

from users.models import User


class Themes(models.Model):
    image = models.ImageField(upload_to="themes_image", blank=True)
    is_private = models.BooleanField(default=False)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="Автор")
    title = models.CharField(max_length=255, verbose_name="Название")
    sub_theme_to = models.ForeignKey(to="self", on_delete=models.CASCADE, blank=True, null=True, verbose_name="Подтема для")

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"

    @staticmethod
    def get_super_themes_by_user(user):
        return Themes.objects.filter(user=user, sub_theme_to__isnull=True)


class Cards(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="Автор")
    image = models.ImageField(upload_to="card_image", blank=True)
    is_private = models.BooleanField(default=False)
    theme = models.ForeignKey(to=Themes, on_delete=models.CASCADE, verbose_name="Тема",
                              blank=True, null=True,
                              )
    title = models.CharField(max_length=255, verbose_name="Название")
    content = models.TextField(verbose_name="Контент")

    def __str__(self):
        return f"{self.theme}, {self.title}"

    class Meta:
        verbose_name = "Карточка"
        verbose_name_plural = "Карточки"

    @staticmethod
    def get_super_cards_by_user(user):
        return Cards.objects.filter(user=user, theme__isnull=True)
